"""post-tilt-up/frame-completion.md and roof-blocking.md figures: pages of
views of the house after tilt-up (model/post_tilt_up.py).

Each page is a view of the house at that step (an isometric from above one
of the house's corners fitted to what it shows, or a perspective from one
of CAMERAS), with close-ups in insets; a view's parts are drawn black, or
light gray for the context under a step's new parts. The notes are the tool
insets at the page's corners, counts, arrows and boxes hung on points and
parts of the model."""

from build123d import Align, Box, Location, Pos, Vector

from model import post_tilt_up as P
from model.notes import Icon, Label, Leader, Span, Lines
from model.platform import DECK, PLATFORM_LENGTH, PLATFORM_WIDTH, platform
from model.roof import RIDGE_BOARD_BOTTOM, RIDGE_TOP, RIDGE_X, bays, wall_bays
from model.house import WALL_TOP
from model.walls import WALL_DEPTH, WALL_HEIGHT

from . import Figure, Viewport
from .pages import (
    PAGE, RED, LOWER_RECT, arrow_between, arrow_to, center_of, frame, inset, inset_edge, inset_rect, inset_view,
    main_rect, page_arrow, perspective, view,
)

FRAME_MD = "post-tilt-up/frame-completion.md"
BLOCKING_MD = "post-tilt-up/roof-blocking.md"
PAPER_NOTES = True
LOWER = LOWER_RECT
HIGHLIGHT = 6  # a red box's line, relative to notes.LINE
PERSON = (29.7, 57.5)  # the silhouette clipart's size, inches of model
PERSON_FEET = 0.37  # where the feet are, across its width from the left

# Perspective cameras, (eye, target, up) in the house's frame (fov 35°).
X, Y = PLATFORM_WIDTH / 2, PLATFORM_LENGTH / 2
CAMERAS = {
    # straight down over the middle of the house, the door side up the page
    "overhead": ((X, Y - 9, 341), (X, Y - 9, 290), (-1, 0, 0)),
    "overhead_walls": ((X - 2, Y - 14, 281), (X - 2, Y - 14, -321), (-1, 0, 0)),
    # over one end of the house, looking down its length at the far corners
    "over_rear": ((X, -5, 165), (X, PLATFORM_LENGTH + 86, -46), (0, 0.6, 0.7)),
    "over_front": ((X, PLATFORM_LENGTH - 15, 165), ((X, PLATFORM_LENGTH - 29, 154)), (0, -0.7, 0.7)),
    # from inside the house, over the walls, at the rear triangle
    "rear_triangle": ((X - 2, 117, 132), (X - 1, 19, 103), (0, 0, 1)),
    "rear_triangle_close": ((X - 1, 87, 127), (X, -11, 98), (0, 0, 1)),
    "triangle_foot": ((39, 6.7, 99.5), (376, -73, 73), (0, 0, 1)),  # along the rear wall's top at the triangle's foot
    "clamp_roof_to_wall": ((31.8, 83.6, 95.8), (-195, 176, 81), (0, 0, 1)),
    "aligning_roof": ((16.4, 95.9, 94), (-207, 93, 177), (0, 0, 1)),
    "lag_bolt": ((-0.2, 90.5, 105), (85, 298, 6.5), (0, 0, 1)),
    "bracket": ((38.4, 149.5, 116.8), (87.6, 73, 56.7), (0, 0, 1)),  # a three-quarter view of a front bracket
    "bird_bay": ((31.4, 129, 116.8), (-58, 130, 49), (0, 0, 1)),
    "bird_block": ((4.6, 111.2, 102.5), (52, 211, 85), (0, 0, 1)),
    "bird_tight": ((11.1, 109.3, 112.4), (-39, 192, 56), (0, 0, 1)),
    "bird_screws": ((17.8, 112.2, 91.7), (-20, 150, 111), (0, 0, 1)),
    "vent_guide": ((200, 70.4, 240), (24, 70.2, 25), (0, 0, 1)),
    "vent_align": ((78, 13.6, 93), (-159, 14.7, 239), (0, 0, 1)),
    "vent_screws": ((70.6, 13.2, 100.6), (-166, 14.3, 246), (0, 0, 1)),
    "vent": ((80, 13.8, 79), (-100, 13.6, 291), (0, 0, 1)),
}


