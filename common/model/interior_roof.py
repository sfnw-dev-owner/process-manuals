"""The inside of the roof: ceiling panels, roof insulation, the interior
half-triangle panels on the end walls, the triangle and ceiling trim, and the
vent cap along the ridge.

Per Interior_Panels/interior_panels.md (+ images/ceiling_panels.dxf,
images/wall_panels.dxf), Cut_Lists/Interior_Panels_Cut_List.md,
Cut_Lists/Insulation.md, Cut_Lists/Interior_Trim_Items.md,
Interior_Trim/interior_trim.md and Interior_Trim/vent_cap_install.md
(+ Images/vent_cap.dxf).

Frame: the roof's (roof.py): the house's X and Y, Z = 0 at the top of the walls.
"""

from .common import *
from .roof import (
    C, S, T, RAFTER, RAFTER_DEPTH, RAFTER_Y, RIDGE_BOARD_BOTTOM, RIDGE_X, SEAT_X, SLOPE, TIP_X,
    TRI_BASE, TRI_D, TRI_E, TRI_HALF, TRI_SIDE_FOOT, VENT_BLOCK_THICKNESS,
    tri_inner, underside, wall_bays,
)
from .interior import END_PANEL_TOP, PANEL
from .interior_notes import (
    FLAT_VIEW, TRIANGLE_PANELS_VIEW, ceiling_panels_notes, triangle_panels_notes, vent_cap_notes, view_at,
)
from .walls import WALL_DEPTH, WALL_HEIGHT
TRIM = "1/2x2"
INSIDE_REAR = WALL_DEPTH  # the end walls' framing, inside faces
INSIDE_FRONT = PLATFORM_LENGTH - WALL_DEPTH

# The half-triangles sit on the end walls' interior panels (interior.py),
# which stop a little short of the wall top.
WALL_PANEL_TOP = END_PANEL_TOP - WALL_HEIGHT

# Ceiling panels butt against the vent blocks at the top.
CEILING_TOP_U = (TIP_X - VENT_BLOCK_THICKNESS - SEAT_X) / C


def ceiling(x):
    """Height of the ceiling (underside of the ceiling panels) at x, left half."""
    return underside(x) - PANEL / C


@component
def interior_roof():
    solids = []
    children = [
        (ceiling_half, Location(), [], ''),
        (ceiling_half, Pos(PLATFORM_WIDTH, 0, 0), ['mirror'], ''),
        (end_wall_interior, Pos(RIDGE_X, INSIDE_REAR, 0), [], ''),
        (end_wall_interior, Pos(RIDGE_X, INSIDE_FRONT, 0) * Rot(Z=180), [], ''),
        (triangle_insulation, Pos(RIDGE_X, 0, 0), [], ''),
        (triangle_insulation, Pos(RIDGE_X, INSIDE_FRONT, 0), [], ''),
        (vent_cap, Location(), [], ''),
    ]
    return solids, children


@component
def ceiling_half():
    """One side's ceiling: panels R1 (from the rear) and R2 under the rafters,
    batts above them in each bay, and trim over the seam between the panels."""
    r1 = CEILING_R1[1]
    width_ = CEILING_R1[0]  # up the slope
    bottom_u = CEILING_TOP_U - width_
    children = [
        (ceiling_panel_r1, SLOPE * Pos(bottom_u, INSIDE_REAR, -PANEL), [], 'panels'),
        (ceiling_panel_r2, SLOPE * Pos(bottom_u, INSIDE_REAR + r1, -PANEL), [], 'ceiling_r2'),
        # Seam trim: 42", from the side wall's top trim up toward the vent.
        (ceiling_seam_trim, SLOPE * Pos(bottom_u, INSIDE_REAR + r1 - width(TRIM) / 2, -PANEL - thickness(TRIM)),
         [], 'ceiling_trim'),
        *[(batt(b - a), SLOPE * Pos(CEILING_TOP_U - ROOF_BATT_LENGTH, (a + b) / 2 - batt_width(b - a) / 2, 0), [], '')
          for a, b in wall_bays()],
        *ceiling_panels_notes(view_at(CEILING_VIEW), ceiling_rafter_screws()),
    ]
    return [], children


