"""The platform: a 2x6 frame on two 4x6 skids, rigid foam between the joists,
and a 3/4" plywood subfloor. (Named platform_assembly so it doesn't shadow
the standard library's platform module.)

Per Platform/platform.md.

Frame: origin at the outside corner of the 2x6 frame, level with the bottom of
the skids. X runs across the platform (0 to PLATFORM_WIDTH), Y along it
(0 to PLATFORM_LENGTH), Z up.
"""

from build123d import Plane, Polygon, Pos, extrude

from .lumber import FourBySix, Sheet, TwoByFour, TwoBySix, thickness, width
from .dimensions import (
    FOAM_END_WIDTH, FOAM_LENGTH, FOAM_WIDTH, JOIST_LENGTH, JOIST_SPACING, PLATFORM_LENGTH, PLATFORM_WIDTH,
    SKID, SKID_INSET, SUBFLOOR
)
from .common import component, spaced

RIM = thickness("2x6")  # the long sides and joists are 2x6s on edge
FRAME_DEPTH = width("2x6")
SKID_HEIGHT = width(SKID)  # 4x6 skids stand on edge
FRAME_BOTTOM = SKID_HEIGHT  # the frame sits on the skids
FRAME_TOP = FRAME_BOTTOM + FRAME_DEPTH
DECK = FRAME_TOP + SUBFLOOR  # top of the subfloor

# Joists along Y: doubled at both ends, and on 16" centers in between.
JOIST_Y = [
    0, RIM,  # doubled rear end
    *[c - RIM / 2 for c in spaced(JOIST_SPACING, JOIST_SPACING, 8)],
    PLATFORM_LENGTH - 2 * RIM, PLATFORM_LENGTH - RIM,  # doubled front end
]

# Foam fills each bay between joists, resting on the skids; the end bays are narrower.
FOAM_THICKNESS = 2  # rests on the skids, level with the bottom of the joists


@component
def platform():
    """The whole platform: skids, frame, foam and subfloor."""
    solids = []
    children = [
        *[(skid, Pos(x, 0, 0), [], '')
          for x in (SKID_INSET, PLATFORM_WIDTH - SKID_INSET - thickness(SKID))],
        (platform_long_side, Pos(0, 0, FRAME_BOTTOM), [], 'Floor Framing'),
        (platform_long_side, Pos(PLATFORM_WIDTH - RIM, 0, FRAME_BOTTOM), [], 'Floor Framing'),
        *[(platform_joist, Pos(RIM, y, FRAME_BOTTOM), [], 'Floor Framing') for y in JOIST_Y],
        # Foam centered in each bay.
        *[(foam(b - a), Pos(RIM + (JOIST_LENGTH - FOAM_LENGTH) / 2,
                            (a + b) / 2 - foam_width(b - a) / 2,
                            SKID_HEIGHT), [], 'Floor Insulation')
          for a, b in bays()],
        *[(platform_plywood, Pos(0, y, FRAME_TOP), [], 'Floor Sheeting')
          for y in spaced(0, 48, 3)],  # three 4x8 sheets, seams over joist centers
    ]
    return solids, children


def bays():
    """(start, end) of the open space between each pair of adjacent joists."""
    edges = sorted(JOIST_Y)
    return [(a + RIM, b) for a, b in zip(edges, edges[1:]) if b - (a + RIM) > 1]


def foam_width(bay):
    """The manual's foam width for a bay this wide: narrower in the end bays."""
    return FOAM_WIDTH if bay > FOAM_WIDTH else FOAM_END_WIDTH


def foam(bay):
    return platform_insulation_foam_wide if bay > FOAM_WIDTH else platform_insulation_foam_narrow


@component
def platform_joist():
    """A 2x6 joist across the platform, between the long sides."""
    solids = [
        TwoBySix(JOIST_LENGTH, along="X", wide="Z"),
    ]
    anchors = {  # the ends, on the top edge's center line
        "left": Pos(0, RIM / 2, FRAME_DEPTH),
        "right": Pos(JOIST_LENGTH, RIM / 2, FRAME_DEPTH),
    }
    return solids, [], anchors


@component
def platform_long_side():
    """SketchUp: 'Platform- Long Side'"""
    solids = [
        TwoBySix(PLATFORM_LENGTH, along="Y", wide="Z"),
    ]
    children = []
    return solids, children


