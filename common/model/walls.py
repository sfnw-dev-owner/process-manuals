"""The four walls: 2x4 framing, house wrap and T1-11 siding.

Per Side_Walls/sidewall_1.md, Front_Wall/front_wall_ada.md, Rear_Wall/rear_wall.md
and the framing drawings in their images/*.dxf (drawn from the other face, so
mirrored left-to-right relative to the walls here).

Every wall is built in its own frame: X along the wall, left to right as seen
from inside the house; Y through it (0 at the inside face of the framing,
increasing outward); Z up from the bottom of the bottom plate. The house places
each wall on the deck.
"""

from .common import *

STUD = thickness("2x4")  # 1 1/2
WALL_DEPTH = width("2x4")  # 3 1/2
WALL_HEIGHT = STUD + STUD_LENGTH + STUD  # bottom plate, stud, top plate
WRAP = 1/16  # house wrap over the framing
SIDING = 5/16  # T1-11, as modeled in SketchUp
SIDING_Y = WALL_DEPTH + WRAP  # inside face of the siding
SIDING_BOTTOM = WALL_HEIGHT - SIDING_HEIGHT  # flush with the top, hanging below the framing


def panel(width, height, thick, holes=()):
    """A flat panel in the XZ plane, thickness along +Y, minimum corner at the
    origin, with rectangular holes given as (x, z, width, height)."""
    face = Rectangle(width, height, align=CORNER)
    for x, z, w, h in holes:
        face -= Pos(x, z) * Rectangle(w, h, align=CORNER)
    return extrude(Plane.XZ * face, -thick)


# ── side walls ─────────────────────────────────────────────────────────────

# Studs along the wall: an upright stud and a flat stud at each end (for the
# end walls to nail to), and studs centered every 24" in between.
SIDE_FLAT_STUD = width("2x4")  # a flat stud's width along the wall
SIDE_STUDS = [
    0, SIDE_WALL_PLATE_LENGTH - STUD,
    *[c - STUD / 2 for c in spaced(STUD_SPACING, STUD_SPACING, 5)],
]


@component
def side_wall():
    """A side wall: 144" long, framing only on the inside, three siding panels."""
    solids = []
    children = [
        (side_wall_framing, Location(), [], 'Wall Framing'),
        (side_wall_skin, Location(), [], ''),
        *side_wall_manual(),
    ]
    return solids, children


def side_wall_steps():
    """Side wall framing by Side_Walls/sidewall_1.md step: {step: members}."""
    return {
        1: [  # plates, the end studs, and a flat stud inside each (against the inside face)
            (side_wall_plate, Location(), [], ''),
            (side_wall_plate, Pos(0, 0, WALL_HEIGHT - STUD), [], ''),
            *[(stud, Pos(x, 0, STUD), [], '') for x in SIDE_STUDS[:2]],
            (flat_stud, Pos(STUD, 0, STUD), [], ''),
            (flat_stud, Pos(SIDE_WALL_PLATE_LENGTH - STUD - SIDE_FLAT_STUD, 0, STUD), [], ''),
        ],
        3: [(stud, Pos(x, 0, STUD), [], '') for x in SIDE_STUDS[2:]],  # inner studs
    }


@component
def side_wall_framing():
    """Side_Walls/images/side_wall.dxf: plates, studs, and flat end studs."""
    return [], [m for members in side_wall_steps().values() for m in members]


@component
def side_wall_skin():
    """House wrap and three 4x8 T1-11 panels."""
    solids = [
        # down to the bottom of the siding, so it's wrapped where it overhangs the platform
        Pos(0, WALL_DEPTH, SIDING_BOTTOM) * panel(SIDE_WALL_PLATE_LENGTH, SIDING_HEIGHT, WRAP),
    ]
    children = [
        (siding_panel_plain, Pos(x, SIDING_Y, SIDING_BOTTOM), [], '')
        for x in spaced(0, SIDING_PANEL_WIDTH, 3)
    ]
    return solids, children


@component
def side_wall_plate():
    solids = [TwoByFour(SIDE_WALL_PLATE_LENGTH, along="X", wide="Y")]
    return solids, []


@component
def stud():
    solids = [TwoByFour(STUD_LENGTH, along="Z", wide="Y")]
    return solids, []


@component
def flat_stud():
    """A stud turned flat, its wide face against the siding's plane."""
    solids = [TwoByFour(STUD_LENGTH, along="Z", wide="X")]
    return solids, []


@component
def siding_panel_plain():
    solids = [panel(SIDING_PANEL_WIDTH, SIDING_HEIGHT, SIDING)]
    return solids, []


# ── end walls (front and rear) ─────────────────────────────────────────────

# The end walls fit between the side walls; their siding runs the full width
# of the house, covering the side walls' ends.
END_SIDING_X = -WALL_DEPTH  # siding starts at the outside of the side wall framing
END_SIDING_WIDTH = 2 * SIDING_PANEL_WIDTH

# Window (both end walls): Front_Wall/images/front_wall_ada.dxf, Rear_Wall/images/rear_wall.dxf.
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_OPENING
WINDOW_X = 46 + 3/4  # rough opening, from the start of the wall
SILL_Z = 43 + 1/2  # bottom of the flat 2x4 sill
WINDOW_Z = SILL_Z + STUD  # rough opening bottom
HEADER_Z = WINDOW_Z + WINDOW_HEIGHT  # three flat 2x4s above the window, up to the top plate

# Front door (front wall): front_wall_ada.dxf.
DOOR_X = 4 + 1/4  # rough opening, from the start of the wall
DOOR_HEADER_Z = [81 + 3/4, 84]  # two flat 2x4 headers; the lower one tops the opening
DOOR_HEADER_SPACER = 3/4  # plywood between the headers (front_wall_ada.dxf step 4)
# Spacer blocks between the end stud and the door's king stud, leaving 8"
# clear above the bottom plate and below the top plate (front_wall_ada.md
# step 5; positions from front_wall_ada.dxf layer step_05).
DOOR_SPACER_BLOCK = (1 + 1/4, 10)  # width along the wall, length
DOOR_SPACER_BLOCK_Z = [9 + 1/2, 29 + 1/2, 49 + 1/2, 67 + 1/2]

# A/C opening (rear wall): rear_wall.dxf, Rear_Wall/rear_wall.md:77-81.
AC_X = 23 + 1/4
AC_SILL_Z = 68 + 3/4  # the lower 20 1/2" block
AC_HEADER_Z = WALL_HEIGHT - 2 * STUD  # the upper block, under the top plate
AC_SIDE_BLOCK = 13 + 3/4  # vertical block beside the opening, between the two
# 6 1/2" blocks under the A/C sill: one against the left stud, two side by
# side against the right studs (rear_wall.md step 4b; rear_wall.dxf layer step_04b).
AC_UNDER_BLOCK = 6 + 1/2