# Interior_Panels/interior_panels.md's ceiling figure: the left half's panels
# seen from below, flattened out of the slope, the rear to the left; the
# figure's last view (with the rafter screws) has R1's rear bottom corner at
# CEILING_VIEW_ORIGIN.
CEILING_VIEW_ORIGIN = (26.5 + INSIDE_REAR, -254)
CEILING_VIEW = (Pos(CEILING_VIEW_ORIGIN[0] - INSIDE_REAR, CEILING_VIEW_ORIGIN[1] - (CEILING_TOP_U - CEILING_R1[0]), 0)
                * FLAT_VIEW * SLOPE.inverse())
CEILING_SCREWS_UP = (1, 13, 25, 37, 42 + 7/8)  # up the slope from the panels' bottom edge (screw pattern board)


def ceiling_rafter_screws():
    """Screws through the panels into each rafter they cover, except at the
    panels' edges (preset): as (x, y) in the ceiling figure."""
    seam = INSIDE_REAR + CEILING_R1[1]
    ends = (INSIDE_REAR, INSIDE_REAR + CEILING_R1[1] + CEILING_R2[1])
    centers = [y + RAFTER / 2 for y in RAFTER_Y]
    inner = [c for c in centers if ends[0] + 2 < c < ends[1] - 2 and abs(c - seam) > 2]
    x0, y0 = CEILING_VIEW_ORIGIN
    return [(x0 + c - INSIDE_REAR, y0 + u) for c in inner for u in CEILING_SCREWS_UP]


@component
def ceiling_panel_r1():
    """Ceiling panel R1: up the slope (X) by along the house (Y), under the
    rafters; its factory edge (the front) on a rafter's centerline."""
    return [Sheet(PANEL, *CEILING_R1, facing="Z")], []


@component
def ceiling_panel_r2():
    """Ceiling panel R2, in front of R1; its factory edge (the rear) against R1."""
    return [Sheet(PANEL, *CEILING_R2, facing="Z")], []


@component
def ceiling_seam_trim():
    return [board(TRIM, CEILING_TRIM_LENGTH, along="X", wide="Y")], []


# ── roof insulation ────────────────────────────────────────────────────────

ROOF_BATT_THICKNESS = 3  # as modeled in SketchUp


def batt_width(bay):
    """The cut list's batt for a bay, squeezed to fit between the rafters."""
    return min(ROOF_BATT_WIDTH if bay > 20 else ROOF_BATT_END_WIDTH, bay)


def batt(bay):
    return _batt(batt_width(bay))


@cache
def _batt(w):
    @component
    def roof_batt():
        return [Box(ROOF_BATT_LENGTH, w, ROOF_BATT_THICKNESS, align=CORNER)], []
    return roof_batt


@component
def triangle_insulation():
    """Insulation cut to fill the open spaces in a structural triangle (from
    the roof batts' cutoffs; Cut_Lists/Insulation.md). Frame: the triangle's."""
    stud = thickness("2x4")
    foot = TRI_HALF - TRI_BASE / T - TRI_SIDE_FOOT
    spaces = [
        [(TRI_D + stud, TRI_BASE), (foot, TRI_BASE), (TRI_D + stud, tri_inner(TRI_D + stud))],
        [(TRI_E + stud, TRI_BASE), (TRI_D, TRI_BASE), (TRI_D, tri_inner(TRI_D)), (TRI_E + stud, tri_inner(TRI_E + stud))],
    ]
    solids = []
    for pts in spaces:
        solids.append(extrude(Plane.XZ * Polygon(*pts, align=None), -WALL_DEPTH))
        mirrored = [(-x, z) for x, z in reversed(pts)]
        solids.append(extrude(Plane.XZ * Polygon(*mirrored, align=None), -WALL_DEPTH))
    return solids, []


# ── end walls: half-triangle panels and trim ───────────────────────────────

# Half-triangle panel (Interior_Panels/images/wall_panels.dxf, layer
# 04_Triangle_Panels): 44 1/2" along the bottom, a 1" x 2" notch at the peak.
HALF_TRIANGLE_BASE = END_WALL_PLATE_LENGTH / 2
HALF_TRIANGLE_NOTCH = (1, 2)
TRIANGLE_TRIM_GAP = 1/2  # between an angled piece's end and the center piece


