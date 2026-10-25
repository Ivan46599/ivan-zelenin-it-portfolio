from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

STATUS = {"measured": "Измерено", "review": "Проверить", "unresolved": "Не разрешено"}


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(dict.fromkeys(k for row in rows for k in row))

    with Path(path).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def save_json(path, value):
    Path(path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def plot_profile(profile, geometry, rows, details, path):
    import matplotlib.pyplot as plt

    x, z = profile.x, profile.z

    fig, ax = plt.subplots(figsize=(14, 5.2), layout="constrained")

    ax.plot(x, z, lw=1.1, color="#245784", label="Исходные высоты")

    colors = {"measured": "#16846b", "review": "#b87500", "unresolved": "#be4854"}

    shown = set()

    for r, detail in zip(rows, details):
        c = r["position"]

        if detail is not None:
            p = geometry["pitch_mm"]

            local = (x >= c - 0.43 * p) & (x <= c + 0.43 * p)

            ax.plot(
                x[local],
                detail["baseline"][local],
                color="#dc8c23",
                lw=1,
                label=("Локальная поверхность" if "bg" not in shown else None),
            )

            ax.scatter(
                x[detail["top_mask"]], z[detail["top_mask"]], color="#dc8c23", s=3
            )

            ax.scatter(
                x[detail["bottom_mask"]],
                z[detail["bottom_mask"]],
                color=colors[r["status"]],
                s=7,
                label=("Область дна" if "bottom" not in shown else None),
            )

            shown.update(("bg", "bottom"))

            ax.vlines(c, r["bottom_nm"], r["top_nm"], color=colors[r["status"]], lw=1.4)

            label_y = r["top_nm"]

        else:
            label_y = float(np.interp(c, x, z))

        number = (
            f"{r['square']}: {r['depth_nm']:.2f}"
            if r["depth_nm"] is not None
            else f"{r['square']}: ?"
        )

        ax.annotate(
            number,
            (c, label_y),
            xytext=(0, 15),
            textcoords="offset points",
            color=colors[r["status"]],
            fontsize=9,
            ha="center",
        )

    ax.set_title(f"{profile.name}: глубина относительно локальной поверхности, нм")
    ax.set_xlabel("X, мм")
    ax.set_ylabel("Z, нм")

    ax.grid(alpha=0.18)
    ax.legend(loc="lower left", fontsize=8)

    fig.savefig(path, dpi=160)

    plt.close(fig)


def plot_curve(
    rows,
    thickness,
    output_path,
    title="Дозовая кривая",
    normalized=False,
):

    import matplotlib.pyplot as plt

    doses = []
    values = []

    for row in rows:
        depth = row.get("depth_nm")
        dose = row.get("dose")

        if depth is None or dose is None:
            continue

        if normalized:
            if thickness is None:
                continue

            value = (thickness - depth) / thickness

        else:
            value = depth

        doses.append(dose)
        values.append(value)

    if not doses:
        print("Нет данных для построения дозовой кривой")
        return

    pairs = sorted(zip(doses, values), key=lambda x: x[0])

    doses = [p[0] for p in pairs]

    values = [p[1] for p in pairs]

    if normalized:
        doses = [math.log10(d) for d in doses if d > 0]

    plt.figure(figsize=(8, 5))

    plt.plot(doses, values, marker="o")

    if normalized:
        plt.xlabel("log10(Dose)")

        plt.ylabel("Normalized depth")

    else:
        plt.xlabel("Dose")

        plt.ylabel("Depth (nm)")

    plt.title(title)

    plt.grid(True)

    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    plt.close()


def write_report(out, rows, metadata):

    import html

    esc = html.escape

    def image(name):

        path = out / name

        if not path.exists():
            return ""

        return f'<p><img src="{name}" style="max-width:100%"></p>'

    parts = [
        "<!doctype html>",
        "<html lang='ru'>",
        "<meta charset='utf-8'>",
        "<title>Анализ дозы</title>",
        "<h1>Анализ экспериментальных профилей</h1>",
    ]

    for name in metadata.get("profiles", {}):
        parts.append(f"<h2>{esc(name)}</h2>")

        parts.append(image(f"{name}_profile.png"))

        parts.append(image(f"{name}_curve.png"))

        parts.append(image(f"{name}_curve_norm.png"))

    parts.append("<h2>Общая дозовая кривая</h2>")

    parts.append(image("dose_curve.png"))

    parts.append(image("dose_curve_norm.png"))

    (out / "report.html").write_text("\n".join(parts), encoding="utf-8")


def compare_reference(rows, reference_rows):
    """Compare resolved measurements with reference depths by exact dose.

    Reference values are used only for validation and never participate in
    feature detection or depth estimation. Returns a comparison table and
    aggregate error metrics for resolved pairs.
    """
    reference_by_dose = {}
    for ref in reference_rows:
        dose = float(ref["dose"])
        if dose in reference_by_dose:
            raise ValueError(f"Повторная доза в эталонных данных: {dose}")
        reference_by_dose[dose] = ref

    comparison = []
    matched_reference_doses = set()
    for row in rows:
        dose_value = row.get("dose")
        if dose_value is None:
            continue
        dose = float(dose_value)
        ref = reference_by_dose.get(dose)
        if ref is None:
            continue
        matched_reference_doses.add(dose)
        measured = row.get("depth_nm")
        reference_depth = float(ref["manual_depth_nm"])
        error = None if measured is None else float(measured) - reference_depth
        comparison.append({
            "profile": row.get("profile"),
            "square": row.get("square"),
            "dose": dose,
            "depth_nm": None if measured is None else float(measured),
            "manual_depth_nm": reference_depth,
            "error_nm": error,
            "abs_error_nm": None if error is None else abs(error),
            "status": row.get("status"),
            "reference_row": ref.get("reference_row"),
        })

    resolved_errors = np.asarray(
        [item["error_nm"] for item in comparison if item["error_nm"] is not None],
        dtype=float,
    )
    if len(resolved_errors):
        all_resolved = {
            "n": int(len(resolved_errors)),
            "mae_nm": float(np.mean(np.abs(resolved_errors))),
            "rmse_nm": float(np.sqrt(np.mean(resolved_errors ** 2))),
            "bias_nm": float(np.mean(resolved_errors)),
        }
    else:
        all_resolved = {"n": 0, "mae_nm": None, "rmse_nm": None, "bias_nm": None}

    metrics = {
        "all_resolved": all_resolved,
        "unresolved_matched": sum(item["depth_nm"] is None for item in comparison),
        "unmatched_reference_doses": sorted(set(reference_by_dose) - matched_reference_doses),
    }
    return comparison, metrics