def camera(name, rect, parts, **kw):
    eye, target, up = CAMERAS[name]
    return perspective(rect, eye, target, parts, up=up, **kw)


def house():
    return P.placed(P.walls())


def roof(sides=("left", "right")):
    """The structural triangles and the installed half-roofs."""
    return P.placed(P.triangles() + [P.half_roof_at(side) for side in sides])


def shapes(entries):
    return P.placed(entries)


def people(group):
    """Viewport notes: the crew's silhouettes (facing the camera), standing
    at their places, sized with the view."""
    out = []
    for (x, y, z), mirrored in P.PEOPLE[group]:
        w, h = PERSON
        dx = (0.5 - PERSON_FEET) * w * (-1 if mirrored else 1)
        out.append((x, y, z, Icon("ptu_person", w, h, flip=mirrored, dx=dx, dy=h / 2, model=True)))
    return out


def corner_box(x, y):
    """A wall corner's end studs, to box in a view."""
    return Pos(x - 4, y - 4, DECK) * Box(8, 8, WALL_HEIGHT, align=(Align.MIN, Align.MIN, Align.MIN))


def gray(shapes):
    return [(s, "hlr_light") for s in shapes]


def black(shapes):
    return [(s, "hlr") for s in shapes]


# ── the figures ────────────────────────────────────────────────────────────
# Each returns (viewports, page notes).

def secure_walls():
    main = camera("overhead_walls", LOWER, house(), highlights=[([platform.shape()], RED, HIGHLIGHT, -0.1)])
    main.notes.append(arrow_to((X, Y, DECK), inset_rect("top left", 1), "bottom", curve=0.25))
    main.notes.append((X, Y, DECK, Label("x18", 0.12, dx=0.15, attach=4)))
    notes = inset("ptu_long_screw", "top left", count="x4") + inset("ptu_4x_nails_in_each_stud_bay", "top left", 1)
    notes.append(arrow_between(inset_edge(inset_rect("top left", 1), "left"), inset_edge(inset_rect("top left"), "right")))
    return [main], notes


def corner_screws(end):
    y = PLATFORM_LENGTH - WALL_DEPTH if end == "front" else WALL_DEPTH
    corners = [[corner_box(x, y)] for x in (WALL_DEPTH, PLATFORM_WIDTH - WALL_DEPTH)]
    main = camera("over_rear" if end == "front" else "over_front", LOWER, house() + shapes(P.CORNER_SCREWS),
                  highlights=[(c, RED, HIGHLIGHT, 0.05) for c in corners])
    return [main], inset("ptu_long_screw", "top left", count="x5") + inset("ptu_impact_driver", "top left", 1)


def triangles():
    both = house() + shapes(P.triangles())
    return [view(main_rect(), "front rhs", gray(house()), fit=both), view(main_rect(), "front rhs", shapes(P.triangles()), fit=both)], []


def inset_alignment_arrows(rect):
    """Vertical arrows meeting at an inset's middle: the edges line up."""
    x, y, w, h = rect
    cx = x + w / 2
    return [(cx, y + 0.45 * h, Leader(((0, 0.35 * h),), weight=4)), (cx, y + 0.55 * h, Leader(((0, -0.35 * h),), weight=4))]


