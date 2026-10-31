"""Frame completion and roof blocking (post-tilt-up/frame-completion.md and
roof-blocking.md): the house between tilt-up and roofing, the half-roofs on
their way up, and the tools and props for it: step ladders, the funky boards
that push a half-roof up, bar clamps, screws and lag bolts.

Frame: the house's (house.py). The loose things' places at each stage (the
half-roofs going up, ladders, funky boards, people, clamps) are where
the SketchUp model's tilt-up scenes had them,
converted to the house's frame: SKETCHUP_HOUSE is where that model had the
house.
"""

import math

from build123d import (
    Align, Axis, Box, Cone, Cylinder, Location, Plane, Polygon, Pos, RegularPolygon, Rot, Vector, extrude
)

from .lumber import TwoByFour, thickness, width
from .common import CORNER, component, driven, key
from .house import WALL_TOP
from .platform_assembly import PLATFORM_LENGTH, PLATFORM_WIDTH, platform
from .roof import (
    PLUMB_DEPTH, RAFTER_DEPTH, RAFTER_Y, RIDGE_BOARD, RIDGE_BOARD_BOTTOM, RIDGE_TOP, RIDGE_X, ROOF_PITCH, SIDING_FACE,
    SLOPE, TAIL_U, TIP_X, VENT_BLOCK_HEIGHT, VENT_BLOCK_THICKNESS, angle_plate, bird_block, bird_length, bored_rafter,
    cross_block, eave_board, half_roof, rafter, ridge_board, underside, vent_block, vent_length, wall_bays
)
from .gables import TRI_HALF, structural_triangle
from .walls import WALL_DEPTH, front_wall, rear_wall, side_wall

# Where the SketchUp model had the house: turned end for end (its front wall
# at low Y), the deck's top at 14 3/8" (the manuals' platform is 2" lower).
SKETCHUP_HOUSE = Pos(103.7285, 164.0849, 14.375 - 11.75) * Rot(Z=180)


# ── the house at frame completion ──────────────────────────────────────────

def walls():
    """The platform and the four walls, as tilted up: (component, placement, mods)."""
    from .platform_assembly import DECK
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

# The half-roofs on the way up (frame-completion.md "Raise Half-Roofs"): a
# half is raised leaning against the side wall it goes on, eave board down,
# RAISE_LEAN from level: set on the floor against the wall (stage 1), lifted
# by the crew (2), pushed up on the funky boards (3). A stage is where its
# bottom edge (the rafter tails' outer corner, under the eave board) is, out
# from the siding and up from the ground; the stage's funky boards are under
# that edge (see funky_boards; stage 4: still under the installed half).
RAISE_LEAN = 75  # degrees from level
RAISE_STAGES = {1: (30, 0), 2: (30, 48), 3: (24, 76)}  # stage -> (out, up): "about 4 feet off the floor", then up the wall
TAIL_EDGE = (SLOPE * Pos(TAIL_U, 0, 0)).position  # the rafter tails' bottom outer edge, in the roof's frame (left half)


def _mirrored_x(x):
    """x mirrored across the ridge, for the right half."""
    return 2 * RIDGE_X - x


def raised(side, stage):
    """The move, in the house's frame, taking a half-roof from its installed
    place to a raising stage."""
    from .tilt_up import GROUND  # (tilt_up imports this module's clamp)
    out, up = RAISE_STAGES[stage]
    lean = RAISE_LEAN - ROOF_PITCH  # past its installed slope
    edge = ROOF * Pos(*TAIL_EDGE)  # the half's bottom edge, installed
    if side == "left":
        at, pivot, turn = (-(SIDING_FACE + out), 0, GROUND + up), edge.position, -lean
    else:
        at, pivot, turn = (PLATFORM_WIDTH + SIDING_FACE + out, 0, GROUND + up), Vector(_mirrored_x(edge.position.X), 0, edge.position.Z), lean
    return Pos(*at) * Rot(Y=turn) * Pos(-pivot.X, -pivot.Y, -pivot.Z)


def on_half(side, x, y, z):
    """(placement, mods) for a part at (x, y, z) in the left half-roof's
    frame, on the given half (mirrored across the ridge for the right)."""
    loc, mods = HALF_ROOFS[side]
    return loc * Pos(-x if mods else x, y, z), mods


def half_roof_at(side, stage=None):
    """(component, placement, mods) for a half-roof, installed or at a raising stage."""
    loc, mods = HALF_ROOFS[side]
    if stage is not None:
        loc = raised(side, stage) * loc
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


# Each fastener stands with its head's top at the origin, pointing down -Z;
# common.driven() places one by its head and the direction it's driven.

