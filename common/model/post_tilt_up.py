"""Frame completion and roof blocking (post-tilt-up/frame-completion.md and
roof-blocking.md): the house between tilt-up and roofing, the half-roofs on
their way up, and the tools and props for it: step ladders, the funky boards
that push a half-roof up, bar clamps, screws and lag bolts.

Frame: the house's (house.py). The loose things' places at each stage (the
half-roofs going up, ladders, funky boards, people, clamps) are where
SketchUp/Tiny_Home_Model_-_with_interiors.skp's tilt-up scenes had them,
converted to the house's frame: SKETCHUP_HOUSE is where that model had the
house.
"""

from .common import *
from .house import WALL_TOP
from .platform import PLATFORM_LENGTH, PLATFORM_WIDTH, platform
from .roof import (
    PLUMB_DEPTH, RIDGE_BOARD, TRI_HALF, RAFTER_Y, RIDGE_BOARD_BOTTOM, RIDGE_TOP, RIDGE_X, TIP_X, VENT_BLOCK_HEIGHT, VENT_BLOCK_THICKNESS,
    angle_plate,
    bird_block, bird_length, bored_rafter, cross_block, eave_board, half_roof, rafter, ridge_board,
    structural_triangle, underside, vent_block, vent_length, wall_bays,
)
from .walls import WALL_DEPTH, front_wall, rear_wall, side_wall

# Where the SketchUp model had the house: turned end for end (its front wall
# at low Y), the deck's top at 14 3/8" (the manuals' platform is 2" lower).
SKETCHUP_HOUSE = Pos(103.7285, 164.0849, 14.375 - 11.75) * Rot(Z=180)


# ── the house at frame completion ──────────────────────────────────────────

def walls():
    """The platform and the four walls, as tilted up: (component, placement, mods)."""
    from .platform import DECK
    return [
        (platform, Location(), []),
        (side_wall, Pos(WALL_DEPTH, 0, DECK) * Rot(Z=90), []),
        (side_wall, Pos(PLATFORM_WIDTH - WALL_DEPTH, PLATFORM_LENGTH, DECK) * Rot(Z=-90), []),
        (front_wall, Pos(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, DECK), []),
        (rear_wall, Pos(PLATFORM_WIDTH - WALL_DEPTH, WALL_DEPTH, DECK) * Rot(Z=180), []),
    ]


ROOF = Pos(0, 0, WALL_TOP)  # the roof's frame: Z = 0 at the top of the walls


def triangles():
    """The structural triangles on the rear and front walls."""
    return [(structural_triangle, ROOF * Pos(RIDGE_X, 0, 0), []),
            (structural_triangle, ROOF * Pos(RIDGE_X, PLATFORM_LENGTH - WALL_DEPTH, 0), [])]


FRAMING = (rafter, bored_rafter, angle_plate, ridge_board, eave_board, cross_block)


@component
def half_roof_frame():
    """A half-roof assembly as it comes off the jig: rafters, angle plates,
    white boards and cross blocks (the bird and vent blocks come later)."""
    return [], [c for c in half_roof()[1] if c[0] in FRAMING]


# The two halves where they end up: "left" at X = 0 (the right half, seen from
# the front door), "right" mirrored at the other side wall.
HALF_ROOFS = {
    "left": (ROOF, []),
    "right": (ROOF * Pos(PLATFORM_WIDTH, 0, 0), ["mirror"]),
}

# The half-roofs on the way up (frame-completion.md "Raise Half-Roofs"), as
# moves of the installed half: lying against the side wall's foot (step 1),
# leaning on its bottom (2), pushed up on the funky boards (3). The right
# half goes up first ("LHS" in the SketchUp model and the LayOut pages).
RAISING = {
    ("right", 1): Location((-18.495, -1.606, 29.313), (0, 56, 0)),
    ("right", 2): Location((-18.763, -1.606, 66.688), (0, 56, 0)),
    ("right", 3): Location((-24.701, -1.606, 93.0), (0, 56, 0)),
    ("left", 1): Location((55.961, -1.606, -50.275), (0, -56, 0)),
    ("left", 2): Location((55.961, -1.606, -12.9), (0, -56, 0)),
    ("left", 3): Location((55.961, -1.606, 13.413), (0, -56, 0)),
}


def on_half(side, x, y, z):
    """(placement, mods) for a part at (x, y, z) in the left half-roof's
    frame, on the given half (mirrored across the ridge for the right)."""
    loc, mods = HALF_ROOFS[side]
    return loc * Pos(-x if mods else x, y, z), mods


