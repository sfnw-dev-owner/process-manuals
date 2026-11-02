"""The gable ends: the structural triangles under the rafters at the end
walls, and the siding and Z-flashing that skin them.

Per Structural_Triangle/triangle.md, Cut_Lists/Structural_Triangle_Parts.md
and Exterior_Trim/exterior_trim.md (triangles).

Frame: the roof's (roof.py), the triangle's own X from the wall's center.
"""

from build123d import Box, Location, Plane, Polygon, Pos, Rectangle, extrude

from .lumber import thickness
from .dimensions import END_WALL_PLATE_LENGTH
from .common import CORNER, component
from .walls import SIDING, WALL_DEPTH, WRAP
from .roof import RIDGE_BOARD, RIDGE_BOARD_BOTTOM, RIDGE_TOP, T


# ── structural triangles and gables ────────────────────────────────────────

# Structural triangle. Frame: X along the end wall from its
# center, Y through it (3 1/2", flush with the wall framing), Z up from the top
# of the wall. Its sloped top edges carry the rafters' underside.
TRI_HALF = END_WALL_PLATE_LENGTH / 2
TRI_BASE = thickness("2x4")  # the base 2x4 lies flat on the wall's top plate
TRI_SIDE_FOOT = 5  # the sides' feet on the base
TRI_NOTCH_HALF = 1 + 1/8  # the notch at the peak for the ridge beam
# Studs, by the distance of their inner edge from the center:
# the center stud C is centered; E studs beside it; D studs further out.
TRI_E = thickness("2x4") / 2
TRI_D = 16 + 1/2


def tri_top(x):
    """The triangle's sloped top edge (= rafters' underside), x from center."""
    return (TRI_HALF - abs(x)) * T


def tri_inner(x):
    """The underside of the triangle's sloped sides."""
    foot = TRI_HALF - TRI_BASE / T - TRI_SIDE_FOOT
    return TRI_BASE + (foot - abs(x)) * T


# Its parts, labeled as in Cut_Lists/Structural_Triangle_Parts.md: the base
# B (2x4 flat, both ends cut at the pitch), the sloped sides A, the center
# stud C, and the studs E beside it and D further out, their tops cut at the
# pitch (E's tip then cut off under the ridge beam). Each part is placed in
# the triangle's frame; the right-hand A, D and E are mirrored.
TRI_BASE_END = TRI_HALF - TRI_BASE / T  # where the base's top meets the sides
TRI_FOOT = TRI_BASE_END - TRI_SIDE_FOOT  # the sides' inner foot on the base
TRI_PEAK = RIDGE_BOARD_BOTTOM  # the studs stop under the ridge beam


def _flat(face):
    return extrude(Plane.XZ * face, -WALL_DEPTH)


@component
def triangle_base():
    """B: 89" at the bottom."""
    face = Polygon((-TRI_HALF, 0), (TRI_HALF, 0), (TRI_BASE_END, TRI_BASE), (-TRI_BASE_END, TRI_BASE), align=None)
    return [_flat(face)], []


@component
def triangle_side():
    """A: the left side, from its foot on the base up to the ridge notch."""
    n = TRI_NOTCH_HALF
    face = Polygon((-TRI_BASE_END, TRI_BASE), (-TRI_FOOT, TRI_BASE), (-n, tri_inner(n)), (-n, tri_top(n)), align=None)
    return [_flat(face)], []


@component
def triangle_center_stud():
    """C: square cut, up to the ridge beam."""
    stud = thickness("2x4")
    return [_flat(Pos(-stud / 2, TRI_BASE) * Rectangle(stud, TRI_PEAK - TRI_BASE, align=CORNER))], []


def triangle_stud(x0):
    """A stud from x0 (its inner edge) outward, its top cut at the pitch to
    follow the sides' underside (the first cut), then flat where that would
    reach above the ridge beam (the second cut)."""
    x1 = x0 + thickness("2x4")
    top0, top1 = tri_inner(x0), tri_inner(x1)
    top = [(x1, min(top1, TRI_PEAK)), (x0, min(top0, TRI_PEAK))]
    if top1 < TRI_PEAK < top0:  # the pitch cut crosses the ridge beam's underside within the stud
        top.insert(1, (x0 + (top0 - TRI_PEAK) / T, TRI_PEAK))
    face = Polygon((x0, TRI_BASE), (x1, TRI_BASE), *top, align=None)
    return [_flat(face)], []


