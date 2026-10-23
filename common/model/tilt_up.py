"""The tilt-up (tilt-up/tilt-up.md): each wall built on its jig beside the
platform, tilted up onto the platform and pushed into place, then braced,
clamped and nailed to its neighbors; and the crew doing it.

Everything here is in the house's frame (see house.py). Each wall's stages
are motions of the wall from its place in the house (a slide, or a turn about
one axis and a slide), as the SketchUp model the manual's pictures were drawn
from (SketchUp/Tiny_Home_Model_-_with_interiors.skp, "Tilt Up" group) had
them. The platform stands on its stands there: the ground, where the jigs and
the crew stand, is GROUND below the bottom of the skids.
"""

import math

from .common import *
from .house import house
from .platform import PLATFORM_LENGTH, PLATFORM_WIDTH
from .roof import SIDING_FACE
from .walls import DOOR_X, STUD, WALL_DEPTH, front_wall, rear_wall, side_wall

GROUND = -13.3  # where the jigs and the crew stand (the platform is up on stands)


def in_house(wall, n=0):
    """Where the house puts a wall (the n-th placement of that component)."""
    return [loc for comp, loc, _, _ in house()[1] if comp is wall][n]


# The walls, as the manual calls them (looking at the platform from its rear).
WALLS = {
    "rhs": (side_wall, 0),  # the door-side side wall
    "lhs": (side_wall, 1),
    "back": (rear_wall, 0),
    "front": (front_wall, 0),
}

# wall -> stage -> motion from its place in the house
STAGES = {
    "rhs": {
        "on_jig": Pos(-208.11, -2.43, 37.16) * Rot(Y=90),  # lying outside face up on its jig
        "tilted": Pos(-71.66, -2.43, 12.35) * Rot(Y=35.8),
        "upright": Location(),
    },
    "lhs": {
        "on_jig": Pos(298.37, -2.43, -58.85) * Rot(Y=-90),
        "tilted": Pos(87.4, -2.43, -48.57) * Rot(Y=-39.2),
        "gap": Pos(0, 34.44, 0),  # upright, short of the back wall (to clear hands)
        "upright": Location(),
    },
    "back": {
        "on_jig": Pos(208.47, 29.35, 37.03) * Rot(X=-90),
        "carried": Pos(206.22, -140.61, 37.03) * Rot(X=-90),  # off the jig
        "at_platform": Pos(-1.54, -140.61, 37.03) * Rot(X=-90),
        "tilted": Pos(3.5, -79.33, 12.6) * Rot(X=-36.05),
        "gap": Pos(19.69, 0, 0),  # upright, short of the side wall
        "upright": Location(),
    },
    "front": {
        "on_jig": Pos(-183.37, 144.1, -106.91) * Rot(X=90),
        "carried": Pos(-183.49, 259.04, -106.91) * Rot(X=90),
        "at_platform": Pos(-0.31, 242.81, -106.16) * Rot(X=90),
        "tilted": Pos(0.05, 67.89, -68.9) * Rot(X=29.71),
        "upright": Location(),
    },
}


def wall_at(wall, stage):
    """(component, placement) of a wall at one of its stages."""
    comp, n = WALLS[wall]
    return comp, STAGES[wall][stage] * in_house(comp, n)


# ── the jigs ───────────────────────────────────────────────────────────────

JIG_HEIGHT = 35
SIDE_JIG = (87, 144)  # a side wall's jig: as big as the wall
END_JIG = (89, 87)  # the end walls' jig, under the middle of the wall

# minimum corners
JIGS = {
    "rhs": (Pos(-196.37, -2.5, GROUND), SIDE_JIG),
    "lhs": (Pos(199.62, -2.5, GROUND), SIDE_JIG),
    "back": (Pos(211.97, 41.1, GROUND), END_JIG),
    "front": (Pos(-179.86, 45.36, GROUND), END_JIG),
}