def half_roof_at(side, step=None):
    """(component, placement, mods) for a half-roof, installed or raising."""
    loc, mods = HALF_ROOFS[side]
    if step is not None:
        loc = RAISING[(side, step)] * loc
    return (half_roof_frame, loc, mods)


BIRD_BLOCK_START = 9 + 3/4  # inward of its place, as it's set on the plate before tapping it out


def bird_blocks(side="left", bays=None, inward=0):
    """Bird blocks on the side wall's top plate, in the given wall bays
    (indexes into roof.wall_bays(); default all); `inward` of their places."""
    from .roof import SIDING_FACE
    all_bays = wall_bays()
    out = []
    for i in (range(len(all_bays)) if bays is None else bays):
        a, b = all_bays[i]
        out.append((bird_block(b - a), *on_half(side, -SIDING_FACE + inward, (a + b - bird_length(b - a)) / 2, 0)))
    return out


VENT_BLOCK_START = (7.3, -9.6)  # out from the ridge and down, where it's set before pushing it up


def vent_blocks(side="left", bays=None, offset=(0, 0)):
    """Vent blocks against the ridge board, in the given wall bays; `offset`
    (out from the ridge, up) from their places."""
    all_bays = wall_bays()
    x0 = TIP_X - VENT_BLOCK_THICKNESS
    z0 = underside(x0) + PLUMB_DEPTH - VENT_BLOCK_HEIGHT
    out = []
    for i in (range(len(all_bays)) if bays is None else bays):
        a, b = all_bays[i]
        out.append((vent_block(b - a), *on_half(side, x0 - offset[0], (a + b - vent_length(b - a)) / 2, z0 + offset[1])))
    return out


# ── tools and props ────────────────────────────────────────────────────────
# Sized as SketchUp modeled them; each in the frame SketchUp's component had,
# so its placements carry over.

LADDER_HEIGHT = 120 + 3/8  # the 12' step ladder, standing
LADDER_SPREAD = 66  # between its feet, front to back
LADDER_WIDTH = (28 + 3/4, 17)  # at the feet and at the top
LADDER_TOP = (8, 4 + 3/8)  # the top cap, front to back and thick
LADDER_RAIL = (3, 1 + 1/4)
LADDER_STEPS = 10  # on the front leg, the top one just under the cap
LADDER_STEP = 3  # deep


def _splayed(p0, p1, section):
    """A rail from p0 to p1 with a (wide, thick) rectangular section, its
    wide face across X."""
    from math import atan2, degrees, dist
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    length = dist(p0, p1)
    tilt = degrees(atan2(x1 - x0, z1 - z0))
    lean = degrees(atan2(y1 - y0, z1 - z0))
    return Pos(x0, y0, z0) * Rot(Y=tilt) * Rot(X=-lean) * Box(section[0], section[1], length,
                                                                     align=(Align.CENTER, Align.CENTER, Align.MIN))


