from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import least_squares

from .io import Profile


def mad(a):
    a = np.asarray(a, float)
    return float(1.4826 * np.median(np.abs(a-np.median(a)))) if len(a) else 0.


def uniform_signal(profile):
    x, z = profile.x, profile.z
    # Interpolation is used ONLY to locate edges. Heights use original unique X.
    u = np.linspace(x[0], x[-1], len(x))
    v = np.interp(u, x, z)
    smooth = gaussian_filter1d(v, 1.2, mode="nearest")
    return u, smooth, np.gradient(smooth, u)


def locate_lattice(profile: Profile, count: int, pitch: float | None = None,
                   first_center: float | None = None) -> dict:
    """Fit a periodic geometric prior, not ten arbitrary signal averages.

    The signed filter compares an inner region with symmetric outer regions.
    Its zero sum and zero first moment cancel a constant and a linear slope.
    The expected count must describe the physical design, not be inferred as
    a claim that every square is resolved in the measurement.
    """
    x, y, _ = uniform_signal(profile)
    span, dx = float(x[-1]-x[0]), float(x[1]-x[0])
    if count < 2 or count > len(x)//12:
        raise ValueError(f"{profile.name}: неверное число квадратов для длины записи")
    if pitch is not None and (pitch <= 12*dx or pitch > span):
        raise ValueError(f"{profile.name}: неверный период {pitch}")
    pitches = [pitch] if pitch is not None else np.linspace(span/(count+1), span/(count-1.5), 151)
    best = None
    # Reduces cancellation error without changing the symmetric filter response.
    yy = y - np.polyval(np.polyfit(x-x.mean(), y, 1), x-x.mean())
    for p in pitches:
        offsets = np.arange(-int(.45*p/dx), int(.45*p/dx)+1)*dx
        center = np.abs(offsets) < .10*p
        sides = (np.abs(offsets) > .26*p) & (np.abs(offsets) < .44*p)
        if center.sum() < 3 or sides.sum() < 4:
            continue
        kernel = np.zeros(len(offsets))
        kernel[center] = -1./center.sum()
        kernel[sides] = 1./sides.sum()
        response = np.convolve(yy, kernel, "same")
        inside = (x >= x[0]+.44*p) & (x <= x[-1]-.44*p)
        cap = max(float(np.percentile(response[inside], 95)), 3*mad(np.diff(yy)), 1e-9)
        starts = [first_center] if first_center is not None else np.linspace(x[0]-.05*p, x[0]+1.1*p, 141)
        for c0 in starts:
            centers = c0+np.arange(count)*p
            if centers[-1] > x[-1]+.1*p:
                continue
            rr = np.interp(centers, x, response)
            rr[(centers < x[0]+.44*p) | (centers > x[-1]-.44*p)] = 0
            score = float(np.clip(rr/cap, -.5, 1).sum())
            if best is None or score > best[0]:
                best = (score, float(c0), float(p))
    if best is None:
        raise ValueError(f"{profile.name}: сетка квадратов не помещается в профиль")
    return dict(score=best[0], first_center_mm=best[1], pitch_mm=best[2], count=count,
                source="configured" if first_center is not None and pitch is not None else "profile")


def shared_pitch(geometries):
    candidates = [g["pitch_mm"] for g in geometries.values() if g["score"] >= .6*g["count"]]
    if len(candidates) < 2:
        return None
    middle = float(np.median(candidates))
    agreeing = [p for p in candidates if abs(p/middle-1) <= .05]
    if len(agreeing) < 2 or len(agreeing) <= len(candidates)/2:
        return None
    return float(np.median(agreeing))


def robust_line(t, z):
    initial = np.polyfit(t, z, 1)
    scale = max(mad(z-np.polyval(initial, t)), 1e-6)
    fit = least_squares(lambda a: np.polyval(a, t)-z, initial,
                        loss="soft_l1", f_scale=scale, max_nfev=300)
    if not fit.success:
        raise ValueError("Не сошлась робастная аппроксимация фоновой поверхности")
    return fit.x


def missing(square, center, reason, method):
    return dict(square=square, position=float(center), depth_nm=None,
                candidate_depth_nm=None, status="unresolved", reason=reason, method=method)