@component
def platform_insulation_foam_narrow():
    """Rigid foam for the end bays."""
    solids = [
        Sheet(FOAM_THICKNESS, FOAM_LENGTH, FOAM_END_WIDTH, facing="Z"),
    ]
    children = []
    return solids, children


@component
def platform_insulation_foam_wide():
    """Rigid foam for the inner bays."""
    solids = [
        Sheet(FOAM_THICKNESS, FOAM_LENGTH, FOAM_WIDTH, facing="Z"),
    ]
    children = []
    return solids, children


@component
def platform_plywood():
    """A 4x8 sheet of subfloor, laid across the platform."""
    solids = [
        Sheet(SUBFLOOR, PLATFORM_WIDTH, 48, facing="Z"),
    ]
    children = []
    return solids, children


# The skid ends are cut at an angle, "longer part of the angled edges up"
# (platform.md): each bottom corner loses a 4" x 3 1/2" triangle.
SKID_END_CUT = (4, 3 + 1/2)  # as modeled in SketchUp


@component
def skid():
    """A 4x6 skid on edge, running the length of the platform."""
    run, rise = SKID_END_CUT
    solids = [
        FourBySix(PLATFORM_LENGTH, along="Y", wide="Z")
        - extrude(Plane.YZ * (Polygon((0, 0), (run, 0), (0, rise), align=None)
                              + Polygon((PLATFORM_LENGTH, 0), (PLATFORM_LENGTH, rise),
                                        (PLATFORM_LENGTH - run, 0), align=None)),
                  thickness(SKID)),
    ]
    children = []
    return solids, children


# ── jig items for Platform/platform.md's figures ──────────────────────────

# "SAVE" spacer blocks (Platform/platform.md step 7): set on the skids,
# centered in each bay, not nailed; shorter "SAVE END" blocks in the end bays.
SAVE_BLOCK, SAVE_END_BLOCK = 12, 10


@component
def save_block():
    return [TwoByFour(SAVE_BLOCK, along="Y", wide="X")], []


@component
def save_end_block():
    return [TwoByFour(SAVE_END_BLOCK, along="Y", wide="X")], []


def save_blocks():
    """The blocks on the skids, centered in each bay: [(component, Location)]."""
    out = []
    for a, b in bays():
        end = b - a < FOAM_WIDTH
        block, length = (save_end_block, SAVE_END_BLOCK) if end else (save_block, SAVE_BLOCK)
        for x in (SKID_INSET, PLATFORM_WIDTH - SKID_INSET - thickness(SKID)):
            out.append((block, Pos(x, (a + b) / 2 - length / 2, SKID_HEIGHT)))
    return out


# Hurricane brackets tie the frame to the skids (platform.md steps 5-6): one
# behind each joist, on alternate sides of each skid, starting inside at the
# front and ending inside at the rear doubled joist (where the mark goes in
# front of it, there being no room behind); the mark for one goes beside the
# skid's face.
BRACKET_MARK_OFF = 1 + 1/2  # the mark, off the skid's face
BRACKET_MARK_BEHIND = 2 + 1/2  # and behind the joist's rear face


def bracket_marks():
    """Where to mark the brackets: [(x, y)] on the platform's plan, from the
    front (where the marking starts), the door-side skid's first."""
    joists = [y for y in sorted(JOIST_Y, reverse=True) if y not in (JOIST_Y[-1], JOIST_Y[0])]  # (the rims cover the outer end joists)
    out = []
    for k, y in enumerate(joists):
        rear_doubled = y == JOIST_Y[1]
        inside = k % 2 == 0 or rear_doubled
        mark_y = y + RIM + BRACKET_MARK_OFF if rear_doubled else y - BRACKET_MARK_BEHIND
        for skid, out_ in ((PLATFORM_WIDTH - SKID_INSET - thickness(SKID), 1), (SKID_INSET, -1)):
            face = skid + thickness(SKID) if out_ > 0 else skid  # the skid's outer face
            x = face + out_ * BRACKET_MARK_OFF if not inside else face - out_ * (thickness(SKID) + BRACKET_MARK_OFF)
            out.append((x, mark_y))
    return out