def triangle_clamped():
    rear = shapes([P.triangles()[0]])
    close_rect = inset_rect("top left")
    close = camera("triangle_foot", close_rect, house() + rear)
    main = camera("rear_triangle", LOWER, gray(house()) + black(rear + shapes(P.TRIANGLE_CLAMPS)),
                  highlights=[(shapes(P.TRIANGLE_CLAMPS[:1]), (0, 0, 0), 4, 0.3)])
    notes = [frame(close_rect)] + inset_alignment_arrows(close_rect)
    notes += inset("ptu_vertically_aligned_blocks", "top left", 1) + inset("ptu_vertically_misaligned_blocks", "top left", 2, struck=True)
    notes += inset_alignment_arrows(inset_rect("top left", 1))
    return [main, close], notes


def triangle_centered():
    rear = shapes([P.triangles()[0]])
    main = camera("rear_triangle", LOWER, gray(house()) + black(rear + shapes(P.TRIANGLE_CLAMPS)))
    bb = rear[0].bounding_box()
    main.notes = [page_arrow((x, bb.min.Y, WALL_TOP), 0, -1.1) for x in (bb.min.X + 2, bb.max.X - 2)]  # the ends overhang equally
    return [main], inset("ptu_centered_blocks", "top left") + inset("ptu_mis_centered_blocks", "top left", 1, struck=True)


def triangle_screws():
    main = camera("rear_triangle_close", LOWER, house() + shapes(P.triangles() + P.TRIANGLE_CLAMPS + P.TRIANGLE_SCREWS))
    return [main], inset("ptu_long_screw", "top left", count="x16")


def raising(side, step, crew=None, ladders=False, installed=()):
    def build():
        parts = house() + roof(installed) + shapes([P.half_roof_at(side, step)] + P.funky_boards(side, step))
        if ladders:
            parts += shapes(P.LADDERS[side])
        return [view(main_rect(), "front lhs", parts, margin=0.1, notes=people(crew) if crew else ())], []
    return build


def installed(side, step):
    """The half-roof on the walls, its funky boards still under it."""
    return lambda: ([view(main_rect(), "front rhs", house() + roof() + shapes(P.funky_boards(side, step)))], [])


def align_half_roof():
    marks = shapes(P.ridge_marks())
    main = view(main_rect(), "front rhs", house() + roof(("right",)) + marks, fit=marks, margin=1.5)
    main.notes = [page_arrow(tuple(P.ridge_marks()[0][1].position), 2.7, 0)]  # the pencil mark on the 1x6, at the triangle's face
    return [main], []


def join_half_roofs():
    marks = shapes(P.ridge_marks())
    main = view(LOWER, "front rhs", house() + roof(), fit=marks, margin=1.0)
    joint = (RIDGE_X, PLATFORM_LENGTH - WALL_DEPTH, WALL_TOP + RIDGE_BOARD_BOTTOM + 2)
    main.notes = [arrow_to(joint, inset_rect("top left"), "bottom", curve=0.2)]
    return [main], inset("ptu_horizontally_aligned_blocks", "top left") + inset("ptu_horizontally_misaligned_blocks", "top left", 1, struck=True)


def ridge_bay(bay, clamp_y, side_y, dimension=False):
    """A ridge bay seen close from the rear rhs: its clamps and screws."""
    def build():
        clamps, screws = shapes(P.ridge_clamps(clamp_y, side_y=side_y)), shapes(P.ridge_screws(bay))
        main = view(LOWER, "rear rhs", house() + roof() + clamps + screws, fit=clamps + screws, margin=0.15)
        if dimension:  # the two screws of a column, 4" apart
            a, b = (s.bounding_box().center() for s in screws[:2])
            main.notes = [(tuple(a), tuple(b), Span('4"', weight=3, color=RED))]
        return [main], inset("ptu_short_screw", "top left", count="x4") + inset("ptu_long_screw_2", "top left", 1, struck=True)
    return build