def window_framing():
    """Sill, triple header, and the king stud right of the window. (The stud
    on its left is the last of the three beside the door or A/C opening.)"""
    return [
        (block(WINDOW_WIDTH), Pos(WINDOW_X, 0, SILL_Z), [], ''),
        *[(block(WINDOW_WIDTH), Pos(WINDOW_X, 0, z), [], '')
          for z in spaced(HEADER_Z, STUD, 3)],  # 3 stacked
        (stud, Pos(WINDOW_X + WINDOW_WIDTH, 0, STUD), [], ''),
    ]


def window_unit_at():
    """The window unit sits on the sill, through the whole wall. (Its own
    frame starts 1/40" short of its edge.)"""
    return (window_unit, Pos(WINDOW_X - 1/40, SIDING_Y + SIDING, WINDOW_Z) * Rot(Z=180), ['mirror'], '')


@component
def front_wall():
    """The front wall: an ADA door on the left and a window on the right."""
    solids = []
    children = [
        (front_wall_framing, Location(), [], 'Wall Framing'),
        (front_wall_skin, Location(), [], ''),
        *window_flashing(),
        window_unit_at(),
        *front_wall_manual(),
    ]
    return solids, children


def front_wall_steps():
    """Front wall framing by Front_Wall/front_wall_ada.md step, as built in the
    jig (bottom plate whole): {step: members}. Three studs stand side by side
    between the door and the window: the window's king stud (step 2), the
    next one (step 3), and the door's (step 4)."""
    door_right = DOOR_X + DOOR_OPENING
    return {
        1: [  # perimeter
            (end_wall_plate, Location(), [], ''),
            (end_wall_plate, Pos(0, 0, WALL_HEIGHT - STUD), [], ''),
            (stud, Pos(0, 0, STUD), [], ''),
            (stud, Pos(END_WALL_PLATE_LENGTH - STUD, 0, STUD), [], ''),
        ],
        2: [*window_framing(), (stud, Pos(WINDOW_X - STUD, 0, STUD), [], '')],  # window
        3: [(stud, Pos(door_right + STUD, 0, STUD), [], '')],  # the next stud
        4: [  # door: studs either side, two headers with plywood between
            (stud, Pos(DOOR_X - STUD, 0, STUD), [], ''),
            (stud, Pos(door_right, 0, STUD), [], ''),
            *[(block(DOOR_OPENING), Pos(DOOR_X, 0, z), [], '') for z in DOOR_HEADER_Z],
            (door_header_spacer, Pos(DOOR_X, 0, DOOR_HEADER_Z[0] + STUD), [], ''),
        ],
        5: [(door_spacer_block, Pos(STUD, 0, z), [], '') for z in DOOR_SPACER_BLOCK_Z],
    }


@component
def front_wall_framing_in_jig():
    """The front wall's framing as built: bottom plate whole."""
    return [], [m for members in front_wall_steps().values() for m in members]


@component
def front_wall_framing():
    """The front wall's framing in the house: after tilt-up the bottom plate
    is cut out across the doorway (post-tilt-up/frame-completion.md:39)."""
    members = [m for members in front_wall_steps().values() for m in members]
    members = [m for m in members if m[0] is not end_wall_plate or m[1] != Location()]
    members += [
        (block(DOOR_X), Location(), [], ''),
        (block(END_WALL_PLATE_LENGTH - DOOR_X - DOOR_OPENING), Pos(DOOR_X + DOOR_OPENING, 0, 0), [], ''),
    ]
    return [], members


@component
def rear_wall():
    """The rear wall: an A/C opening on the left and a window on the right."""
    solids = []
    children = [
        (rear_wall_framing, Location(), [], 'Wall Framing'),
        (rear_wall_skin, Location(), [], ''),
        *window_flashing(),
        window_unit_at(),
        *rear_wall_manual(),
    ]
    return solids, children


def rear_wall_steps():
    """Rear wall framing by Rear_Wall/rear_wall.md step: {step: members}.
    Two studs stand side by side between the A/C opening and the window: the
    window's king stud (step 2) and the next one (step 3)."""
    return {
        "1": [  # perimeter
            (end_wall_plate, Location(), [], ''),
            (end_wall_plate, Pos(0, 0, WALL_HEIGHT - STUD), [], ''),
            (stud, Pos(0, 0, STUD), [], ''),
            (stud, Pos(END_WALL_PLATE_LENGTH - STUD, 0, STUD), [], ''),
        ],
        "2": [*window_framing(), (stud, Pos(WINDOW_X - STUD, 0, STUD), [], '')],  # window
        "3": [(stud, Pos(AC_X + AC_OPENING, 0, STUD), [], '')],  # the next stud
        "4": [  # A/C opening: the stud on its left, blocks above and below, a block on the right
            (stud, Pos(AC_X - STUD, 0, STUD), [], ''),
            (block(AC_OPENING), Pos(AC_X, 0, AC_HEADER_Z), [], ''),
            (ac_side_block, Pos(AC_X + AC_OPENING - STUD, 0, AC_SILL_Z + STUD), [], ''),
            (block(AC_OPENING), Pos(AC_X, 0, AC_SILL_Z), [], ''),
        ],
        "4b": [(ac_under_block, Pos(x, 0, AC_SILL_Z - AC_UNDER_BLOCK), [], '')
               for x in (AC_X, AC_X + AC_OPENING - 2 * STUD, AC_X + AC_OPENING - STUD)],
    }


@component
def rear_wall_framing():
    """Rear_Wall/images/rear_wall.dxf."""
    return [], [m for members in rear_wall_steps().values() for m in members]


@component
def front_wall_skin():
    """House wrap and two T1-11 panels: the door's on the left, the window's on the right."""
    door = (DOOR_X - END_SIDING_X, -SIDING_BOTTOM, DOOR_OPENING, DOOR_HEADER_Z[0])
    window = (WINDOW_X - END_SIDING_X, WINDOW_Z - SIDING_BOTTOM, WINDOW_WIDTH, WINDOW_HEIGHT)
    solids = [
        Pos(END_SIDING_X, WALL_DEPTH, SIDING_BOTTOM)
        * panel(END_SIDING_WIDTH, SIDING_HEIGHT, WRAP, holes=[door, window]),
    ]
    children = [
        (siding_panel_door, Pos(END_SIDING_X, SIDING_Y, SIDING_BOTTOM), [], ''),
        (siding_panel_window, Pos(END_SIDING_X + SIDING_PANEL_WIDTH, SIDING_Y, SIDING_BOTTOM), [], ''),
    ]
    return solids, children


