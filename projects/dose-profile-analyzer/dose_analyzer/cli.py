from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

from . import __version__
from .io import file_hash, load_profile
from .measurement import analyze_profile, locate_lattice, shared_pitch
from .outputs import (
    plot_curve,
    plot_profile,
    save_json,
    write_csv,
    write_report,
)


def run(args):
    import matplotlib

    matplotlib.use("Agg")

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))

    base = config_path.parent
    out = (args.out or base / "results").resolve()
    out.mkdir(parents=True, exist_ok=True)

    defaults = config.get("measurement", {})

    profiles = {}
    options = {}
    geometries = {}
    doses = {}

    # =========================
    # Ввод доз пользователем
    # =========================

    dose_min = float(input("Минимальная доза: "))
    dose_max = float(input("Максимальная доза: "))
    dose_step = float(input("Шаг дозы: "))

    if dose_min <= 0 or dose_max <= 0 or dose_step <= 0:
        raise ValueError("Дозы должны быть положительными")

    doses_list = []

    value = dose_min

    while value <= dose_max + 1e-12:
        doses_list.append(round(value, 10))
        value += dose_step

    print("Всего введённых доз:", len(doses_list))

    # =========================
    # Толщина (если используется)
    # =========================

    thickness = config.get("film_thickness_nm")

    if thickness is not None and (
        not isinstance(thickness, (int, float))
        or not math.isfinite(thickness)
        or thickness <= 0
    ):
        raise ValueError("film_thickness_nm должно быть положительным числом или null")

    # =========================
    # Автоматический поиск рядов
    # =========================

    data_folder = args.data or base / "data"

    profile_files = sorted(
        [
            p
            for p in data_folder.glob("*.txt")
            if (p.stem.lower().startswith("r") and p.stem[1:].isdigit())
        ]
    )
    if not profile_files:
        raise ValueError("В папке нет файлов r*.txt")

    print("\nНайдены профили:")

    for p in profile_files:
        print(" ", p.name)

    # =========================
    # Загрузка профилей
    # =========================

    for profile_path in profile_files:
        name = profile_path.stem

        opts = defaults.copy()

        if args.mode:
            opts["mode"] = args.mode

        count = opts.get("count", 10)

        if not isinstance(count, int) or isinstance(count, bool):
            raise ValueError(f"{name}: count должно быть целым числом")

        p = load_profile(profile_path, name, None, None)

        profiles[name] = p
        options[name] = opts

        geometries[name] = locate_lattice(
            p, count, opts.get("pitch_mm"), opts.get("first_center_mm")
        )

    # =========================
    # Проверка количества доз
    # =========================

    expected_doses = len(profiles) * 10

    if len(doses_list) != expected_doses:
        raise ValueError(
            f"Для {len(profiles)} рядов "
            f"по 10 ступеней нужно "
            f"{expected_doses} доз, "
            f"получено: {len(doses_list)}"
        )

    dose_index = 0

    for name in profiles:
        doses[name] = doses_list[dose_index : dose_index + 10]

        dose_index += 10

    print("\nИспользуемые дозы:", doses_list)

    # =========================
    # Общий pitch
    # =========================

    common = shared_pitch(geometries) if config.get("shared_pitch", False) else None

    if common is not None:
        for name, p in profiles.items():
            opts = options[name]

            if opts.get("pitch_mm") is None:
                g = locate_lattice(
                    p, opts.get("count", 10), common, opts.get("first_center_mm")
                )

                g["source"] = "shared_pitch_from_profiles"

                geometries[name] = g

    # =========================
    # Анализ
    # =========================

    all_rows = []
    profile_meta = {}

    for name, p in profiles.items():
        rows, details = analyze_profile(p, geometries[name], options[name], doses[name])

        print("\n======", name, "======")

        print("Найдено ступеней:", len(rows))

        plot_curve(rows, thickness, out / f"{name}_curve.png", f"Дозовая кривая {name}")

        plot_curve(
            rows,
            thickness,
            out / f"{name}_curve_norm.png",
            f"Нормированная дозовая кривая {name}",
            normalized=True,
        )

        for r in rows:
            r["log10_dose"] = None if r["dose"] is None else math.log10(r["dose"])

        all_rows.extend(rows)

        write_csv(out / f"{name}_details.csv", rows)

        write_csv(out / f"{name}_curve.csv", rows)

        plot_profile(p, geometries[name], rows, details, out / f"{name}_profile.png")

        profile_meta[name] = {
            **p.metadata,
            "geometry": geometries[name],
            "measurement": options[name],
            "doses": doses[name],
        }

    # =========================
    # Общие графики
    # =========================

    save_json(out / "measurements.json", all_rows)

    write_csv(out / "measurements.csv", all_rows)

    plot_curve(all_rows, thickness, out / "dose_curve.png", "Общая дозовая кривая")

    plot_curve(
        all_rows,
        thickness,
        out / "dose_curve_norm.png",
        "Общая нормированная дозовая кривая",
        normalized=True,
    )

    metadata = {
        "analyzer_version": __version__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "config_sha256": file_hash(config_path),
        "film_thickness_nm": thickness,
        "profiles": profile_meta,
    }

    save_json(out / "run_metadata.json", metadata)

    write_report(out, all_rows, metadata)

    print(f"\nГотово: {out / 'report.html'}")

    if args.show:
        import webbrowser

        webbrowser.open((out / "report.html").as_uri())

    return 0


def main(argv=None):

    parser = argparse.ArgumentParser(
        description=("Глубины периодических квадратов: автоматический анализ профилей")
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=(Path(__file__).resolve().parents[1] / "config.json"),
    )

    parser.add_argument(
        "--data",
        type=Path,
        help=("Папка с txt-профилями (ряды определяются автоматически)"),
    )

    parser.add_argument(
        "--out",
        type=Path,
        help="Папка результатов",
    )

    parser.add_argument(
        "--mode",
        choices=("auto", "grid", "manual"),
        help="Режим анализа",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="Открыть HTML отчёт",
    )

    args = parser.parse_args(argv)

    try:
        return run(args)

    except (ValueError, OSError, KeyError, IndexError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)

        return 2