@component
def side_wall_jig():
    """The table a side wall is built on (drawn as a plain block)."""
    return [Box(*SIDE_JIG, JIG_HEIGHT, align=CORNER)], []


@component
def end_wall_jig():
    return [Box(*END_JIG, JIG_HEIGHT, align=CORNER)], []


def jig_at(wall):
    loc, size = JIGS[wall]
    return (side_wall_jig if size == SIDE_JIG else end_wall_jig), loc


# ── bracing, clamping, nailing ─────────────────────────────────────────────

BRACE = 50.5  # a 2x4, square-cut
BRACE_ANGLE = 70.8  # from level
BRACE_FOOT = (18.3, 0.58)  # the middle of its foot, in its frame (X, Z)
BRACE_AT = Pos(-0.62, 144.07, 7.72)  # just off the platform's front end, by the rhs wall


@component
def wall_brace():
    """A 2x4 from the platform's end up to the rhs wall, holding it upright
    until the back wall is on: in the XZ plane (1 1/2" thick along +Y),
    leaning toward -X."""
    a = math.radians(BRACE_ANGLE)
    along, across = (-math.cos(a), math.sin(a)), (math.sin(a) / 2 * width("2x4"), math.cos(a) / 2 * width("2x4"))
    fx, fz = BRACE_FOOT
    tx, tz = fx + BRACE * along[0], fz + BRACE * along[1]
    corners = [(fx - across[0], fz - across[1]), (fx + across[0], fz + across[1]),
               (tx + across[0], tz + across[1]), (tx - across[0], tz - across[1])]
    return [extrude(Plane.XZ * Polygon(*corners, align=None), -thickness("2x4"))], []


# The corner clamps (one-handed bar clamps, post_tilt_up's). At the three
# corners away from the door, the fixed jaw sits in the side wall's
# California corner (the pocket between its siding and its flat stud), its
# pad on the flat stud; the head clamps the end wall's end stud from inside;
# the bar and its tail run inside the house along the end wall. At the door
# corner the fixed jaw stands in the doorway, its pad on the jamb stud; the
# bar runs outside the siding, the head clamps the side wall's exterior and
# the tail sticks out past it.
CORNER_CLAMP_OPENING = STUD + STUD  # the flat stud and the end wall's end stud
DOOR_CLAMP_OPENING = WALL_DEPTH + DOOR_X + SIDING_FACE  # the jamb stud's doorway face to the side wall's siding


@component
def bar_clamp():
    from .post_tilt_up import _bar_clamp
    return _bar_clamp(CORNER_CLAMP_OPENING)


@component
def door_clamp():
    from .post_tilt_up import _bar_clamp
    return _bar_clamp(DOOR_CLAMP_OPENING)


NAIL = 4.5


@component
def nail():
    """A framing nail, its head at the origin, pointing along +Z (as
    SketchUp's stood, preset where it's to be driven)."""
    return [Cylinder(0.08, NAIL, align=(Align.CENTER, Align.CENTER, Align.MIN)),
            Cylinder(0.25, 0.06, align=(Align.CENTER, Align.CENTER, Align.MIN))], []


def frame(origin, x_dir, z_dir):
    return Location(Plane(origin, x_dir=x_dir, z_dir=z_dir))


def _clamp_frame(x_fixed, y_pads, z, out, inward, reach):
    """A clamp with its fixed pad's face at x_fixed (the head `out` along X
    from it), its pads centered at y_pads, z, its jaws reaching `reach`
    (+1 or -1 along Y) from its bar to the pads."""
    from .post_tilt_up import CLAMP_BAR, CLAMP_BAR_Y, CLAMP_JAW_TOP
    pads = (CLAMP_JAW_TOP + 12.4) / 2  # the pads' middle, up the jaws from the bar
    x_dir, z_dir = (-out, 0, 0), (0, reach, 0)  # the bar's fixed end away from the head
    y_up = -z_dir[1] * x_dir[0]  # Y (= Z x X) up or down
    return frame((x_fixed + out * (CLAMP_BAR[1] - 0.35), y_pads - reach * pads, z - y_up * CLAMP_BAR_Y), x_dir, z_dir)


