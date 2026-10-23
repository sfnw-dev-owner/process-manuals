"""Cut_Lists/Structural_Triangle_Parts.md: the structural triangle's parts,
spread apart, seen from inside, with a detail of the E studs' two cuts."""

from build123d import Cylinder, Location, Pos, Rot, scale

from model.common import key
from model.notes import Circle, Label, Leader
from model.roof import TRI_E, TRI_PEAK, structural_triangle, triangle_parts

from . import Figure, camera, figure_names

MD = "Cut_Lists/Structural_Triangle_Parts.md"
VIEW = camera((0, -1, 0))  # from inside: X to the right, Z up
# How far each part is moved apart from where it goes in the triangle
EXPLODE = {"B": (0, 4), "C": (0, 8), "D": (0, 8), "E": (4, 8), "A": (0, 16)}
DETAIL_SCALE = 2
DETAIL_AT = (24.08, 32.05)  # where the enlarged E top is drawn
DETAIL_R = 2.43  # radius of the circled area


def figures():
    parts, notes = [], []
    shown = {"manual:structural_triangle_parts"}
    e_top = None
    for letter, instances in triangle_parts().items():
        dx, dy = EXPLODE[letter]
        for comp, loc, mods in instances:
            mirrored = "mirror" in mods
            at = Pos(-dx if mirrored else dx, dy, 0) * VIEW
            shape = at * loc * comp.shape(frozenset(), key(mods))
            parts.append((shape, "outline"))
            for l, note in comp.notes(shown):
                p = (loc * l).position
                q = (at * Pos(-p.X if mirrored else p.X, p.Y, p.Z)).position
                notes.append((q.X, q.Y, note))
            if letter == "E" and not mirrored:
                e_top = (shape, (dx + TRI_E + 0.75, dy + TRI_PEAK - DETAIL_R / 3))
    # Detail: the E stud's top, enlarged, showing its two cuts
    shape, (x, y) = e_top
    clip = Pos(x, y, 0) * Cylinder(DETAIL_R, 100)
    X, Y = DETAIL_AT
    # (scale() scales about the origin, but not a shape's own placement: scale
    # the clipped part where it is, then move it)
    k = DETAIL_SCALE
    detail = Pos(X - k * x, Y - k * y, 0) * scale(shape & clip, k)
    parts.append((detail, "outline"))
    notes += [
        (x, y, Circle(DETAIL_R)),
        (X, Y, Circle(DETAIL_R * DETAIL_SCALE)),
        (7.15, 21.71, Leader(((12.79, 7.81),), arrow=False)),
        (29.36, 31.83, Leader(((5.1, -1.68), (7.1, -1.68)))),
        (29.08, 33.72, Leader(((4.93, 0),))),
        (37.46, 31.15, Label("First Cut", 2, attach=1)),
        (34.46, 35.15, Label("Second Cut", 2, attach=1)),
    ]
    fig_name, = figure_names(MD)
    return [Figure(MD, fig_name, parts, notes)]
