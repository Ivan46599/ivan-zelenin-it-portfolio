from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Profile:
    name: str
    path: Path
    x: np.ndarray
    z: np.ndarray
    metadata: dict


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    data = path.read_bytes()
    encodings = ["utf-8-sig", "utf-16", "cp1251"] if data.startswith((b"\xff\xfe", b"\xfe\xff")) else ["utf-8-sig", "cp1251"]
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeError:
            pass
    raise ValueError(f"Не удалось определить кодировку: {path}")


def load_profile(path: Path, name: str | None = None, x_unit: str | None = None,
                 z_unit: str | None = None) -> Profile:
    """Read two columns; preserve heights, aggregate rounded equal X by median.

    X is converted to mm, Z to nm. Reversed monotonic scans are allowed;
    mixed scan directions are rejected instead of blending separate sweeps.
    """
    rows, headers, invalid = [], [], 0
    for lineno, line in enumerate(read_text(path).splitlines(), 1):
        line = line.strip()
        if not line or line.startswith(("#", "//")):
            continue
        if "\t" in line or ";" in line:
            tokens = re.split(r"[\t;]+", line)
            tokens = [v.strip().replace(",", ".") for v in tokens]
        else:
            tokens = re.split(r"\s+", line)
            if len(tokens) == 1 and "," in line:
                tokens = line.split(",")
        try:
            numbers = [float(v) for v in tokens]
        except ValueError:
            if rows:
                raise ValueError(f"{path.name}:{lineno}: текст внутри числовых данных")
            headers.append(line)
            continue
        if len(numbers) != 2:
            raise ValueError(f"{path.name}:{lineno}: ожидается 2 столбца X Z, получено {len(numbers)}. Матрица высот не является профилем.")
        if not np.all(np.isfinite(numbers)):
            invalid += 1
            continue
        rows.append(numbers)
    if len(rows) < 20:
        raise ValueError(f"{path.name}: недостаточно конечных числовых точек (нужно >= 20)")
    header = " ".join(headers).lower().replace("µ", "u").replace("μ", "u")
    aliases = {"мм": "mm", "нм": "nm", "мкм": "um"}
    for src, dst in aliases.items():
        header = header.replace(src, dst)
    def unit_from_header(axis):
        m = re.search(r"\b" + axis + r"\s*[\[(]\s*(mm|nm|um|m)\s*[\])]", header)
        return m.group(1) if m else None
    xu, zu = x_unit or unit_from_header("x"), z_unit or unit_from_header("z")
    xscale = {"m": 1000., "mm": 1., "um": .001, "nm": .000001}
    zscale = {"m": 1e9, "mm": 1e6, "um": 1000., "nm": 1.}
    if xu not in xscale or zu not in zscale:
        raise ValueError(f"{path.name}: неизвестны единицы. Нужен заголовок X(mm) Z(nm) или x_unit/z_unit в настройках.")
    a = np.asarray(rows, float)
    x, z = a[:, 0] * xscale[xu], a[:, 1] * zscale[zu]
    diff = np.diff(x)
    reversed_scan = bool(np.any(diff < 0))
    if np.any(diff < 0) and np.any(diff > 0):
        raise ValueError(f"{path.name}: X меняет направление. Экспортируйте один проход отдельно.")
    if reversed_scan:
        x, z = x[::-1], z[::-1]
    ux, first, counts = np.unique(x, return_index=True, return_counts=True)
    uz = np.asarray([np.median(z[i:i+n]) for i, n in zip(first, counts)])
    if len(ux) < 20 or ux[-1] <= ux[0]:
        raise ValueError(f"{path.name}: недостаточно различных координат X")
    gaps = np.diff(ux)
    median_gap = float(np.median(gaps))
    meta = dict(filename=path.name, sha256=file_hash(path), raw_points=len(rows),
                unique_points=len(ux), duplicate_x=len(rows)-len(ux),
                nonfinite_removed=invalid, reversed_scan=reversed_scan,
                input_x_unit=xu, input_z_unit=zu, x_unit="mm", z_unit="nm",
                x_min_mm=float(ux[0]), x_max_mm=float(ux[-1]),
                median_dx_mm=median_gap, max_gap_mm=float(gaps.max()))
    return Profile(name or path.stem, path, ux, uz, meta)


def load_reference(path: Path, spec: dict) -> list[dict]:
    """Read values only. Reference depths never enter detection or measurement."""
    if path.suffix.lower() == ".xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        sheet = spec.get("sheet", 0)
        ws = wb.worksheets[sheet] if isinstance(sheet, int) else wb[sheet]
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
    elif path.suffix.lower() == ".csv":
        text = read_text(path)
        delimiter = ";" if text.splitlines()[0].count(";") > text.splitlines()[0].count(",") else ","
        rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
    else:
        raise ValueError("Ручная кривая: поддерживаются .xlsx и .csv")
    dc, hc = spec.get("dose_column", 1)-1, spec.get("depth_column", 2)-1
    out, seen = [], set()
    for rownum, row in enumerate(rows, 1):
        if rownum < spec.get("start_row", 1) or len(row) <= max(dc, hc):
            continue
        if row[dc] is None and row[hc] is None:
            continue
        try:
            dose, depth = float(str(row[dc]).replace(",", ".")), float(str(row[hc]).replace(",", "."))
        except (TypeError, ValueError):
            raise ValueError(f"Ручная кривая, строка {rownum}: доза и глубина должны быть числами. Проверьте start_row и столбцы.")
        if not np.isfinite(dose) or dose <= 0 or not np.isfinite(depth):
            raise ValueError(f"Ручная кривая, строка {rownum}: недопустимые значения")
        if dose in seen:
            raise ValueError(f"Ручная кривая: повторная доза {dose}; задайте однозначный эталон")
        seen.add(dose)
        out.append(dict(dose=dose, manual_depth_nm=depth, reference_row=rownum))
    if not out:
        raise ValueError("В ручной кривой не найдено числовых строк")
    return out