def corner_clamp(side, y_wall, z, inward):
    """A clamp across a corner away from the door, at height z: `side` the
    side wall's X (0 or PLATFORM_WIDTH), y_wall the end wall's outer face,
    `inward` the way into the house from it."""
    out = -1 if side == 0 else 1  # which way is outside the side wall
    pocket = side - out * (WALL_DEPTH - STUD)  # the flat stud's face in the California corner
    pads_y = y_wall + inward * (STUD + WALL_DEPTH / 2)  # the pocket's middle, along the side wall
    return (bar_clamp, _clamp_frame(pocket, pads_y, z, -out, inward, -inward))


def door_clamp_at(z):
    """The clamp at the door corner, at height z."""
    jamb = WALL_DEPTH + DOOR_X  # the jamb stud's doorway face
    return (door_clamp, _clamp_frame(jamb, PLATFORM_LENGTH - WALL_DEPTH / 2, z, -1, -1, -1))


# The clamps and nails at each corner: (component, placement); the clamps
# at the heights the SketchUp model had them
CORNERS = {
    "back_rhs": [
        *[corner_clamp(0, 0, z, 1) for z in (92.78, 37.91)],
        *[(nail, frame((9.1, 3.2, z), (0.42, -0.91, 0), (-0.91, -0.42, 0))) for z in (94.94, 75.94, 56.33, 39.39, 19.02)],
    ],
    "back_lhs": [
        *[corner_clamp(PLATFORM_WIDTH, 0, z, 1) for z in (92.44, 38.19)],
        *[(nail, frame((86.9, 4.5, z), (-0.42, -0.91, 0), (0.91, -0.42, 0))) for z in (94.62, 75.62, 57.13, 40.2, 20.52)],
    ],
    "front_lhs": [
        *[corner_clamp(PLATFORM_WIDTH, PLATFORM_LENGTH, z, -1) for z in (89.8, 38.24)],
        *[(nail, frame((87.2, 139.5, z), (-0.42, 0.91, 0), (0.91, 0.42, 0))) for z in (94.94, 75.94, 57.89, 39.7, 18.27)],
    ],
    "front_rhs": [
        *[door_clamp_at(z) for z in (84.7, 18.39)],
        *[(nail, frame((9.8, 137.7, z), (0.29, 0.96, 0), (-0.96, 0.29, 0))) for z in (94.05, 70.24, 54.06, 34.56, 18.71)],
    ],
}


BRACE_NAILS = [(nail, frame(p, (1, 0, 0), (0, -1, 0))) for p in ((1.73, 151.06, 53.21), (16.81, 151.06, 9.82))]
IMPACT_DRIVER_AT = (0.21, 161.48, 45.69)


@component
def funky_board_16():
    """Funky board #16: a 2x4 across the front wall's outside, low down, to
    carry and tilt it by (it spans the doorway)."""
    return [TwoByFour(96, along="X", wide="Z")], []


FUNKY_BOARD_16 = Pos(0, 144.38, 22.85)  # with the front wall upright in the house


# ── the crew ───────────────────────────────────────────────────────────────
# Cut-out silhouettes, as SketchUp's "face me" people: the figures turn them
# to face the camera.

PERSON = 1/8  # thickness of the cut-out


def silhouette(loops):
    face = Polygon(*loops[0], align=None)
    for hole in loops[1:]:
        face -= Polygon(*hole, align=None)
    return extrude(Plane.XZ * face, -PERSON / 2, both=True)


@component
def person_arms_up():
    """On the platform, arms up, catching a wall as it tilts up."""
    return [silhouette(ARMS_UP)], []


