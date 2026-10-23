"""The inside of the walls: plywood wall panels, trim, window shelves and
liners.

Per Interior_Panels/interior_panels.md (+ images/wall_panels.dxf),
Cut_Lists/Interior_Panels_Cut_List.md (panel sizes), Interior_Trim/interior_trim.md
(+ Images/combo_trim.dxf, rear_window.dxf, front_window.dxf) and
Cut_Lists/Interior_Trim_Items.md (trim stock). The ceiling, the half-triangle
panels, their trim and the vent cap are in interior_roof.py.

Each wall's interior is built in that wall's frame (walls.py): X along the
wall, left to right as seen from inside the house; Y through it, 0 at the
framing's inside face and increasing outward (so everything here is at
negative Y); Z up from the deck. Children are tagged with the interior-trim
step that installs them (see STEPS), so the manuals' figures can show a wall
as it is at each step.

SketchUp's converted insulation and staged trim are in interior_sketchup.py.
"""

from .common import *
from .interior_sketchup import (  # noqa: F401 (the iron-cart scenes use these)
    insulation,
    interior_trim_painted,
    interior_trim_raw,
)
from .interior_notes import (
    FRONT_PANELS_VIEW, REAR_PANELS_VIEW, SIDE_PANELS_VIEW, front_panels_notes, front_trim_notes, rear_panels_notes,
    rear_trim_notes, side_panels_notes, view_at,
)
from .platform import DECK
from .walls import (
    AC_HEADER_Z, AC_OPENING, AC_SILL_Z, AC_X, DOOR_HEADER_Z, DOOR_OPENING, DOOR_X, STUD, WALL_DEPTH,
    WALL_HEIGHT, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_X, WINDOW_Z,
)

# ── panels ─────────────────────────────────────────────────────────────────

PANEL = 15/32  # interior plywood; Panel_Cutting/Panel_Saw_Operation.md:121

# Panel sizes (along the wall, up it); Cut_Lists/Interior_Panels_Cut_List.md.
PANEL_A = (92, 48)  # side walls, upper, at the rear
PANEL_B = (92, 38 + 1/4)  # side walls, lower, at the rear
PANEL_C = (44, 86 + 1/2)  # side walls, full height, at the front
PANEL_D = (88, 48)  # front wall, upper
PANEL_E = (46 + 1/4, 38 + 1/4)  # front wall, lower, beside the door
PANEL_E2 = (4, 38 + 1/4)  # front wall, the strip on the other side of the door
PANEL_G = (88, 48)  # rear wall, upper
PANEL_H = (88, 38 + 1/4)  # rear wall, lower

# The panels stand 1/2" up (on the finished floor's level; wall_panels.dxf).
# The end walls' panels stop 1/2" short of each side wall's framing, where
# the side walls' panels are; the side walls' panels start 1/2" from the end
# walls' framing, clear of the end walls' panels.
PANEL_BOTTOM = 1/2
END_GAP = 1/2
SEAM_Z = PANEL_BOTTOM + PANEL_B[1]  # the seam between the lower and upper panels
END_PANEL_TOP = SEAM_Z + PANEL_G[1]

# Side walls: A and B from the rear, their factory edges on the "magic" stud
# (walls.py SIDE_STUDS), C from there to the front.
MAGIC_STUD = 96  # from the rear end of a side wall
SIDE_INSIDE = (WALL_DEPTH, SIDE_WALL_PLATE_LENGTH - WALL_DEPTH)  # between the end walls' framing


def plywood(size):
    """An interior panel standing on the wall: `size` along the wall and up
    it, its back against the framing."""
    w, h = size
    return Pos(0, -PANEL, 0) * Box(w, PANEL, h, align=CORNER)


def routed(size, holes):
    """A panel with the openings routed out, as (x, z, width, height) in the
    panel's frame."""
    w, h = size
    face = Rectangle(w, h, align=CORNER)
    for x, z, hw, hh in holes:
        face -= Pos(x, z) * Rectangle(hw, hh, align=CORNER)
    return extrude(Plane.XZ * face, PANEL)


def _panel(size, doc):
    @component
    def panel():
        return [plywood(size)], []
    panel.__doc__ = doc
    return panel


