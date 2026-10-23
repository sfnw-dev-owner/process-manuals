"""Exterior trim: corner boards and window trim. (Fascia is with the roof.)

Per Exterior_Trim/exterior_trim.md. Frame: Z = 0 at the top of the walls.
"""

from functools import cache
from math import cos, radians, sin, tan

from .common import *
from .dimensions import WINDOW_OPENING
from .platform import DECK
from .walls import SIDING, SIDING_Y, WALL_DEPTH, WALL_HEIGHT, WINDOW_X, WINDOW_Z, WRAP

# The house puts this assembly at its origin: its children are in the
# house's frame.
# The end walls' places in the house (as house.py puts them).
FRONT_WALL_IN_HOUSE = Pos(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, DECK)
REAR_WALL_IN_HOUSE = Pos(PLATFORM_WIDTH - WALL_DEPTH, WALL_DEPTH, DECK) * Rot(Z=180)

# ── corner boards ──────────────────────────────────────────────────────────
# Exterior_Trim/exterior_trim.md (Corner Trim) and images/back_corner.dxf.
# At each corner two 1x4s, flush with the T1-11 siding top and bottom: Board
# #1 on the side wall, its corner edge flush with the end wall's siding, its
# top notched around the rafter that crosses it; Board #2 on the end wall,
# its corner edge flush with Board #1's face. Caulk goes behind each board
# along its inner edge (away from the corner).
CORNER_BOARD = "1x4"
CB_W, CB_T = width(CORNER_BOARD), thickness(CORNER_BOARD)
SIDING_OUT = WRAP + SIDING  # the siding's face, outside the framing
CORNERS = [(0, 0), (1, 0), (0, 1), (1, 1)]  # (left/right, rear/front)
CAULK_BEAD = (1/4, 1/16)  # wide, thick (squeezed flat)
CAULK_INSET = 1/2  # from the board's edge


def corner_frame(corner):
    """(side face X, outward X sign, end face Y, outward Y sign) at a corner."""
    sx, sy = corner
    ox, oy = (-1, 1)[sx], (-1, 1)[sy]
    side_face = (0, PLATFORM_WIDTH)[sx] + ox * SIDING_OUT
    end_face = (0, PLATFORM_LENGTH)[sy] + oy * SIDING_OUT
    return side_face, ox, end_face, oy


def span(a, b):
    """(start, length) of the interval between a and b."""
    return min(a, b), abs(b - a)


def rafters_in_house():
    from .roof import RAFTER_Y, SLOPE, TAIL_U, rafter
    left = [Pos(0, 0, DECK + WALL_HEIGHT) * SLOPE * Pos(TAIL_U, y, 0) * rafter.shape() for y in RAFTER_Y]
    return left + [Pos(PLATFORM_WIDTH, 0, 0) * r.mirror(Plane.YZ) for r in left]


def corner_board_boxes(corner):
    """Board #1 and Board #2 (unnotched) at a corner, in the house frame."""
    side_face, ox, end_face, oy = corner_frame(corner)
    z0 = DECK + WALL_HEIGHT - SIDING_HEIGHT
    x1, dx1 = span(side_face, side_face + ox * CB_T)
    y1, dy1 = span(end_face, end_face - oy * CB_W)
    x2, dx2 = span(side_face + ox * CB_T, side_face + ox * CB_T - ox * CB_W)
    y2, dy2 = span(end_face, end_face + oy * CB_T)
    return (Pos(x1, y1, z0) * Box(dx1, dy1, SIDING_HEIGHT, align=CORNER),
            Pos(x2, y2, z0) * Box(dx2, dy2, SIDING_HEIGHT, align=CORNER))


def board_notch(corner):
    """Board #1's notch: from the face of the rafter crossing it to its inner
    edge, and from the rafter's bottom up."""
    board = corner_board_boxes(corner)[0]
    _, _, end_face, oy = corner_frame(corner)
    hits = [h for h in (board & r for r in rafters_in_house()) if h.volume > 1e-6]
    if not hits:
        return None
    bb = board.bounding_box()
    boxes = [h.bounding_box() for h in hits]
    face = max(b.min.Y for b in boxes) if oy > 0 else min(b.min.Y for b in boxes)  # nearest the corner
    if oy > 0:
        face = max(b.max.Y for b in boxes)
    inner = bb.max.Y if oy < 0 else bb.min.Y
    bottom = min(b.min.Z for b in boxes)
    y, dy = span(face, inner)
    return Pos(bb.min.X - 1, y, bottom) * Box(bb.size.X + 2, dy, bb.max.Z - bottom + 1, align=CORNER)