@component
def screw_long():
    return screw_like(*SCREW_LONG, 0.12), []


@component
def screw_short():
    return screw_like(*SCREW_SHORT, 0.1), []


HEX_HEAD_HEIGHT = 0.2


@component
def hex_screw():
    return screw_like(*HEX_SCREW, HEX_HEAD_HEIGHT, hex=True), []


@component
def lag_bolt():
    """Head up, its top at the origin; into the wall's top plate below."""
    return screw_like(*LAG_BOLT, 0.25, hex=True), []


def lag_bolts(side="left", rafters=None, lift=0):
    """Lag bolts in the bored rafters' counterbores (roof-blocking.md
    "Install Magic Stud Lag Bolts"), by index into roof.RAFTER_Y; `lift`
    inches up, before they're driven home."""
    from math import cos, radians
    from .roof import (
        EAVE_BOARD, LAG_COUNTERBORE, LAG_COUNTERBORE_DEPTH, RAFTER, RAFTER_DEPTH, ROOF_PITCH, SLOPE, TAIL_U,
        UNBORED
    )
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


# ── the ladders and the funky boards, where the crew has them ──────────────

LADDER_OUT = 12  # a 12' ladder's near feet from the end wall's siding
STOOL_FROM_WALL = 12  # the step stool's near feet from the side wall's framing, inside
STOOL_Y = 60  # the stool's middle along the house: in a stud bay, not under a stud ("not aligned with a stud")


def ladders(side):
    """"12' ladder at each end" of the house, spread along the end wall and
    centered on it, its steps on the far side from the half-roof being raised
    (so the climber faces it), feet on the ground; and the "3-step ladder
    inside the home", the stool, on the deck STOOL_FROM_WALL in from that
    side's wall at STOOL_Y, climbing toward the wall."""
    from .platform_assembly import DECK
    from .tilt_up import GROUND
    center = PLATFORM_WIDTH / 2 - LADDER_SPREAD / 2  # the ladder's rear leg, centered on the house
    turned = Rot(Z=180) if side == "right" else Rot()  # steps toward -X for the right half, +X for the left
    shift = Pos(LADDER_SPREAD, LADDER_WIDTH[0], 0) if side == "right" else Pos()  # (turned about its rear-leg corner)
    out = []
    for y in (-(SIDING_FACE + LADDER_OUT + LADDER_WIDTH[0]), PLATFORM_LENGTH + SIDING_FACE + LADDER_OUT):
        out.append((step_ladder, Pos(center, y, GROUND) * shift * turned, []))
    wide, deep, _ = STOOL
    if side == "right":  # its stepped leg (frame Y = 0) toward the house's middle, rising toward the wall
        stool = Pos(PLATFORM_WIDTH - WALL_DEPTH - STOOL_FROM_WALL - deep, STOOL_Y + wide / 2, DECK) * Rot(Z=-90)
    else:
        stool = Pos(WALL_DEPTH + STOOL_FROM_WALL + deep, STOOL_Y - wide / 2, DECK) * Rot(Z=90)
    out.append((step_stool, stool, []))
    return out


FUNKY_LEAN = {3: 45, 4: 15}  # degrees from plumb where the pole can't reach the ground ("push up at a 45° angle")
FUNKY_STANDING_OUT = 108  # at stage 1 they stand upright on the ground, this far out from the siding
FUNKY_BOARD_Y = (2, 134)  # along the house: one near the rear end of the eave board, one 15" from its front end


def funky_lean(stage):
    """A funky board's lean from plumb at a raising stage: its foot on the
    ground and its head under the half-roof's bottom edge where the pole
    reaches, else held up by its wielder at FUNKY_LEAN."""
    from .tilt_up import GROUND
    high, _ = FUNKY_BOARD
    up = RAISE_STAGES[stage][1] if stage in RAISE_STAGES else WALL_TOP + TAIL_EDGE.Z - GROUND
    return math.degrees(math.acos(up / high)) if up <= high else FUNKY_LEAN[stage]