@component
def triangle_stud_e():
    """E: beside C."""
    return triangle_stud(TRI_E)


@component
def triangle_stud_d():
    """D: further out."""
    return triangle_stud(TRI_D)


def triangle_parts():
    """{label: [(component, location, mods)]} in the triangle's frame."""
    return {
        "B": [(triangle_base, Location(), [])],
        "A": [(triangle_side, Location(), []), (triangle_side, Location(), ['mirror'])],
        "C": [(triangle_center_stud, Location(), [])],
        "E": [(triangle_stud_e, Location(), []), (triangle_stud_e, Location(), ['mirror'])],
        "D": [(triangle_stud_d, Location(), []), (triangle_stud_d, Location(), ['mirror'])],
    }


@component
def structural_triangle():
    return [], [(c, loc, mods, '') for parts in triangle_parts().values() for c, loc, mods in parts]


# The gable skin (Exterior_Trim/exterior_trim.md, "Exterior Triangles"):
# pre-cut Tyvek stapled to the structural triangle, Z-flashing over the top
# of the wall's siding, then T1-11 in two pieces: a large triangle and a small
# one at the left corner (as seen from outside).
# Frame: X along the wall from its center, Y outward from the framing, Z up
# from the wall top. Seen from outside, the left is +X.
GABLE_NOTCH = thickness(RIDGE_BOARD)  # half-width of the notch around the ridge boards
Z_FLASHING = 1/32  # sheet metal
Z_FLASHING_SHORT_LEG = 1/2  # down over the wall's siding
Z_FLASHING_LONG_LEG = 2  # up behind the gable siding
GABLE_SIDING_LIFT = 1/2  # "a pencil-width above the Z-flashing fold"
GABLE_SMALL_PIECE = 8 + 1/2  # the small triangle's length at the bottom


def gable_outline(bottom=0):
    """The gable up to the rafters' underside, notched for the ridge boards,
    from `bottom` up."""
    half = TRI_HALF - bottom / T
    n = GABLE_NOTCH
    return Polygon((-half, bottom), (half, bottom), (n, tri_top(n)), (n, RIDGE_BOARD_BOTTOM),
                   (-n, RIDGE_BOARD_BOTTOM), (-n, tri_top(n)), align=None)


@component
def gable_wrap():
    return [extrude(Plane.XZ * gable_outline(), -WRAP)], []


@component
def z_flashing():
    """Centered on the wall, its long leg's ends cut to the roof pitch."""
    half, t = TRI_HALF, Z_FLASHING
    long_leg = Polygon((-half, 0), (half, 0), (half - Z_FLASHING_LONG_LEG / T, Z_FLASHING_LONG_LEG),
                       (-half + Z_FLASHING_LONG_LEG / T, Z_FLASHING_LONG_LEG), align=None)
    solids = [
        Pos(0, WRAP, t) * extrude(Plane.XZ * long_leg, -t),
        Pos(-half, WRAP, 0) * Box(2 * half, SIDING + t, t, align=CORNER),  # resting on the siding's top edge
        Pos(-half, WRAP + SIDING, -Z_FLASHING_SHORT_LEG) * Box(2 * half, t, Z_FLASHING_SHORT_LEG + t, align=CORNER),
    ]
    return solids, []


def gable_siding_piece(x0, x1):
    """The gable's T1-11 between x0 and x1 (along the wall from its center)."""
    face = gable_outline(GABLE_SIDING_LIFT) & Pos(x0, 0) * Rectangle(x1 - x0, RIDGE_TOP, align=CORNER)
    return Pos(0, WRAP + Z_FLASHING, 0) * extrude(Plane.XZ * face, -SIDING)


SMALL_PIECE_X = TRI_HALF - GABLE_SIDING_LIFT / T - GABLE_SMALL_PIECE  # the seam


@component
def gable_siding_large():
    return [gable_siding_piece(-TRI_HALF, SMALL_PIECE_X)], []


@component
def gable_siding_small():
    return [gable_siding_piece(SMALL_PIECE_X, TRI_HALF)], []


@component
def gable_skin():
    """House wrap, Z-flashing and T1-11 in a gable, above the end wall's siding."""
    children = [
        (gable_wrap, Location(), [], ''),
        (z_flashing, Location(), [], ''),
        (gable_siding_large, Location(), [], ''),
        (gable_siding_small, Location(), [], ''),
    ]
    return [], children
