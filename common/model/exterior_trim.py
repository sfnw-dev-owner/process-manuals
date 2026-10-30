"""Exterior trim: corner boards and window trim. (Fascia is with the roof.)

Per Exterior_Trim/exterior_trim.md. Frame: Z = 0 at the top of the walls.
"""

from functools import cache
from math import radians, tan

from build123d import Box, Location, Plane, Polygon, Pos, Rot, extrude

from .lumber import board, thickness, width
from .dimensions import Degrees, PLATFORM_LENGTH, PLATFORM_WIDTH, SIDING_HEIGHT
from .common import CORNER, component
from .dimensions import WINDOW_OPENING
from .platform_assembly import DECK
from .walls import SIDING, SIDING_Y, WALL_DEPTH, WALL_HEIGHT, WINDOW_X, WINDOW_Z, WRAP

# The house puts this assembly at its origin: its children are in the
# house's frame.
# The end walls' places in the house (as house.py puts them).
FRONT_WALL_IN_HOUSE = Pos(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, DECK)
REAR_WALL_IN_HOUSE = Pos(PLATFORM_WIDTH - WALL_DEPTH, WALL_DEPTH, DECK) * Rot(Z=180)

# ── corner boards ──────────────────────────────────────────────────────────
# Exterior_Trim/exterior_trim.md (Corner Trim).
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
    ]
    return [], children


# ── window trim ────────────────────────────────────────────────────────────
# Exterior_Trim/exterior_trim.md (Rear/Front Window Trim). Precut 1x4s
# around the window's rough
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
WINDOW_TOP_BEVEL = Degrees(30)
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
    return [], [(c, loc, mods, '') for c, loc, mods in window_trim_parts().values()]


def window_trim_in_wall():
    """Where the window trim goes in an end wall's frame (see walls.py): its
    X runs left from the rough opening's right edge (as seen from inside),
    Z out of the wall from the siding's face."""
    return Location(Plane((WINDOW_X + RO_W, SIDING_Y + SIDING, WINDOW_Z), x_dir=(-1, 0, 0), z_dir=(0, 1, 0)))


# ── the corner trim's jig tool ─────────────────────────────────────────────

ALIGNMENT_BLOCK = (20, "1x4")  # length; a jig tool
ALIGNMENT_BLOCK_BELOW_TOP = 18  # its top, below the top of the siding
ALIGNMENT_BLOCK_PAST = 2  # past the side wall's siding: Board #1's edge rests against it


@component
def alignment_block():
    """Held flat against the end wall's siding, sticking out past the corner
    so Board #1's edge lines up with the end wall."""
    length, nominal = ALIGNMENT_BLOCK
    return [board(nominal, length, along="X", wide="Z")], []


def alignment_block_at(corner):
    """Where the block is held at a corner (the house's frame)."""
    side_face, ox, end_face, oy = corner_frame(corner)
    block_top = DECK + WALL_HEIGHT - ALIGNMENT_BLOCK_BELOW_TOP
    return Pos(side_face + ox * ALIGNMENT_BLOCK_PAST, end_face - thickness(ALIGNMENT_BLOCK[1]),
               block_top - width(ALIGNMENT_BLOCK[1]))