@component
def person_hands_out():
    """At a jig, lifting."""
    return [silhouette(HANDS_OUT)], []


# (x, y, z) of each person's feet; "mirror" for the figure drawn flipped (the
# crews at the jigs face the wall they're lifting)
CREW = {
    "rhs_jig": [(x, y, -12.92, True) for x in (-199.06, -167.18, -132.31) for y in (158.34, -23.14)],
    "rhs_platform": [(16.84, y, 11.75, True) for y in (21.56, 65.43, 112.81)],
    "back_platform": [(x, 12.24, 11.75, True) for x in (29.24, 57.42, 82.61)],
    "back_jig": [(x, y, -16.52, m) for x, m in ((190.32, True), (313.9, False)) for y in (45.87, 79.87, 113.87)],
    "back_carried": [(x, y, -16.52, m) for x, m in ((188.07, True), (316.7, False)) for y in (-124.09, -90.09, -59.28)],
    "back_at_platform": [(x, y, -16.52, m) for x, m in ((-19.69, True), (108.94, False)) for y in (-124.09, -90.09, -59.28)],
    "lhs_jig": [(x, y, -12.92, True) for x in (218.67, 250.55, 285.42) for y in (158.34, -23.14)],
    "lhs_platform": [(73.41, y, 11.75, False) for y in (21.56, 65.43, 112.81)],
    "front_platform": [(24.8, 131.55, 11.75, False), (45.92, 135.61, 11.75, False), (73.05, 135.61, 11.75, False)],
    "front_jig": [(x, y, -16.52, m) for x, m in ((-201.51, False), (-72.5, True)) for y in (62.77, 93.59, 127.59)],
    "front_carried": [(x, y, -16.52, m) for x, m in ((-201.64, False), (-72.62, True)) for y in (177.71, 208.52, 242.52)],
    "front_at_platform": [(x, y, -15.78, m) for x, m in ((-18.46, False), (110.69, True)) for y in (161.48, 192.29, 226.29)],
}
CREW_KIND = {k: (person_arms_up if "platform" in k and "at_platform" not in k else person_hands_out) for k in CREW}