panel_a = _panel(PANEL_A, "Side wall panel A (upper, rear).")
panel_b = _panel(PANEL_B, "Side wall panel B (lower, rear).")
panel_c = _panel(PANEL_C, "Side wall panel C (full height, front).")
panel_d = _panel(PANEL_D, "Front wall panel D (upper), before routing.")
panel_e = _panel(PANEL_E, "Front wall panel E (lower, window side of the door).")
panel_e2 = _panel(PANEL_E2, "Front wall strip E2, under D on the other side of the door.")
panel_g = _panel(PANEL_G, "Rear wall panel G (upper), before routing.")
panel_h = _panel(PANEL_H, "Rear wall panel H (lower).")

# Openings routed out of D and G, in the wall's frame.
DOORWAY = (DOOR_X, 0, DOOR_OPENING, DOOR_HEADER_Z[0])
WINDOW = (WINDOW_X, WINDOW_Z, WINDOW_WIDTH, WINDOW_HEIGHT)
AC_HOLE = (AC_X, AC_SILL_Z + STUD, AC_OPENING, AC_HEADER_Z - AC_SILL_Z - STUD)


def _in_panel(hole):
    x, z, w, h = hole
    return x - END_GAP, z - SEAM_Z, w, h


@component
def panel_d_routed():
    """D with the doorway and the window routed out."""
    return [routed(PANEL_D, [_in_panel(DOORWAY), _in_panel(WINDOW)])], []


@component
def panel_g_routed():
    """G with the window and the A/C opening routed out."""
    return [routed(PANEL_G, [_in_panel(WINDOW), _in_panel(AC_HOLE)])], []


# ── trim stock ─────────────────────────────────────────────────────────────

TRIM = "1/2x2"  # "2 inch" trim
BASEBOARD = "3/4x4"  # PVC
LINER = "1/2x3-1/8"  # window liner
SHELF = "3/4x8"
T = thickness(TRIM)
W = width(TRIM)
BASEBOARD_SPACER = 1/2  # squares of thin flooring under the baseboards
BASEBOARD_Z = PANEL_BOTTOM + BASEBOARD_SPACER
BASEBOARD_TOP = BASEBOARD_Z + width(BASEBOARD)
TOP_TRIM_Z = WALL_HEIGHT - W  # tight against the ceiling
LONG_TRIM = 96
HORIZONTAL_TRIM_Z = SEAM_Z - 1  # "1 inch less than" the seam's height

# The door's jamb, as seen from the inside; trim meets it at its center.
DOOR_JAMB = 3/4
DOOR_LEFT_JAMB = DOOR_X + DOOR_JAMB / 2  # centers
DOOR_RIGHT_JAMB = DOOR_X + DOOR_OPENING - DOOR_JAMB / 2


def piece(x0, x1, z0, z1, thick, back=PANEL):
    """A flat piece on the wall from x0 to x1 and z0 to z1, `thick` deep,
    its back `back` in front of the framing."""
    return Pos(x0, -back - thick, z0) * Box(x1 - x0, thick, z1 - z0, align=CORNER)


def trim(x0, x1, z0, z1, back=PANEL):
    """2" trim on the wall (horizontal or vertical, by its extent)."""
    return piece(x0, x1, z0, z1, T, back)


def baseboard(x0, x1):
    return piece(x0, x1, BASEBOARD_Z, BASEBOARD_TOP, thickness(BASEBOARD))


@component
def baseboard_spacer():
    """A job item: a square of thin flooring marked "O", under the baseboard
    so that the flooring can float."""
    return [Box(2, 2, BASEBOARD_SPACER, align=CORNER)], []


def spacers(x0, x1, tag):
    """Spacers under a baseboard, near each end and every 24" between."""
    n = max(2, round((x1 - x0) / 24) + 1)
    xs = [x0 + 2 + i * (x1 - x0 - 6) / (n - 1) for i in range(n)]
    return [(baseboard_spacer, Pos(x, -PANEL - 2, PANEL_BOTTOM), [], tag) for x in xs]


# ── window shelves ─────────────────────────────────────────────────────────