@component
def rear_wall_skin():
    """House wrap and two T1-11 panels: plain on the left, the window's on the right."""
    window = (WINDOW_X - END_SIDING_X, WINDOW_Z - SIDING_BOTTOM, WINDOW_WIDTH, WINDOW_HEIGHT)
    solids = [
        Pos(END_SIDING_X, WALL_DEPTH, SIDING_BOTTOM)
        * panel(END_SIDING_WIDTH, SIDING_HEIGHT, WRAP, holes=[window]),
    ]
    children = [
        (siding_panel_plain, Pos(END_SIDING_X, SIDING_Y, SIDING_BOTTOM), [], ''),
        (siding_panel_window, Pos(END_SIDING_X + SIDING_PANEL_WIDTH, SIDING_Y, SIDING_BOTTOM), [], ''),
    ]
    return solids, children


@component
def siding_panel_door():
    """The left front panel, with the doorway cut out of it."""
    hole = (DOOR_X - END_SIDING_X, -SIDING_BOTTOM, DOOR_OPENING, DOOR_HEADER_Z[0])
    solids = [panel(SIDING_PANEL_WIDTH, SIDING_HEIGHT, SIDING, holes=[hole])]
    return solids, []


@component
def siding_panel_window():
    """The right end-wall panel, with the window cut out of it."""
    hole = (WINDOW_X - END_SIDING_X - SIDING_PANEL_WIDTH, WINDOW_Z - SIDING_BOTTOM,
            WINDOW_WIDTH, WINDOW_HEIGHT)
    solids = [panel(SIDING_PANEL_WIDTH, SIDING_HEIGHT, SIDING, holes=[hole])]
    return solids, []


@component
def end_wall_plate():
    solids = [TwoByFour(END_WALL_PLATE_LENGTH, along="X", wide="Y")]
    return solids, []


@component
def door_header_spacer():
    solids = [Sheet(DOOR_HEADER_SPACER, DOOR_OPENING, WALL_DEPTH, facing="Z")]
    return solids, []


@component
def door_spacer_block():
    w, length = DOOR_SPACER_BLOCK
    solids = [Box(w, WALL_DEPTH, length, align=CORNER)]
    return solids, []


@component
def ac_under_block():
    solids = [TwoByFour(AC_UNDER_BLOCK, along="Z", wide="Y")]
    return solids, []


@component
def ac_side_block():
    solids = [TwoByFour(AC_SIDE_BLOCK, along="Z", wide="Y")]
    return solids, []


def block(length):
    """A flat 2x4 of the given length along the wall (plates, sills, headers)."""
    return _blocks(length)


@cache
def _blocks(length):
    @component
    def flat_2x4():
        solids = [TwoByFour(length, along="X", wide="Y")]
        return solids, []
    flat_2x4.__name__ = f"flat_2x4_{length:g}"
    return flat_2x4


# ── window unit (as modeled in SketchUp) ───────────────────────────────────

# The window unit: a double-hung window, 24 x 36 (the rough opening) and
# 3 7/8" deep, its outside face at Y = 0 (window_unit_at turns it into the
# wall). SketchUp's "Window#1" transcribed to a frame (jambs, head, sill),
# the upper sash outside and the lower sash inside, each with its pane.
UNIT_W, UNIT_H, UNIT_D = 24, 36, 3 + 7/8
UNIT_X0 = 0.025  # the frame starts 1/40" in from the unit's edge (as SketchUp's did)
UNIT_JAMB, UNIT_HEAD, UNIT_SILL = 1.2, 1 + 1/2, 2 + 1/16
SASH_STILE, SASH_RAIL, SASH_MEET, SASH_T = 1 + 1/2, 1 + 1/2, 1, 1 + 1/4  # stiles, top/bottom rail, meeting rail, thickness
PANE = 1/8


def _sash(x0, x1, z0, z1, y, bottom_rail, top_rail):
    """A sash between x0..x1 and z0..z1, its outside at y: stiles, the two
    rails, and its pane in the middle of its thickness."""
    stiles = [Pos(x0, y, z0) * Box(SASH_STILE, SASH_T, z1 - z0, align=CORNER),
              Pos(x1 - SASH_STILE, y, z0) * Box(SASH_STILE, SASH_T, z1 - z0, align=CORNER)]
    rails = [Pos(x0, y, z0) * Box(x1 - x0, SASH_T, bottom_rail, align=CORNER),
             Pos(x0, y, z1 - top_rail) * Box(x1 - x0, SASH_T, top_rail, align=CORNER)]
    pane = Pos(x0 + SASH_STILE, y + (SASH_T - PANE) / 2, z0 + bottom_rail) * Box(
        x1 - x0 - 2 * SASH_STILE, PANE, z1 - z0 - bottom_rail - top_rail, align=CORNER)
    return stiles + rails + [pane]


def lower_pane():
    """(x, z, width, height) of the lower sash's pane in the unit's frame."""
    x0, z0 = UNIT_X0 + UNIT_JAMB + SASH_STILE, UNIT_SILL + SASH_RAIL
    meet = (UNIT_SILL + UNIT_H - UNIT_HEAD) / 2
    return x0, z0, UNIT_W - 2 * (UNIT_JAMB + SASH_STILE), meet + SASH_MEET / 2 - SASH_MEET - z0


@component
def window_unit():
    """SketchUp: 'Window#1', as a double-hung window (see above)."""
    x0, x1 = UNIT_X0, UNIT_X0 + UNIT_W
    frame = [
        Pos(x0, 0, 0) * Box(UNIT_JAMB, UNIT_D, UNIT_H, align=CORNER),
        Pos(x1 - UNIT_JAMB, 0, 0) * Box(UNIT_JAMB, UNIT_D, UNIT_H, align=CORNER),
        Pos(x0, 0, 0) * Box(UNIT_W, UNIT_D, UNIT_SILL, align=CORNER),
        Pos(x0, 0, UNIT_H - UNIT_HEAD) * Box(UNIT_W, UNIT_D, UNIT_HEAD, align=CORNER),
    ]
    ox0, ox1 = x0 + UNIT_JAMB, x1 - UNIT_JAMB  # the opening
    oz0, oz1 = UNIT_SILL, UNIT_H - UNIT_HEAD
    meet = (oz0 + oz1) / 2  # where the meeting rails overlap
    upper = _sash(ox0, ox1, meet - SASH_MEET / 2, oz1, (UNIT_D / 2 - SASH_T) / 2, SASH_MEET, SASH_RAIL)
    lower = _sash(ox0, ox1, oz0, meet + SASH_MEET / 2, UNIT_D / 2 + (UNIT_D / 2 - SASH_T) / 2, SASH_RAIL, SASH_MEET)
    return frame + upper + lower, []