ARMS_UP = (  # outline, then holes: (x, z) inches, feet at the origin
    ((-3.4, 0.1), (-3.2, 0), (0, 0), (0.4, 0.5), (0.8, 1), (0.9, 2.4), (1, 3.8), (1.2, 4.5), (1.6, 5.2),
     (1.8, 5.2), (1.6, 7), (1.1, 9), (1.1, 11.4), (1, 13.8), (0.8, 15.8), (0.6, 17.7), (0.3, 18.4),
     (0, 19.3), (0.3, 22), (0.8, 24.8), (1.1, 27.3), (1.4, 29.7), (1.5, 30.8), (1.8, 31.5), (2.3, 30.5),
     (2.4, 29), (2.9, 26.6), (3.2, 23.9), (4, 17.9), (4.8, 11.7), (5.3, 8.9), (5.5, 7), (5.1, 6.8),
     (4.8, 6.5), (4.5, 5.4), (4.5, 4.4), (4.6, 4.5), (5, 5.2), (5.2, 5.9), (5.3, 5.5), (5.3, 5.1),
     (4.6, 2.8), (4.5, 0.1), (4.7, 0.1), (4.9, 0), (7.4, 0), (8.9, 1.3), (9.8, 5.8), (9.8, 12.2),
     (9.8, 13.4), (9.7, 14.6), (9.6, 18.1), (8.9, 21.2), (8.9, 21.9), (9, 22.5), (8.7, 27.5), (8.9, 32.5),
     (8.5, 34.6), (7.9, 36.6), (7.8, 37.9), (7.7, 39.1), (7.5, 39.5), (7.2, 39.8), (7.2, 41), (7.5, 42.1),
     (7.3, 44.5), (7.6, 47), (7.9, 48.5), (8.3, 50), (9.6, 51.2), (11, 52.4), (11.8, 53.5), (12.7, 54.5),
     (13.2, 54.5), (13.7, 54.6), (14.3, 55.5), (14.9, 56.4), (15, 57), (15.1, 57.6), (15.5, 57.8),
     (16.1, 58), (16.9, 58.7), (17.6, 59.5), (19.1, 62), (20.6, 64.6), (22.3, 66.2), (23.6, 67.9),
     (23.6, 68.1), (23.3, 69.1), (23.5, 69.9), (23.4, 70.1), (23.1, 70.2), (22.8, 70.4), (23.1, 70.9),
     (23.2, 71.6), (23.1, 71.8), (22.9, 71.7), (22.1, 70.5), (21.2, 69.5), (20.5, 69.2), (20, 68.8),
     (20, 68.5), (20, 68.1), (19.8, 67.4), (19.7, 66.7), (17.5, 64.2), (15.1, 61.9), (14.3, 60.9),
     (13.5, 60), (11.9, 59.6), (10.4, 59.4), (8.6, 57.9), (6.3, 56.9), (4.8, 58), (2.7, 58.1), (3, 59.4),
     (3.5, 60.5), (4, 60.9), (4.3, 61.1), (4.5, 62.2), (4.5, 62.9), (4.4, 63), (4.4, 64.3), (4.3, 64.8),
     (3.5, 66.8), (2.8, 67.4), (2.4, 67.6), (1.8, 67.8), (0.2, 67.8), (-0.8, 67.6), (-1.7, 66.9), (-2, 66.3),
     (-2.5, 65.2), (-2.5, 64.1), (-2.5, 63), (-2.8, 62.6), (-2.8, 61.9), (-1.9, 60.1), (-1.6, 58.3),
     (-2.2, 58), (-2.8, 57.9), (-3.4, 57.1), (-4.4, 56.6), (-6.1, 57.5), (-7.9, 58.4), (-8.6, 59),
     (-9.3, 59.5), (-10.5, 59.6), (-11.4, 59.5), (-13.2, 60.9), (-14.6, 62.6), (-15.9, 63.6), (-17.2, 64.6),
     (-18.2, 65.8), (-19.1, 67.1), (-19.3, 67.7), (-19.4, 68.3), (-21, 69.9), (-22.4, 71.4), (-22.7, 71.4),
     (-22.8, 71.2), (-22.8, 70.9), (-22.1, 70.2), (-21.5, 69.2), (-21.8, 69.2), (-22.1, 69.4), (-22.5, 69.5),
     (-22.7, 69.4), (-22.8, 69.2), (-22.6, 68.1), (-22.8, 67), (-22.7, 66.7), (-17.7, 62.1), (-12.8, 57),
     (-12.7, 56.3), (-12.2, 55.9), (-12.2, 55.3), (-12.1, 54.6), (-10.5, 54.1), (-9.4, 53.1), (-6.7, 50.5),
     (-4.8, 47.3), (-4.7, 46.4), (-4.6, 45.5), (-4, 39.6), (-5.1, 34.1), (-5.4, 30.5), (-5.3, 26.6),
     (-5.4, 24.4), (-5.5, 22.1), (-5.3, 21.1), (-5.1, 20.1), (-5.1, 18.3), (-5.1, 16.5), (-4.4, 14.1),
     (-3.7, 11.8), (-3.6, 11.1), (-3.5, 10.3), (-3, 8.7), (-2.5, 7), (-2.7, 6.2), (-3, 5.2), (-2.7, 5.3),
     (-2.5, 5.2), (-3.4, 2.8),),
)
HANDS_OUT = (  # outline, then holes: (x, z) inches, feet at the origin
    ((7.5, 36.8), (6.3, 43.7), (6.6, 44.2), (6.9, 44.8), (6.9, 44.5), (7.5, 43.5), (8.5, 42.8), (10, 43),
     (11, 43.8), (14.6, 45.6), (17.1, 48.2), (17.1, 48.4), (17, 48.6), (17.2, 48.8), (17.4, 49),
     (17.4, 49.2), (17.2, 49.2), (16.8, 49), (15.9, 48.2), (15, 47.8), (14.9, 47.9), (15.4, 48.6),
     (15.6, 49), (15.2, 49.2), (14.1, 48.1), (12.9, 46.4), (11, 46.2), (9.2, 46), (8.9, 47.9), (8.4, 49.5),
     (8.3, 51.4), (8.2, 53.6), (7.8, 55.6), (7.3, 56.3), (6.7, 56.9), (5.3, 57.3), (4.4, 58.2), (4.8, 58.9),
     (4.5, 59.6), (5, 60.4), (4.8, 61.3), (5.2, 62.3), (5, 63.7), (5.3, 64.5), (5.4, 64.8), (5.6, 64.8),
     (5.7, 64.6), (5.5, 64.4), (5.4, 64.2), (5.3, 63.7), (5.7, 64), (6, 64.8), (5.9, 65.8), (5.5, 66.5),
     (5.2, 67.3), (3.7, 68.9), (1.4, 69.6), (-0.2, 68.7), (-1.7, 67.7), (-1.7, 67.3), (-1.7, 67),
     (-2.1, 65.9), (-2.5, 64.8), (-2.5, 64.3), (-2.4, 63.6), (-3, 62.7), (-3.5, 62), (-3.5, 60.9),
     (-3.4, 59.9), (-3.7, 58.8), (-3.9, 57.6), (-5.7, 56.6), (-6.7, 54.7), (-7.1, 52), (-6.9, 49.3),
     (-7, 49.1), (-8.1, 49.6), (-9.3, 50), (-9.3, 49.8), (-8.6, 49), (-8, 48.3), (-8.3, 48.3), (-9.1, 48.6),
     (-10.2, 48.9), (-10.3, 48.8), (-9.9, 48.3), (-9.5, 47.8), (-9.8, 47.7), (-8.8, 46.7), (-7.5, 46.1),
     (-7.9, 44.1), (-7.9, 43.8), (-6.9, 42.3), (-6.7, 42.2), (-6.4, 42.2), (-5.8, 42.9), (-5.3, 43.7),
     (-4.8, 45.2), (-4.4, 46.8), (-4.2, 47.8), (-3.8, 48.5), (-3.5, 47.7), (-3.3, 46.9), (-3.1, 43.4),
     (-4.5, 40.7), (-4.9, 39.2), (-5, 38.2), (-5.4, 36.1), (-5.4, 33.1), (-4.7, 26.7), (-4.4, 25),
     (-4.4, 23.5), (-4.5, 22.1), (-4.5, 19.2), (-4.8, 16.5), (-4.7, 14.9), (-4.7, 13.3), (-4.7, 9.3),
     (-4.7, 7.5), (-5.4, 3.1), (-5.8, 1.9), (-4.4, 1.9), (-4.7, 0.9), (-4.7, 0), (1.6, 0), (2.4, 0),
     (8.1, 0), (8.1, 0.9), (7.5, 1.5), (5.7, 2), (5.1, 3), (5.7, 3), (5.1, 8.8), (5.4, 18), (6.3, 21.7),
     (6.3, 22.4), (6.3, 23.1), (6.5, 23.4), (6.7, 23.7), (6.8, 25.5), (6.9, 27.2), (7.6, 34.6),),
    ((0.6, 11.2), (0.7, 6.7), (0.5, 2.9), (0.9, 2.7), (1.3, 2.6), (1.2, 2.1), (0.3, 2.7), (0.2, 3.3),
     (-0.1, 8.3), (0.2, 10.6), (0.2, 11.8), (0.4, 13.9),),
    ((4.1, 58.6), (4.3, 58.9), (4.4, 58.7), (4.2, 58.4), (3.9, 58.4),),
)