def funky_boards(side, stage):
    """The two funky boards at a raising stage: (component, placement, mods).
    At stage 1 standing on the ground beside the half-roof; after that their
    heads under its bottom edge, leaning funky_lean() from plumb, feet
    toward the crew."""
    from .tilt_up import GROUND
    high, head = FUNKY_BOARD
    top = Pos(-head / 2, -thickness("2x4") / 2, -high)  # the board's frame, from its head's top center
    sign = -1 if side == "left" else 1  # outward from the house
    out = []
    for y in FUNKY_BOARD_Y:
        if stage == 1:
            x = -(SIDING_FACE + FUNKY_STANDING_OUT) if side == "left" else PLATFORM_WIDTH + SIDING_FACE + FUNKY_STANDING_OUT
            out.append((funky_board, Pos(x, y, GROUND + high) * top, []))
        else:
            comp, loc, mods = half_roof_at(side, None if stage == 4 else stage)
            edge = loc * Pos(-TAIL_EDGE.X if mods else TAIL_EDGE.X, y, TAIL_EDGE.Z)  # (the right half is mirrored in its own frame)
            out.append((funky_board, Pos(*edge.position) * Rot(Y=-sign * funky_lean(stage)) * top, []))
    return out


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

# The screws preset in a structural triangle's base (frame-completion.md
# "Structural Triangles"), on the base's top, in two rows TRIANGLE_ROWS in
# from its faces: in each center bay (between an E stud and a D stud) two
# toe screws, TOE_IN from the E stud's outer face and TOE_IN from the D
# stud's inner face, each tilted TOE_ANGLE toward its stud; in each outer
# bay two screws, OUTER_IN beyond the D stud and OUTER_APART apart, tilted
# OUTER_ANGLE in from the inside row; and two straight down through each
# side's foot.
TRIANGLE_ROWS = (3/4, WALL_DEPTH - 3/4)
TOE_IN, TOE_ANGLE = 1 + 3/4, 33  # inches from the stud's face; degrees from plumb
OUTER_IN, OUTER_APART, OUTER_ANGLE = 1 + 1/4, 2 + 5/8, 48
FOOT_SCREW_IN = 3  # from the side's outer foot


def triangle_screws(at=None):
    """The 16 screws in the rear triangle's base, in the house's frame (or a
    triangle placed by `at`)."""
    from .gables import TRI_BASE, TRI_BASE_END, TRI_D, TRI_E, TRI_SIDE_FOOT
    at = at or ROOF * Pos(RIDGE_X, 0, 0)
    stud = thickness("2x4")
    top = TRI_BASE  # the base's top, in the triangle's frame
    toe = (math.sin(math.radians(TOE_ANGLE)), math.cos(math.radians(TOE_ANGLE)))
    out = []
    for sign in (-1, 1):  # each half, by the distance from the center
        for x in (TRI_E + stud + TOE_IN, TRI_D - TOE_IN):  # outside the E stud, inside the D stud
            tilt = -sign if x < TRI_D / 2 else sign  # toward the stud: in toward E, out toward D
            for y in TRIANGLE_ROWS:
                out.append(((sign * x, y, top), (tilt * toe[0], 0, -toe[1])))
        for x in (TRI_D + stud + OUTER_IN, TRI_D + stud + OUTER_IN + OUTER_APART):  # the outer bay
            a = math.radians(OUTER_ANGLE)
            out.append(((sign * x, TRIANGLE_ROWS[1], top), (0, -math.sin(a), -math.cos(a))))
        for y in TRIANGLE_ROWS:  # the side's foot
            out.append(((sign * (TRI_BASE_END - TRI_SIDE_FOOT + FOOT_SCREW_IN), y, top), (0, 0, -1)))
    def in_house(head, d):  # the head and direction, taken into the house's frame
        return tuple((at * Pos(*head)).position), tuple((at * Location(Plane((0, 0, 0), z_dir=d))).z_axis.direction)
    return [(screw_long, driven(*in_house(head, d)), []) for head, d in out]


TRIANGLE_SCREWS = triangle_screws()


def corner_screws():
    """5 #10 x 3" screws in each wall corner, where the tilt-up's nails went
    (frame-completion.md "Secure Walls")."""
    from .tilt_up import corner_nailing
    return [(screw_long, driven(head, d), []) for corner in ("back_rhs", "back_lhs", "front_lhs", "front_rhs")
            for head, d in corner_nailing(corner)]


CORNER_SCREWS = corner_screws()


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
    (frame-completion.md): a sliver standing off the board, so it draws as
    a line. Its origin is on that face, at the board's bottom."""
    from .roof import RIDGE_BOARD, RIDGE_BOARD_BOTTOM, RIDGE_TOP
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
    # the heads on the near board's face, driven across the ridge
    side = 1 if flip else -1
    x, direction = RIDGE_X + side * thickness(RIDGE_BOARD), (-side, 0, 0)
    top = WALL_TOP + RIDGE_TOP
    out = []
    for y in (a + inset, b - inset):
        for quarter, stagger in ((1, RIDGE_SCREWS_STAGGER), (3, -RIDGE_SCREWS_STAGGER)):
            z = top - quarter * width(RIDGE_BOARD) / 4
            out.append((screw_short, driven((x, y + stagger, z), direction), []))
    return out


