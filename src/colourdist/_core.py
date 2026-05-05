"""Pure-Python colour-difference metrics + sRGB/XYZ/Lab conversions.

References:
* Bruce Lindbloom (sRGB ↔ XYZ ↔ Lab matrices, D65 reference white)
* CIE76: simple Euclidean distance in L*a*b*.
* CIE94: weighted with kL, kC, kH.
* CIEDE2000: Sharma/Wu/Dalal 2005 implementation.
"""
from __future__ import annotations

import math
from typing import Tuple

__all__ = [
    "ColourDistError",
    "delta_e_76",
    "delta_e_94",
    "delta_e_2000",
    "hex_to_lab",
    "srgb_to_lab",
    "srgb_to_xyz",
    "xyz_to_lab",
]


class ColourDistError(ValueError):
    """Raised on invalid colour input."""


# D65 reference white (2° observer)
_XN, _YN, _ZN = 95.047, 100.000, 108.883


def _sanitize_rgb(rgb: Tuple[float, float, float]) -> Tuple[float, float, float]:
    if not (isinstance(rgb, tuple) and len(rgb) == 3):
        raise ColourDistError("rgb must be a 3-tuple of floats in [0, 1]")
    r, g, b = rgb
    for ch in (r, g, b):
        if not isinstance(ch, (int, float)) or isinstance(ch, bool):
            raise ColourDistError(f"rgb channel must be a number, got {type(ch).__name__}")
        if not 0.0 <= float(ch) <= 1.0:
            raise ColourDistError(f"rgb channel out of [0, 1]: {ch}")
    return float(r), float(g), float(b)


def _gamma_decode(c: float) -> float:
    """Inverse sRGB companding."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def srgb_to_xyz(rgb: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert sRGB (each channel in [0, 1]) to CIE XYZ (D65, 0-100)."""
    r, g, b = _sanitize_rgb(rgb)
    rl, gl, bl = _gamma_decode(r), _gamma_decode(g), _gamma_decode(b)
    # D65 sRGB → XYZ matrix (Bruce Lindbloom).
    x = 100.0 * (0.4124564 * rl + 0.3575761 * gl + 0.1804375 * bl)
    y = 100.0 * (0.2126729 * rl + 0.7151522 * gl + 0.0721750 * bl)
    z = 100.0 * (0.0193339 * rl + 0.1191920 * gl + 0.9503041 * bl)
    return x, y, z


def _f_lab(t: float) -> float:
    eps = 216.0 / 24389.0  # 0.008856
    kappa = 24389.0 / 27.0  # 903.3
    if t > eps:
        return t ** (1.0 / 3.0)
    return (kappa * t + 16.0) / 116.0