def shape_component(shape, name):
    """A plain shape as a component (a caulk bead and the like)."""
    def solid():
        return [shape], []
    solid.__name__ = name
    return component(solid)


@cache
def corner_board_1(corner):
    def board_1():
        board = corner_board_boxes(corner)[0]
        notch = board_notch(corner)
        side_face, ox, end_face, oy = corner_frame(corner)
        bb = board.bounding_box()
        w, t = CAULK_BEAD
        i = CAULK_INSET
        d = -oy  # along Y from the corner edge to the inner edge
        outer, inner = (bb.min.Y, bb.max.Y) if d > 0 else (bb.max.Y, bb.min.Y)
        x, dx = span(side_face, side_face - ox * t)

        def across(y0, y1, z):  # a run across the board, its lower edge at z
            y, dy = span(y0, y1)
            return Pos(x, y, z) * Box(dx, dy, w, align=CORNER)

        def up(edge, z0, z1):  # a run up the board, inset from the edge at y = edge toward the corner
            y, dy = span(edge - d * i, edge - d * (i + w))
            return Pos(x, y, z0) * Box(dx, dy, z1 - z0, align=CORNER)

        # The bead follows the board's edges: along the top, around the notch
        # (inset from its cut faces too), then down the inner edge.
        if notch:
            nb = notch.bounding_box()
            face = nb.min.Y if d > 0 else nb.max.Y  # the notch's face, toward the corner
            runs = [across(outer + d * i, face - d * i, bb.max.Z - i - w), up(face, nb.min.Z - i, bb.max.Z - i),
                    across(face - d * i, inner - d * i, nb.min.Z - i - w), up(inner, bb.min.Z + i, nb.min.Z - i)]
        else:
            runs = [across(outer + d * i, inner - d * i, bb.max.Z - i - w), up(inner, bb.min.Z + i, bb.max.Z - i)]
        bead = runs[0]
        for r in runs[1:]:
            bead = bead + r
        return [board - notch if notch else board], [(shape_component(bead, "caulk_bead"), Location(), [], 'Caulk')]
    board_1.__name__ = f"corner_board_1_{corner[0]}{corner[1]}"
    return component(board_1)


@cache
def corner_board_2(corner):
    def board_2():
        board = corner_board_boxes(corner)[1]
        side_face, ox, end_face, oy = corner_frame(corner)
        bb = board.bounding_box()
        w, t = CAULK_BEAD
        x = (bb.min.X + CAULK_INSET) if ox > 0 else (bb.max.X - CAULK_INSET - w)
        y, dy = span(end_face, end_face - oy * t)
        bead = Pos(x, y, bb.min.Z + CAULK_INSET) * Box(w, dy, SIDING_HEIGHT - 2 * CAULK_INSET, align=CORNER)
        across = Pos(bb.min.X + CAULK_INSET, y, bb.min.Z + SIDING_HEIGHT - CAULK_INSET - w) * Box(bb.size.X - 2 * CAULK_INSET, dy, w, align=CORNER)
        return [board], [(shape_component(bead + across, "caulk_bead"), Location(), [], 'Caulk')]
    board_2.__name__ = f"corner_board_2_{corner[0]}{corner[1]}"
    return component(board_2)


@component
def external_trim():
    """Corner boards and window trim, placed in the house's frame."""
    children = []
    for corner in CORNERS:
        children += [(corner_board_1(corner), Location(), [], ''), (corner_board_2(corner), Location(), [], '')]
    children += [
        (window_trim, FRONT_WALL_IN_HOUSE * window_trim_in_wall(), [], ''),
        (window_trim, REAR_WALL_IN_HOUSE * window_trim_in_wall(), [], ''),
        *corner_manual(),
    ]
    return [], children