# A shelf (as measured off the cut shelves): a 3/4" board, a tab 1/4"
# narrower than the window sitting in the opening on the sill, and the shelf
# proper in the room with its front corners cut off at 45°. Lengths are seen
# from the room, left to right; depths from the panel's face.
SHELF_TAB_WIDTH = WINDOW_WIDTH - 1/4
REAR_SHELF = 39 + 3/4
REAR_SHELF_LEFT = 7 + 3/4  # past the tab's left side (8-1/4" past its right)
REAR_SHELF_TAB = 3 + 1/8  # into the opening
REAR_SHELF_DEPTH = 6 + 1/4  # into the room (TODO.md: re-measure)
REAR_SHELF_CHAMFERS = (2, 2)
FRONT_SHELF = 39 + 1/4  # the tab flush with its window end
FRONT_SHELF_TAB = 3 + 1/4
FRONT_SHELF_DEPTH = 5 + 7/8
FRONT_SHELF_CHAMFERS = (3 + 7/8, 0)  # the window end only
FRONT_SHELF_OVERHANG = 1/2  # past its support block, at the side wall end
SHELF_Z = WINDOW_Z  # on the sill
BLOCK_Z = SHELF_Z - width("2x4")  # the 2x4 support block under it, on edge


def shelf_shape(x0, length, tab_x, tab, depth, chamfers):
    """The shelf's outline seen from above: x along the wall, y into the room
    from the framing's inside face."""
    (c0, c1), room, x1 = chamfers, -(PANEL + depth), x0 + length
    tab_x1 = tab_x + SHELF_TAB_WIDTH
    end1 = [(x1, room + c1), (x1 - c1, room)] if c1 else [(x1, room)]
    end0 = [(x0 + c0, room), (x0, room + c0)] if c0 else [(x0, room)]
    pts = [(tab_x, tab - PANEL), (tab_x1, tab - PANEL), (tab_x1, -PANEL),
           (x1, -PANEL), *end1, *end0, (x0, -PANEL), (tab_x, -PANEL)]
    pts = [p for i, p in enumerate(pts) if p != pts[i - 1]]  # a tab flush with an end
    return Polygon(*pts, align=None)


def shelf_solid(*shape):
    return Pos(0, 0, SHELF_Z) * extrude(shelf_shape(*shape), thickness(SHELF), dir=(0, 0, 1))


REAR_TAB_X = WINDOW_X + (WINDOW_WIDTH - SHELF_TAB_WIDTH) / 2  # centered in the opening
REAR_SHELF_X = REAR_TAB_X - REAR_SHELF_LEFT


@component
def rear_shelf():
    """The rear window's shelf (Interior_Trim_Items.md "Rear Shelf")."""
    return [shelf_solid(REAR_SHELF_X, REAR_SHELF, REAR_TAB_X, REAR_SHELF_TAB, REAR_SHELF_DEPTH, REAR_SHELF_CHAMFERS)], []


def support_block(x0, length):
    """2x4 under a shelf, on edge, its wide face against the wall."""
    return Pos(x0, -PANEL - thickness("2x4"), BLOCK_Z) * TwoByFour(length, along="X", wide="Z")


def window_liners():
    """Liners (1/2 x 3-1/8) around a window opening, their room-side edges
    flush with the wall panel: the sides tight on the shelf, the top between
    them."""
    t, w = thickness(LINER), width(LINER)
    bottom, top = SHELF_Z + thickness(SHELF), WINDOW_Z + WINDOW_HEIGHT
    x0, x1 = WINDOW_X, WINDOW_X + WINDOW_WIDTH
    solids = [
        Pos(x0, -PANEL, bottom) * Box(t, w, top - bottom, align=CORNER),
        Pos(x1 - t, -PANEL, bottom) * Box(t, w, top - bottom, align=CORNER),
        Pos(x0 + t, -PANEL, top - t) * Box(x1 - x0 - 2 * t, w, t, align=CORNER),
    ]
    return solids


LINER_INSIDE = (WINDOW_X + thickness(LINER), WINDOW_X + WINDOW_WIDTH - thickness(LINER))
LINER_TOP = WINDOW_Z + WINDOW_HEIGHT - thickness(LINER)
SHELF_TOP = SHELF_Z + thickness(SHELF)


def _solids(*solids):
    @component
    def part():
        return list(solids), []
    return part


# ── the side walls ─────────────────────────────────────────────────────────