LAG_CLAMP = (bar_clamp, Location((16.233, 101.264, 91.312), (0, -90, -132.701)), ["mirror"])

BIRD_BLOCK_SCREWS_IN = 3  # from the block's ends


def bird_block_screws(side="left", bay=5):
    """Two #10 x 3" screws up through the side wall's top plate into a bird
    block (roof-blocking.md "Install Bird Blocks"), their heads under the
    plate, BIRD_BLOCK_SCREWS_IN from the block's ends."""
    (comp, loc, mods), = bird_blocks(side, [bay])
    bb = (loc * comp.shape(frozenset(), key(mods))).bounding_box()
    under = WALL_TOP - thickness("2x4")  # the top plate's underside
    x = (bb.min.X + bb.max.X) / 2
    return [(screw_long, driven((x, y, under), (0, 0, 1)), [])
            for y in (bb.min.Y + BIRD_BLOCK_SCREWS_IN, bb.max.Y - BIRD_BLOCK_SCREWS_IN)]


BIRD_BLOCK_SCREWS = bird_block_screws()

VENT_GUIDE = (vent_guide_board, Location((57.661, 149.969, 114.269), (0, 0, -180)), [])
VENT_GUIDE_CLAMPS = [
    (bar_clamp, Location((45.4, -18.97, 116.504), (-90, 0, -70.787)), []),
    (bar_clamp, Location((45.4, 162.702, 116.504), (90, 0, -109.213)), ["mirror"]),
    (bar_clamp, Location((59.335, 88.335, 111.623), (71.784, -41.891, -116.236)), ["mirror"]),
]
VENT_CLAMP = (bar_clamp, Location((48.419, 24.743, 98.71), (0, 0, -180)), ["mirror"])
VENT_SCREWS_AT = (1, 1/2, 5/6)  # along the block: an inch from the rear end, the middle, five sixths along


def vent_block_screws(side="right", bay=0, offset=(0, 0)):
    """The three screws preset in a vent block (roof-blocking.md "Install
    Ridge Vent Blocks"), on its outer face at mid-height, driven into the
    ridge board; `offset` as vent_blocks()'s, for a block not yet pushed up."""
    (comp, loc, mods), = vent_blocks(side, [bay], offset=offset)
    bb = (loc * comp.shape(frozenset(), key(mods))).bounding_box()
    outer, direction = (bb.max.X, (-1, 0, 0)) if side == "right" else (bb.min.X, (1, 0, 0))
    z = (bb.min.Z + bb.max.Z) / 2
    ys = (bb.min.Y + VENT_SCREWS_AT[0], (bb.min.Y + bb.max.Y) / 2, bb.min.Y + (bb.max.Y - bb.min.Y) * VENT_SCREWS_AT[2])
    return [(screw_short, driven((outer, y, z), direction), []) for y in ys]


VENT_SCREWS = vent_block_screws()
VENT_SCREWS_TO_ALIGN = vent_block_screws(offset=VENT_BLOCK_START)

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
    from .roof import (
        ANGLE_PLATE, ANGLE_PLATE_EDGES, ANGLE_PLATE_GAUGE, ANGLE_PLATE_HOLES, ANGLE_PLATE_HOLE_OUT, RAFTER, SLOPE,
        TIP_U
    )
    length = ANGLE_PLATE[0]
    if end == "front":
        plate = SLOPE * Pos(TIP_U - ANGLE_PLATE_EDGES[0], RAFTER_Y[-2] + RAFTER, 0)
    else:
        plate = SLOPE * Pos(TIP_U - ANGLE_PLATE_EDGES[1], RAFTER_Y[1], 0) * Rot(Z=180)
    out = []
    for hx in ANGLE_PLATE_HOLES:
        # the head on the plate's flat leg over its hole, driven down through it (in the left half's frame)
        at = HALF_ROOFS["left"][0] * plate * Pos(-length + hx, ANGLE_PLATE_HOLE_OUT, ANGLE_PLATE_GAUGE)
        head, d = at.position, -at.z_axis.direction
        if HALF_ROOFS[side][1]:  # the right half: the left's, mirrored across the ridge
            head, d = Vector(2 * RIDGE_X - head.X, head.Y, head.Z), Vector(-d.X, d.Y, d.Z)
        out.append((hex_screw, driven(tuple(head), tuple(d)), []))
    return out


BRACKET_SCREWS = bracket_screws("left") + bracket_screws("right")  # the front two brackets' (the ones shown)
