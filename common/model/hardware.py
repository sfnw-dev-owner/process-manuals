"""Hand-modeled stand-ins for hardware that was imported into the SketchUp
model as dense meshes (casters, door knobs, Simpson ties).

Each function builds the part in its SketchUp definition's own coordinate
frame and is handed that definition's bounding box (lo, hi) in inches, so the
stand-in lands where the original was. Dimensions are rough, read off the
original meshes; they only need to read correctly in line drawings.
"""

from build123d import *


def _extent(lo, hi):
    return [h - l for l, h in zip(lo, hi)]


def cart_caster(lo, hi):
    """Plate-mount swivel caster under an iron cart: square top plate, a
    two-sided fork, and a 6" wheel on an axle along X at the +Y end."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    cx = (x0 + x1) / 2
    wheel_d, wheel_w = 6.0, 2.4
    plate_t = 0.47
    wy, wz = y1 - wheel_d / 2, z0 + wheel_d / 2
    plate = Pos(cx, y0 + 2.24, z1 - plate_t / 2) * Box(x1 - x0, 4.48, plate_t)
    fork = [
        Pos(cx + s * (wheel_w / 2 + 0.25), (y0 + 2.24 + wy) / 2, (wz + z1 - plate_t) / 2)
        * Box(0.25, wy - y0 - 1.2, z1 - plate_t - wz)
        for s in (-1, 1)
    ]
    wheel = Pos(cx, wy, wz) * Rot(Y=90) * Cylinder(wheel_d / 2, wheel_w)
    hub = Pos(cx, wy, wz) * Rot(Y=90) * Cylinder(1.1, wheel_w + 0.6)
    return Compound([plate, *fork, wheel, hub])


def dolly_caster(lo, hi):
    """Small swivel caster under a car dolly: mounting plate on top, a
    fork, and a ~1.6" wheel at the bottom."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    wheel_d, wheel_w = 1.6, 0.6
    plate = Pos(cx, cy, z1 - 0.1) * Box(x1 - x0, x1 - x0, 0.2)
    swivel = Pos(cx, cy, z1 - 0.35) * Cylinder(0.6, 0.3)
    wy = cy + (y1 - y0) / 4
    fork = Pos(cx, (cy + wy) / 2, (z0 + wheel_d / 2 + z1 - 0.5) / 2) * Box(
        wheel_w + 0.3, abs(wy - cy) + 0.6, z1 - 0.5 - z0 - wheel_d / 2
    )
    wheel = Pos(cx, wy, z0 + wheel_d / 2) * Rot(Y=90) * Cylinder(wheel_d / 2, wheel_w)
    return Compound([plate, swivel, fork, wheel])


def door_knob(lo, hi):
    """Door knob: round rose against the door (the door is the -Y side of the
    bounding box), a short stem, and a ball knob."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    r = min(x1 - x0, z1 - z0) / 2
    rose = Pos(cx, y0 + 0.15, cz) * Rot(X=90) * Cylinder(r, 0.3)
    stem = Pos(cx, (y0 + y1) / 2, cz) * Rot(X=90) * Cylinder(r * 0.3, y1 - y0 - 0.6)
    knob = Pos(cx, y1 - r * 0.7, cz) * Sphere(r * 0.7)
    return Compound([rose, stem, knob])


def a35_bracket(lo, hi):
    """Simpson A35 framing clip: a thin bent plate, drawn as an L of two
    18-gauge (0.05") legs along the bounding box's two longest sides."""
    ext = _extent(lo, hi)
    t = 0.05
    c = [(l + h) / 2 for l, h in zip(lo, hi)]
    order = sorted(range(3), key=lambda i: -ext[i])
    a, b, n = order  # long side, second side, thickness direction of leg 1
    legs = []
    for thin in (n, b):
        dims = list(ext)
        dims[thin] = t
        pos = list(c)
        pos[thin] = lo[thin] + t / 2
        legs.append(Pos(*pos) * Box(*dims))
    return Compound(legs)


def six_panel_door(lo, hi):
    """Six-panel door slab: two columns of panels (short, tall, tall from the
    top down) on both faces. Each panel is a slightly raised frame with a
    raised field inside it, which gives the double outline of a real panel.
    The door's thickness runs along Y."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    w, h = x1 - x0, z1 - z0
    slab = Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(w, y1 - y0, h)

    stile, rail = 0.14 * w, 0.06 * h  # frame widths between panels
    pw = (w - 3 * stile) / 2
    # panel heights from the top: short, tall, tall (with rails between)
    heights = [0.17 * h, 0.32 * h]
    heights.append(h - 4 * rail - sum(heights))
    rows, top = [], z1 - rail
    for ph in heights:
        rows.append((top - ph / 2, ph))
        top -= ph + rail

    panels = []
    for face_y, sign in ((y0, -1), (y1, 1)):
        for col in range(2):
            cx = x0 + stile + pw / 2 + col * (pw + stile)
            for cz, ph in rows:
                panels.append(Pos(cx, face_y + sign * 0.06, cz) * Box(pw, 0.12, ph))
                panels.append(Pos(cx, face_y + sign * 0.18, cz) * Box(pw - 1.5, 0.12, ph - 1.5))
    return Compound([slab, *panels])
