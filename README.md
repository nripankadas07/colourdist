# colourdist

Colour-difference metrics — **CIE76, CIE94, CIEDE2000** — plus the
sRGB ↔ XYZ ↔ Lab conversions you need to feed them. Pure Python,
zero deps.

```python
from colourdist import hex_to_lab, delta_e_2000

red    = hex_to_lab("#e8443c")
salmon = hex_to_lab("#fa8072")
delta_e_2000(red, salmon)   # ≈ 17.4 — clearly distinguishable
```

| Metric | Use when |
|---|---|
| `delta_e_76` | You want fast and don't care about perceptual accuracy. |
| `delta_e_94` | Reasonable middle ground; widely cited. |
| `delta_e_2000` | Modern standard. Use this unless you have a reason not to. |

D65 reference white throughout. CIEDE2000 implementation matches the
Sharma/Wu/Dalal 2005 reference values to within 1e-3.

MIT.