def ridge_beam():
    screws = [s for bay, flip in ((7, False), (6, False), (4, False), (2, False), (3, True), (1, True), (5, True))
              for s in shapes(P.ridge_screws(bay, flip))]
    main = camera("overhead", LOWER, gray(house() + roof() + screws + shapes(P.ridge_clamps(136.134))))
    # alternate bays, screwed from alternate sides: an arrow at each
    for k, (a, b) in enumerate(bays()):
        main.notes.append(page_arrow((RIDGE_X, (a + b) / 2, WALL_TOP + RIDGE_TOP), 0, 1.0 if k % 2 else -1.0))
    return [main], inset("ptu_clamp", "top left", count="x2") + inset("ptu_short_screw", "top left", 1, count="x4")


def magic_boxes():
    """The magic rafters' lag bolts, boxed."""
    return [(shapes(P.lag_bolts(side, P.MAGIC_RAFTERS)), (0, 0, 0), 4, 0.15) for side in ("left", "right")]


def align_magic_rafters():
    main = camera("overhead", LOWER, gray(house() + roof()), highlights=magic_boxes())
    aligning_rect, clamp_rect = inset_rect("top left"), inset_rect("top left", 1)
    aligning = camera("aligning_roof", aligning_rect, house() + roof())
    clamp = camera("clamp_roof_to_wall", clamp_rect, house() + roof() + shapes([P.LAG_CLAMP]))
    # the center lines on the rafter and the stud, lined up
    x, y, w, h = aligning_rect
    cx = x + 0.53 * w
    notes = [frame(aligning_rect), frame(clamp_rect),
             (cx + 0.19 * w, y + 0.19 * h, Leader(((0, -0.35 * h),), arrow=False, weight=4)),
             (cx - 0.19 * w, y + 0.19 * h, Leader(((0, -0.35 * h),), arrow=False, weight=4)),
             (cx + 0.19 * w, y + 0.54 * h, Leader(((0.3 * w, 0),), weight=4)),
             (cx - 0.19 * w, y + 0.54 * h, Leader(((-0.3 * w, 0),), weight=4)),
             (cx, y + 0.41 * h, Leader(((0, -0.43 * h),), arrow=False, weight=4))]
    return [main, clamp, aligning], notes


LAG_OFFSET = (0.27, 0.19)  # slides the lag bolt close-up to put the bolt in the middle


def lag_close():
    """A lag bolt going into a magic rafter's counterbore."""
    return house() + roof() + shapes(P.lag_bolts("left", P.MAGIC_RAFTERS, lift=3))


def magic_lag_bolts():
    main = camera("overhead", LOWER, gray(house() + roof() + shapes(P.lag_bolts("left", P.MAGIC_RAFTERS) + P.lag_bolts("right", P.MAGIC_RAFTERS))),
                  highlights=magic_boxes())
    rect = inset_rect("top left")
    close = camera("lag_bolt", rect, lag_close(), offset=LAG_OFFSET)
    return [main, close], [frame(rect), (rect[0] + rect[2] + 0.1, rect[1] + rect[3] - 0.1, Label("x2", 0.12, attach=7))]


def bracket_screws():
    brackets = [shapes(P.bracket_screws(side, end)) for side in ("left", "right") for end in ("front", "rear")]
    main = camera("overhead", LOWER, gray(house() + roof()), highlights=[(b, (0, 0, 0), 4, 0.12) for b in brackets])
    rect = inset_rect("top left", 1)
    close = camera("bracket", rect, house() + roof() + shapes(P.BRACKET_SCREWS))
    notes = inset("ptu_hex_bolt", "top left", count="x3") + [frame(rect)]
    notes.append((rect[0] + rect[2] + 0.1, rect[1] + rect[3] - 0.1, Label("x4", 0.12, attach=7)))
    notes.append(arrow_between(inset_edge(rect, "left"), inset_edge(inset_rect("top left"), "right")))
    return [main, close], notes


