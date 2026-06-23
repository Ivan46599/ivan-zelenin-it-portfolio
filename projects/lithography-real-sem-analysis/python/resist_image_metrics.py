"""Analysis of real SEM/TIF photoresist images for CD, LER and LWR.

The original course code worked with a synthetic height map.  Real SEM images are
not height maps: they are grayscale intensity images with several vertical
photoresist features.  This module therefore adds the missing steps:

1. read a TIFF image;
2. remove the black microscope footer from the analysis crop;
3. estimate nm/px from the 100 nm scale bar in the footer;
4. normalize SEM contrast;
5. find dark or bright vertical features;
6. extract left and right edges row by row;
7. calculate CD, LWR and LER.

NILS is not calculated here because a SEM image of developed resist does not
contain the optical intensity profile I(x).  NILS must be calculated from an
optical/air-image intensity simulation or from measured intensity data.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import csv
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d, label, find_objects
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt


@dataclass
class RealImageAnalysisParams:
    """Parameters controlling real SEM image processing."""

    feature_polarity: str = "dark"    # "dark" for the supplied developed bands; "bright" for bright ridges.
    scale_bar_nm: float = 100.0       # The uploaded SEM images contain a 100 nm scale bar.
    scale_nm_per_px: float | None = None  # If known from microscope metadata, set it directly.
    top_crop_px: int = 70             # Removes the green label and top overlay area from the SEM image.
    peak_distance_px: int = 25        # Minimum distance between neighboring vertical features.
    edge_margin_px: int = 15          # Rejects partial features touching left/right image borders.
    min_width_nm: float = 3.0         # Rejects very small noise components.
    max_width_nm: float = 70.0        # Rejects background regions that are too wide to be one line.
    min_valid_fraction: float = 0.30  # A line must be detected in at least this fraction of rows.
    background_sigma_px: float = 30.0 # Broad illumination/background correction.
    smooth_sigma_y_px: float = 1.0    # SEM noise smoothing along the line.
    smooth_sigma_x_px: float = 1.2    # SEM noise smoothing across the line.


def estimate_scale_bar_px(rgb_image: Image.Image) -> Tuple[float | None, List[Tuple[int, int, int, int, int, int]]]:
    """Estimate the pixel length of the green scale bar in the microscope footer.

    The footer of the supplied images has a green horizontal bar labelled 100 nm.
    The longest green horizontal component in the bottom part of the image is
    used as the scale bar.  For the supplied files this gives 138 px, so the
    calibration is 100 / 138 = 0.7246 nm/px.
    """

    rgb = np.asarray(rgb_image.convert("RGB"))
    green_mask = (rgb[:, :, 1] > 120) & (rgb[:, :, 0] < 100) & (rgb[:, :, 2] < 100)
    height, _ = green_mask.shape
    green_mask[: int(0.8 * height), :] = False

    labeled, n_labels = label(green_mask)
    objects = find_objects(labeled)
    components: List[Tuple[int, int, int, int, int, int]] = []

    for component_id, component_slice in enumerate(objects, start=1):
        if component_slice is None:
            continue
        yy, xx = component_slice
        area = int((labeled[component_slice] == component_id).sum())
        width = int(xx.stop - xx.start)
        height_px = int(yy.stop - yy.start)
        if area > 30 and width > 80 and height_px < 25:
            components.append((width, area, int(xx.start), int(xx.stop - 1), int(yy.start), int(yy.stop - 1)))

    components.sort(key=lambda item: (item[0], item[1]), reverse=True)
    if not components:
        return None, []
    return float(components[0][0]), components


def read_grayscale_image(path: Path) -> Tuple[Image.Image, np.ndarray]:
    """Read an image and return RGB PIL image plus grayscale numpy array."""

    rgb = Image.open(path).convert("RGB")
    gray = np.asarray(rgb.convert("L"), dtype=np.float64)
    return rgb, gray


def crop_sem_area(gray: np.ndarray, top_crop_px: int = 70) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """Remove the black microscope footer and the top label area.

    Returns the crop and a bbox tuple (top, left, bottom, right) in original image
    coordinates.  The black footer is detected automatically by row intensity.
    """

    image_height, image_width = gray.shape
    row_mean = gray.mean(axis=1)
    lower_rows = np.arange(int(0.65 * image_height), image_height)
    footer_candidates = lower_rows[row_mean[lower_rows] < 30]
    bottom = int(footer_candidates[0]) if footer_candidates.size else int(0.95 * image_height)
    top = min(int(top_crop_px), bottom - 100)
    top = max(top, 0)
    return gray[top:bottom, :], (top, 0, bottom, image_width)


def preprocess_sem_crop(crop: np.ndarray, params: RealImageAnalysisParams) -> Tuple[np.ndarray, np.ndarray]:
    """Normalize a SEM crop and convert it to a feature score image.

    For bright lines, the score is high where pixels are bright.  For dark lines
    or trenches, the score is high where pixels are dark.
    """

    background = gaussian_filter(crop, sigma=params.background_sigma_px)
    corrected = crop - background + np.median(background)
    smoothed = gaussian_filter(corrected, sigma=(params.smooth_sigma_y_px, params.smooth_sigma_x_px))

    low, high = np.percentile(smoothed, [1, 99])
    normalized = np.clip((smoothed - low) / (high - low + 1e-12), 0.0, 1.0)

    if params.feature_polarity == "bright":
        score = normalized
    elif params.feature_polarity == "dark":
        score = 1.0 - normalized
    else:
        raise ValueError("feature_polarity must be 'bright' or 'dark'")

    return score, normalized


def _linear_crossing(x0: float, y0: float, x1: float, y1: float, threshold: float) -> float:
    """Linearly interpolate a threshold crossing between two samples."""

    if y1 == y0:
        return 0.5 * (x0 + x1)
    return x0 + (threshold - y0) * (x1 - x0) / (y1 - y0)


def _edges_near_peak(
    row: np.ndarray,
    center_px: float,
    threshold: float,
    half_window_px: int,
    min_width_px: float,
    max_width_px: float,
) -> Tuple[float, float, float, float] | None:
    """Find left/right threshold crossings around one nominal feature center."""

    n_points = len(row)
    center_index = int(round(center_px))
    left_limit = max(0, center_index - half_window_px)
    right_limit = min(n_points - 1, center_index + half_window_px)

    local = row[left_limit : right_limit + 1]
    above = local >= threshold
    runs: List[Tuple[int, int, float, int]] = []

    index = 0
    while index < len(above):
        if not above[index]:
            index += 1
            continue
        start = index
        while index < len(above) and above[index]:
            index += 1
        end = index - 1
        start_global = left_limit + start
        end_global = left_limit + end
        center_global = 0.5 * (start_global + end_global)
        width_global = end_global - start_global + 1
        runs.append((start_global, end_global, center_global, width_global))

    if not runs:
        return None

    start, end, _, width = min(runs, key=lambda item: abs(item[2] - center_px))
    if width < min_width_px or width > max_width_px:
        return None

    left_edge = float(start)
    right_edge = float(end)

    if start > 0:
        left_edge = _linear_crossing(start - 1, row[start - 1], start, row[start], threshold)
    if end < n_points - 1:
        right_edge = _linear_crossing(end + 1, row[end + 1], end, row[end], threshold)

    final_width = right_edge - left_edge
    if final_width < min_width_px or final_width > max_width_px:
        return None

    return left_edge, right_edge, 0.5 * (left_edge + right_edge), final_width


def detect_feature_specs(score: np.ndarray, params: RealImageAnalysisParams, scale_nm_per_px: float) -> List[Dict[str, float]]:
    """Detect nominal vertical feature centers from the average horizontal profile."""

    average_profile = gaussian_filter1d(score.mean(axis=0), 3.0)
    prominence = max(0.025, 0.20 * float(np.std(average_profile)))
    peaks, properties = find_peaks(average_profile, distance=params.peak_distance_px, prominence=prominence)
    widths_px, width_heights, left_ips, right_ips = peak_widths(average_profile, peaks, rel_height=0.5)

    min_width_px = params.min_width_nm / scale_nm_per_px
    max_width_px = params.max_width_nm / scale_nm_per_px
    image_width = score.shape[1]
    specs: List[Dict[str, float]] = []

    for peak, width_px, width_height, left_ip, right_ip, prominence_px in zip(
        peaks, widths_px, width_heights, left_ips, right_ips, properties["prominences"]
    ):
        if peak < params.edge_margin_px or peak > image_width - params.edge_margin_px:
            continue
        if left_ip < params.edge_margin_px or right_ip > image_width - params.edge_margin_px:
            continue
        if min_width_px <= width_px <= max_width_px:
            specs.append(
                {
                    "raw_line_id": float(len(specs) + 1),
                    "center_px": float(peak),
                    "initial_width_px": float(width_px),
                    "threshold_score": float(width_height),
                    "left_ip_px": float(left_ip),
                    "right_ip_px": float(right_ip),
                    "prominence": float(prominence_px),
                    "profile_peak_score": float(average_profile[peak]),
                }
            )

    return specs


def _detrended_std(y_nm: np.ndarray, edge_nm: np.ndarray) -> float:
    """Standard deviation of edge position after removing a linear trend."""

    if len(y_nm) < 3:
        return float("nan")
    polynomial = np.polyfit(y_nm, edge_nm, 1)
    trend = np.polyval(polynomial, y_nm)
    return float(np.std(edge_nm - trend, ddof=1))


def analyze_real_image(path: Path, params: RealImageAnalysisParams) -> Dict[str, object]:
    """Analyze one SEM image and return metrics, edge arrays and diagnostic data."""

    rgb, gray = read_grayscale_image(path)
    scale_bar_px, scale_components = estimate_scale_bar_px(rgb)

    if params.scale_nm_per_px is not None:
        scale_nm_per_px = float(params.scale_nm_per_px)
    elif scale_bar_px is not None:
        scale_nm_per_px = params.scale_bar_nm / scale_bar_px
    else:
        # Fallback for the supplied images if the green scale bar cannot be found.
        scale_nm_per_px = params.scale_bar_nm / 138.0

    crop, bbox = crop_sem_area(gray, params.top_crop_px)
    score, normalized = preprocess_sem_crop(crop, params)
    specs = detect_feature_specs(score, params, scale_nm_per_px)

    image_height, _ = score.shape
    min_width_px = params.min_width_nm / scale_nm_per_px
    max_width_px = params.max_width_nm / scale_nm_per_px

    per_line_metrics: List[Dict[str, float]] = []
    section_rows: List[Dict[str, float]] = []

    for spec in specs:
        initial_width_px = max(spec["initial_width_px"], min_width_px)
        half_window_px = int(max(8, min(max_width_px * 1.2, initial_width_px * 2.5)))
        min_row_width_px = max(1.5, 0.7 * min_width_px)
        max_row_width_px = max_width_px

        left_edges_nm: List[float] = []
        right_edges_nm: List[float] = []
        y_values_nm: List[float] = []
        current_center_px = spec["center_px"]

        for row_index in range(image_height):
            extracted = _edges_near_peak(
                score[row_index],
                current_center_px,
                spec["threshold_score"],
                half_window_px,
                min_row_width_px,
                max_row_width_px,
            )
            if extracted is None:
                continue
            left_px, right_px, center_px, _ = extracted
            current_center_px = 0.98 * current_center_px + 0.02 * center_px
            left_edges_nm.append(left_px * scale_nm_per_px)
            right_edges_nm.append(right_px * scale_nm_per_px)
            y_values_nm.append(row_index * scale_nm_per_px)

        if len(y_values_nm) < params.min_valid_fraction * image_height:
            continue

        left_edges = np.asarray(left_edges_nm)
        right_edges = np.asarray(right_edges_nm)
        y_values = np.asarray(y_values_nm)
        widths = right_edges - left_edges

        median_width = float(np.median(widths))
        mad = float(np.median(np.abs(widths - median_width))) + 1e-12
        keep = np.abs(widths - median_width) <= 4.0 * 1.4826 * mad

        left_edges = left_edges[keep]
        right_edges = right_edges[keep]
        y_values = y_values[keep]
        widths = widths[keep]

        if len(y_values) < params.min_valid_fraction * image_height:
            continue

        lwr_sigma = float(np.std(widths, ddof=1))
        ler_left_sigma = _detrended_std(y_values, left_edges)
        ler_right_sigma = _detrended_std(y_values, right_edges)
        ler_avg_sigma = 0.5 * (ler_left_sigma + ler_right_sigma)
        line_id = len(per_line_metrics) + 1

        metrics = {
            "line_id": float(line_id),
            "n_sections": float(len(widths)),
            "valid_fraction": float(len(widths) / image_height),
            "center_nm": float(0.5 * (np.median(left_edges) + np.median(right_edges))),
            "CD_mean_nm": float(np.mean(widths)),
            "CD_median_nm": float(np.median(widths)),
            "LWR_sigma_nm": lwr_sigma,
            "LWR_3sigma_nm": 3.0 * lwr_sigma,
            "LER_left_sigma_nm": ler_left_sigma,
            "LER_right_sigma_nm": ler_right_sigma,
            "LER_avg_sigma_nm": ler_avg_sigma,
            "LER_avg_3sigma_nm": 3.0 * ler_avg_sigma,
            "threshold_score": float(spec["threshold_score"]),
            "initial_width_nm": float(spec["initial_width_px"] * scale_nm_per_px),
        }
        per_line_metrics.append(metrics)

        for y_nm, left_nm, right_nm, width_nm in zip(y_values, left_edges, right_edges, widths):
            section_rows.append(
                {
                    "line_id": float(line_id),
                    "y_nm": float(y_nm),
                    "left_nm": float(left_nm),
                    "right_nm": float(right_nm),
                    "width_nm": float(width_nm),
                }
            )

    global_metrics: Dict[str, float] = {
        "n_lines": float(len(per_line_metrics)),
        "n_sections_total": float(sum(line["n_sections"] for line in per_line_metrics)),
        "scale_nm_per_px": float(scale_nm_per_px),
        "scale_bar_px": float(scale_bar_px) if scale_bar_px is not None else float("nan"),
    }

    if per_line_metrics:
        for key in ["CD_mean_nm", "CD_median_nm", "LWR_sigma_nm", "LWR_3sigma_nm", "LER_avg_sigma_nm", "LER_avg_3sigma_nm"]:
            global_metrics[key] = float(np.nanmean([line[key] for line in per_line_metrics]))
        centers = np.asarray([line["center_nm"] for line in per_line_metrics])
        if len(centers) > 1:
            global_metrics["pitch_mean_nm"] = float(np.mean(np.diff(np.sort(centers))))

    return {
        "image_name": Path(path).name,
        "params": params,
        "bbox": bbox,
        "crop": crop,
        "score": score,
        "normalized": normalized,
        "feature_specs": specs,
        "per_line_metrics": per_line_metrics,
        "section_rows": section_rows,
        "global_metrics": global_metrics,
        "scale_components": scale_components,
    }


def save_diagnostic_plots(result: Dict[str, object], output_dir: Path) -> None:
    """Save overlay, width trace and CD histogram plots for one image."""

    output_dir.mkdir(parents=True, exist_ok=True)
    image_name = str(result["image_name"])
    stem = Path(image_name).stem.replace(" ", "_")
    crop = np.asarray(result["crop"])
    params: RealImageAnalysisParams = result["params"]  # type: ignore[assignment]
    scale = float(result["global_metrics"]["scale_nm_per_px"])  # type: ignore[index]
    section_rows: List[Dict[str, float]] = result["section_rows"]  # type: ignore[assignment]
    per_line: List[Dict[str, float]] = result["per_line_metrics"]  # type: ignore[assignment]

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.imshow(crop, cmap="gray", origin="upper")
    for line in per_line:
        line_id = int(line["line_id"])
        rows = [row for row in section_rows if int(row["line_id"]) == line_id]
        if not rows:
            continue
        y_px = np.asarray([row["y_nm"] / scale for row in rows])
        left_px = np.asarray([row["left_nm"] / scale for row in rows])
        right_px = np.asarray([row["right_nm"] / scale for row in rows])
        ax.plot(left_px, y_px, linewidth=0.7)
        ax.plot(right_px, y_px, linewidth=0.7)
    ax.set_title(f"{image_name}: extracted {params.feature_polarity} feature edges")
    ax.set_xlabel("x, px")
    ax.set_ylabel("y, px")
    fig.tight_layout()
    fig.savefig(output_dir / f"{stem}_edges_overlay.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    for line in per_line:
        line_id = int(line["line_id"])
        rows = [row for row in section_rows if int(row["line_id"]) == line_id]
        if not rows:
            continue
        y_nm = np.asarray([row["y_nm"] for row in rows])
        width_nm = np.asarray([row["width_nm"] for row in rows])
        ax.plot(y_nm, width_nm, linewidth=0.8, alpha=0.75)
    ax.set_title(f"{image_name}: local width W(y)")
    ax.set_xlabel("y, nm")
    ax.set_ylabel("width, nm")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / f"{stem}_width_traces.png", dpi=180)
    plt.close(fig)

    all_widths = np.asarray([row["width_nm"] for row in section_rows], dtype=float)
    fig, ax = plt.subplots(figsize=(8, 5))
    if all_widths.size:
        ax.hist(all_widths, bins=40)
    ax.set_title(f"{image_name}: width distribution")
    ax.set_xlabel("width, nm")
    ax.set_ylabel("count")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / f"{stem}_width_histogram.png", dpi=180)
    plt.close(fig)


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> None:
    """Write rows to CSV with a stable column order."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