@component
def end_wall_interior():
    """The inside of an end wall above the wall panels. Frame: X along the
    wall from the center (as seen from inside, left to right), Y into the
    house from the framing's inside face, Z from the wall top."""

    # Trim on the panels: two angled 42" pieces tight up against the ceiling,
    # meeting a 12" vertical piece over the seam at the center; and a
    # straight 42" piece on the ceiling tight against each angled piece.
    t, w = thickness(TRIM), width(TRIM)
    c = width(TRIM) / 2  # the center piece's half-width
    run = TRIANGLE_TRIM_LENGTH * C

    def ceiling_at(x):  # ceiling height over this wall, x from the center
        return ceiling(RIDGE_X - abs(x))

    # (As the drawing had them: each angled piece runs from the corner, where
    # its bottom is cut square to sit on the top trim, up along the ceiling
    # to just short of the center piece, which stands on the top trim too,
    # leaving the peak above it open. The corner-to-center run is about the
    # 42" piece.)
    def angled(sign):
        x0, x1 = sign * (c + TRIANGLE_TRIM_GAP), sign * (HALF_TRIANGLE_BASE + 2)
        # its top end cut square to its length (down and away from the ceiling)
        pts = [(x0, ceiling_at(x0)), (x1, ceiling_at(x1)), (x1, ceiling_at(x1) - w / C), (x0 - sign * w * S, ceiling_at(x0) - w * C)]
        strip = Pos(0, PANEL, 0) * into_house(pts, t)
        above = Pos(-200, -50, 0) * Box(400, 100, 100, align=CORNER)  # above the top trim
        return strip & above

    center = Pos(-c, PANEL, 0) * board(TRIM, TRIANGLE_CENTER_TRIM_LENGTH, along="Z", wide="X")

    def on_ceiling(sign):  # a straight piece on the ceiling, beside the angled one
        x0, x1 = sign * c, sign * (c + run)
        pts = [(x0, ceiling_at(x0)), (x1, ceiling_at(x1)), (x1, ceiling_at(x1) - t / C), (x0, ceiling_at(x0) - t / C)]
        return Pos(0, PANEL + t, 0) * into_house(pts, w)

    return [], [
        (half_triangle_left, Pos(0, 0, WALL_PANEL_TOP), [], 'half_triangles'),
        (half_triangle_right, Pos(0, 0, WALL_PANEL_TOP), [], 'half_triangles'),
        (_part(angled(1), angled(-1), center, on_ceiling(1), on_ceiling(-1)), Location(), [], 'triangle_trim'),
        *triangle_panels_notes(view_at(TRIANGLE_PANELS_VIEW * END_INTERIOR_AT)),
    ]


# An end wall's interior (above) in that wall's frame (walls.py: Y outward,
# Z from the deck); with the 'mirror' modifier, it flips only Y.
END_INTERIOR_AT = Pos(END_WALL_PLATE_LENGTH / 2, 0, WALL_HEIGHT) * Rot(Z=180)


def half_triangle(sign):
    """A half-triangle panel (wall_panels.dxf, layer 04_Triangle_Panels), its
    short edge at the center (x = 0), a 1" x 2" notch at the peak; sign -1
    for the left one as seen from inside, +1 for the right."""
    b = HALF_TRIANGLE_BASE
    nw, nh = HALF_TRIANGLE_NOTCH
    rise = b * T
    pts = [(b, 0), (0, 0), (0, rise - nh), (nw, rise - nh), (nw, rise - nw * T)]
    return into_house([(sign * x, z) for x, z in pts], PANEL)


def into_house(pts, depth):
    """A flat piece against the end wall: the outline pts (x, z), `depth`
    thick into the house (+Y), whichever way the outline winds."""
    return extrude(Plane.XZ * Polygon(*pts, align=None), amount=depth, dir=(0, 1, 0))


@component
def half_triangle_left():
    return [half_triangle(-1)], []


@component
def half_triangle_right():
    return [half_triangle(1)], []


def _part(*solids):
    @component
    def part():
        return list(solids), []
    return part