def all_lag_bolts():
    rows = [shapes(P.lag_bolts(side)) for side in ("left", "right")]
    main = camera("overhead", LOWER, gray(house() + roof() + rows[0] + rows[1]), highlights=[(r, (0, 0, 0), HIGHLIGHT, 0.05) for r in rows])
    rect = inset_rect("top left")
    close = camera("lag_bolt", rect, lag_close(), offset=LAG_OFFSET)
    return [main, close], [frame(rect), (rect[0] + rect[2] + 0.1, rect[1] + rect[3] - 0.1, Label("x12", 0.12, attach=7))]


BIRD_BAY = 5  # the bay (of roof.wall_bays()) the bird-blocking pages show


def bird_block_entries(**kw):
    return P.bird_blocks("left", [BIRD_BAY], **kw)


def insert_bird_block():
    setting = shapes(bird_block_entries(inward=P.BIRD_BLOCK_START))
    main = camera("bird_bay", LOWER, gray(house() + roof()) + black(setting))
    # the bays either side too, from above
    for i in range(BIRD_BAY - 1, min(BIRD_BAY + 2, len(wall_bays()))):
        a, b = wall_bays()[i]
        main.notes.append(page_arrow((WALL_DEPTH / 2, (a + b) / 2, WALL_TOP), 0, 0.72))
    rect = inset_rect("top left")
    close = camera("bird_block", rect, setting)
    return [main, close], [frame(rect)]


def tap_bird_block():
    block = shapes(bird_block_entries())
    main = camera("bird_tight", LOWER, house() + roof() + block)
    at = tuple(block[0].bounding_box().center())
    main.notes = [arrow_to(at, inset_rect("top right"), "bottom", curve=-0.2),
                  arrow_to(at, inset_rect("top left"), "bottom", curve=0.3)]
    notes = inset("ptu_blocks_without_gap", "top left") + inset("ptu_blocks_with_gap", "top left", 1, struck=True)
    notes += inset("ptu_mallet", "top right")
    return [main], notes


def bird_block_screws():
    main = camera("bird_screws", LOWER, house() + roof() + shapes(bird_block_entries() + P.BIRD_BLOCK_SCREWS))
    return [main], inset("ptu_long_screw", "top left", count="x2")


def block_arrows(entries, side):
    """An arrow at each block, from up the page for the left side's, from down it for the right's."""
    return [page_arrow(tuple(s.bounding_box().center()), 0, 0.82 if side == "left" else -0.82) for s in shapes(entries)]


def all_bird_blocks():
    blocks = {side: P.bird_blocks(side) for side in ("left", "right")}
    main = camera("overhead", LOWER, gray(house() + roof() + shapes(blocks["left"] + blocks["right"])),
                  notes=block_arrows(blocks["left"], "left") + block_arrows(blocks["right"], "right"))
    rect = inset_rect("top left")
    close = camera("bird_block", rect, shapes(bird_block_entries(inward=P.BIRD_BLOCK_START)))
    return [main, close], [frame(rect), (rect[0] + rect[2] + 0.1, rect[1] + rect[3] - 0.1, Label("x12", 0.12, attach=7))]


def vent_guide_board():
    blocks = shapes(P.bird_blocks("left") + P.bird_blocks("right"))
    main = camera("vent_guide", main_rect(), gray(house() + roof() + blocks) + black(shapes([P.VENT_GUIDE] + P.VENT_GUIDE_CLAMPS)))
    return [main], []


def align_vent_block():
    blocks = shapes(P.bird_blocks("left") + P.bird_blocks("right"))
    block = shapes(P.vent_blocks("right", [0], offset=P.VENT_BLOCK_START))
    main = camera("vent_align", main_rect(), gray(house() + roof() + blocks + shapes([P.VENT_GUIDE])) + black(block + shapes(P.VENT_SCREWS_TO_ALIGN)))
    bb = block[0].bounding_box()
    main.notes = [page_arrow((bb.center().X, bb.min.Y, bb.max.Z), -0.3, 0.5), page_arrow((bb.center().X, bb.max.Y, bb.max.Z), 0.3, 0.5)]
    return [main], []


