"""The platform: a 2x6 frame on two 4x6 skids, rigid foam between the joists,
and a 3/4" plywood subfloor. Also the finished floor laid on top of it.

Per Platform/platform.md and Platform/images/platform.dxf.

Frame: origin at the outside corner of the 2x6 frame, level with the bottom of
the skids. X runs across the platform (0 to PLATFORM_WIDTH), Y along it
(0 to PLATFORM_LENGTH), Z up.
"""

from .common import *

RIM = thickness("2x6")  # the long sides and joists are 2x6s on edge
FRAME_DEPTH = width("2x6")
SKID_HEIGHT = width(SKID)  # 4x6 skids stand on edge
FRAME_BOTTOM = SKID_HEIGHT  # the frame sits on the skids
FRAME_TOP = FRAME_BOTTOM + FRAME_DEPTH
DECK = FRAME_TOP + SUBFLOOR  # top of the subfloor

# Joists along Y: doubled at both ends, and on 16" centers in between.
JOIST_Y = [
    0, RIM,  # doubled front end
    *[c - RIM / 2 for c in spaced(JOIST_SPACING, JOIST_SPACING, 8)],
    PLATFORM_LENGTH - 2 * RIM, PLATFORM_LENGTH - RIM,  # doubled rear end
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
        *platform_manual(),
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
    """SketchUp: 'Platform - Joist'"""
    solids = [
        TwoBySix(JOIST_LENGTH, along="X", wide="Z"),
    ]
    children = []
    return solids, children


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
# (platform.md:55): each bottom corner loses a 4" x 3 1/2" triangle.
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


@component
def floor():
    """SketchUp: 'Group#78'"""
    solids = []
    children = [
        (floor_finished, Pos(87, 136 + 1/2, 0) * Rot(Z=180), [], ''),  # Floor (Finished)
    ]
    return solids, children


@component
def floor_finished():
    """SketchUp: 'Group#29'"""
    solids = [
        Pos(87, -0.0205, 0) * Rot(Z=90) * Sheet(1/2, 136.5205, 87, facing="Z"),
    ]
    children = []
    return solids, children


# ── Platform/platform.md figures ───────────────────────────────────────────
#
# Jig items and annotations for the figures in Platform/platform.md, tagged
# "manual:platform:<step>" so they appear only there. Annotations are placed
# in that manual's drawing: looking down on the platform with the FRONT at
# the bottom, so drawing (x, y) is the platform's (PLATFORM_WIDTH - x,
# PLATFORM_LENGTH - y). Offsets inside notes are in the drawing too.

from .notes import Icon, Label, Leader  # noqa: E402


def drawing(x, y):
    """A point given in the platform manual's drawing."""
    return Pos(PLATFORM_WIDTH - x, PLATFORM_LENGTH - y, DECK)


def steps(*ns):
    return " ".join(f"manual:platform:{n}" for n in ns)


def joist_center(y):
    """A joist's center line, in the drawing."""
    return PLATFORM_LENGTH - (y + RIM / 2)


def nail_through_rims(y, tag):
    """A nail gun and "x3" at each end of a joist, nailing through the rims."""
    c = joist_center(y)
    return [
        (Icon("NailGun", 14.5, 14, rotation=90, dx=-7.45, dy=-4.25), drawing(0, c), [], tag),
        (Label("x3", 2.5, attach=1, dx=-19, dy=RIM / 2), drawing(0, c), [], tag),
        (Icon("NailGun", 14.5, 14, rotation=-90, flip=True, dx=7.67, dy=-4.25), drawing(PLATFORM_WIDTH, c), [], tag),
        (Label("x3", 2.5, attach=1, dx=16.19, dy=RIM / 2), drawing(PLATFORM_WIDTH, c), [], tag),
    ]


# "SAVE" spacer blocks (Platform/platform.md step 7): set on the skids,
# centered in each bay, not nailed; shorter "SAVE END" blocks in the end bays.
SAVE_BLOCK, SAVE_END_BLOCK = 12, 10


@component
def save_block():
    return [TwoByFour(SAVE_BLOCK, along="Y", wide="X")], []


@component
def save_end_block():
    return [TwoByFour(SAVE_END_BLOCK, along="Y", wide="X")], []


# Brackets go alternately inside and outside the skids (platform.md step 5);
# the marks' positions are from platform.dxf.
BRACKET_MARKS = [(16.5, y) for y in (5.9, 35.65, 67.65, 99.65, 131.65, 141)] \
    + [(10.25, y) for y in (19.9, 51.9, 83.9, 115.9)] \
    + [(77.5, y) for y in (5.9, 35.65, 67.65, 99.65, 131.65, 141)] \
    + [(84, y) for y in (19.9, 51.9, 83.9, 115.9)]


def platform_manual():
    """Everything only the platform manual's figures show."""
    out = []
    ends, doubled, inner = [JOIST_Y[0], JOIST_Y[-1]], [JOIST_Y[1], JOIST_Y[-2]], JOIST_Y[2:-2]

    # Step 1: nail the perimeter at the corners.
    for y in ends:
        out += nail_through_rims(y, steps(1))

    # Step 2: clamp the doubled end joists and nail them together in 4
    # places; mark the joist lines on the outside of the rims.
    t = steps(2)
    for x in (21, 79):
        for yd, up in ((0, -1), (PLATFORM_LENGTH, 1)):
            out.append((Leader(((0, 6 * up),)), drawing(x, yd), [], t))
    out += [
        (Label("CLAMP", 3, attach=1), drawing(25.28, 136), [], t),
        (Label("CLAMP", 3, attach=1), drawing(60.49, 136), [], t),
        (Label("CLAMP", 3, attach=1), drawing(26.54, 10), [], t),
        (Label("CLAMP", 3, attach=1), drawing(59.34, 10), [], t),
        (Leader(((0, -6.5), (3, -6.5))), drawing(21, 141), [], t),
        (Leader(((0, -6.5), (-3, -6.5))), drawing(79, 141), [], t),
        (Leader(((0, 5.5), (4, 5.5))), drawing(21, 3), [], t),
        (Leader(((0, 5.5), (-4, 5.5))), drawing(79, 3), [], t),
    ]
    for x in (18.54, 47.54, 62.04, 91.04):
        out.append((Icon("NailGun", 8.7, 8.4, rotation=180, dx=-3.75, dy=-3.6), drawing(x, -0.25), [], t))
        out.append((Icon("NailGun", 8.7, 8.4, flip=True, dx=-3.75, dy=3.6), drawing(x, 144.66), [], t))
    for (x, y), flip in (((-0.79, 147.84), True), ((96.6, 147.99), False), ((-0.56, 8.51), True), ((96.82, 8.66), False)):
        out.append((Icon("NailGun", 8.7, 8.4, rotation=90 if flip else -90, flip=flip, dx=-3.6 if flip else 3.6, dy=-3.75), drawing(x, y), [], t))
    for (x, y) in ((-13.7, 143.09), (-13.48, 3.76), (106.42, 143.09), (106.64, 3.76)):
        out.append((Label("x3", 2.5, attach=1), drawing(x, y), [], t))
    for y in inner:
        c = joist_center(y)
        out += [
            (Leader(((2.19, 0),), dx=0.58, arrow=False), drawing(PLATFORM_WIDTH, c), [], t),
            (Icon("Pencil", 7.2, 7.2, dx=7.33, dy=3.56), drawing(PLATFORM_WIDTH, c), [], t),
            (Leader(((-2, 0),), dx=-0.5, arrow=False), drawing(0, c), [], t),
            (Icon("Pencil", 7.2, 7.2, flip=True, dx=-7.1, dy=3.56), drawing(0, c), [], t),
        ]

    # Step 3: nail each joist through the rims (and the doubled ones).
    for y in doubled + inner:
        out += nail_through_rims(y, steps(3))

    # Steps 4-12: which end is which.
    t = steps(*range(4, 13))
    out += [(Label("REAR", 3, attach=1), drawing(42.99, 151.93), [], t),
            (Label("FRONT", 3, attach=1), drawing(42.06, -4.35), [], t)]

    # Steps 5-6: bracket marks; step 6's inset shows the bracket and its screws.
    for x, y in BRACKET_MARKS:
        out.append((Label("x", 2.5, attach=1), drawing(x, y), [], steps(5, 6)))
    out += [
        (Icon("Pencil", 7.2, 7.2, dx=3.08, dy=3.08), drawing(19.52, 4.52), [], steps(5)),
        (Label("Start Here", 2.5, attach=1), drawing(27.93, 9), [], steps(5)),
        (Icon("Hurricane_Bracket", 16.4, 31.6, dx=5, dy=9.6), drawing(-17.67, -21.29), [], steps(6)),
        (Icon("Screw", 5, 12, rotation=-90, dx=4.5, dy=-1.87), drawing(-7.68, -4.09), [], steps(6)),
        (Icon("Screw", 5, 12, rotation=-90, dx=4.5, dy=-1.88), drawing(-4.28, -19.68), [], steps(6)),
        (Label("x3", 2.5, attach=1), drawing(3.94, -4.51), [], steps(6)),
        (Label("x3", 2.5, attach=1), drawing(7.34, -20.11), [], steps(6)),
    ]

    # Step 7: spacer blocks on the skids, centered in each bay.
    for a, b in bays():
        end = b - a < FOAM_WIDTH
        block, length = (save_end_block, SAVE_END_BLOCK) if end else (save_block, SAVE_BLOCK)
        for x in (SKID_INSET, PLATFORM_WIDTH - SKID_INSET - thickness(SKID)):
            out.append((block, Pos(x, (a + b) / 2 - length / 2, SKID_HEIGHT), [], steps(7)))
    out += [
        (Leader(((4, 4), (8, 4))), drawing(16, 101), [], steps(7)),
        (Leader(((4, 4), (8, 4))), drawing(16, 131), [], steps(7)),
        (Label('Blocks labeled "SAVE"', 2.5, attach=1), drawing(25, 106), [], steps(7)),
        (Label('Blocks labeled "SAVE END"', 2.5, attach=1), drawing(25.24, 135.67), [], steps(7)),
        (Label("DO NOT NAIL BLOCKS", 2.5, attach=1), drawing(25.13, 90.59), [], steps(7)),
    ]

    # Step 8: foam in every bay, sealed.
    out += [
        (Label("RIGID INSULATION", 3, attach=1), drawing(31.46, 74.48), [], steps(8, 9)),
        (Leader(((8, -8), (10, -8))), drawing(55.53, 3.81), [], steps(8)),
        (Label("Foam Sealant (Great Stuff) all 4 sides\n  of each bay", 2, attach=1), drawing(66.48, -2.77), [], steps(8)),
        (Leader(((6.77, 11.61), (12.15, 11.61))), drawing(50.99, 136.86), [], steps(8)),
        (Label("Install insulation silver side up", 2.5, attach=1), drawing(65.49, 149.99), [], steps(8)),
        (Label("RIGID INSULATION", 3, attach=1), drawing(31.46, 26.48), [], steps(10)),
    ]

    # Steps 9-11: the plywood panels, from the rear.
    for n, (x, y) in enumerate(((34.43, 123.02), (34.12, 76.61), (33.9, 27.3)), 1):
        out.append((Label(f"Panel {n}", 4, attach=1), drawing(x, y), [], steps(*range(8 + n, 12))))

    # Step 12: a pencil line 3 1/2" in from the edges, for routing.
    m = width("2x4")
    corners = [(m, m), (PLATFORM_WIDTH - m, m), (PLATFORM_WIDTH - m, PLATFORM_LENGTH - m), (m, PLATFORM_LENGTH - m)]
    out += [
        (Leader(tuple((x - m, y - m) for x, y in corners[1:] + corners[:1]), arrow=False), drawing(m, m), [], steps(12)),
        (Icon("Pencil", 12, 12, dx=4.5, dy=4.5), drawing(93.87, 118.22), [], steps(12)),
    ]
    return out