# ── vent cap ───────────────────────────────────────────────────────────────

VENT_CAP_THICKNESS = 1/2  # plywood; as modeled in SketchUp


@component
def vent_cap():
    """Plywood along the underside of the ridge, on 2x4 support blocks laid
    crosswise under the vent blocks: a 96" piece from the rear wall's trim,
    then a piece cut to reach the front wall's trim."""
    block_z = underside(TIP_X - VENT_BLOCK_THICKNESS) + RAFTER_DEPTH / C - VENT_BLOCK_HEIGHT
    cap_z = block_z - thickness("2x4")
    x = RIDGE_X - VENT_CAP_WIDTH / 2
    # Support blocks: at the rear end, the middle of the long piece, its
    # seam (its front edge half-way onto that block), and the front end.
    b, w = VENT_CAP_BLOCK_LENGTH, width("2x4")
    blocks = [VENT_CAP_REAR, VENT_CAP_REAR + VENT_CAP_LENGTH / 2 - w / 2, VENT_CAP_SEAM - w / 2, VENT_CAP_FRONT - w]
    return [], [
        (vent_cap_long, Pos(x, VENT_CAP_REAR, cap_z - VENT_CAP_THICKNESS), [], ''),
        (vent_cap_short, Pos(x, VENT_CAP_SEAM, cap_z - VENT_CAP_THICKNESS), [], ''),
        *[(vent_cap_block, Pos(RIDGE_X - b / 2, y, cap_z), [], '') for y in blocks],
        *vent_cap_notes(view_at(VENT_CAP_VIEW), VENT_CAP_SHORT),
    ]


VENT_CAP_REAR = INSIDE_REAR + PANEL + thickness(TRIM)  # against the rear wall's trim
VENT_CAP_FRONT = INSIDE_FRONT - PANEL - thickness(TRIM)
VENT_CAP_SEAM = VENT_CAP_REAR + VENT_CAP_LENGTH
VENT_CAP_SHORT = VENT_CAP_FRONT - VENT_CAP_SEAM  # cut to fit

# Screw holes (Images/vent_cap.dxf): drilled and countersunk in pairs, 3 1/2"
# in from each long edge, over the blocks' centers: 1 3/4" from the ends at
# the walls, 3/4" from the seam (the blocks there are shared), and at the
# middle block.
VENT_CAP_HOLE = 1/2
VENT_CAP_HOLE_INSET = 3 + 1/2
VENT_CAP_END_HOLES = width("2x4") / 2
VENT_CAP_SEAM_HOLES = 3/4


def vent_cap_piece(length, holes_along):
    board = Box(VENT_CAP_WIDTH, length, VENT_CAP_THICKNESS, align=CORNER)
    for y in holes_along:
        for x in (VENT_CAP_HOLE_INSET, VENT_CAP_WIDTH - VENT_CAP_HOLE_INSET):
            board -= Pos(x, y, 0) * Cylinder(VENT_CAP_HOLE / 2, VENT_CAP_THICKNESS, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return board


@component
def vent_cap_long():
    """The 96" piece (1/2 x 9-1/2 wide trim), from the rear."""
    L = VENT_CAP_LENGTH
    return [vent_cap_piece(L, [VENT_CAP_END_HOLES, L / 2, L - VENT_CAP_SEAM_HOLES])], []


@component
def vent_cap_short():
    """The piece cut to reach the front wall's trim."""
    L = VENT_CAP_SHORT
    return [vent_cap_piece(L, [VENT_CAP_SEAM_HOLES, L - VENT_CAP_END_HOLES])], []


@component
def vent_cap_block():
    """A support block: half of an 11 1/2" 2x4, laid crosswise; two brown
    screws preset through its middle."""
    return [TwoByFour(VENT_CAP_BLOCK_LENGTH, along="X", wide="Y")], []


# Interior_Trim/vent_cap_install.md's figure: the vent cap's pieces seen from
# below, laid out with the rear to the left: the long piece's rear-left
# corner at (42, 100).
VENT_CAP_VIEW = Pos(42 - VENT_CAP_REAR, 100 - (RIDGE_X - VENT_CAP_WIDTH / 2), 0) * FLAT_VIEW
