"""Structural_Triangle/triangle.md: building the structural triangle from
its cut parts (model/roof.py triangle_parts), seen face on, step by step:
B and the A sides, then C and the E studs, nailing them, then the D studs.

A table of its figures: the parts, and the notes hung on the parts'
extents in the drawing (X from the triangle's center, Y up from the base)."""

import math

from model.common import key
from model.lumber import thickness
from model.notes import Label, aimed, callout, next_to, pointer
from model.roof import T, TRI_BASE, TRI_BASE_END, TRI_D, TRI_E, TRI_NOTCH_HALF, tri_top, triangle_parts

from . import Extent, camera, table

MD = "Structural_Triangle/triangle.md"
PAPER_NOTES = True
VIEW = camera((0, -1, 0))  # face on: X to the right, Z up
SMALL_GUN = 0.6  # the nail gun icon, scaled down
SCREWS_IN = 4  # the sides' screws into the base, this far in from the base's ends
CLAMP_IN = 2  # the clamps, this far in

# step -> (the parts it adds, the parts it's still working on); earlier
# parts are drawn gray
STEPS = {1: ("BA", ""), 2: ("CE", ""), 3: ("", "CE"), 4: ("", "CE"), 5: ("D", "")}


def figures():
    stud = thickness("2x4")
    pitch = math.degrees(math.atan(T))
    shapes = {letter: [VIEW * loc * comp.shape(frozenset(), key(mods)) for comp, loc, mods in instances]
              for letter, instances in triangle_parts().items()}
    everything = [s for ss in shapes.values() for s in ss]
    e_studs = sorted((Extent(s) for s in shapes["E"]), key=lambda e: e.x0)

    def on_side(x):
        """A point on a side's top edge, and the direction (degrees) from a
        tool outside the slope in toward it."""
        return (x, tri_top(x)), (pitch - 90 if x < 0 else 270 - pitch)

    def side_screw(x):
        p, toward = on_side(x)
        screw = aimed(p, "Screw", toward)
        return [screw, next_to(screw, "above right" if x < 0 else "above left", Label("x3"))]

    def clamp(x):
        p, _ = on_side(x)
        return [pointer(p, 0, 3/8)] + callout((x, 0), "CLAMP", "below", lead=1/2)

    def gun(point, toward, count=None, size=SMALL_GUN, flip=None):
        g = aimed(point, "NailGun", toward, size, flip=flip)
        return [g] if count is None else [g, next_to(g, toward if isinstance(toward, str) else "below", Label(count))]

    # (the guns' bodies point away from the center, so a pair doesn't collide)
    def through_side(x, count="x2"):
        """A gun on the side above a stud, nailing down into it."""
        return gun(on_side(x)[0], "above", count, flip=x < 0)

    def through_base(x, count="x2"):
        """A gun under the base, nailing up into a stud."""
        return gun((x, 0), "below", count, flip=x > 0)

    notes = {
        1: (side_screw(-(TRI_BASE_END - SCREWS_IN)) + side_screw(TRI_BASE_END - SCREWS_IN)
            + clamp(-(TRI_BASE_END - CLAMP_IN)) + clamp(TRI_BASE_END - CLAMP_IN)),
        # C to the base from below, a gun at each side of it
        2: through_base(-stud / 3) + through_base(stud / 3),
        # E's outer faces into C, two nails each
        3: [g for e, side in zip(e_studs, ("left", "right"))
            for g in gun((e.x0 if side == "left" else e.x1, e.y0 + e.height / 4), side) + gun((e.x0 if side == "left" else e.x1, e.y0 + 3 * e.height / 4), side)],
        # the E studs' tops through the sides, and C through the base
        4: through_side(-(TRI_E + stud / 2)) + through_side(TRI_E + stud / 2) + through_base(-stud / 3),
        # the D studs: through the sides and the base
        5: (through_side(-(TRI_D + stud / 2)) + through_side(TRI_D + stud / 2)
            + through_base(-(TRI_D + stud / 2)) + through_base(TRI_D + stud / 2)),
    }
    rows, done = {}, ""
    for step, (adds, working) in STEPS.items():
        parts = [(s, "jig") for s in everything]
        parts += [(s, "context") for letter in done if letter not in working for s in shapes[letter]]
        parts += [(s, "new") for letter in adds + working for s in shapes[letter]]
        rows[f"step_{step}"] = (parts, [], notes[step])
        done += adds
    return table(MD, rows)