# ── Side_Walls/sidewall_1.md and sidewall_3.md figures ─────────────────────
# Jig tools and annotations, tagged "manual:side_wall:<step>" with the step
# layers of Side_Walls/images/side_wall.dxf: 1-5 are shared, 6a/7a are wall
# #1's panel order and 6b/7b wall #3's.

from .notes import Circle, Icon, Label, Leader, crossed_box, vertical_dimension  # noqa: E402


def side_drawing(x, y):
    """A point of the side-wall drawing, as it lies in the jig outside face
    up: x down from the top of the wall, y along it from the far end."""
    return Pos(SIDE_WALL_PLATE_LENGTH - y, SIDING_Y + SIDING, WALL_HEIGHT - x)


def side_steps(*ns):
    return " ".join(f"manual:side_wall:{n}" for n in ns)


FUNKY_BOARD = (7, 3, 3/4)  # across the top plate, along the wall, thick


@component
def funky_board():
    """A jig tool: sits in a slot at the top of the jig to line up a wall's
    first siding panel."""
    length, wide, thick = FUNKY_BOARD
    return [Box(wide, thick, length, align=CORNER)], []


def funky_board_at(panel_edge, side, tag):
    """The funky board against a panel's edge; side is +1 if the panel is
    toward +X of the board, -1 if toward -X."""
    x = panel_edge if side < 0 else panel_edge - FUNKY_BOARD[1]
    return (funky_board, Pos(x, SIDING_Y, WALL_HEIGHT - FUNKY_BOARD[0] + 2), [], tag)


def side_wall_manual():
    out = []
    at = side_drawing
    # Step 1: nail the corners, 2 nails each.
    t = side_steps(1)
    for x, y, rot, flip in ((-7.45, -3.32, 90, False), (-7.56, 138.93, 90, False),
                            (94.13, 139.23, -90, True), (94.46, -3.57, -90, True)):
        out.append((Icon("NailGun", 14.5, 14, rotation=rot, flip=flip), at(x, y), [], t))
    for x, y in ((-20.3, 144.9), (-20.77, 2.63), (102.4, 144.9), (102.53, 3.02)):
        out.append((Label("x2", 4, attach=1), at(x, y), [], t))
    # Step 2: clamp, then screw through the plates into the flat studs, and the corner detail.
    t = side_steps(2)
    for i in range(8):
        x = 4.93 + 11 * i
        out.append((Icon("Screw", 2.4, 5.76, flip=True, rotation=180), at(x, -3.57), [], t))
        out.append((Icon("Screw", 2.4, 5.76), at(x, 147.57), [], t))
    for y, flip in ((142, False), (2, True), (139.66, False), (4.34, True)):
        out.append((Icon("Screw", 2.4, 5.76, rotation=90, flip=flip), at(-3.03, y), [], t))
        out.append((Icon("Screw", 2.4, 5.76, rotation=-90, flip=not flip), at(90.1, y), [], t))
    for x, tail in ((21, 3), (66, -4)):  # clamps across the wall, their labels between them
        out += [
            (Leader(((0.14, -7),)), at(x, 0), [], t),
            (Leader(((0.14, 7),)), at(x, SIDE_WALL_PLATE_LENGTH), [], t),
            (Leader(((0, -6), (tail, -6))), at(x, 139), [], t),
            (Leader(((0, 6), (tail, 6))), at(x, 5), [], t),
        ]
    out += [
        (Label("CLAMP", 2.5, attach=1), at(25.35, 134.34), [], t),
        (Label("CLAMP", 2.5, attach=7), at(25.35, 9.66), [], t),
        (Label("CLAMP", 2.5, attach=1), at(48.56, 134.57), [], t),
        (Label("CLAMP", 2.5, attach=7), at(48.56, 9.43), [], t),
        (Label("8 screws", 2, attach=1), at(37.42, 154.91), [], t),
        (Label("8 screws", 2, attach=1), at(38.56, -8.12), [], t),
        # the corner in section: the end stud and the flat stud, circled
        (Leader(((8.58, 3.88),)), at(87.2, 142.97), [], t),
        (Circle(8.28), at(103.32, 150.26), [], t),
    ]
    out += [(n, at(101.99, 147.26), [], t) for n in crossed_box(7, 3)]  # the plate
    out += [(n, at(98.99, 147.26), [], t) for n in crossed_box(3, 7)]  # the flat stud
    # Step 3: mark the inner studs' centers on the plates.
    t = side_steps(3)
    for c in spaced(STUD_SPACING, STUD_SPACING, 5):
        out += [
            (Icon("Pencil", 7.2, 7.2, flip=True), at(-11.6, c + 3.6), [], t),
            (Leader(((-5, 0),), arrow=False), at(-2, c), [], t),
            (Icon("Pencil", 7.2, 7.2), at(98.6, c + 3.6), [], t),
            (Leader(((5, 0),), arrow=False), at(89, c), [], t),
        ]
    # Step 4: nail through the plates into the inner studs, 2 nails each.
    t = side_steps(4)
    for c in spaced(STUD_SPACING, STUD_SPACING, 5):
        out += [
            (Icon("NailGun", 14.5, 14, rotation=90), at(-7.03, c - 4.4), [], t),
            (Icon("NailGun", 14.5, 14, rotation=-90, flip=True), at(93.84, c - 4.14), [], t),
            (Label("x2", 2.5, attach=1), at(-12, c - 13), [], t),
            (Label("x2", 2.5, attach=1), at(96, c - 12), [], t),
        ]
    out.append((Label("Final QC before Tyvek", 3, attach=1), at(14.46, 16.75), [], t))
    # Step 5: staple on the Tyvek.
    t = side_steps(5)
    out += [
        (Icon("staple-gun", 16, 16, flip=True), at(55, 56), [], t),
        (Label("TYVEK", 2.5, attach=1), at(34.51, 87.05), [], t),
        (Label("TOP", 3, attach=1), at(-12.05, 63.21), [], side_steps(5, "6a", "7a", "6b", "7b")),
    ]
    # Step 6: the first panel, against a funky board.
    for step, board, y in (("6a", funky_board_at(SIDING_PANEL_WIDTH, -1, side_steps("6a")), 94.5),
                           ("6b", funky_board_at(2 * SIDING_PANEL_WIDTH, 1, side_steps("6b")), 50.25)):
        t = side_steps(step)
        out += [
            board,
            (Leader(((-13, -11.5), (-11, -11.5))), at(-2, y), [], t),
            (Label("Funky\nBoard", 2.5, attach=1), at(-12.26, y - 10.2), [], t),
        ]
    out += [
        (Label("Panel 1", 3, attach=1), at(34.72, 113.39), [], side_steps("6a")),
        (Label("Panel 1", 3, attach=1), at(34.72, 18.14), [], side_steps("6b")),
    ]
    # Step 7: the other panels; rout the edges flush.
    t = side_steps("7a", "7b")
    for y, rot, text_y in ((-3.5, 0, -2), (147.5, 180, 151.16)):
        out += [
            (Icon("Router", 9.6, 9.6, rotation=rot), at(62.2, y + (0.2 if rot == 0 else -0.2)), [], t),
            (Leader(((17.5, 0),)), at(0, y), [], t),
            (Leader(((-18, 0),)), at(WALL_HEIGHT, y), [], t),
            (Leader(((5.75, 0),)), at(SIDING_HEIGHT - 1/4, y), [], t),
            (Label("Rout off excess edge after\nnailing down panel", 2, attach=1), at(21, text_y), [], t),
        ]
        for x in (0, WALL_HEIGHT, SIDING_HEIGHT - 1/4):  # extension lines
            out.append((Leader(((0, 5),), arrow=False), at(x, -6 if rot == 0 else 145), [], t))
    out += [
        (Label("Use jigsaw\n  here", 2, attach=1), at(85.82, -6.3), [], t),
        (Label("Use jigsaw\n  here", 2, attach=1), at(86, 156), [], t),
    ]
    for n, y in ((1, 113.45), (2, 65.45), (3, 17.45)):
        out.append((Label(f"Panel {n}", 3, attach=1), at(44.28, y), [], side_steps("7a")))
        out.append((Label(f"Panel {4 - n}", 3, attach=1), at(44.28, y), [], side_steps("7b")))
    return out