# ── window trim ────────────────────────────────────────────────────────────
# Exterior_Trim/exterior_trim.md (Rear/Front Window Trim) and
# images/{rear,front}_window.dxf. Precut 1x4s around the window's rough
# opening, overlapping it by TRIM_REVEAL on the window's flange: two sides,
# a top with a 30° bevel on its upper edge (overhanging the left side 1/2",
# flush with the right one: an A/C unit goes to the right of the rear
# window, the door jamb to the right of the front one), and a bottom cut to
# fit between the sides. Caulk goes behind the sides' outer edges and the
# top's bevel and ends; none behind the bottom.
#
# Frame: seen from outside: X to the right from the rough opening's left
# edge, Y up from its bottom, Z out from the siding's face.

WINDOW_TRIM = "1x4"
TRIM_REVEAL = 1/4  # the trim's overlap onto the rough opening
WINDOW_UNIT_INSET = 1/2  # the window unit's frame, inside the rough opening (as drawn)
WINDOW_SIDE_TRIM = 39 + 1/2  # precut
WINDOW_TOP_TRIM = 31  # precut
WINDOW_TOP_OVERHANG = 1/2  # past the left side trim
WINDOW_TOP_BEVEL = 30  # degrees
TRIM_NAIL_INSET = 1 + 1/2  # nails from each end
TRIM_NAIL_SPACING = 8  # "1 nail in the middle of the board every 8\""

TRIM_W, TRIM_T = width(WINDOW_TRIM), thickness(WINDOW_TRIM)
RO_W, RO_H = WINDOW_OPENING


@component
def window_side_trim():
    """Upright, X across its width, caulk behind its outer (left) edge; the
    right-hand side is the same board turned around."""
    solids = [Box(TRIM_W, WINDOW_SIDE_TRIM, TRIM_T, align=CORNER)]
    children = [(caulk_bead_up, Pos(CAULK_INSET, CAULK_INSET, -CAULK_BEAD[1]), [], 'Caulk')]
    return solids, children


@component
def caulk_bead_up():
    """Up the board's outer edge and across its top end (under the top trim)."""
    w, t = CAULK_BEAD
    i = CAULK_INSET
    return [Box(w, WINDOW_SIDE_TRIM - 2 * i, t, align=CORNER),
            Pos(0, WINDOW_SIDE_TRIM - 2 * i - w, 0) * Box(TRIM_W - 2 * i, w, t, align=CORNER)], []


@component
def window_top_trim():
    """Its upper front edge beveled 30° to shed water."""
    drop = TRIM_T * tan(radians(WINDOW_TOP_BEVEL))
    profile = Polygon((0, 0), (TRIM_W, 0), (TRIM_W - drop, TRIM_T), (0, TRIM_T), align=None)  # (y, z)
    board = extrude(Plane.YZ * profile, WINDOW_TOP_TRIM)
    return [board], [(window_top_caulk, Location(), [], 'Caulk')]


@component
def window_top_caulk():
    """Behind the beveled edge and at both ends."""
    w, t = CAULK_BEAD
    L, i = WINDOW_TOP_TRIM, CAULK_INSET
    return [
        Pos(i, TRIM_W - i - w, -t) * Box(L - 2 * i, w, t, align=CORNER),
        Pos(i, i, -t) * Box(w, TRIM_W - 2 * i - w, t, align=CORNER),
        Pos(L - i - w, i, -t) * Box(w, TRIM_W - 2 * i - w, t, align=CORNER),
    ], []


@component
def window_bottom_trim():
    """Cut to fit between the side trims. No caulk."""
    return [Box(RO_W - 2 * TRIM_REVEAL, TRIM_W, TRIM_T, align=CORNER)], []


def nail_marks(x0, y0, length, along_y, middle):
    """Panel-nail marks on a board from (x0, y0), `length` long along Y (or
    X): 2 nails TRIM_NAIL_INSET from each end, and `middle` evenly between."""
    ends = [TRIM_NAIL_INSET, length - TRIM_NAIL_INSET]
    along = [ends[0] + (ends[1] - ends[0]) * k / (middle + 1) for k in range(1, middle + 1)]
    across_pair, across_mid = (TRIM_W / 2 - 1, TRIM_W / 2 + 1), (TRIM_W / 2,)
    pts = [(a, c) for a in ends for c in across_pair] + [(a, c) for a in along for c in across_mid]
    return [Pos(x0 + c, y0 + a, TRIM_T) if along_y else Pos(x0 + a, y0 + c, TRIM_T) for a, c in pts]