# Install steps (Interior_Panels/interior_panels.md, Interior_Trim/interior_trim.md),
# as the children's tags, in order.
STEPS = [
    "panels", "baseboards", "rear_shelf", "rear_window_trim", "top_trim", "vertical_trim",
    "horizontal_trim", "front_baseboard", "front_shelf", "front_window_trim", "front_trim_a",
    "front_trim_b", "final_trim",
]


def side_wall_interior(rear_at_left):
    """A side wall's panels and trim. rear_at_left: the door-side wall (its
    frame starts at the rear); the other side wall starts at the front."""
    lo, hi = SIDE_INSIDE[0] + PANEL, SIDE_INSIDE[1] - PANEL  # the end walls' panel faces
    along = (lambda d: lo + d) if rear_at_left else (lambda d: hi - d)  # d from the rear panel face
    assert abs(WALL_DEPTH + END_GAP + PANEL_A[0] - MAGIC_STUD) < 1e-9  # A and B's factory edges on the stud

    def span(d0, d1):  # an extent given from the rear, in this wall's X
        a, b = sorted((along(d0), along(d1)))
        return a, b

    ab0, ab1 = span(-PANEL + END_GAP, -PANEL + END_GAP + PANEL_A[0])
    c0, c1 = span(-PANEL + END_GAP + PANEL_A[0], -PANEL + END_GAP + PANEL_A[0] + PANEL_C[0])
    rear_corner = span(0, W)
    seam_x = along(-PANEL + END_GAP + PANEL_A[0])
    front_corner = span(hi - lo - W, hi - lo)
    rear_top = span(0, LONG_TRIM)
    front_top = span(LONG_TRIM, hi - lo)

    children = [
        (panel_b, Pos(ab0, 0, PANEL_BOTTOM), [], 'panels'),
        (panel_a, Pos(ab0, 0, SEAM_Z), [], 'panels'),
        (panel_c, Pos(c0, 0, PANEL_BOTTOM), [], 'panels'),
        (_solids(baseboard(lo, hi)), Location(), [], 'baseboards'),
        *spacers(lo, hi, 'baseboards'),
        (_solids(trim(*rear_top, TOP_TRIM_Z, WALL_HEIGHT), trim(*front_top, TOP_TRIM_Z, WALL_HEIGHT)),
         Location(), [], 'top_trim'),
        (_solids(trim(*rear_corner, BASEBOARD_TOP, TOP_TRIM_Z),
                 trim(seam_x - W / 2, seam_x + W / 2, BASEBOARD_TOP, TOP_TRIM_Z)), Location(), [], 'vertical_trim'),
    ]
    # Horizontal trim over the A/B seam: the rear part (from the rear corner
    # to the seam trim) early, the front part (to the front corner) last.
    rear_part = sorted((rear_corner[1] if rear_at_left else rear_corner[0],
                        seam_x - W / 2 if rear_at_left else seam_x + W / 2))
    front_part = sorted((seam_x + W / 2 if rear_at_left else seam_x - W / 2,
                         front_corner[0] if rear_at_left else front_corner[1]))
    children += [
        (_solids(trim(*rear_part, HORIZONTAL_TRIM_Z, HORIZONTAL_TRIM_Z + W)), Location(), [], 'horizontal_trim'),
        (_solids(trim(*front_part, HORIZONTAL_TRIM_Z, HORIZONTAL_TRIM_Z + W)), Location(), [], 'final_trim'),
        # The front corner: behind the door (front trim part I) on the door
        # side; next to the front shelf (part II) on the other.
        (_solids(trim(*front_corner, BASEBOARD_TOP, TOP_TRIM_Z)), Location(), [],
         'front_trim_a' if rear_at_left else 'front_trim_b'),
    ]
    return [], children


@component
def side_wall_interior_door_side():
    """The side wall on the door's side (its frame starts at the rear)."""
    solids, children = side_wall_interior(True)
    return solids, children + side_panels_notes(view_at(SIDE_PANELS_VIEW), (PANEL_A, PANEL_B, PANEL_C))


@component
def side_wall_interior_far_side():
    """The other side wall, "left side wall (facing rear)" in the trim
    manual (its frame starts at the front)."""
    return side_wall_interior(False)


# ── the end walls ──────────────────────────────────────────────────────────