def xyz_to_lab(xyz: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert CIE XYZ (D65, 0-100) to CIE L*a*b* (D65)."""
    if not (isinstance(xyz, tuple) and len(xyz) == 3):
        raise ColourDistError("xyz must be a 3-tuple")
    x, y, z = xyz
    fx = _f_lab(x / _XN)
    fy = _f_lab(y / _YN)
    fz = _f_lab(z / _ZN)
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return L, a, b


def srgb_to_lab(rgb: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert sRGB (each channel in [0, 1]) to CIE L*a*b*."""
    return xyz_to_lab(srgb_to_xyz(rgb))


def hex_to_lab(hex_str: str) -> Tuple[float, float, float]:
    """Convert ``"#rrggbb"`` (or ``"rrggbb"``) to CIE L*a*b*."""
    if not isinstance(hex_str, str):
        raise ColourDistError(f"hex must be str, got {type(hex_str).__name__}")
    s = hex_str.lstrip("#").strip().lower()
    if len(s) != 6 or any(c not in "0123456789abcdef" for c in s):
        raise ColourDistError(f"invalid hex colour: {hex_str!r}")
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    return srgb_to_lab((r, g, b))


def _lab_check(lab: Tuple[float, float, float], name: str) -> Tuple[float, float, float]:
    if not (isinstance(lab, tuple) and len(lab) == 3):
        raise ColourDistError(f"{name} must be a 3-tuple of L*a*b*")
    return tuple(float(c) for c in lab)  # type: ignore[return-value]


def delta_e_76(lab1: Tuple[float, float, float], lab2: Tuple[float, float, float]) -> float:
    """CIE76 ΔE — straight Euclidean distance in L*a*b*."""
    L1, a1, b1 = _lab_check(lab1, "lab1")
    L2, a2, b2 = _lab_check(lab2, "lab2")
    return math.sqrt((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


def delta_e_94(
    lab1: Tuple[float, float, float],
    lab2: Tuple[float, float, float],
    *,
    kL: float = 1.0,
    K1: float = 0.045,
    K2: float = 0.015,
) -> float:
    """CIE94 ΔE."""
    L1, a1, b1 = _lab_check(lab1, "lab1")
    L2, a2, b2 = _lab_check(lab2, "lab2")
    dL = L1 - L2
    C1 = math.sqrt(a1 * a1 + b1 * b1)
    C2 = math.sqrt(a2 * a2 + b2 * b2)
    dC = C1 - C2
    da = a1 - a2
    db = b1 - b2
    dH2 = max(0.0, da * da + db * db - dC * dC)
    sL, sC, sH = 1.0, 1.0 + K1 * C1, 1.0 + K2 * C1
    return math.sqrt((dL / (kL * sL)) ** 2 + (dC / sC) ** 2 + dH2 / (sH * sH))


def delta_e_2000(
    lab1: Tuple[float, float, float],
    lab2: Tuple[float, float, float],
    *,
    kL: float = 1.0,
    kC: float = 1.0,
    kH: float = 1.0,
) -> float:
    """CIEDE2000 ΔE (Sharma/Wu/Dalal 2005)."""
    L1, a1, b1 = _lab_check(lab1, "lab1")
    L2, a2, b2 = _lab_check(lab2, "lab2")
    C1 = math.sqrt(a1 * a1 + b1 * b1)
    C2 = math.sqrt(a2 * a2 + b2 * b2)
    Cbar = (C1 + C2) / 2.0
    G = 0.5 * (1.0 - math.sqrt((Cbar ** 7) / (Cbar ** 7 + 25 ** 7)))
    a1p = (1.0 + G) * a1
    a2p = (1.0 + G) * a2
    C1p = math.sqrt(a1p * a1p + b1 * b1)
    C2p = math.sqrt(a2p * a2p + b2 * b2)

    def _h(ap: float, bp: float) -> float:
        if ap == 0.0 and bp == 0.0:
            return 0.0
        h = math.degrees(math.atan2(bp, ap))
        return h + 360.0 if h < 0.0 else h

    h1p, h2p = _h(a1p, b1), _h(a2p, b2)
    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0.0:
        dhp = 0.0
    else:
        diff = h2p - h1p
        if diff > 180.0:
            diff -= 360.0
        elif diff < -180.0:
            diff += 360.0
        dhp = diff
    dHp = 2.0 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2.0))
    Lbarp = (L1 + L2) / 2.0
    Cbarp = (C1p + C2p) / 2.0
    if C1p * C2p == 0.0:
        hbarp = h1p + h2p
    else:
        diff = abs(h1p - h2p)
        sum_h = h1p + h2p
        if diff <= 180.0:
            hbarp = sum_h / 2.0
        elif sum_h < 360.0:
            hbarp = (sum_h + 360.0) / 2.0
        else:
            hbarp = (sum_h - 360.0) / 2.0
    T = (
        1.0
        - 0.17 * math.cos(math.radians(hbarp - 30))
        + 0.24 * math.cos(math.radians(2 * hbarp))
        + 0.32 * math.cos(math.radians(3 * hbarp + 6))
        - 0.20 * math.cos(math.radians(4 * hbarp - 63))
    )
    delta_theta = 30.0 * math.exp(-(((hbarp - 275.0) / 25.0) ** 2))
    Rc = 2.0 * math.sqrt((Cbarp ** 7) / (Cbarp ** 7 + 25 ** 7))
    Sl = 1.0 + (0.015 * (Lbarp - 50) ** 2) / math.sqrt(20 + (Lbarp - 50) ** 2)
    Sc = 1.0 + 0.045 * Cbarp
    Sh = 1.0 + 0.015 * Cbarp * T
    Rt = -math.sin(math.radians(2 * delta_theta)) * Rc
    return math.sqrt(
        (dLp / (kL * Sl)) ** 2
        + (dCp / (kC * Sc)) ** 2
        + (dHp / (kH * Sh)) ** 2
        + Rt * (dCp / (kC * Sc)) * (dHp / (kH * Sh))
    )