def vent_block_screws():
    blocks = shapes(P.bird_blocks("left") + P.bird_blocks("right"))
    main = camera("vent_screws", main_rect(), house() + roof() + blocks + shapes(P.vent_blocks("right", [0]) + [P.VENT_CLAMP] + P.VENT_SCREWS))
    return [main], []


def all_vent_blocks():
    blocks = shapes(P.bird_blocks("left") + P.bird_blocks("right"))
    vents = {side: P.vent_blocks(side) for side in ("left", "right")}
    main = camera("overhead", LOWER, gray(house() + roof() + blocks + shapes(vents["left"] + vents["right"])),
                  notes=block_arrows(vents["left"], "left") + block_arrows(vents["right"], "right"))
    rect = inset_rect("top left")
    close = camera("vent", rect, shapes(P.vent_blocks("right", [0])))
    return [main, close], [frame(rect), (rect[0] + rect[2] + 0.1, rect[1] + rect[3] - 0.1, Label("x12", 0.12, attach=7))]


STEPS = {  # figure name -> (manual, builder), in the manuals' order
    "secure_walls": (FRAME_MD, secure_walls),
    "corner_screws_front": (FRAME_MD, lambda: corner_screws("front")),
    "corner_screws_rear": (FRAME_MD, lambda: corner_screws("rear")),
    "triangles": (FRAME_MD, triangles),
    "triangle_centered": (FRAME_MD, triangle_centered),
    "triangle_clamped": (FRAME_MD, triangle_clamped),
    "triangle_screws": (FRAME_MD, triangle_screws),
    "half_roof_setup": (FRAME_MD, raising("right", 1, crew="right", ladders=True)),
    "raise_half_roof": (FRAME_MD, raising("right", 2)),
    "raise_half_roof_up": (FRAME_MD, raising("right", 3)),
    "align_half_roof": (FRAME_MD, align_half_roof),
    "second_half_roof_setup": (FRAME_MD, raising("left", 1, crew="left", ladders=True, installed=("right",))),
    "raise_second_half_roof": (FRAME_MD, raising("left", 3, installed=("right",))),
    "second_half_roof_on": (FRAME_MD, installed("left", 4)),
    "join_half_roofs": (FRAME_MD, join_half_roofs),
    "ridge_screws": (FRAME_MD, ridge_bay(7, 136.134, sum(bays()[7]) / 2)),
    "ridge_beam_bay": (BLOCKING_MD, ridge_bay(6, 118.196, sum(bays()[6]) / 2, dimension=True)),
    "ridge_beam": (BLOCKING_MD, ridge_beam),
    "align_magic_rafters": (BLOCKING_MD, align_magic_rafters),
    "magic_lag_bolts": (BLOCKING_MD, magic_lag_bolts),
    "bracket_screws": (BLOCKING_MD, bracket_screws),
    "all_lag_bolts": (BLOCKING_MD, all_lag_bolts),
    "insert_bird_block": (BLOCKING_MD, insert_bird_block),
    "tap_bird_block": (BLOCKING_MD, tap_bird_block),
    "bird_block_screws": (BLOCKING_MD, bird_block_screws),
    "all_bird_blocks": (BLOCKING_MD, all_bird_blocks),
    "vent_guide_board": (BLOCKING_MD, vent_guide_board),
    "align_vent_block": (BLOCKING_MD, align_vent_block),
    "vent_block_screws": (BLOCKING_MD, vent_block_screws),
    "all_vent_blocks": (BLOCKING_MD, all_vent_blocks),
}


def figures(only=None):
    """The figures (just those named by `only`, if given)."""
    out = []
    for name, (md, build) in STEPS.items():
        if only is not None and name not in only:
            continue
        views, notes = build()
        out.append(Figure(md, name, notes=list(notes), page=PAGE, viewports=views))
    return out
