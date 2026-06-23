"""Run CD/LER/LWR analysis for real SEM/TIF images of developed photoresist.

The scientific target in the supplied SEM images is the thin dark developed
bands. Therefore the default feature polarity is "dark".

NILS is intentionally not calculated here: a SEM image after resist development
is not an optical intensity profile. NILS should be calculated only from an
optical/air-image intensity profile I(x) or from a corresponding simulation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from resist_image_metrics import (
    RealImageAnalysisParams,
    analyze_real_image,
    save_diagnostic_plots,
    write_csv,
)


def _default_project_dir() -> Path:
    """Return project root for both archive layout and direct script execution."""
    script_dir = Path(__file__).resolve().parent
    if (script_dir.parent / "input_images").exists():
        return script_dir.parent
    return script_dir


def parse_args() -> argparse.Namespace:
    project_dir = _default_project_dir()
    parser = argparse.ArgumentParser(
        description="Measure CD, LER and LWR for real SEM/TIF photoresist images."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=project_dir / "input_images",
        help="Folder with .tif/.tiff/.png/.jpg SEM images. Default: ../input_images when present.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=project_dir / "results",
        help="Folder for CSV output tables.",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=project_dir / "figures",
        help="Folder for diagnostic plots.",
    )
    parser.add_argument(
        "--polarity",
        choices=("dark", "bright"),
        default="dark",
        help="Target feature contrast. Use 'dark' for the supplied developed bands.",
    )
    parser.add_argument(
        "--scale-nm-per-px",
        type=float,
        default=None,
        help="Known microscope scale in nm/px. If omitted, it is estimated from the 100 nm green scale bar.",
    )
    parser.add_argument(
        "--top-crop-px",
        type=int,
        default=70,
        help="Pixels removed from the top overlay area before analysis.",
    )
    return parser.parse_args()


def _find_images(input_dir: Path) -> list[Path]:
    patterns = ("*.tif", "*.tiff", "*.png", "*.jpg", "*.jpeg")
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(input_dir.glob(pattern))
    return sorted(paths)


def main() -> None:
    args = parse_args()
    image_paths = _find_images(args.input_dir)
    if not image_paths:
        raise FileNotFoundError(f"No image files found in {args.input_dir}")

    params = RealImageAnalysisParams(
        feature_polarity=args.polarity,
        scale_nm_per_px=args.scale_nm_per_px,
        top_crop_px=args.top_crop_px,
    )

    summary_rows = []
    per_line_rows = []
    section_rows = []

    for image_path in image_paths:
        result = analyze_real_image(image_path, params)
        save_diagnostic_plots(result, args.figures_dir)

        summary_row = {"image_name": image_path.name, "feature_polarity": params.feature_polarity}
        summary_row.update(result["global_metrics"])
        summary_rows.append(summary_row)

        for line in result["per_line_metrics"]:
            row = {"image_name": image_path.name, "feature_polarity": params.feature_polarity}
            row.update(line)
            per_line_rows.append(row)

        for section in result["section_rows"]:
            row = {"image_name": image_path.name, "feature_polarity": params.feature_polarity}
            row.update(section)
            section_rows.append(row)

    write_csv(
        args.results_dir / "summary_metrics.csv",
        summary_rows,
        [
            "image_name", "feature_polarity", "n_lines", "n_sections_total",
            "scale_nm_per_px", "scale_bar_px", "pitch_mean_nm", "CD_mean_nm",
            "CD_median_nm", "LWR_sigma_nm", "LWR_3sigma_nm", "LER_avg_sigma_nm",
            "LER_avg_3sigma_nm",
        ],
    )
    write_csv(
        args.results_dir / "per_line_metrics.csv",
        per_line_rows,
        [
            "image_name", "feature_polarity", "line_id", "n_sections",
            "valid_fraction", "center_nm", "CD_mean_nm", "CD_median_nm",
            "LWR_sigma_nm", "LWR_3sigma_nm", "LER_left_sigma_nm",
            "LER_right_sigma_nm", "LER_avg_sigma_nm", "LER_avg_3sigma_nm",
            "threshold_score", "initial_width_nm",
        ],
    )
    write_csv(
        args.results_dir / "section_edges.csv",
        section_rows,
        ["image_name", "feature_polarity", "line_id", "y_nm", "left_nm", "right_nm", "width_nm"],
    )

    print(f"Processed {len(image_paths)} images with feature_polarity='{params.feature_polarity}'.")
    print(f"Summary: {args.results_dir / 'summary_metrics.csv'}")
    print(f"Per-line metrics: {args.results_dir / 'per_line_metrics.csv'}")
    print(f"Section edges: {args.results_dir / 'section_edges.csv'}")
    print(f"Figures: {args.figures_dir}")


if __name__ == "__main__":
    main()
