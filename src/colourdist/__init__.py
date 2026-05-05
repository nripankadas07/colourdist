"""colourdist — pure-Python colour-difference metrics and conversions.

Public API:

* :func:`srgb_to_xyz`     — sRGB (0-1) to CIE XYZ (D65).
* :func:`xyz_to_lab`      — CIE XYZ to CIE L*a*b* (D65).
* :func:`srgb_to_lab`     — convenience: sRGB → Lab.
* :func:`hex_to_lab`      — convenience: ``"#aabbcc"`` → Lab.
* :func:`delta_e_76`      — CIE76 ΔE (Euclidean in Lab).
* :func:`delta_e_94`      — CIE94 ΔE.
* :func:`delta_e_2000`    — CIEDE2000 ΔE (the modern standard).
* :class:`ColourDistError` — raised on invalid input.
"""
from __future__ import annotations

from ._core import (
    ColourDistError,
    delta_e_76,
    delta_e_94,
    delta_e_2000,
    hex_to_lab,
    srgb_to_lab,
    srgb_to_xyz,
    xyz_to_lab,
)

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

__version__ = "0.1.0"