# ── window flashing ────────────────────────────────────────────────────────
# Peel-and-stick around the window, on the Tyvek (Front_Wall step 8 / 10,
# Rear_Wall step 6 / 8): first 1" strips around the rough opening with a
# 2 1/2" square turned 45° at each corner, then, over the window's flange,
# the sides and last a top strip overlapping them.

PEEL_AND_STICK = 1/32
FLASHING = 1  # strip width
FLASHING_PATCH = 2 + 1/2
FLASHING_TOP_OVERHANG = 1 + 1/8  # the last top strip, past each side strip


def strip(x, z, w, h):
    return Pos(x, WALL_DEPTH + WRAP, z) * panel(w, h, PEEL_AND_STICK)


@component
def window_opening_flashing():
    x0, x1, z0, z1 = WINDOW_X, WINDOW_X + WINDOW_WIDTH, WINDOW_Z, WINDOW_Z + WINDOW_HEIGHT
    solids = [
        strip(x0 - FLASHING, z0, FLASHING, WINDOW_HEIGHT), strip(x1, z0, FLASHING, WINDOW_HEIGHT),
        strip(x0, z0 - FLASHING, WINDOW_WIDTH, FLASHING), strip(x0, z1, WINDOW_WIDTH, FLASHING),
    ]
    for x in (x0 - FLASHING, x1 + FLASHING):
        for z in (z0 - FLASHING, z1 + FLASHING):
            solids.append(Pos(x, WALL_DEPTH + WRAP, z) * Rot(Y=45)
                          * Pos(-FLASHING_PATCH / 2, 0, -FLASHING_PATCH / 2) * panel(FLASHING_PATCH, FLASHING_PATCH, PEEL_AND_STICK))
    return solids, []


@component
def window_flange_flashing():
    x0, x1, z0, z1 = WINDOW_X, WINDOW_X + WINDOW_WIDTH, WINDOW_Z, WINDOW_Z + WINDOW_HEIGHT
    solids = [
        strip(x0 - FLASHING, z0, FLASHING, WINDOW_HEIGHT), strip(x1, z0, FLASHING, WINDOW_HEIGHT),
        strip(x0 - FLASHING - FLASHING_TOP_OVERHANG, z1, WINDOW_WIDTH + 2 * (FLASHING + FLASHING_TOP_OVERHANG), FLASHING),
    ]
    return solids, []


def window_flashing():
    return [(window_opening_flashing, Location(), [], 'Flashing'),
            (window_flange_flashing, Location(), [], 'Flashing')]


# ── Front_Wall/front_wall_ada.md and Rear_Wall/rear_wall.md figures ────────
# Tagged "manual:front_wall:<step>" / "manual:rear_wall:<step>" with the step
# layers of their images/*.dxf. Positions are in the drawings' frame (seen
# from outside, x from the wall's right end as built, y up from the bottom).

STRETCHER = DOOR_OPENING - 1/4  # doorway test stretcher
STRETCHER_Z = 10 + 3/4


@component
def stretcher():
    """A jig tool: a flat 2x4 that must just fit across the doorway before
    the door studs are nailed."""
    return [TwoByFour(STRETCHER, along="X", wide="Y")], []


def end_drawing(x, y):
    return Pos(END_WALL_PLATE_LENGTH - x, SIDING_Y + SIDING, y)


