"""Tests for colourdist."""
import pytest
from colourdist import (
    ColourDistError, delta_e_2000, delta_e_76, delta_e_94,
    hex_to_lab, srgb_to_lab, srgb_to_xyz, xyz_to_lab,
)


def _close(a, b, tol=1e-3):
    return abs(a - b) < tol


def _close_tuple(a, b, tol=1e-3):
    return all(_close(x, y, tol) for x, y in zip(a, b))


class TestSrgbToXyz:
    def test_white(self):
        x, y, z = srgb_to_xyz((1.0, 1.0, 1.0))
        # White → D65 reference white XYZ.
        assert _close_tuple((x, y, z), (95.047, 100.000, 108.883), tol=0.05)

    def test_black(self):
        assert _close_tuple(srgb_to_xyz((0.0, 0.0, 0.0)), (0.0, 0.0, 0.0))

    def test_red(self):
        # Pure red (sRGB 1,0,0) → reference values from Bruce Lindbloom calculator
        x, y, z = srgb_to_xyz((1.0, 0.0, 0.0))
        assert _close_tuple((x, y, z), (41.246, 21.267, 1.933), tol=0.05)

    def test_invalid_range(self):
        with pytest.raises(ColourDistError):
            srgb_to_xyz((1.5, 0.0, 0.0))

    def test_invalid_type(self):
        with pytest.raises(ColourDistError):
            srgb_to_xyz([1.0, 0.0, 0.0])  # list, not tuple


class TestXyzToLab:
    def test_white(self):
        L, a, b = xyz_to_lab((95.047, 100.000, 108.883))
        assert _close(L, 100.0, tol=0.01)
        assert _close(a, 0.0, tol=0.01)
        assert _close(b, 0.0, tol=0.01)

    def test_black(self):
        L, a, b = xyz_to_lab((0.0, 0.0, 0.0))
        assert _close(L, 0.0, tol=0.01)


class TestSrgbToLab:
    def test_white(self):
        L, a, b = srgb_to_lab((1.0, 1.0, 1.0))
        assert _close(L, 100.0, tol=0.05)

    def test_black(self):
        L, a, b = srgb_to_lab((0.0, 0.0, 0.0))
        assert _close(L, 0.0, tol=0.05)


class TestHexToLab:
    def test_white_hex(self):
        L, a, b = hex_to_lab("#ffffff")
        assert _close(L, 100.0, tol=0.05)

    def test_no_hash(self):
        assert hex_to_lab("ffffff") == hex_to_lab("#ffffff")

    def test_invalid(self):
        with pytest.raises(ColourDistError):
            hex_to_lab("notacolour")
        with pytest.raises(ColourDistError):
            hex_to_lab("#ff")


class TestDeltaE76:
    def test_zero(self):
        assert delta_e_76((50, 0, 0), (50, 0, 0)) == 0.0

    def test_simple(self):
        # Delta L by 10 units → ΔE = 10.
        assert _close(delta_e_76((50, 0, 0), (60, 0, 0)), 10.0)


class TestDeltaE94:
    def test_zero(self):
        assert delta_e_94((50, 0, 0), (50, 0, 0)) == 0.0

    def test_symmetric_with_l(self):
        # Pure L change with C1=0 → CIE94 reduces to dL.
        assert _close(delta_e_94((50, 0, 0), (60, 0, 0)), 10.0)


class TestDeltaE2000:
    def test_zero(self):
        assert delta_e_2000((50, 0, 0), (50, 0, 0)) == 0.0

    def test_known_pair_1(self):
        # Sharma et al test data: pair 1 → ΔE ≈ 2.0425
        d = delta_e_2000((50.0000, 2.6772, -79.7751), (50.0000, 0.0000, -82.7485))
        assert _close(d, 2.0425, tol=0.01)

    def test_known_pair_2(self):
        # Sharma pair 14 → ΔE ≈ 4.3065
        d = delta_e_2000((63.0109, -31.0961, -5.8663), (62.8187, -29.7946, -4.0864))
        assert _close(d, 1.2630, tol=0.01)
