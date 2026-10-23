"""The floating floor: laminate planks over the subfloor, and the flooring
strip across the doorway.

Per floor_door/floor_install.md and images/flooring.dxf. Frame: the house's
(see house.py), with Z = 0 at the top of the subfloor (the deck): X across
the house (the door-side side wall at X = 0), Y along it (the rear wall at
Y = 0, the front wall with the doorway at the far end).
"""

import math

from .common import *
from .walls import DOOR_OPENING, DOOR_X, SIDING, WALL_DEPTH, WRAP

FLOORING = 3/8  # plank thickness (not given in the manuals)
PLANK_WIDTH = 9 + 1/2  # face width, flooring.dxf
PLANK_LENGTH = 48  # a full length, flooring.dxf
HALF_PLANK = PLANK_LENGTH / 2  # "start with 2' length" on even rows
INTERIOR_PLYWOOD = 1/2  # the wall panels the floor stops short of (flooring.dxf, door_preparation.dxf)
WALL_GAP = 1/4  # "1/4" space from walls", kept with spacer strips
INTO_DOORWAY = 3/4  # the limit line: the floor extends 3/4" past the inside of the framing
DOORWAY_STRIP = (36, 3)  # "3" strip of flooring across the doorway" (floor_install.md, door_manual.md), length and width;
# a little shy of the floor's limit line is fine (the threshold overhangs it)
DOORWAY_BLOCKS = 4

# The room inside the wall panels.
ROOM_X = (WALL_DEPTH + INTERIOR_PLYWOOD, PLATFORM_WIDTH - WALL_DEPTH - INTERIOR_PLYWOOD)
ROOM_Y = (WALL_DEPTH + INTERIOR_PLYWOOD, PLATFORM_LENGTH - WALL_DEPTH - INTERIOR_PLYWOOD)
FLOOR_X = (ROOM_X[0] + WALL_GAP, ROOM_X[1] - WALL_GAP)
FLOOR_Y = (ROOM_Y[0] + WALL_GAP, ROOM_Y[1] - WALL_GAP)
# The doorway, in the front wall: its framing starts at the inside face of the
# door-side side wall.
DOORWAY_X = (WALL_DEPTH + DOOR_X, WALL_DEPTH + DOOR_X + DOOR_OPENING)
LIMIT_Y = PLATFORM_LENGTH - WALL_DEPTH + INTO_DOORWAY  # the limit line in the doorway
SIDING_FACE_Y = PLATFORM_LENGTH + WRAP + SIDING  # the outside of the building at the doorway

ROWS = math.ceil((FLOOR_X[1] - FLOOR_X[0]) / PLANK_WIDTH)  # the last one ripped to fit


def row_x(row):
    """Where row `row` (0 = the first, against the door-side side wall) starts
    across the house, and its width (the last row is ripped)."""
    x = FLOOR_X[0] + row * PLANK_WIDTH
    return x, min(PLANK_WIDTH, FLOOR_X[1] - x)


def row_lengths(row):
    """The planks of a row from the rear wall: odd rows (counting from 1) start
    with a full length, even rows with a 2' piece; the last is cut to fit."""
    first = PLANK_LENGTH if row % 2 == 0 else HALF_PLANK
    lengths, y = [], FLOOR_Y[0]
    for length in [first] + [PLANK_LENGTH] * 3:
        lengths.append(length)
        y += length
        if y >= FLOOR_Y[1]:
            break
    return lengths


def row_planks(row):
    """[(plank component, y)] of a row. The last plank stops at the wall gap,
    or, where the row meets the doorway, at the limit line, with the corner
    beside the doorway cut out for the wall ("Note notch cut out for wall
    clearance")."""
    x, w = row_x(row)
    out, y = [], FLOOR_Y[0]
    lengths = row_lengths(row)
    for i, length in enumerate(lengths):
        if i < len(lengths) - 1:
            out.append((plank(w, length), y))
            y += length
            continue
        # The doorway's part of this row, if any, across the row (0..w).
        a, b = max(DOORWAY_X[0] + WALL_GAP, x) - x, min(DOORWAY_X[1] - WALL_GAP, x + w) - x
        if b <= 0 or a >= w:
            out.append((plank(w, FLOOR_Y[1] - y), y))
        else:
            out.append((plank(w, LIMIT_Y - y, notch=(a, b, LIMIT_Y - FLOOR_Y[1])), y))
    return out


@cache
def plank(width, length, notch=None):
    """A plank, `width` x `length`; notch = (a, b, depth): only the part a..b
    across it runs the full length, the rest is cut back by depth."""
    @component
    def flooring_plank():
        solid = Box(width, length, FLOORING, align=CORNER)
        if notch:
            a, b, depth = notch
            for x0, x1 in ((0, a), (b, width)):
                if x1 > x0:
                    solid -= Pos(x0, length - depth, 0) * Box(x1 - x0, depth, FLOORING, align=CORNER)
        return [solid], []
    return flooring_plank


def floor_rows(rows):
    """Children for the first `rows` rows of planks."""
    return [(p, Pos(row_x(r)[0], y, 0), [], '') for r in range(rows) for p, y in row_planks(r)]


@component
def flooring():
    """The whole floating floor, and the doorway strip."""
    return [], [
        *floor_rows(ROWS),
        (doorway_strip, Pos((DOORWAY_X[0] + DOORWAY_X[1] - DOORWAY_STRIP[0]) / 2,
                            SIDING_FACE_Y - DOORWAY_STRIP[1], 0), [], ''),
        *floor_manual(),
    ]


@component
def doorway_strip():
    """Flooring across the doorway, flush with the outside of the building,
    nailed down; the door frame stands on it (over the flexible flashing).
    Made of scraps interlocked together, "e.g. 4 x 9" = 36"" (a single 36"
    piece does as well)."""
    length, wide = DOORWAY_STRIP
    block = length / DOORWAY_BLOCKS
    return [Pos(i * block, 0, 0) * Box(block, wide, FLOORING, align=CORNER) for i in range(DOORWAY_BLOCKS)], []


# ── floor_door/floor_install.md figure ─────────────────────────────────────
# Tagged "manual:floor:tiles". Positions in the drawing's frame, which is the
# house's plan (X, Y) as is.

from .notes import Circle, Label, Leader  # noqa: E402


def floor_manual():
    t = "manual:floor:tiles"
    at = lambda x, y: Pos(x, y, FLOORING)
    return [
        (Label("DOORWAY", 3, attach=1), at(20, 150), [], t),
        (Circle(12.68), at(2.05, 141.87), [], t),
        (Leader(((5, 6), (16, 6))), at(11, 151), [], t),
        (Label("Note notch cut out for wall clearance.", 2.5, attach=1), at(29.14, 158.22), [], t),
        (Leader(((-10, -19), (14, -19))), at(FLOOR_X[0], 12), [], t),
        (Leader(((9.12, -11.12), (12.12, -11.12))), at(8.88, FLOOR_Y[0]), [], t),
        (Label('1/4" space from walls', 2.5, attach=1), at(22, -5), [], t),
    ]