END_INSIDE = (PANEL, END_WALL_PLATE_LENGTH - PANEL)  # between the side walls' panels
CORNER_TRIM = (END_INSIDE[0] + T, END_INSIDE[1] - T)  # between the side walls' corner trim


def end_top_trim():
    return trim(*CORNER_TRIM, TOP_TRIM_Z, WALL_HEIGHT)


@component
def rear_wall_interior():
    lo, hi = END_INSIDE
    (l0, l1), top = LINER_INSIDE, LINER_TOP
    children = [
        (panel_h, Pos(END_GAP, 0, PANEL_BOTTOM), [], 'panels'),
        (panel_g_routed, Pos(END_GAP, 0, SEAM_Z), [], 'panels'),
        (_solids(baseboard(lo + thickness(BASEBOARD), hi - thickness(BASEBOARD))), Location(), [], 'baseboards'),
        *spacers(lo + thickness(BASEBOARD), hi - thickness(BASEBOARD), 'baseboards'),
        # The shelf, with its support block 1/2" in from each end.
        (rear_shelf, Location(), [], 'rear_shelf'),
        (_solids(support_block(REAR_SHELF_X + 1/2, REAR_SHELF - 1)), Location(), [], 'rear_shelf'),
        # Liners, then 2" trim beside the window flush with them, and over it
        # 1/2" past the side trim each way.
        (_solids(*window_liners()), Location(), [], 'rear_window_liner'),
        (_solids(trim(l0 - W, l0, SHELF_TOP, top), trim(l1, l1 + W, SHELF_TOP, top),
                 trim(l0 - W - 1/2, l1 + W + 1/2, top, top + W)), Location(), [], 'rear_window_trim'),
        (_solids(end_top_trim()), Location(), [], 'top_trim'),
        (_solids(trim(CORNER_TRIM[0], CORNER_TRIM[0] + W, BASEBOARD_TOP, TOP_TRIM_Z),
                 trim(CORNER_TRIM[1] - W, CORNER_TRIM[1], BASEBOARD_TOP, TOP_TRIM_Z)), Location(), [], 'vertical_trim'),
        (_solids(trim(CORNER_TRIM[0] + W, CORNER_TRIM[1] - W, HORIZONTAL_TRIM_Z, HORIZONTAL_TRIM_Z + W)),
         Location(), [], 'horizontal_trim'),
        *rear_panels_notes(view_at(REAR_PANELS_VIEW), (PANEL_G, PANEL_H)),
        *rear_trim_notes(),
    ]
    return [], children


# Front wall: the wide board beside the door (ripped from the 1/2 x 9-1/2)
# runs from the door jamb's center to the window liner, notched around the
# shelf; the narrow rest of it goes behind the door, from the jamb's center
# to the corner trim.
FRONT_SHELF_X = CORNER_TRIM[1] - W - FRONT_SHELF  # its other end against the corner trim
FRONT_BLOCK = FRONT_SHELF - FRONT_SHELF_OVERHANG  # flush with the shelf's door-side end
WIDE_BOARD = (DOOR_RIGHT_JAMB, LINER_INSIDE[0])
NARROW_BOARD = (CORNER_TRIM[0], DOOR_LEFT_JAMB)


@component
def front_shelf():
    """The front window's shelf (Interior_Trim_Items.md "Front Shelf")."""
    return [shelf_solid(FRONT_SHELF_X, FRONT_SHELF, FRONT_SHELF_X, FRONT_SHELF_TAB, FRONT_SHELF_DEPTH,
                        FRONT_SHELF_CHAMFERS)], []


@component
def front_wide_board():
    board = piece(*WIDE_BOARD, BASEBOARD_TOP, TOP_TRIM_Z, T)
    notch = (Pos(WINDOW_X, -PANEL - FRONT_SHELF_DEPTH, BLOCK_Z)
             * Box(WINDOW_WIDTH, FRONT_SHELF_DEPTH + PANEL, SHELF_TOP - BLOCK_Z, align=CORNER))
    return [board - notch], []