SIDE_NAILS = int((WINDOW_SIDE_TRIM - 2 * TRIM_NAIL_INSET) // TRIM_NAIL_SPACING) - 1


def window_trim_parts():
    """{name: (component, location, mods)} of the trim boards, in the
    window-trim frame."""
    side_bottom = RO_H - TRIM_REVEAL - WINDOW_SIDE_TRIM
    left_x, right_x = TRIM_REVEAL - TRIM_W, RO_W - TRIM_REVEAL
    top_y = RO_H - TRIM_REVEAL
    return {
        "left": (window_side_trim, Pos(left_x, side_bottom, 0), []),
        "right": (window_side_trim, Pos(right_x + TRIM_W, side_bottom, 0), ['mirror']),
        "top": (window_top_trim, Pos(right_x + TRIM_W - WINDOW_TOP_TRIM, top_y, 0), []),
        "bottom": (window_bottom_trim, Pos(TRIM_REVEAL, TRIM_REVEAL - TRIM_W, 0), []),
    }


def window_trim_nails():
    side_bottom = RO_H - TRIM_REVEAL - WINDOW_SIDE_TRIM
    left_x, right_x = TRIM_REVEAL - TRIM_W, RO_W - TRIM_REVEAL
    top_x = right_x + TRIM_W - WINDOW_TOP_TRIM
    return (nail_marks(left_x, side_bottom, WINDOW_SIDE_TRIM, True, SIDE_NAILS)
            + nail_marks(right_x, side_bottom, WINDOW_SIDE_TRIM, True, SIDE_NAILS)
            + nail_marks(top_x, RO_H - TRIM_REVEAL, WINDOW_TOP_TRIM, False, 2)
            + nail_marks(TRIM_REVEAL, TRIM_REVEAL - TRIM_W, RO_W - 2 * TRIM_REVEAL, False, 2))


@component
def window_trim():
    from .notes import Circle
    children = [(c, loc, mods, '') for c, loc, mods in window_trim_parts().values()]
    children += [(Circle(0.15, fill=(0, 0, 0)), loc, [], "manual:exterior_trim:rear_window manual:exterior_trim:front_window")
                 for loc in window_trim_nails()]
    children += window_trim_manual()
    return [], children


def window_trim_in_wall():
    """Where the window trim goes in an end wall's frame (see walls.py): its
    X runs left from the rough opening's right edge (as seen from inside),
    Z out of the wall from the siding's face."""
    return Location(Plane((WINDOW_X + RO_W, SIDING_Y + SIDING, WINDOW_Z), x_dir=(-1, 0, 0), z_dir=(0, 1, 0)))


# The trim figures' annotations, in images/{rear,front}_window.dxf's frame
# (the window unit's lower-left corner at 0, 0, WINDOW_UNIT_INSET inside the
# rough opening's), tagged "manual:exterior_trim:rear_window"/"front_window".

def flip_arrow(cx, cy, r, a0, a1, at):
    """A curved double-headed "flip" arrow: an arc of radius r around
    (cx, cy) from angle a0 to a1 (degrees)."""
    from .notes import Leader
    pts = [(cx + r * cos(radians(a)), cy + r * sin(radians(a))) for a in
           [a0 + (a1 - a0) * k / 16 for k in range(17)]]
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    return [(Leader(tuple((x - x0, y - y0) for x, y in pts[1:])), at(x0, y0)),
            (Leader(((pts[-2][0] - x1, pts[-2][1] - y1),)), at(x1, y1))]


def circled(text, x, y, cx, cy, at):
    from .notes import Circle, Label
    return [(Label(text, 2, attach=1), at(x, y)), (Circle(1.62), at(cx, cy))]


def window_trim_manual():
    from .notes import Label, Leader

    def at(x, y):
        return Pos(x + WINDOW_UNIT_INSET, y + WINDOW_UNIT_INSET, TRIM_T)

    rear, front = "manual:exterior_trim:rear_window", "manual:exterior_trim:front_window"
    both = f"{rear} {front}"
    notes = [
        (both, Label('1/2" overhang', 1, attach=3), at(-9.4, 31.23)),
        (both, Leader(((-3.02, -4.27), (-5.02, -4.27))), at(-4.01, 35.22)),
        # rear
        (rear, Leader(((-2.75, -5), (-4.63, -5))), at(-3.76, -1.2)),
        (rear, Leader(((2.75, -5), (4.62, -5))), at(26.74, -1.2)),
        (rear, Leader(((2.5, 4.25), (5.12, 4.25))), at(26.75, 37)),
        (rear, Leader(((-1.57, -4.87), (-2.97, -4.86))), at(10, -3.75)),
        (rear, Label("30° bevel", 1, attach=1), at(6.34, 41.54)),
        (rear, Leader(((2.5, 2.25), (4.5, 2.25))), at(0.5, 38.75)),
        (rear, Leader(((-4.5, -4.2), (-6, -4.2))), at(19, 45.2)),
        (rear, Label("Measure and cut to fit", 1, attach=1), at(15.57, -7.51)),
        (rear, Leader(((2.87, -4.29), (3.87, -4.29))), at(11.13, -3.71)),
        (rear, Label("DO NOT CAULK", 1.5, attach=1), at(15.44, -9.71)),
        (rear, Label("Flip", 1, attach=1), at(-10, 43)),
        (rear, Label("Flip", 1, attach=2), at(-9.09, 16)),
        (rear, Label("Flip", 1, attach=2), at(32, 16)),
        (rear, Label('Note: nail 1½" in from each end each board', 1.5, attach=2), at(12.64, -17.03)),
        # front
        (front, Leader(((2, 4.25), (4.63, 4.25))), at(18.25, 38.75)),
        (front, Leader(((-2.75, -5), (-4.63, -5))), at(-3.75, 25)),
        (front, Leader(((2.75, -5), (4.63, -5))), at(26.75, 25)),
        (front, Leader(((-3, -4.3), (-5, -4.3))), at(4, -3.7)),
        (front, Label("Measure and\n cut to fit", 2, attach=1), at(8.72, -7.48)),
        (front, Leader(((-3, -4.3), (0, -4.3))), at(8, -3.7)),
        (front, Label("DO NOT CAULK", 2, attach=1), at(4.01, -13.96)),
        (front, Label("Door Jamb", 2, attach=1), at(25.23, -19.98)),
    ]
    for tag, args in ((rear, ("1", -10.61, -5.1, -10.01, -6.2)), (rear, ("2", 32.29, -5.2, 32.99, -6.2)),
                      (rear, ("3", 32.9, 42.35, 33.5, 41.25)), (rear, ("4", 4.76, -7.7, 5.4, -8.61)),
                      (front, ("1", 23.9, 44.1, 24.5, 43)), (front, ("2", -10.6, 21.1, -10, 20)),
                      (front, ("3", 32.3, 21, 33, 20)), (front, ("4", -3.22, -6.9, -2.62, -8))):
        notes += [(tag, n, loc) for n, loc in circled(*args, at)]
    for arc in ((-1, 42.5, 6.02, 131.6, 228.4), (39.73, 26.26, 14.73, 207.4, 261.7),
                (-16.82, 26.26, 14.73, 278.3, 332.6)):
        notes += [(rear, n, loc) for n, loc in flip_arrow(*arc, at)]
    return [(n, loc, [], tag) for tag, n, loc in notes]


# ── Corner Trim figures ─────────────────────────────────────────────────────
# images/back_corner.dxf: the rear-left corner in isometric (looking from
# the rear, left and above), each board's back laid flat beside it, and a
# section at the top of the corner. Jig tools and annotations are tagged
# "manual:exterior_trim:corners_1" / "corners_2" (the two steps).

ALIGNMENT_BLOCK = (20, "1x4")  # length; a jig tool
ALIGNMENT_BLOCK_BELOW_TOP = 18  # its top, below the top of the siding
ALIGNMENT_BLOCK_PAST = 2  # past the side wall's siding: Board #1's edge rests against it


def iso_view(direction, up=(0, 0, 1)):
    """The Location taking the house into a drawing looking from `direction`."""
    z = Vector(*direction).normalized()
    x = Vector(*up).cross(z).normalized()
    return Location(Plane((0, 0, 0), x_dir=x, z_dir=z)).inverse()


# The drawing's frame: the corner of the siding, at its bottom, is at
# (0.74, -0.47) as in back_corner.dxf.
BACK_CORNER = (0, 0)
_side, _, _end, _ = corner_frame(BACK_CORNER)
BACK_CORNER_DRAWING = (Pos(0.74, -0.47, 0) * iso_view((-1, -1, 1))
                       * Pos(-_side, -_end, -(DECK + WALL_HEIGHT - SIDING_HEIGHT)))


@component
def alignment_block():
    """Held flat against the end wall's siding, sticking out past the corner
    so Board #1's edge lines up with the end wall."""
    length, nominal = ALIGNMENT_BLOCK
    return [board(nominal, length, along="X", wide="Z")], []


def corner_manual():
    from .notes import Label, Leader

    def at(x, y):
        return BACK_CORNER_DRAWING.inverse() * Pos(x, y, 0)

    side_face, ox, end_face, oy = corner_frame(BACK_CORNER)
    block_top = DECK + WALL_HEIGHT - ALIGNMENT_BLOCK_BELOW_TOP
    block = Pos(side_face + ox * ALIGNMENT_BLOCK_PAST, end_face - thickness(ALIGNMENT_BLOCK[1]),
                block_top - width(ALIGNMENT_BLOCK[1]))
    one, two = "manual:exterior_trim:corners_1", "manual:exterior_trim:corners_2"
    notes = [
        (one, Label("Flip", 4, attach=1), at(-50, 0)),
        (one, Label("Cutout for rafter", 2.5, attach=3), at(-90.38, 85.5)),
        (one, Leader(((6.03, 15.01), (-4.3, 14.75))), at(-83.5, 69.2)),
        (one, Label("Caulk line", 2.5, attach=1), at(-67.13, 22.21)),
        (one, Leader(((6.34, -11.59), (10.34, -11.66))), at(-80.8, 32.86)),
        (one, Label("Alignment Block", 2.5, attach=1), at(37.97, 35.27)),
        (one, Leader(((14.73, -25.41), (33.23, -25.41))), at(3.77, 58.41)),
        (one, Label("Board #1", 4, attach=1), at(-72.33, -14.97)),
        (one, Leader(((9.35, -21.86), (12.26, -21.86))), at(-86.15, 4.92)),
        (one, Label("Corner Edge", 3, attach=1), at(-101.18, -24.96)),
        (one, Leader(((-17.5, -43.35), (-10.4, -43.35))), at(-92.65, 16.85)),
        (one, Leader(((9.77, -7.67),)), at(-78.06, 7.42)),
        (one, Leader(((-13.82, -5.23),)), at(-1.15, -0.13)),
        (one, Label("Double Rafter", 2.5, attach=1), at(98.75, 56)),
        (one, Leader(((-7.5, 13), (-2, 13))), at(99.43, 41.35)),
        (one, Label("Board #1", 2.5, attach=3), at(90.94, 12.88)),
        (one, Leader(((-7.26, -10.95), (-11.45, -10.95))), at(104, 22.7)),
        (one, Label("Board #2", 2.5, attach=1), at(126.43, 38.85)),
        (one, Leader(((7, 11.25), (13, 11.25))), at(111.43, 25.85)),
        (one, Label("Surface of end wall", 2.5, attach=1), at(125.77, 7.15)),
        (one, Leader(((8.5, -11.04), (17.25, -11.04))), at(109.43, 20.67)),
        (two, Label("Flip", 4, attach=1), at(-44.43, -22.13)),
        (two, Label("Caulk", 3, attach=1), at(-73.31, 39.37)),
        (two, Leader(((10, 9), (13, 9))), at(-88, 28.88)),
        (two, Label("Board #2", 4, attach=1), at(-91.59, -33.38)),
        (two, Leader(((-15.68, -25.71), (-9.48, -25.71))), at(-83.5, -10)),
        (two, Label("Corner Edge", 3, attach=3), at(-74.56, 63.7)),
        (two, Leader(((8.72, 18.56), (4.61, 18.69))), at(-77.05, 43.14)),
        (two, Leader(((5.77, -9.88),)), at(-77, 5)),
        (two, Leader(((-12.36, -10.06),)), at(0.74, -1.22)),
    ]
    out = [(n, loc, [], tag) for tag, n, loc in notes]
    for tag, arc in ((one, (-36.38, 51.96, 61.19, 238.6, 290.5)), (two, (-37.96, 24.22, 44.21, 221.2, 306.6))):
        out += [(n, loc, [], tag) for n, loc in flip_arrow(*arc, at)]
    out.append((alignment_block, block, [], one))
    return out
