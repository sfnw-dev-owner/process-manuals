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
    ]
    return solids, children


def side_wall_members():
    """The side wall's framing by name: {name: (component, Location, step)},
    the step being Side_Walls/sidewall_1.md's that places it."""
    return {
        # plates, the end studs, and a flat stud inside each (against the inside face)
        "bottom_plate": (side_wall_plate, Location(), 1),
        "top_plate": (side_wall_plate, Pos(0, 0, WALL_HEIGHT - STUD), 1),
        "end_stud_0": (stud, Pos(SIDE_STUDS[0], 0, STUD), 1),
        "end_stud_1": (stud, Pos(SIDE_STUDS[1], 0, STUD), 1),
        "flat_stud_0": (flat_stud, Pos(STUD, 0, STUD), 1),
        "flat_stud_1": (flat_stud, Pos(SIDE_WALL_PLATE_LENGTH - STUD - SIDE_FLAT_STUD, 0, STUD), 1),
        # the inner studs
        **{f"stud_{k}": (stud, Pos(x, 0, STUD), 3) for k, x in enumerate(SIDE_STUDS[2:], 1)},
    }


def by_step(members):
    """{step: [(component, Location, mods, tag)]} from named members."""
    out = {}
    for comp, loc, step in members.values():
        out.setdefault(step, []).append((comp, loc, [], ''))
    return out


def side_wall_steps():
    """Side wall framing by Side_Walls/sidewall_1.md step: {step: members}."""
    return by_step(side_wall_members())


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
    ]
    return solids, children


def window_members(step):
    """The window's framing: sill, triple header, and the studs either side
    of it (its "king" studs), placed in this step."""
    return {
        "sill": (block(WINDOW_WIDTH), Pos(WINDOW_X, 0, SILL_Z), step),
        **{f"header_{k}": (block(WINDOW_WIDTH), Pos(WINDOW_X, 0, z), step)
           for k, z in enumerate(spaced(HEADER_Z, STUD, 3), 1)},  # 3 stacked
        "window_stud_far": (stud, Pos(WINDOW_X + WINDOW_WIDTH, 0, STUD), step),  # toward the wall's end
        "window_stud_near": (stud, Pos(WINDOW_X - STUD, 0, STUD), step),  # toward the middle of the wall
    }


def front_wall_members():
    """The front wall's framing by name: {name: (component, Location, step)},
    the step being Front_Wall/front_wall_ada.md's that places it, as built in
    the jig (bottom plate whole). Three studs stand side by side between the
    door and the window: the window's king stud (step 2), the next one (step
    3), and the door's (step 4)."""
    door_right = DOOR_X + DOOR_OPENING
    return {
        "bottom_plate": (end_wall_plate, Location(), 1),
        "top_plate": (end_wall_plate, Pos(0, 0, WALL_HEIGHT - STUD), 1),
        "end_stud_door": (stud, Pos(0, 0, STUD), 1),  # the door end of the wall
        "end_stud_window": (stud, Pos(END_WALL_PLATE_LENGTH - STUD, 0, STUD), 1),
        **window_members(2),
        "middle_stud": (stud, Pos(door_right + STUD, 0, STUD), 3),  # the next stud, beside the window's
        "door_stud_end": (stud, Pos(DOOR_X - STUD, 0, STUD), 4),  # the doorway's, toward the wall's end
        "door_stud_middle": (stud, Pos(door_right, 0, STUD), 4),  # the doorway's, toward the middle
        "door_header_lower": (block(DOOR_OPENING), Pos(DOOR_X, 0, DOOR_HEADER_Z[0]), 4),
        "door_header_upper": (block(DOOR_OPENING), Pos(DOOR_X, 0, DOOR_HEADER_Z[1]), 4),
        "door_spacer": (door_header_spacer, Pos(DOOR_X, 0, DOOR_HEADER_Z[0] + STUD), 4),  # plywood between the headers
        **{f"spacer_block_{k}": (door_spacer_block, Pos(STUD, 0, z), 5) for k, z in enumerate(DOOR_SPACER_BLOCK_Z, 1)},
    }


def front_wall_steps():
    """Front wall framing by Front_Wall/front_wall_ada.md step: {step: members}."""
    return by_step(front_wall_members())


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
    ]
    return solids, children


def rear_wall_members():
    """The rear wall's framing by name: {name: (component, Location, step)},
    the step being Rear_Wall/rear_wall.md's that places it. Two studs stand
    side by side between the A/C opening and the window: the window's king
    stud (step 2) and the next one (step 3)."""
    return {
        "bottom_plate": (end_wall_plate, Location(), "1"),
        "top_plate": (end_wall_plate, Pos(0, 0, WALL_HEIGHT - STUD), "1"),
        "end_stud_ac": (stud, Pos(0, 0, STUD), "1"),  # the A/C end of the wall
        "end_stud_window": (stud, Pos(END_WALL_PLATE_LENGTH - STUD, 0, STUD), "1"),
        **window_members("2"),
        "middle_stud": (stud, Pos(AC_X + AC_OPENING, 0, STUD), "3"),  # the next stud, beside the window's
        # the A/C opening: the stud on its far side, blocks above and below, a block beside it
        "ac_stud": (stud, Pos(AC_X - STUD, 0, STUD), "4"),
        "ac_header": (block(AC_OPENING), Pos(AC_X, 0, AC_HEADER_Z), "4"),
        "ac_side_block": (ac_side_block, Pos(AC_X + AC_OPENING - STUD, 0, AC_SILL_Z + STUD), "4"),
        "ac_sill": (block(AC_OPENING), Pos(AC_X, 0, AC_SILL_Z), "4"),
        **{f"ac_under_{k}": (ac_under_block, Pos(x, 0, AC_SILL_Z - AC_UNDER_BLOCK), "4b")
           for k, x in enumerate((AC_X, AC_X + AC_OPENING - 2 * STUD, AC_X + AC_OPENING - STUD), 1)},
    }


def rear_wall_steps():
    """Rear wall framing by Rear_Wall/rear_wall.md step: {step: members}."""
    return by_step(rear_wall_members())


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


# ── jig tools ──────────────────────────────────────────────────────────────

FUNKY_BOARD = (7, 3, 3/4)  # across the top plate, along the wall, thick


@component
def funky_board():
    """A jig tool: sits in a slot at the top of the jig to line up a wall's
    first siding panel."""
    length, wide, thick = FUNKY_BOARD
    return [Box(wide, thick, length, align=CORNER)], []


def funky_board_at(panel_edge, side):
    """The funky board against a panel's edge, in the wall's frame; side is
    +1 if the panel is toward +X of the board, -1 if toward -X."""
    x = panel_edge if side < 0 else panel_edge - FUNKY_BOARD[1]
    return Pos(x, SIDING_Y, WALL_HEIGHT - FUNKY_BOARD[0] + 2)


STRETCHER = DOOR_OPENING - 1/4  # doorway test stretcher
STRETCHER_Z = 10 + 3/4


@component
def stretcher():
    """A jig tool: a flat 2x4 that must just fit across the doorway before
    the door studs are nailed."""
    return [TwoByFour(STRETCHER, along="X", wide="Y")], []


STRETCHER_AT = Pos(DOOR_X + (DOOR_OPENING - STRETCHER) / 2, 0, STRETCHER_Z)  # in the doorway, near the bottom


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