def measure_square(profile, square, expected_center, pitch, signal,
                   mode="auto", roi=None, edge_sigma=2.5, min_snr=2.5):
    x, z = profile.x, profile.z
    u, smooth, derivative = signal
    c = expected_center
    if roi is not None:
        left, right = map(float, roi)
        if not x[0] <= left < right <= x[-1] or right-left >= .8*pitch:
            raise ValueError(f"{profile.name}, квадрат {square}: неверный ручной интервал {roi}")
        method = "manual"
    elif mode == "grid":
        left, right, method = c-.15*pitch, c+.15*pitch, "grid"
    else:
        lm = np.flatnonzero((u >= c-.25*pitch) & (u <= c-.05*pitch))
        rm = np.flatnonzero((u >= c+.05*pitch) & (u <= c+.25*pitch))
        if len(lm) == 0 or len(rm) == 0:
            return missing(square, c, "Квадрат обрезан границей записи", "edges"), None
        left = float(u[lm[np.argmin(derivative[lm])]])
        right = float(u[rm[np.argmax(derivative[rm])]])
        method = "edges"
    c, width = (left+right)/2, right-left
    # Outer surface windows on both sides; edge zones are excluded.
    tl = (x >= c-.43*pitch) & (x <= left-.06*pitch)
    tr = (x >= right+.06*pitch) & (x <= c+.43*pitch)
    top_mask = tl | tr
    bottom_mask = (x >= left+.25*width) & (x <= right-.25*width)
    if tl.sum() < 5 or tr.sum() < 5 or bottom_mask.sum() < 5:
        return missing(square, c, "Не хватает точек дна или поверхности с обеих сторон", method), None
    gap_region = (x[:-1] >= c-.43*pitch) & (x[1:] <= c+.43*pitch)
    if np.any(np.diff(x)[gap_region] > .08*pitch):
        return missing(square, c, "Пропуск координат внутри области измерения", method), None
    t = (x-c)/pitch
    coef = robust_line(t[top_mask], z[top_mask])
    baseline = np.polyval(coef, t)
    residual = baseline-z
    depth = float(np.median(residual[bottom_mask]))
    scatter = float(np.hypot(mad(residual[top_mask]), mad(residual[bottom_mask])))
    snr = depth/max(scatter, 1e-9)
    il, ir = int(np.argmin(abs(u-left))), int(np.argmin(abs(u-right)))
    gradient_noise = max(mad(derivative), 1e-9)
    left_edge, right_edge = float(-derivative[il]), float(derivative[ir])
    edge_ratio = min(left_edge, right_edge)/gradient_noise
    reasons = []
    if depth <= 0:
        reasons.append("Нет положительной глубины впадины")
    if snr < min_snr:
        reasons.append("Глубина мала относительно разброса поверхности")
    if method == "edges" and edge_ratio < edge_sigma:
        reasons.append("Одна или обе границы неотличимы от фоновых изменений")
    if not .12*pitch <= width <= .42*pitch:
        reasons.append("Ширина не согласуется с моделью квадрата")
    status = "unresolved" if reasons else ("review" if snr < 4 or (method == "edges" and edge_ratio < 3) else "measured")
    if status == "review":
        reasons.append("Слабый контраст: проверить выделенные области на графике")
    top = float(np.polyval(coef, 0.))
    result = dict(square=square, position=float(c), depth_nm=depth if status != "unresolved" else None,
                  candidate_depth_nm=depth, top_nm=top, bottom_nm=top-depth,
                  left_mm=float(left), right_mm=float(right), width_mm=float(width),
                  baseline_slope_nm_per_mm=float(coef[0]/pitch),
                  scatter_nm=scatter, signal_to_scatter=snr, edge_to_background=edge_ratio,
                  n_left=int(tl.sum()), n_right=int(tr.sum()), n_bottom=int(bottom_mask.sum()),
                  status=status, reason="; ".join(reasons), method=method)
    detail = dict(top_mask=top_mask, bottom_mask=bottom_mask, baseline=baseline)
    return result, detail


def analyze_profile(profile, geometry, options, doses=None):
    count = geometry["count"]
    mode = options.get("mode", "auto")
    if mode not in ("auto", "grid", "manual"):
        raise ValueError(f"Неизвестный режим {mode}")
    rois = options.get("intervals_mm", {})
    if mode == "manual" and any(str(i+1) not in rois for i in range(count)):
        raise ValueError(f"{profile.name}: в ручном режиме нужны intervals_mm для всех квадратов")
    signal = uniform_signal(profile)
    results, details = [], []
    for i in range(count):
        center = geometry["first_center_mm"] + i*geometry["pitch_mm"]
        r, detail = measure_square(profile, i+1, center, geometry["pitch_mm"], signal,
                                  mode, rois.get(str(i+1)),
                                  options.get("edge_sigma", 2.5), options.get("min_snr", 2.5))
        r["profile"] = profile.name
        r["dose"] = float(doses[i]) if doses is not None else None
        results.append(r)
        details.append(detail)
    return results, details