@component
def front_wall_interior():
    lo, hi = END_INSIDE
    l1, top = LINER_INSIDE[1], LINER_TOP
    bb = thickness(BASEBOARD)
    door_top = DOOR_HEADER_Z[0]
    children = [
        (panel_e, Pos(END_INSIDE[1] - END_GAP + PANEL - PANEL_E[0], 0, PANEL_BOTTOM), [], 'panels'),
        # E2, a 4" strip, trimmed to fit between the side wall's panel and the doorway.
        (_solids(piece(lo, DOOR_X, PANEL_BOTTOM, SEAM_Z, PANEL, 0)), Location(), [], 'panel_e2'),
        (panel_d_routed, Pos(END_GAP, 0, SEAM_Z), [], 'panel_d'),
        # Baseboard from the door jamb to the far side wall, before the shelf.
        (_solids(baseboard(DOOR_RIGHT_JAMB, hi - bb)), Location(), [], 'front_baseboard'),
        *spacers(DOOR_RIGHT_JAMB, hi - bb, 'front_baseboard'),
        (front_shelf, Location(), [], 'front_shelf'),
        (_solids(support_block(FRONT_SHELF_X, FRONT_BLOCK)), Location(), [], 'front_shelf'),
        (_solids(*window_liners()), Location(), [], 'front_window_liner'),
        # Part I: the top trim, the baseboard behind the door, the wide board,
        # the narrow board behind the door (and the side wall's corner trim).
        (_solids(end_top_trim(), baseboard(lo + bb, DOOR_LEFT_JAMB)), Location(), [], 'front_trim_a'),
        *spacers(lo + bb, DOOR_LEFT_JAMB, 'front_trim_a'),
        (front_wide_board, Location(), [], 'front_trim_a'),
        (_solids(piece(*NARROW_BOARD, BASEBOARD_TOP, TOP_TRIM_Z, T)), Location(), [], 'front_trim_a'),
        # Part II: over the door, halfway over the door's frame; around the
        # window, flush with the liners, the top 1/2" past the side; the
        # corner by the window.
        (_solids(trim(CORNER_TRIM[0], WIDE_BOARD[0], door_top - DOOR_JAMB / 2, door_top - DOOR_JAMB / 2 + W),
                 trim(l1, l1 + W, SHELF_TOP, top), trim(WIDE_BOARD[1], l1 + W + 1/2, top, top + W),
                 trim(CORNER_TRIM[1] - W, CORNER_TRIM[1], BASEBOARD_TOP, TOP_TRIM_Z)), Location(), [], 'front_trim_b'),
        # Final: under the shelf at the seam's height, and behind the door.
        (_solids(trim(WIDE_BOARD[1], CORNER_TRIM[1] - W, HORIZONTAL_TRIM_Z, HORIZONTAL_TRIM_Z + W),
                 trim(*NARROW_BOARD, HORIZONTAL_TRIM_Z, HORIZONTAL_TRIM_Z + W, back=PANEL + T)),
         Location(), [], 'final_trim'),
        *front_panels_notes(view_at(FRONT_PANELS_VIEW), (PANEL_D, PANEL_E)),
        *front_trim_notes(),
    ]
    return [], children


# ── assembly ───────────────────────────────────────────────────────────────

# Where each wall's interior goes in the house: the walls' placements (house.py).
DOOR_SIDE_WALL_AT = Pos(WALL_DEPTH, 0, DECK) * Rot(Z=90)
FAR_SIDE_WALL_AT = Pos(PLATFORM_WIDTH - WALL_DEPTH, PLATFORM_LENGTH, DECK) * Rot(Z=-90)
FRONT_WALL_AT = Pos(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, DECK)
REAR_WALL_AT = Pos(PLATFORM_WIDTH - WALL_DEPTH, WALL_DEPTH, DECK) * Rot(Z=180)


@component
def interior():
    """All the walls' interior, in the house's frame."""
    return [], [
        (side_wall_interior_door_side, DOOR_SIDE_WALL_AT, [], ''),
        (side_wall_interior_far_side, FAR_SIDE_WALL_AT, [], ''),
        (front_wall_interior, FRONT_WALL_AT, [], ''),
        (rear_wall_interior, REAR_WALL_AT, [], ''),
    ]


@component
def interior_panel_raw():
    """The interior, where house.py places SketchUp's interior panels (at
    (3 1/2, 3 3/8, 3/4) above the deck's corner)."""
    return [], [(interior, Pos(-(3 + 1/2), -(3 + 3/8), -(DECK + 3/4)), [], '')]