def front_wall_manual():
    at = end_drawing

    def steps(*ns):
        return " ".join(f"manual:front_wall:{n}" for n in ns)

    out = [
        (Label("Top", 4, attach=1), at(40, 110), [], "manual:front_wall"),
        (Label("Bottom", 4, attach=1), at(37.37, -13.51), [], "manual:front_wall"),
        (stretcher, Pos(DOOR_X + (DOOR_OPENING - STRETCHER) / 2, 0, STRETCHER_Z), [], steps(6)),
    ]
    out += [(n, at(-5.04, STUD), [], steps(1)) for n in vertical_dimension(STUD_LENGTH, "84")]
    # step_01
    t = steps('1')
    out += [
        (Icon('NailGun', 11.6, 11.2), at(-1.76, 93.91), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180), at(4.21, -5.99), [], t),
        (Icon('NailGun', 11.6, 11.2), at(84.83, 93.7), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180), at(91.42, -6.23), [], t),
        (Label('89"', 2, attach=1), at(51, 92), [], t),
        (Label('89"', 2, attach=1), at(58, -3), [], t),
        (Label('Bottom Plate', 2, attach=1), at(63, -3), [], t),
        (Label('Top Plate', 2, attach=1), at(56, 92), [], t),
        (Label('x2', 2, attach=1), at(-4.62, -6.69), [], t),
        (Label('x2', 2, attach=1), at(4.58, 95.14), [], t),
        (Label('x2', 2, attach=1), at(82.07, -6.69), [], t),
        (Label('x2', 2, attach=1), at(90.74, 94.75), [], t),
        (Leader(((4, 4), (10, 4))), at(40, 87), [], t),
        (Leader(((4.59, -4.29), (12.22, -4.29))), at(44.5, 0), [], t),
    ]
    # step_02
    t = steps('2')
    out += [
        (Icon('NailGun', 11.6, 11.2, rotation=90), at(10.97, 40.79), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=90), at(11.2, 78.4), [], t),
        (Icon('NailGun', 6.96, 6.72, flip=True), at(22.78, 90.5), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=180), at(23.95, 77.5), [], t),
        (Icon('NailGun', 6.96, 6.72, flip=True), at(30.19, 90.5), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=180), at(31.36, 77.5), [], t),
        (Icon('NailGun', 6.96, 6.72, flip=True), at(37.6, 90.51), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=180), at(38.77, 77.49), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=-90, flip=True), at(49.77, 41.11), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=-90, flip=True), at(49.99, 78.6), [], t),
        (Label('Clamp 3 header boards to top plate', 2, attach=1), at(32.46, 103.76), [], t),
        (Label('x1 into each header\nboth ends', 2, attach=1), at(56.05, 82.23), [], t),
        (Label('x2', 2, attach=1), at(2.31, 44.5), [], t),
        (Label('x2', 2, attach=1), at(56.05, 45.54), [], t),
        (Leader(((0, 15.62), (4.92, 15.62))), at(26.71, 87.14), [], t),
    ]
    # step_03
    t = steps('3')
    out += [
        (Icon('NailGun', 11.6, 11.2), at(14.16, 92.6), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180, flip=True), at(14.35, -5.6), [], t),
        (Icon('NailGun', 11.6, 11.2), at(39.48, 92.6), [], t),
        (Icon('NailGun', 8.7, 8.4, rotation=180), at(46.74, -5.57), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=-90, flip=True), at(50.79, 7.65), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=-90, flip=True), at(50.99, 21.27), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=-90, flip=True), at(51.2, 34.9), [], t),
        (Label('Clamp\nTIGHT', 2.5, attach=1), at(24.97, 15.5), [], t),
        (Label('x2 both studs', 2, attach=1), at(46, 95), [], t),
        (Label('x2', 2, attach=1), at(5.1, 93.71), [], t),
        (Label('x2', 2, attach=1), at(21.26, -6.5), [], t),
        (Leader(((-5.31, 0),)), at(42.01, 13.87), [], t),
        (Leader(((5.72, 0.02),)), at(46.83, 13.87), [], t),
        (Leader(((7.81, 7.32),), arrow=False), at(42.77, -9.7), [], t),
        (Circle(5.32), at(46.72, -6.05), [], t),
    ]
    # step_04
    t = steps('4')
    out += [
        (Icon('NailGun', 11.6, 11.2), at(47.18, 93.31), [], t),
        (Icon('NailGun', 8.7, 8.4, rotation=180), at(48.43, -5.31), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180), at(52.7, 76.46), [], t),
        (Icon('NailGun', 11.6, 11.2), at(63.2, 93.4), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180), at(66.91, 76.53), [], t),
        (Icon('NailGun', 11.6, 11.2), at(77.2, 93.4), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180), at(81.13, 76.6), [], t),
        (Icon('NailGun', 8.7, 8.4, rotation=180), at(87.95, -5.3), [], t),
        (Icon('NailGun', 8.7, 8.4, flip=True), at(87.99, 92.34), [], t),
        (Label('2x4', 2.5, attach=1), at(50.85, 115.47), [], t),
        (Label('3/4" plywood', 2, attach=1), at(69.13, 116.59), [], t),
        (Label('CLAMP', 3, attach=1), at(63, 70), [], t),
        (Leader(((-19, 0),), arrow=False), at(85, 106), [], t),
        (Leader(((-5, 7.25),)), at(66, 106.75), [], t),
        (Leader(((-5, 5), (-8, 5))), at(66, 109), [], t),
        (Leader(((0, 6.71),)), at(59.41, 87.21), [], t),
        (Leader(((0.01, -13.35), (2.58, -13.42))), at(59.42, 82.42), [], t),
        (Leader(((19, 0),), arrow=False), at(66, 107.5), [], t),
        (Leader(((19, 0),), arrow=False), at(66, 108.25), [], t),
        (Leader(((19, 0),), arrow=False), at(66, 109.75), [], t),
        (Leader(((4, 6.12), (0, 6.12))), at(85, 107.88), [], t),
        (Leader(((7.81, 7.32),), arrow=False), at(44.45, -9.44), [], t),
        (Leader(((7.81, 7.32),), arrow=False), at(83.98, -9.43), [], t),
        (Leader(((7.9, -7.21),), arrow=False), at(83.96, 96.42), [], t),
        (Circle(5.32), at(48.41, -5.79), [], t),
        (Circle(5.32), at(87.93, -5.78), [], t),
        (Circle(5.32), at(87.97, 92.82), [], t),
    ]
    # step_05
    t = steps('5')
    out += [
        (Icon('NailGun', 6.96, 6.72, rotation=90, flip=True), at(38.32, 23.03), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=90, flip=True), at(38.5, 10.96), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=90), at(38.68, 39.08), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90, flip=True), at(50.22, 37.09), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90, flip=True), at(50.36, 9.52), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90, flip=True), at(50.49, 69.84), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=90, flip=True), at(80.82, 73.21), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=90, flip=True), at(81.01, 20.01), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=90, flip=True), at(81.01, 40.25), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=90, flip=True), at(81.02, 12.98), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=90, flip=True), at(81.02, 33.22), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=90, flip=True), at(81.05, 60.1), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=90, flip=True), at(81.06, 53.07), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90), at(92.36, 70.52), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90, flip=True), at(92.52, 16.24), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90, flip=True), at(92.52, 36.48), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90, flip=True), at(92.56, 56.33), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90, flip=True), at(92.65, 8.56), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90, flip=True), at(92.65, 28.8), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90), at(92.65, 77.41), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=-90, flip=True), at(92.68, 48.65), [], t),
        (Label('CLAMP', 3, attach=1), at(21.84, 6.02), [], t),
        (Label('CLAMP', 3, attach=1), at(21.88, 29.39), [], t),
        (Label('CLAMP', 3, attach=1), at(64.48, 67.77), [], t),
        (Leader(((-5.31, 0),)), at(42, 4), [], t),
        (Leader(((-5.31, 0),)), at(42.03, 27.37), [], t),
        (Leader(((-5.31, 0),)), at(84.63, 65.75), [], t),
        (Leader(((5.72, 0.02),)), at(46.82, 4), [], t),
        (Leader(((5.72, 0.02),)), at(46.85, 27.37), [], t),
        (Leader(((5.72, 0.02),)), at(88.95, 65.75), [], t),
    ]
    # step_06
    t = steps('6')
    out += [
        (Icon('NailGun', 11.6, 11.2), at(42.38, 93.48), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180), at(49.32, -5.87), [], t),
        (Icon('NailGun', 11.6, 11.2), at(81.87, 93.43), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180), at(88.82, -5.92), [], t),
        (Label('Nail all 3 studs\nonly after\nstretcher fits', 2.5, attach=1), at(4.88, -2.66), [], t),
        (Label('Test with stretcher\nbefore nailing', 2.2, attach=1), at(56.19, 22.02), [], t),
        (Label('x2', 2, attach=1), at(40, -6), [], t),
        (Label('x2', 2, attach=1), at(48.5, 94.81), [], t),
        (Label('x2', 2, attach=1), at(80, -6), [], t),
        (Label('x2', 2, attach=1), at(89.21, 94.81), [], t),
        (Leader(((-4.43, -4.14), (-11.97, -3.99))), at(44.5, 0), [], t),
        (Leader(((3.7, 7.15), (7.52, 7.15))), at(48.18, 12.66), [], t),
    ]
    # step_07
    t = steps('7')
    out += [
        (Label('Align Tyvek roll to top of wall,\n  even on both sides.  Roll out Tyvek,\n  and staple to frame.', 2.5, attach=1), at(24, 101), [], t),
        (Leader(((-5, 13), (3, 13))), at(20, 87), [], t),
    ]
    # step_08
    t = steps('8')
    out += [
        (Label('Apply peel-and-stick\nABOVE (not on) jig brackets\nto all 4 sides of window opening.', 1.5, attach=1, bold=("ABOVE",)), at(51.25, 68), [], t),
        (Label('Trim Tyvek flush with inside of window opening', 2, attach=1), at(-1, 100), [], t),
        (Leader(((-26.25, 26.34), (-19.25, 26.34))), at(17.25, 71.66), [], t),
        (Leader(((5, 5), (7, 5))), at(43.25, 62), [], t),
    ]
    # step_09
    t = steps('9')
    out += [
        (Label('Exterior caulk between panels', 2.5, attach=1), at(40.97, 97.34), [], t),
        (Label('NO NAILS', 3, attach=1), at(56.88, 7.12), [], t),
        (Label('PANEL 1', 3, attach=1), at(22.04, 40.05), [], t),
        (Label('PANEL 2', 3, attach=1), at(50, 40), [], t),
        (Label('Three #8 (yellow)\ntemporary screws', 2.5, attach=1), at(64.44, -8.59), [], t),
        (Label('Use Panel Nails', 2.5, attach=1, bold=True), at(49.25, 64.12), [], t),
        (Leader(((-10.5, 9), (-4.5, 9))), at(44.5, 87), [], t),
        (Leader(((-3.65, 3.9), (-6.28, 3.9))), at(84.18, 1.59), [], t),
        (Leader(((-8.52, -10.76), (-2.82, -10.76))), at(65.31, 0.76), [], t),
        (Leader(((4.01, 3.95), (7.96, 3.95))), at(47.67, 1.56), [], t),
    ]
    # step_10
    t = steps('10')
    out += [
        (Label('Bore clearance hole 8" below top edge\n and 9 1/2" in from right edge, \nand rout out the door opening', 2, attach=1), at(45, 104), [], t),
        (Label('Caulk around opening,\ninstall window unit', 2, attach=1), at(6.59, 103.04), [], t),
        (Label('Peel-and-stick first', 2, attach=1), at(11, 96), [], t),
        (Label('Peel-and-stick last', 2, attach=1), at(42.49, 91.4), [], t),
        (Leader(((-10, 21), (-7, 21))), at(17, 74), [], t),
        (Leader(((-18.82, 34.76), (-12.49, 34.77))), at(17.39, 67.33), [], t),
        (Leader(((-35.25, 24.25),)), at(42.25, 70.75), [], t),
        (Leader(((7, 8), (12, 8))), at(29, 82), [], t),
        (Leader(((8, 19), (2, 19))), at(80, 80), [], t),
    ]
    # step_11
    t = steps('11')
    out += [
        (Label('Nail sides and top of door opening,\n every 8".  DO NOT nail across\n bottom of door opening.', 2.5, attach=1), at(36.65, 102.22), [], t),
    ]
    return out