@component
def step_ladder():
    """A 12' step ladder, open: the front (stepped) leg toward +X from its
    top, the rear leg toward X = 0; Y across it."""
    top_x = LADDER_SPREAD / 2
    h = LADDER_HEIGHT - LADDER_TOP[1]
    (w0, w1) = LADDER_WIDTH
    solids = []
    for foot_x, top in ((LADDER_SPREAD, top_x + LADDER_TOP[0] / 2 - 1), (0, top_x - LADDER_TOP[0] / 2 + 1)):
        for side in (-1, 1):
            solids.append(_splayed((foot_x, w0 / 2 + side * (w0 / 2 - 1), 0),
                                   (top, w0 / 2 + side * (w1 / 2 - 1), h), LADDER_RAIL))
    front_top = top_x + LADDER_TOP[0] / 2 - 1
    for i in range(1, LADDER_STEPS):
        z = h * i / LADDER_STEPS
        x = LADDER_SPREAD + (front_top - LADDER_SPREAD) * z / h
        w = w0 + (w1 - w0) * z / h
        solids.append(Pos(x, w0 / 2, z) * Box(LADDER_STEP, w - 2, 1, align=(Align.CENTER, Align.CENTER, Align.MAX)))
    spreader_z = 64
    x_front = LADDER_SPREAD + (front_top - LADDER_SPREAD) * spreader_z / h
    x_rear = (top_x - LADDER_TOP[0] / 2 + 1) * spreader_z / h
    solids.append(Pos((x_front + x_rear) / 2, 1, spreader_z) * Box(x_front - x_rear, 1/2, 1, align=(Align.CENTER, Align.MIN, Align.CENTER)))
    solids.append(Pos(top_x, w0 / 2, h) * Box(LADDER_TOP[0], w1 + 1, LADDER_TOP[1], align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return solids, []


STOOL = (15 + 5/8, 24, 42 + 1/2)  # the step stool: wide, deep (feet), high


@component
def step_stool():
    """A 3-step stool: its stepped front leg rising from Y = 0 toward +Y, a
    rear leg behind; X across it."""
    wide, deep, high = STOOL
    rail = (1 + 1/4, 3)
    solids = []
    for x in (rail[0] / 2, wide - rail[0] / 2):
        solids.append(_splayed((x, 1, 0), (x, 20, high - 1), (rail[0], rail[1])))
        solids.append(_splayed((x, deep - 1, 0), (x, 18.5, 35), (rail[0], rail[1])))
    for i in (1, 2, 3):
        z = (high - 1) * i / 4
        y = 1 + 19 * z / (high - 1)
        solids.append(Pos(wide / 2, y, z) * Box(wide, 5, 1, align=(Align.CENTER, Align.CENTER, Align.MAX)))
    solids.append(Pos(wide / 2, 19, high) * Box(wide, 6, 1, align=(Align.CENTER, Align.CENTER, Align.MAX)))
    return solids, []


FUNKY_BOARD = (73 + 1/2, 36)  # a half-roof funky board: high, and its head across


@component
def funky_board():
    """Funky Boards #3 and #4 (frame-completion.md "Raise Half-Roofs"): a 2x4
    pole with a 2x4 head across its top, braced, that pushes a half-roof up
    by its eave board."""
    high, head = FUNKY_BOARD
    pole = TwoByFour(high - thickness("2x4"), along="Z", wide="Y")
    brace_drop = 13
    solids = [
        Pos(head / 2 - thickness("2x4") / 2, 0, 0) * pole,
        Pos(0, 0, high - thickness("2x4")) * TwoByFour(head, along="X", wide="Y"),
        *[_splayed((head / 2, width("2x4") / 2, high - thickness("2x4") - brace_drop),
                   (head / 2 + side * (head / 2 - 3), width("2x4") / 2, high - thickness("2x4")), (3/4, 1 + 1/2))
          for side in (-1, 1)],
    ]
    return solids, []


# A one-hand bar clamp (quick-grip style): a bar along X, its fixed jaw at the
# +X end, the sliding head with its pistol grip; the jaws rise to Z = 16.
CLAMP_BAR = (-12.73, 2.82, 10.7, 11.64)  # x from, x to, z from, z to
CLAMP_BAR_Y = 8.15  # the bar's center line
CLAMP_JAW_TOP = 16
CLAMP_OPENING = 2.35  # between the pads as modeled (the head near the fixed jaw)


def _profile(points, thick, y):
    """A flat piece: a profile in the XZ plane, `thick` across Y, centered on y."""
    return Pos(0, y + thick / 2, 0) * extrude(Plane.XZ * Polygon(*points, align=None), thick)


def _rounded(solid, radius, axis):
    """The solid with its edges along `axis` rounded (or as is, if that fails)."""
    try:
        return solid.fillet(radius, solid.edges().filter_by(axis))
    except Exception:
        return solid


def _bar_clamp(opening):
    """The clamp with its jaws `opening` apart: the head (and its grip) slid
    along the bar from where it's modeled."""
    x0, x1, z0, z1 = CLAMP_BAR
    y = CLAMP_BAR_Y
    top = CLAMP_JAW_TOP
    dx = CLAMP_OPENING - opening  # the head's slide (toward the bar's free end when opening)
    pad = lambda x, z: _rounded(Pos(x, y, z) * Box(0.35, 1.8, top - z, align=(Align.MIN, Align.CENTER, Align.MIN)), 0.3, Axis.X)
    head = [
        # the sliding head around the bar (rounded), its jaw, and its pad facing the fixed jaw
        _rounded(Pos(-4.26, y, 10.36) * Box(4.03, 1.74, 2.3, align=(Align.MIN, Align.CENTER, Align.MIN)), 0.4, Axis.Y),
        _profile([(-1.6, 12.66), (-0.23, 12.66), (-0.23, top - 0.4), (-0.9, top - 0.4)], 1.3, y),
        pad(-0.23, 12.8),
        # the pistol grip under the head (curving back), and the trigger in front of it
        _profile([(-0.3, 10.36), (-1.4, 10.36), (-1.85, 9.0), (-2.3, 7.4), (-2.8, 5.9), (-3.0, 4.9), (-2.8, 4.2),
                  (-2.3, 4.0), (-1.7, 4.3), (-1.3, 5.2), (-1.0, 6.6), (-0.6, 8.2), (-0.3, 9.4)], 1.1, y),
        _profile([(-4.1, 10.36), (-3.4, 10.36), (-3.6, 9.0), (-4.0, 7.6), (-4.6, 6.3), (-5.2, 5.9), (-5.5, 6.4),
                  (-5.0, 7.4), (-4.5, 8.4), (-4.2, 9.4)], 0.8, y),
    ]
    solids = [
        Pos(x0, y, z0) * Box(x1 - x0, 0.74, z1 - z0, align=(Align.MIN, Align.CENTER, Align.MIN)),
        # the fixed jaw on the end of the bar, and its pad facing the head
        _profile([(x1, 10.2), (x1 + 1.3, 10.2), (x1 + 1.3, 12.2), (x1 + 0.8, top - 0.4), (x1 + 0.1, top - 0.4), (x1, 12.2)], 1.3, y),
        pad(x1 - 0.35, 12.4),
    ] + [Pos(dx, 0, 0) * s for s in head]
    return solids, []


@component
def bar_clamp():
    return _bar_clamp(CLAMP_OPENING)


@component
def plate_clamp():
    """A bar clamp opened to a structural triangle's base on the wall's top
    plate, to clamp the two (its fixed jaw on the base, its head under the
    plate)."""
    return _bar_clamp(2 * thickness("2x4"))


@component
def ridge_clamp():
    """A bar clamp opened to the ridge boards' height, to clamp them top to
    bottom."""
    return _bar_clamp(RIDGE_TOP - RIDGE_BOARD_BOTTOM)


SCREW_LONG = (3, 0.19, 0.37)  # #10 x 3" (brown): long, shank, head (diameters)
SCREW_SHORT = (1 + 1/2, 0.16, 0.31)  # #8 x 1 1/2" (yellow)
HEX_SCREW = (1 + 1/8, 0.19, 0.39)  # galvanized hex-head, for the roof brackets
LAG_BOLT = (4, 3/8, 9/16)  # 3/8 x 4" lag bolt


THREAD_PITCH = 0.14  # between the thread's turns, drawn as rings


FLANGE = 1/16  # the washer flange under a hex head
TORX_DEPTH = 0.05  # the star recess in a wood screw's head


def _star(outer, inner, points=6):
    """A star polygon (the Torx recess, seen from above)."""
    from math import cos, pi, sin
    return Polygon(*[((outer if i % 2 == 0 else inner) * cos(i * pi / points), (outer if i % 2 == 0 else inner) * sin(i * pi / points))
                     for i in range(2 * points)], align=None)


def screw_like(length, shank, head, head_height, hex=False):
    """A fastener along +Z, its head's top at Z = 0 and its tip at -length: a
    hex head on its washer flange, or a wood screw's countersunk one with
    its Torx recess; the shank, threaded (rings standing for the thread's
    turns) over its lower two thirds, down to the point."""
    if hex:
        parts = [extrude(Plane.XY.offset(-head_height) * RegularPolygon(head / 2, 6), head_height),
                 Pos(0, 0, -head_height - FLANGE) * Cylinder(head * 0.8, FLANGE, align=(Align.CENTER, Align.CENTER, Align.MIN))]
    else:
        recess = extrude(Plane.XY.offset(-TORX_DEPTH) * _star(head * 0.3, head * 0.17), TORX_DEPTH)
        parts = [Pos(0, 0, -head_height) * Cone(shank / 2, head / 2, head_height, align=(Align.CENTER, Align.CENTER, Align.MIN)) - recess]
    tip = shank  # the point's length
    core = shank / 2 * 0.7
    parts.append(Pos(0, 0, -head_height) * Cylinder(core, length - head_height - tip, align=(Align.CENTER, Align.CENTER, Align.MAX)))
    parts.append(Pos(0, 0, -length) * Cone(0, core, tip, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    z = -length + THREAD_PITCH / 2
    while z < -length / 3:
        r = shank / 2 * min(1, (z + length) / tip)  # narrowing down the point
        parts.append(Pos(0, 0, z) * Cylinder(r, THREAD_PITCH / 3, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        z += THREAD_PITCH
    if hex:
        parts.append(Pos(0, 0, -head_height) * Cylinder(shank / 2, length / 3, align=(Align.CENTER, Align.CENTER, Align.MAX)))
    return parts


# SketchUp's fasteners stand on their local Z, heads up, the head's top at
# this height (and centered on this X, Y).
SKP_SCREW_HEAD = (0.1475, 0.1475, 2.608)
SKP_NAIL_HEAD = (0.34, 0.355, 4.505)
SKP_HEX_HEAD = (0.195, 0.195, 1.16)


@component
def screw_long():
    return [Pos(*SKP_SCREW_HEAD) * s for s in screw_like(*SCREW_LONG, 0.12)], []


@component
def screw_short():
    return [Pos(*SKP_SCREW_HEAD) * s for s in screw_like(*SCREW_SHORT, 0.1)], []


@component
def corner_screw():
    """#10 x 3" through a wall's end stud into the next wall (in SketchUp's
    nail's frame)."""
    return [Pos(*SKP_NAIL_HEAD) * s for s in screw_like(*SCREW_LONG, 0.12)], []


HEX_HEAD_HEIGHT = 0.2


@component
def hex_screw():
    return [Pos(*SKP_HEX_HEAD) * s for s in screw_like(*HEX_SCREW, HEX_HEAD_HEIGHT, hex=True)], []


@component
def lag_bolt():
    """Head up, its top at the origin; into the wall's top plate below."""
    return screw_like(*LAG_BOLT, 0.25, hex=True), []


def lag_bolts(side="left", rafters=None, lift=0):
    """Lag bolts in the bored rafters' counterbores (roof-blocking.md
    "Install Magic Stud Lag Bolts"), by index into roof.RAFTER_Y; `lift`
    inches up, before they're driven home."""
    from math import cos, radians
    from .roof import (EAVE_BOARD, LAG_COUNTERBORE, LAG_COUNTERBORE_DEPTH, RAFTER, RAFTER_DEPTH, ROOF_PITCH, SLOPE,
                       TAIL_U, UNBORED)
    C = cos(radians(ROOF_PITCH))
    x = width(EAVE_BOARD) + 1/2 + LAG_COUNTERBORE / 2 / C  # the bore's center on the rafter's top, from its tail
    out = []
    for i, y in enumerate(RAFTER_Y):
        if i in UNBORED or (rafters is not None and i not in rafters):
            continue
        top = SLOPE * Pos(TAIL_U, y, 0) * Pos(x, RAFTER / 2, RAFTER_DEPTH)
        # plumb down from the rafter's top face by the counterbore's depth
        out.append((lag_bolt, *on_half(side, top.position.X, top.position.Y,
                                        top.position.Z - LAG_COUNTERBORE_DEPTH / C + lift)))
    return out


MAGIC_RAFTERS = [RAFTER_Y.index(y) for y in RAFTER_Y if abs(y + 1.5 / 2 - (PLATFORM_LENGTH - 48)) < 1]


VENT_GUIDE_BOARD = (156 + 1/4, width("1x8"), thickness("1x8"))  # the vent jig


@component
def vent_guide_board():
    """The vent jig (roof-blocking.md "Install Ridge Vent Blocks"): a 1x8
    clamped on the rafters, down the slope from the ridge, that the vent
    blocks are pushed up against. Along Y; X down the slope; Z square to it."""
    from .roof import ROOF_PITCH
    length, wide, thick = VENT_GUIDE_BOARD
    return [Rot(Y=-ROOF_PITCH) * Box(wide, length, thick, align=CORNER)], []


# ── where SketchUp had things (house frame) ────────────────────────────────

LADDERS = {  # "12' ladder at each end" and a step stool inside, per half
    "right": [(step_ladder, Location((71.661, -40.758, -9.875), (0, 0, 0)), ["mirror"]),
              (step_ladder, Location((71.661, 186.881, -9.875), (0, 0, -180)), []),
              (step_stool, Location((52.705, 79.058, 3.875), (0, 0, -90)), [])],
    "left": [(step_ladder, Location((76.69, -12.181, -9.875), (0, 0, -180)), []),
             (step_ladder, Location((76.69, 186.881, -9.875), (0, 0, -180)), []),
             (step_stool, Location((29.646, 79.058, 3.875), (0, 0, 90)), ["mirror"])],
}

FUNKY_BOARDS = {  # (side, raising step) -> the two funky boards under the half-roof
    ("right", 1): [Location((180.321, -7.358, 6.823), (0, 0.061, 0)), Location((178.946, 125.204, 6.823), (0, 0.061, 0))],
    ("right", 2): [Location((176.31, 2.252, -14.997), (0, -63.1, 0)), Location((177.987, 135.101, -11.691), (0, -63.1, 0))],
    ("right", 3): [Location((153.89, 135.385, -0.993), (0, -45, 0)), Location((153.89, 0.447, -0.993), (0, -45, 0))],
    ("right", 4): [Location((156.192, 134.719, 40.033), (0, -19.8, 0)), Location((156.237, 4.969, 40.049), (0, -19.8, 0))],
    ("left", 1): [Location((-95.268, -5.352, 6.823), (0, -0.061, 0)), Location((-95.859, 123.892, 6.823), (0, -0.061, 0))],
    ("left", 2): [Location((-84.356, 1.326, -14.723), (0, 60, 0)), Location((-84.356, 135.264, -14.723), (0, 60, 0))],
    ("left", 3): [Location((-68.947, 135.135, -0.993), (0, 45, 0)), Location((-68.947, -1.553, -0.993), (0, 45, 0))],
    ("left", 4): [Location((-22.171, 134.719, 26.863), (0, 14.939, 0)), Location((-22.553, 4.969, 26.965), (0, 14.939, 0))],
}
FUNKY_BOARD_MIRRORED = {("right", 4), ("left", 1), ("left", 2), ("left", 3), ("left", 4)}


def funky_boards(side, step):
    mods = ["mirror"] if (side, step) in FUNKY_BOARD_MIRRORED else []
    return [(funky_board, loc, mods) for loc in FUNKY_BOARDS[(side, step)]]


# Clamps and fasteners at each step, (component, placement, mods).
def triangle_clamp(x):
    """A bar clamp holding the rear structural triangle's base down on the
    wall's top plate, its pads centered x along the wall: fixed jaw on the
    base, head under the plate, bar inside the house, grip pointing in."""
    from .walls import WALL_DEPTH
    base_top = WALL_TOP + thickness("2x4")
    pads = (CLAMP_JAW_TOP + 12.4) / 2  # the pads' middle, up the jaws from the bar
    # bar (X) up, fixed end at the top; jaws (Z) reaching to the wall from inside
    return (plate_clamp, Location(Plane((x + CLAMP_BAR_Y, WALL_DEPTH / 2 + pads, base_top - (CLAMP_BAR[1] - 0.35)),
                                        x_dir=(0, 0, 1), z_dir=(0, -1, 0))), [])


TRIANGLE_CLAMPS = [triangle_clamp(x) for x in (RIDGE_X - TRI_HALF + 6, RIDGE_X + TRI_HALF - 6)]  # "about 6" from each end"

TRIANGLE_SCREWS = [  # preset in the rear triangle's base
    (screw_long, Location(p, r), ["mirror"] if m else []) for p, r, m in (
        ((45.582, 2.283, 100.352), (0, -32.9, 0), True), ((45.582, 0.533, 100.352), (0, -32.9, 0), True),
        ((50.533, 0.533, 100.352), (0, 32.9, 0), False), ((50.533, 2.283, 100.352), (0, 32.9, 0), False),
        ((26.192, 1.552, 100.469), (47.9, 0, 90), True), ((28.817, 1.552, 100.469), (47.9, 0, 90), True),
        ((34.033, 0.533, 100.352), (0, 32.9, 0), False), ((34.033, 2.283, 100.352), (0, 32.9, 0), False),
        ((62.207, 0.533, 100.352), (0, -32.9, 0), True), ((62.207, 2.283, 100.352), (0, -32.9, 0), True),
        ((69.629, 1.552, 100.469), (47.9, 0, 90), True), ((67.004, 1.552, 100.469), (47.9, 0, 90), True),
        ((11.15, 2.452, 100.839), (0, 0, -180), False), ((11.15, 1.014, 100.839), (0, 0, -180), False),
        ((85.145, 2.452, 100.839), (0, 0, -180), False), ((85.145, 1.014, 100.839), (0, 0, -180), False),
    )
]

CORNER_SCREWS = [  # 5 in each wall corner, up the end studs
    (corner_screw, Location((x, y, z), r), ["mirror"] if m else []) for (x, y, r, m), zs in (
        ((9.068, 3.133, (90, -65.3, -180), True), (94.946, 75.946, 56.331, 39.393, 19.025)),
        ((86.932, 4.386, (90, 65.3, 180), False), (94.63, 75.63, 57.14, 40.202, 20.521)),
        ((87.298, 139.433, (-90, 65.3, 0), True), (94.946, 75.946, 57.893, 39.706, 18.275)),
        # (the door side: between the door's spacer blocks, centered in the gaps)
        ((9.702, 137.664, (-90, -73.101, 0), False), (93.25, 75.25, 56.25, 36.25, 17.25)),
    ) for z in zs
]


UPRIGHT_CLAMP_X = 62.326  # the upright ridge clamp's jaw tips' X + CLAMP_JAW_TOP (where the LayOut page had it)


def ridge_clamps(bay_y, side_y=None, side_z=100.208):
    """The two clamps holding the ridge boards at a bay: one upright, clamping
    them top to bottom from the far (right) side (fixed jaw under the boards,
    head and the bar's tail above, for safety), one on its side across them
    at `side_y` (default where the page had it, along from the bay), its
    fixed jaw on the left (toward the pages' camera), its head and the bar's
    tail off to the right, its bar `side_z` up."""
    side_y = bay_y + 2.086 + CLAMP_BAR_Y if side_y is None else side_y
    # The clamp's frame: its bar (X) points down (fixed end at the bottom), its
    # jaws (Z) point left, into the boards, and the fixed pad's face sits at
    # the boards' bottom.
    upright = Plane((UPRIGHT_CLAMP_X, bay_y + 2 * CLAMP_BAR_Y, WALL_TOP + RIDGE_BOARD_BOTTOM + CLAMP_BAR[1] - 0.35),
                    x_dir=(0, 0, -1), z_dir=(-1, 0, 0))
    # On its side: bar along -X (fixed end left), jaws up, the head's pad on
    # the boards' right face.
    side = Plane((RIDGE_X + thickness(RIDGE_BOARD) + (CLAMP_OPENING - CLAMP_BAR[1] + 0.35), side_y + CLAMP_BAR_Y, side_z),
                 x_dir=(-1, 0, 0), z_dir=(0, 0, 1))
    return [(ridge_clamp, Location(upright), []), (bar_clamp, Location(side), [])]


@component
def ridge_mark():
    """The pencil line on a half-roof's 1x6, 6 1/4" from its front end, down
    its inner face (the one the other half's 1x6 meets) and across its top
    (frame-completion.md:92): a sliver standing off the board, so it draws as
    a line. Its origin is on that face, at the board's bottom."""
    from .roof import RIDGE_BOARD_BOTTOM, RIDGE_TOP, RIDGE_BOARD
    h = RIDGE_TOP - RIDGE_BOARD_BOTTOM
    return [Box(0.02, 0.04, h, align=(Align.MAX, Align.CENTER, Align.MIN)),
            Pos(-0.02, 0, h) * Box(0.02 + thickness(RIDGE_BOARD), 0.04, 0.02, align=(Align.MIN, Align.CENTER, Align.MIN))], []


def ridge_marks():
    """The right half-roof's mark, where it lines up with the front triangle's
    outer face (as installed, it does)."""
    from .roof import RIDGE_BOARD_BOTTOM, RIDGE_X
    return [(ridge_mark, Location((RIDGE_X, PLATFORM_LENGTH, WALL_TOP + RIDGE_BOARD_BOTTOM)), [])]


RIDGE_SCREWS_IN = 4  # the columns of screws, in from the bay's rafters
RIDGE_SCREWS_STAGGER = 0.4  # a column's two screws, off its line (so a top-down view shows both)


def ridge_screws(bay, flip=False):
    """4 short screws through the ridge boards across a bay (an index into
    roof.bays()), driven from the left (or, flipped, the right): two columns
    RIDGE_SCREWS_IN from the rafters, at the boards' quarter and three-quarter
    marks, each column's pair staggered RIDGE_SCREWS_STAGGER."""
    from .roof import RIDGE_BOARD, RIDGE_TOP, bays
    a, b = bays()[bay]
    inset = min(RIDGE_SCREWS_IN, (b - a) / 4)  # (a narrow end bay: its columns a quarter in)
    rot = (0, 90, 0) if flip else (0, -90, 0)
    x = 47.896 if flip else 48.136
    # SketchUp's screw stands off its origin by SKP_SCREW_HEAD in X and Y; turned
    # on its side, that's Z (down the page for the unflipped one) and Y
    dz, dy0 = (-SKP_SCREW_HEAD[0] if flip else SKP_SCREW_HEAD[0]), -SKP_SCREW_HEAD[1]
    top = WALL_TOP + RIDGE_TOP
    out = []
    for y in (a + inset, b - inset):
        for quarter, stagger in ((1, RIDGE_SCREWS_STAGGER), (3, -RIDGE_SCREWS_STAGGER)):
            z = top - quarter * width(RIDGE_BOARD) / 4
            out.append((screw_short, Location((x, y + stagger + dy0, z + dz), rot), [] if flip else ["mirror"]))
    return out


LAG_CLAMP = (bar_clamp, Location((16.233, 101.264, 91.312), (0, -90, -132.701)), ["mirror"])

BIRD_BLOCK_SCREWS = [(screw_long, Location((2.203, 133.748, 97.257), (180, 0, -180)), []),
                     (screw_long, Location((2.141, 124.771, 97.25), (-180, 0, 180)), [])]

VENT_GUIDE = (vent_guide_board, Location((57.661, 149.969, 114.269), (0, 0, -180)), [])
VENT_GUIDE_CLAMPS = [
    (bar_clamp, Location((45.4, -18.97, 116.504), (-90, 0, -70.787)), []),
    (bar_clamp, Location((45.4, 162.702, 116.504), (90, 0, -109.213)), ["mirror"]),
    (bar_clamp, Location((59.335, 88.335, 111.623), (71.784, -41.891, -116.236)), ["mirror"]),
]
VENT_CLAMP = (bar_clamp, Location((48.419, 24.743, 98.71), (0, 0, -180)), ["mirror"])
VENT_SCREWS = [(screw_short, Location((49.186, y, 114.372), (90, 90, -180)), []) for y in (6.339, 13.214, 22.026)]
VENT_SCREWS_TO_ALIGN = [(screw_short, Location((56.67, y, 105.097), (90, 90, -180)), []) for y in (6.566, 13.441, 22.253)]

# The crews, where SketchUp's 2D silhouettes stood (their feet), and
# whether mirrored: raising the right half, and the left.
PEOPLE = {
    "right": [((23.781, 173.567, 64.731), True), ((22.781, -25.495, 65.731), True), ((68.394, 73.759, 42.75), True),
                      ((132.052, 71.987, -2.002), False), ((132.052, 108.362, -2.002), False),
                      ((132.052, 34.216, -2.002), False), ((115.698, -15.957, -2.002), False),
                      ((110.753, 163.57, -2.002), True), ((197.526, 142.06, -2.002), False),
                      ((197.472, 8.607, -1.989), False)],
    "left": [((-42.89, 34.216, -2.002), False), ((-42.89, 71.987, -2.002), False), ((-42.89, 108.362, -2.002), False),
             ((60.526, 173.567, 64.731), False), ((61.526, -25.495, 65.731), False), ((15.914, 73.759, 42.75), False),
             ((-108.311, 142.06, -2.002), False), ((-26.453, 156.471, -2.002), False),
             ((-31.39, -15.957, -2.002), False), ((-108.365, 8.607, -1.989), False)],
}


def placed(entries):
    """Shapes for (component, placement, mods) entries."""
    from .common import key
    return [loc * c.shape(frozenset(), key(mods)) for c, loc, mods in entries]


def bracket_screws(side="left", end="front"):
    """The three galvanized hex-head screws down through a roof bracket's flat
    leg (its holes) into the structural triangle (roof-blocking.md "Secure
    Brackets")."""
    from .roof import (ANGLE_PLATE, ANGLE_PLATE_FROM_TIP, ANGLE_PLATE_GAUGE, ANGLE_PLATE_HOLE_OUT, ANGLE_PLATE_HOLES,
                       RAFTER, SLOPE, TIP_U)
    length = ANGLE_PLATE[0]
    if end == "front":
        plate = SLOPE * Pos(TIP_U - ANGLE_PLATE_FROM_TIP[0], RAFTER_Y[-2] + RAFTER, 0)
    else:
        plate = SLOPE * Pos(TIP_U - ANGLE_PLATE_FROM_TIP[1], RAFTER_Y[1], 0) * Rot(Z=180)
    mods = HALF_ROOFS[side][1]
    head_under = SKP_HEX_HEAD[2] - HEX_HEAD_HEIGHT - FLANGE  # the head's flange, up from SketchUp's screw's origin
    out = []
    for hx in ANGLE_PLATE_HOLES:
        # SketchUp's hex screw stands on its tip, its axis SKP_HEX_HEAD off its
        # origin; its head sits on the plate (in the left half's frame)
        screw = HALF_ROOFS["left"][0] * plate * Pos(-length + hx - SKP_HEX_HEAD[0], ANGLE_PLATE_HOLE_OUT - SKP_HEX_HEAD[1],
                                                     ANGLE_PLATE_GAUGE - head_under)
        if mods:  # the right half: the left's, mirrored across the ridge
            p, d = screw.position, screw.z_axis.direction
            screw = Location(Plane((2 * RIDGE_X - p.X, p.Y, p.Z), z_dir=(-d.X, d.Y, d.Z)))
        out.append((hex_screw, screw, mods))
    return out


BRACKET_SCREWS = bracket_screws("left") + bracket_screws("right")  # the front two brackets' (the ones shown)
