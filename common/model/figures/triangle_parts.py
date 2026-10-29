"""Cut_Lists/Structural_Triangle_Parts.md: the structural triangle's parts,
spread apart, seen from inside, lettered, with a detail of the E studs' two
cuts."""

from build123d import Cylinder, Pos

from model.common import key
from model.notes import Label, around, callout, line, beside
from model.roof import TRI_E, TRI_NOTCH_HALF, TRI_PEAK, tri_top, triangle_parts

from . import Extent, camera, enlarged, table

MD = "Cut_Lists/Structural_Triangle_Parts.md"
PAPER_NOTES = True
VIEW = camera((0, -1, 0))  # from inside: X to the right, Z up
# How far each part is moved apart from where it goes in the triangle
EXPLODE = {"B": (0, 4), "C": (0, 8), "D": (0, 8), "E": (4, 8), "A": (0, 16)}
LETTER = 3/16  # the parts' letters, paper inches
DETAIL_SCALE = 2
DETAIL_R = 2.43  # radius of the circled area, drawing inches
DETAIL_OFF = (20, 6)  # the enlarged detail this far right of and above the peak


def figures(scale=1/15):
    parts, notes = [], []
    e_top = None
    for letter, instances in triangle_parts().items():
        dx, dy = EXPLODE[letter]
        for comp, loc, mods in instances:
            mirrored = "mirror" in mods
            at = Pos(-dx if mirrored else dx, dy, 0) * VIEW
            shape = at * loc * comp.shape(frozenset(), key(mods))
            parts.append((shape, "outline"))
            e = Extent(shape)
            # the letter: below B, above A and C, beside the studs (outside E, inside D)
            if letter == "B":
                notes.append(beside(e.bottom, "below", Label(letter, LETTER), 1/8))
            elif letter == "A":
                notes.append(beside(e.point(0.5, 1), "above", Label(letter, LETTER), 0))
            elif letter == "C":
                notes.append(beside(e.top, "above", Label(letter, LETTER), 1/8))
            else:  # E outside (away from the center), D inside
                outward = e.center[0] > 0
                on_right = outward if letter == "E" else not outward
                notes.append(beside(e.right if on_right else e.left, "right" if on_right else "left", Label(letter, LETTER), 1/8))
            if letter == "E" and not mirrored:
                e_top = (shape, (dx + TRI_E + 0.75, dy + TRI_PEAK - DETAIL_R / 3))
    # Detail: the E stud's top, enlarged, showing its two cuts
    shape, (x, y) = e_top
    clip = Pos(x, y, 0) * Cylinder(DETAIL_R, 100)
    peak = (0, EXPLODE["A"][1] + tri_top(TRI_NOTCH_HALF))
    at = (peak[0] + DETAIL_OFF[0], peak[1] + DETAIL_OFF[1] + DETAIL_R * DETAIL_SCALE)
    detail, to_drawing = enlarged(shape & clip, Pos(0, 0, 0), DETAIL_SCALE, at)
    parts.append((detail, "outline"))
    r = DETAIL_R * scale
    notes += [around((x, y), r), around(at, r * DETAIL_SCALE),
              line((x, y), at, scale, short=(r, r * DETAIL_SCALE))]
    # the cuts, on the enlarged stud: the pitch cut (first), then the flat top under the ridge (second)
    top = Extent(detail)
    notes += callout(top.point(0.3, 1), "Second Cut", "above right", lead=1/2)
    notes += callout(top.point(1, 0.85), "First Cut", "right", lead=1/2)
    return table(MD, {"parts": (parts, [], notes)})