def rear_wall_manual():
    at = end_drawing

    def steps(*ns):
        return " ".join(f"manual:rear_wall:{n}" for n in ns)

    out = [(Label("Rear Wall", 3, attach=1), at(33.57, -21.98), [], "manual:rear_wall")]
    out += [(n, at(-4, STUD), [], steps(1)) for n in vertical_dimension(STUD_LENGTH, "84")]
    # step_01
    t = steps('1')
    out += [
        (Icon('NailGun', 11.6, 11.2), at(-1.76, 93.91), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180), at(4.21, -5.99), [], t),
        (Icon('NailGun', 11.6, 11.2), at(84.2, 93.6), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180, flip=True), at(84.58, -6.23), [], t),
        (Label('89" Bottom Plate', 2, attach=1), at(40.39, -3.54), [], t),
        (Label('89" Top Plate', 2, attach=1), at(49.65, 92.84), [], t),
        (Label('x2', 2, attach=1), at(-4.62, -6.69), [], t),
        (Label('x2', 2, attach=1), at(4.58, 95.14), [], t),
        (Label('x2', 2, attach=1), at(90.74, 94.75), [], t),
        (Label('x2', 2, attach=1), at(91, -7), [], t),
        (Leader(((4.5, 4), (21.5, 4))), at(26.5, 87), [], t),
        (Leader(((4.59, -4.29), (12.22, -4.29))), at(25, 0), [], t),
    ]
    # step_02
    t = steps('2')
    out += [
        (Icon('NailGun', 11.6, 11.2, rotation=90), at(10.97, 40.79), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=90), at(11.2, 78.4), [], t),
        (Icon('NailGun', 6.96, 6.72, flip=True), at(22.78, 90.5), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=180), at(23.95, 77.5), [], t),
        (Icon('NailGun', 6.96, 6.72, flip=True), at(30.19, 90.5), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=180), at(31.36, 77.5), [], t),
        (Icon('NailGun', 6.96, 6.72, flip=True), at(37.6, 90.51), [], t),
        (Icon('NailGun', 6.96, 6.72, rotation=180), at(38.77, 77.49), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=-90, flip=True), at(49.77, 41.11), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=-90, flip=True), at(49.99, 78.6), [], t),
        (Label('Clamp 3 header boards to top plate', 2, attach=1), at(32.46, 103.76), [], t),
        (Label('x1 into each header\nboth ends', 2, attach=1), at(56.05, 82.23), [], t),
        (Label('x2', 2, attach=1), at(2.31, 44.5), [], t),
        (Label('x2', 2, attach=1), at(56.05, 45.54), [], t),
        (Leader(((0, 15.62), (4.92, 15.62))), at(26.71, 87.14), [], t),
    ]
    # step_03
    t = steps('3')
    out += [
        (Icon('NailGun', 11.6, 11.2), at(14.16, 92.6), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180, flip=True), at(14.35, -5.6), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180, flip=True), at(39.45, -5.6), [], t),
        (Icon('NailGun', 11.6, 11.2), at(39.48, 92.6), [], t),
        (Icon('NailGun', 8.7, 8.4, rotation=-90, flip=True), at(49.45, 24.34), [], t),
        (Icon('NailGun', 8.7, 8.4, rotation=-90, flip=True), at(49.52, 38.65), [], t),
        (Icon('NailGun', 8.7, 8.4, rotation=-90, flip=True), at(49.7, 6.96), [], t),
        (Label('CLAMP', 3, attach=1), at(21, 32), [], t),
        (Label('x1', 2, attach=1), at(53.9, 11.31), [], t),
        (Label('x1', 2, attach=1), at(54, 27), [], t),
        (Label('x1', 2, attach=1), at(54.23, 37.53), [], t),
        (Label('x2 into both studs', 1.8, attach=1), at(31.88, 100.52), [], t),
        (Label('x2 into both studs', 2, attach=1), at(32.05, -11), [], t),
        (Label('x2', 2, attach=1), at(5.1, 93.71), [], t),
        (Label('x2', 2, attach=1), at(21.26, -6.5), [], t),
        (Leader(((-5, 0),)), at(42, 30), [], t),
        (Leader(((6.75, 0), (6.75, 0))), at(45.25, 30), [], t),
    ]
    # step_04
    t = steps('4')
    out += [
        (Icon('NailGun', 4.06, 3.92, rotation=-90), at(48.86, 75), [], t),
        (Icon('NailGun', 4.06, 3.92, rotation=-90), at(48.87, 81.63), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180), at(49.31, 62.86), [], t),
        (Icon('NailGun', 4.06, 3.92, rotation=180), at(52.45, 82), [], t),
        (Icon('NailGun', 4.06, 3.92, rotation=180), at(62.03, 82), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=180, flip=True), at(63.39, -6.04), [], t),
        (Icon('NailGun', 11.6, 11.2, flip=True), at(69.64, 93.01), [], t),
        (Icon('NailGun', 11.6, 11.2, rotation=-89, flip=True), at(73.11, 66.26), [], t),
        (Label('1', 5, attach=1), at(75.08, 30.15), [], t),
        (Label('2', 5, attach=1), at(42.75, 96.64), [], t),
        (Label('3', 5, attach=1), at(27.46, 77.01), [], t),
        (Label('4', 5, attach=1), at(59.29, 57.53), [], t),
        (Label('CLAMP', 2.5, attach=1), at(49.26, 97.73), [], t),
        (Label('x2', 2, attach=1), at(47, 55.5), [], t),
        (Label('x2', 2, attach=1), at(70.3, -6.94), [], t),
        (Label('x2', 2, attach=1), at(71.12, 60.26), [], t),
        (Label('x2', 2, attach=1), at(75.7, 93.35), [], t),
        (Leader(((-11.92, -3.6),)), at(45.27, 79.35), [], t),
        (Leader(((-4.17, 4.96),)), at(51.35, 85.63), [], t),
        (Leader(((0, -8.5),)), at(55.5, 84), [], t),
        (Leader(((0, 8.5),)), at(55.5, 85.5), [], t),
        (Leader(((5.04, -10.09),)), at(54, 69), [], t),
        (Leader(((6.04, -6.16),)), at(67, 37), [], t),
        (Circle(4.37), at(29.17, 74.49), [], t),
        (Circle(4.37), at(44.36, 93.93), [], t),
        (Circle(4.37), at(61, 55), [], t),
        (Circle(4.37), at(76.1, 27.72), [], t),
    ]
    # step_04b
    t = steps('4b')
    out += [
        (Icon('NailGun', 5.8, 5.6, rotation=-90, flip=True), at(51.13, 63.82), [], t),
        (Icon('NailGun', 5.8, 5.6, rotation=90), at(61.34, 63.7), [], t),
        (Label('x2 into\neach block', 1.5, attach=1), at(47, 60), [], t),
        (Label('x2', 1.5, attach=1), at(62, 60), [], t),
    ]
    # step_05
    t = steps('5')
    out += [
        (Label('Align Tyvek roll to top of wall, even on both sides\nRoll out Tyvek, and staple to frame.', 1.5, attach=1), at(24, 96), [], t),
        (Label('TYVEK', 3, attach=1), at(47.93, 46.53), [], t),
        (Leader(((-5, 8), (3, 8))), at(20, 87), [], t),
    ]
    # step_06
    t = steps('6')
    out += [
        (Label('Apply peel-and-stick\nABOVE (not on) jig brackets\nto all 4 sides of window opening.', 1.5, attach=1, bold=("ABOVE",)), at(51.25, 68), [], t),
        (Label('TYVEK', 3, attach=1), at(47.93, 46.53), [], t),
        (Label('Trim Tyvek flush with inside of window opening', 2, attach=1), at(-1, 100), [], t),
        (Leader(((-26.25, 26.34), (-19.25, 26.34))), at(17.25, 71.66), [], t),
        (Leader(((5, 5), (7, 5))), at(43.25, 62), [], t),
    ]
    # step_07
    t = steps('7')
    out += [
        (Label('Exterior caulk between panels', 2, attach=1), at(49, 98), [], t),
        (Label('PANEL 1', 3, attach=1), at(22, 40), [], t),
        (Label('PANEL 2', 3, attach=1), at(47, 40), [], t),
        (Label('Panel nails, using A/C template', 2, attach=1), at(51, 93), [], t),
        (Label('Use Panel Nails', 2.5, attach=1, bold=True), at(27.98, 18.31), [], t),
        (Leader(((-5.31, 9.21), (3.48, 9.22))), at(44.5, 87), [], t),
        (Leader(((-9, 21),)), at(56, 71), [], t),
        (Leader(((1, 12), (4, 12))), at(46, 80), [], t),
    ]
    # step_08
    t = steps('8')
    out += [
        (Label('Install window unit', 2, attach=1), at(6.59, 103.04), [], t),
        (Label('Peel-and-stick first', 2, attach=1), at(10.35, 99.76), [], t),
        (Label('Peel-and-stick last,\noverlapping side strips', 2, attach=1), at(41.48, 94.98), [], t),
        (Leader(((-14, 25), (-7, 25))), at(17, 74), [], t),
        (Leader(((-18.82, 34.76), (-12.49, 34.77))), at(17.39, 67.33), [], t),
        (Leader(((-39.25, 28.25),)), at(42.25, 70.75), [], t),
        (Leader(((7, 12), (12, 12))), at(29, 82), [], t),
    ]
    return out
