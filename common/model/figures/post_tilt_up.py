"""post-tilt-up/frame-completion.md and roof-blocking.md figures: pages of
views of the house after tilt-up (model/post_tilt_up.py), laid out as the
LayOut pages they replace (SketchUp/Tilt-up-isometric-a5.layout, whose
export was post-tilt-up/images/image_NN.png).

Each page's views keep LayOut's cameras, in the SketchUp model's
coordinates (converted with post_tilt_up.SKETCHUP_HOUSE); a view's parts
are drawn black, or light gray for the context under a step's new parts.
"""

from build123d import Location, Vector

from model import post_tilt_up as P
from model.notes import Icon, Label, Leader, Lines
from model.roof import bays

from . import Figure, Viewport

FRAME_MD = "post-tilt-up/frame-completion.md"
BLOCKING_MD = "post-tilt-up/roof-blocking.md"
PAGE = (8.203125, 5.796875)  # LayOut's page, inches
BORDER = 1 / 300  # the exported PNGs' one-pixel border (to drop once the figures are blessed: see ../TODO.md)
# The gray LayOut's exports drew each page's background view in, where it
# wasn't the default (see render/model2svg.py PAGE_COLORS).
LIGHT_GRAY = {"triangles": "#c4c4c4", "triangle_centered": "#c4c4c4", "triangle_clamped": "#c4c4c4",
              "insert_bird_block": "#bfbfbf", "vent_guide_board": "#bfbfbf", "align_vent_block": "#bfbfbf"}

TO_HOUSE = P.SKETCHUP_HOUSE.inverse()


def camera(eye, target, up):
    """A SketchUp camera in the house's frame."""
    point = lambda p: tuple((TO_HOUSE * Location(p)).position)
    origin = Vector(*point((0, 0, 0)))
    return point(eye), point(target), tuple(Vector(*point(up)) - origin)


NEAR = 1  # a perspective view shows only what's this far in front of the eye


def in_front(shapes, eye, target):
    """The parts of shapes in front of a perspective camera's eye."""
    from build123d import Align, Box, Plane
    e, t = Vector(*eye), Vector(*target)
    fwd = (t - e).normalized()
    keep = []
    front = None
    for s in [sol for shape in shapes for sol in (shape.solids() or [shape])]:
        bb = s.bounding_box()
        depths = [(Vector(x, y, z) - e).dot(fwd) for x in (bb.min.X, bb.max.X)
                  for y in (bb.min.Y, bb.max.Y) for z in (bb.min.Z, bb.max.Z)]
        if min(depths) >= NEAR:
            keep.append(s)
        elif max(depths) > NEAR:
            if front is None:
                front = Location(Plane(e + fwd * NEAR, z_dir=fwd)) * Box(1e4, 1e4, 1e4, align=(Align.CENTER, Align.CENTER, Align.MIN))
            part = s & front
            if part is not None and part.volume > 1e-6:
                keep.append(part)
    return keep


def view(spec, parts, style="hlr", notes=(), offset=(0, 0)):
    """A Viewport for a LayOut view spec (scene, rect, eye, target, up,
    (kind, value)) showing `parts` ((component, placement, mods) entries),
    its picture slid `offset` (page inches, right and down) in its rect."""
    _, rect, eye, target, up, (kind, value) = spec
    e, t, u = camera(eye, target, up)
    shapes = P.placed(parts)
    if kind == "fov":
        shapes = in_front(shapes, e, t)
    return Viewport(tuple(rect), e, t, u, [(s, style) for s in shapes], **{kind: value}, notes=list(notes), offset=offset)


def house():
    return P.walls()


def roof(sides=("left", "right")):
    """The structural triangles and the installed half-roofs."""
    return P.triangles() + [P.half_roof_at(side) for side in sides]


PERSON = (29.7, 57.5)  # the silhouette clipart's size, inches of model
PERSON_FEET = 0.37  # where the feet are, across its width from the left


def people(group, spec):
    """Viewport notes for a parallel view: the crew's silhouettes (facing the
    camera), standing at their places."""
    _, rect, *_, (kind, value) = spec
    scale = rect[3] / value  # page inches per inch of model
    w, h = PERSON[0] * scale, PERSON[1] * scale
    out = []
    for (x, y, z), mirrored in P.PEOPLE[group]:
        dx = (0.5 - PERSON_FEET) * w * (-1 if mirrored else 1)
        out.append((x, y, z, Icon("ptu_person", w, h, flip=mirrored, dx=dx, dy=h / 2)))
    return out


def figures(only=None):
    """The figures (just those named by `only`, if given)."""
    out = []
    for n in ORDER:
        md, name, build = STEPS[n]
        if only is not None and name not in only:
            continue
        page = PAGES[n]
        views, notes = build(page["views"])
        fig = Figure(md, name, notes=list(page["notes"]) + list(notes), page=PAGE, viewports=views,
                     border=BORDER, light=LIGHT_GRAY.get(name))
        out.append(fig)
    return out


# ── the figures ────────────────────────────────────────────────────────────
# Each takes its page's view specs and returns (viewports, extra notes); the
# tool insets are icons among the page's notes.

def f31(views):
    main, *_ = views
    return [view(main, house())], []


def corner_screws(views):
    main, *_ = views
    return [view(main, house() + P.CORNER_SCREWS)], []


def f34(views):
    lower, upper = views
    return [view(lower, house(), "hlr_light"), view(upper, P.triangles())], []


def f35(views):
    upper, lower, _, _, close = views
    rear = [P.triangles()[0]]
    return [view(lower, house(), "hlr_light"), view(upper, rear + P.TRIANGLE_CLAMPS),
            view(close, house() + rear)], []


def f36(views):
    lower, upper, *_ = views
    return [view(lower, house(), "hlr_light"), view(upper, [P.triangles()[0]] + P.TRIANGLE_CLAMPS)], []


def f37(views):
    main, *_ = views
    return [view(main, house() + P.triangles() + P.TRIANGLE_CLAMPS + P.TRIANGLE_SCREWS)], []


def raising(side, step, crew=None, ladders=False, installed=()):
    def build(views):
        main, *_ = views
        parts = house() + roof(installed) + [P.half_roof_at(side, step)] + P.funky_boards(side, step)
        if ladders:
            parts += P.LADDERS[side]
        return [view(main, parts, notes=people(crew, main) if crew else ())], []
    return build


def installed(side, step):
    """The half-roof on the walls, its funky boards still under it."""
    def build(views):
        main, *_ = views
        return [view(main, house() + roof() + P.funky_boards(side, step))], []
    return build


def close_roof(extra=()):
    def build(views):
        main, *_ = views
        return [view(main, house() + roof() + list(extra))], []
    return build


def f42(views):
    main, *_ = views
    return [view(main, house() + roof(("right",)) + P.ridge_marks())], []


def f48(views):
    main, *_ = views  # the first bay from the front
    # the side clamp across the middle of the end bay, the screws either side of it
    return [view(main, house() + roof() + P.ridge_clamps(136.134, side_y=sum(bays()[7]) / 2) + P.ridge_screws(7))], []


def f49(views):
    main, *_ = views
    # The bay the LayOut page showed screwed, the side clamp a bay along
    # (positions found back from the page's image).
    return [view(main, house() + roof() + P.ridge_clamps(118.196, side_y=sum(bays()[6]) / 2) + P.ridge_screws(6))], []


def f50(views):
    main, *_ = views
    # each bay from one side or the other, as the page had them
    screws = [s for bay, flip in ((7, False), (6, False), (4, False), (2, False), (3, True), (1, True), (5, True))
              for s in P.ridge_screws(bay, flip)]
    return [view(main, house() + roof() + screws + P.ridge_clamps(136.134), "hlr_light")], []


def overhead(extra=(), close=None):
    """The roof from overhead in light gray, and maybe a close-up."""
    def build(views):
        main, *rest = views
        out = [view(main, house() + roof() + list(extra), "hlr_light")]
        if close is not None:
            out.append(view(rest[-1], close()))
        return out, []
    return build


BIRD_BAY = 5  # the bay (of roof.wall_bays()) the bird-blocking pages show


LAG_OFFSET = (0.27, 0.19)  # slides the lag bolt close-up to put the bolt in the middle


def lag_close():
    """A lag bolt going into a magic rafter's counterbore."""
    return house() + roof() + P.lag_bolts("left", P.MAGIC_RAFTERS, lift=3)


def clamp_close():
    return house() + roof() + [P.LAG_CLAMP]


def f51(views):
    main, clamp, align = views
    return [view(main, house() + roof(), "hlr_light"), view(clamp, clamp_close()), view(align, house() + roof())], []


def f56(views):
    lower, upper, close = views
    setting = P.bird_blocks("left", [BIRD_BAY], inward=P.BIRD_BLOCK_START)
    return [view(lower, house() + roof() + setting, "hlr_light"), view(close, setting)], []


def f57(views):
    main, *_ = views
    return [view(main, house() + roof() + P.bird_blocks("left", [BIRD_BAY]))], []


def f58(views):
    main, *_ = views
    return [view(main, house() + roof() + P.bird_blocks("left", [BIRD_BAY]) + P.BIRD_BLOCK_SCREWS)], []


def f60(views):
    lower, upper = views
    return [view(lower, house() + roof() + P.bird_blocks("left") + P.bird_blocks("right"), "hlr_light"),
            view(upper, [P.VENT_GUIDE] + P.VENT_GUIDE_CLAMPS)], []


def f61(views):
    lower, upper = views
    blocks = house() + roof() + P.bird_blocks("left") + P.bird_blocks("right")
    return [view(lower, blocks + [P.VENT_GUIDE], "hlr_light"),
            view(upper, P.vent_blocks("right", [0], offset=P.VENT_BLOCK_START) + P.VENT_SCREWS_TO_ALIGN)], []


def f62(views):
    main, *_ = views
    return [view(main, house() + roof() + P.bird_blocks("left") + P.bird_blocks("right")
                 + P.vent_blocks("right", [0]) + [P.VENT_CLAMP] + P.VENT_SCREWS)], []


def f63(views):
    main, close = views
    blocks = P.bird_blocks("left") + P.bird_blocks("right")
    return [view(main, house() + roof() + blocks + P.vent_blocks("left") + P.vent_blocks("right"), "hlr_light"),
            view(close, P.vent_blocks("right", [0]))], []


def f59(views):
    main, close = views
    blocks = P.bird_blocks("left") + P.bird_blocks("right")
    return [view(main, house() + roof() + blocks, "hlr_light"),
            view(close, P.bird_blocks("left", [BIRD_BAY], inward=P.BIRD_BLOCK_START))], []


def f52(views):
    main, close = views
    return [view(main, house() + roof() + P.lag_bolts("left", P.MAGIC_RAFTERS) + P.lag_bolts("right", P.MAGIC_RAFTERS),
                 "hlr_light"), view(close, lag_close(), offset=LAG_OFFSET)], []


def f53(views):
    main, _, close = views
    return [view(main, house() + roof(), "hlr_light"), view(close, house() + roof() + P.BRACKET_SCREWS)], []


def f54(views):
    main, close = views
    bolts = P.lag_bolts("left") + P.lag_bolts("right")
    return [view(main, house() + roof() + bolts, "hlr_light"), view(close, lag_close(), offset=LAG_OFFSET)], []


STEPS = {  # image number -> (manual, figure name, builder)
    31: (FRAME_MD, "secure_walls", f31),
    32: (FRAME_MD, "corner_screws_front", corner_screws),
    33: (FRAME_MD, "corner_screws_rear", corner_screws),
    34: (FRAME_MD, "triangles", f34),
    36: (FRAME_MD, "triangle_centered", f36),
    35: (FRAME_MD, "triangle_clamped", f35),
    37: (FRAME_MD, "triangle_screws", f37),
    38: (FRAME_MD, "half_roof_setup", raising("right", 1, crew="right", ladders=True)),
    39: (FRAME_MD, "raise_half_roof", raising("right", 2)),
    40: (FRAME_MD, "raise_half_roof_up", raising("right", 3)),
    42: (FRAME_MD, "align_half_roof", f42),
    43: (FRAME_MD, "second_half_roof_setup", raising("left", 1, crew="left", ladders=True, installed=("right",))),
    45: (FRAME_MD, "raise_second_half_roof", raising("left", 3, installed=("right",))),
    46: (FRAME_MD, "second_half_roof_on", installed("left", 4)),
    47: (FRAME_MD, "join_half_roofs", close_roof()),
    48: (FRAME_MD, "ridge_screws", f48),
    49: (BLOCKING_MD, "ridge_beam_bay", f49),
    50: (BLOCKING_MD, "ridge_beam", f50),
    51: (BLOCKING_MD, "align_magic_rafters", f51),
    52: (BLOCKING_MD, "magic_lag_bolts", f52),
    53: (BLOCKING_MD, "bracket_screws", f53),
    54: (BLOCKING_MD, "all_lag_bolts", f54),
    56: (BLOCKING_MD, "insert_bird_block", f56),
    57: (BLOCKING_MD, "tap_bird_block", f57),
    58: (BLOCKING_MD, "bird_block_screws", f58),
    59: (BLOCKING_MD, "all_bird_blocks", f59),
    60: (BLOCKING_MD, "vent_guide_board", f60),
    61: (BLOCKING_MD, "align_vent_block", f61),
    62: (BLOCKING_MD, "vent_block_screws", f62),
    63: (BLOCKING_MD, "all_vent_blocks", f63),
}
ORDER = list(STEPS)  # the manuals' order



ALIGN_X = 0.875  # page 51's inset: where the magic rafter's (and its stud's) center line falls

# Each LayOut page: its views (scene, rect, eye, target, up, ("height" | "fov", value))
# and its annotations, (x, y, note) in page inches from the top-left.
PAGES = {
    # image_31.png: LayOut page 'Nail Stud Bays'
    31: dict(
        views=[
            ('Tilt up - top down all walls for adding screws to bays', [0.2051, 1.4977, 7.7949, 4.1023], (57.688, 95.716, 283.671), (57.688, 95.716, -318.375), (1.0, 0.0, 0.0), ('fov', 35.0)),
            ('Tools - long screw', [0.2051, 0.2, 1.2687, 1.1365], (373.167, 492.594, 444.421), (-208.702, 471.939, -263.525), (-0.772, -0.027, 0.635), ('height', 2.7624)),
            ('ISO version - Tools - 4x nails in each stud bay', [2.1313, 0.2, 1.2687, 1.1365], (-355.956, -283.294, 465.636), (40.46, 113.122, 69.22), (0.408, 0.408, 0.816), ('height', 17.0775)),
        ],
        notes=[
            (0.8383, 0.7667, Icon('ptu_long_screw', 1.21, 1.0733)),  # Tools - long screw
            (2.765, 0.7667, Icon('ptu_4x_nails_in_each_stud_bay', 1.21, 1.0733)),  # ISO version - Tools - 4x nails in each stud bay
            (0.2051, 0.2, Lines((((0, 0), (1.2688, 0)), ((1.2688, 0), (1.2688, -1.1365)), ((1.2688, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (2.1313, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (0.9838, 1.0404, Label('x4', 0.119, attach=1)),
            (2.3426, 2.3705, Lines((((0, 0), (3.7164, 0)), ((3.7164, 0), (3.7164, -2.4885)), ((3.7164, -2.4885), (0, -2.4885)), ((0, -2.4885), (0, 0))), weight=11.57, color=(255, 0, 0))),
            (3.5379, 1.063, Label('x18', 0.119, attach=1)),
            (2.1313, 0.7682, Leader(((-0.6574, 0),), weight=3.86)),
            (4.5177, 2.5, Leader(((0.0434, 0.1238), (0.0706, 0.2479), (0.0818, 0.3719), (0.0772, 0.4952), (0.057, 0.6176), (0.0217, 0.7387), (-0.0287, 0.858), (-0.0939, 0.9752), (-0.1736, 1.0899), (-0.2676, 1.2017), (-0.3757, 1.3101), (-0.4975, 1.4148), (-0.6328, 1.5154), (-0.7815, 1.6115), (-0.9432, 1.7028), (-1.1177, 1.7887)), weight=3.86)),
        ]),
    # image_32.png: LayOut page 'Screw all walls together - front'
    32: dict(
        views=[
            ('ISO version - Tilt up - screws in front wall corners', [0.2, 1.5, 7.8, 4.1], (56.632, 169.308, 167.665), (55.323, -86.112, -43.528), (-0.003, -0.637, 0.771), ('fov', 35.0)),
            ('Tools - long screw', [0.2118, 0.2, 1.2687, 1.1365], (373.167, 492.594, 444.421), (-208.702, 471.939, -263.525), (-0.772, -0.027, 0.635), ('height', 2.7624)),
            ('Tools - impact driver', [1.6313, 0.2, 1.2687, 1.1365], (22.084, 596.517, -13.949), (-737.375, 557.484, -145.824), (-0.171, -0.009, 0.985), ('fov', 35.0)),
        ],
        notes=[
            (0.845, 0.7667, Icon('ptu_long_screw', 1.21, 1.0733)),  # Tools - long screw
            (2.265, 0.7667, Icon('ptu_impact_driver', 1.21, 1.0733)),  # Tools - impact driver
            (5.293, 1.5, Lines((((0, 0), (0.8394, 0)), ((0.8394, 0), (0.8394, -3.085)), ((0.8394, -3.085), (0, -3.085)), ((0, -3.085), (0, 0))), weight=11.57, color=(255, 0, 0))),
            (2.1184, 1.5, Lines((((0, 0), (0.8423, 0)), ((0.8423, 0), (0.8423, -3.075)), ((0.8423, -3.075), (0, -3.075)), ((0, -3.075), (0, 0))), weight=11.57, color=(255, 0, 0))),
            (1.0545, 0.9967, Label('x5', 0.119, attach=1)),
            (0.2118, 0.2, Lines((((0, 0), (1.2688, 0)), ((1.2688, 0), (1.2688, -1.1365)), ((1.2688, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.6313, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
        ]),
    # image_33.png: LayOut page 'Screw all walls together - back'
    33: dict(
        views=[
            ('ISO version - tilt up - screws in back wall corners', [0.2, 1.5, 7.8, 4.1], (55.05, 15.203, 167.941), (55.12, 28.874, 156.637), (0.003, 0.637, 0.771), ('fov', 35.0)),
            ('Tools - long screw', [0.2096, 0.2, 1.2687, 1.1365], (373.167, 492.594, 444.421), (-208.702, 471.939, -263.525), (-0.772, -0.027, 0.635), ('height', 2.7624)),
            ('Tools - impact driver', [1.6313, 0.2, 1.2687, 1.1365], (22.084, 596.517, -13.949), (-737.375, 557.484, -145.824), (-0.171, -0.009, 0.985), ('fov', 35.0)),
        ],
        notes=[
            (0.8417, 0.7667, Icon('ptu_long_screw', 1.21, 1.0733)),  # Tools - long screw
            (2.265, 0.7667, Icon('ptu_impact_driver', 1.21, 1.0733)),  # Tools - impact driver
            (0.2096, 0.2, Lines((((0, 0), (1.2688, 0)), ((1.2688, 0), (1.2688, -1.1365)), ((1.2688, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.6313, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.0523, 0.9967, Label('x5', 0.119, attach=1)),
            (5.3866, 1.5, Lines((((0, 0), (0.8394, 0)), ((0.8394, 0), (0.8394, -3.085)), ((0.8394, -3.085), (0, -3.085)), ((0, -3.085), (0, 0))), weight=11.57, color=(255, 0, 0))),
            (2.032, 1.5, Lines((((0, 0), (0.8423, 0)), ((0.8423, 0), (0.8423, -3.075)), ((0.8423, -3.075), (0, -3.075)), ((0, -3.075), (0, 0))), weight=11.57, color=(255, 0, 0))),
        ]),
    # image_34.png: LayOut page 'Structural triangles - begin'
    34: dict(
        views=[
            ('ISO version - Tilt up - add both structural triangles (lower)', [0.2, 0.2, 7.8, 5.4], (476.714, -324.511, 479.365), (-21.675, 173.878, -19.025), (-0.408, 0.408, 0.816), ('height', 198.6738)),
            ('ISO version - Tilt up - add both structural triangles (upper)', [0.2, 0.2, 7.8, 5.4], (476.714, -324.511, 479.365), (-21.675, 173.878, -19.025), (-0.408, 0.408, 0.816), ('height', 198.6738)),
        ],
        notes=[
        ]),
    # image_35.png: LayOut page 'Structural triangles - align and clamp'
    35: dict(
        views=[
            ('Tilt up - add structural triangle (upper)', [0.2, 1.5427, 7.8, 4.0573], (57.691, 47.404, 134.757), (56.382, 144.786, 106.086), (-0.004, 0.282, 0.959), ('fov', 35.0)),
            ('Tilt up - add structural triangle (lower)', [0.2, 1.5427, 7.8, 4.0573], (57.691, 47.404, 134.757), (56.382, 144.786, 106.086), (-0.004, 0.282, 0.959), ('fov', 35.0)),
            ('Tools - vertically aligned blocks', [1.7577, 0.2, 1.2687, 1.1365], (623.5, 494.881, 12.571), (-278.728, 557.51, -35.004), (-0.052, 0.004, 0.999), ('height', 4.9686)),
            ('Tools - vertically misaligned blocks', [3.2901, 0.2, 1.2687, 1.1365], (588.716, 500.766, -0.375), (-280.668, 529.958, -29.85), (-0.034, 0.001, 0.999), ('height', 4.5184)),
            ('Tilt up - close up structural triangle vertical alignment', [0.2, 0.2, 1.2687, 1.1365], (64.728, 157.395, 102.164), (-271.926, 237.138, 75.866), (-0.074, 0.017, 0.997), ('fov', 35.0)),
        ],
        notes=[
            (2.39, 0.7667, Icon('ptu_vertically_aligned_blocks', 1.2067, 1.0733)),  # Tools - vertically aligned blocks
            (3.9233, 0.7667, Icon('ptu_vertically_misaligned_blocks', 1.2067, 1.0733)),  # Tools - vertically misaligned blocks
            (1.7577, 0.2, Lines((((0, 0), (1.2688, 0)), ((1.2688, 0), (1.2688, -1.1365)), ((1.2688, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (2.7629, 2.6585, Lines((((0, 0), (1.1142, 0)), ((1.1142, 0), (1.1142, -1.0143)), ((1.1142, -1.0143), (0, -1.0143)), ((0, -1.0143), (0, 0))), weight=7.72)),
            (3.2901, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (0.2, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (3.2901, 1.3365, Leader(((1.2638, 1.1365),), arrow=False, weight=9.65, color=(255, 0, 0))),
            (0.7384, 1.2555, Leader(((0, 0.9555),), weight=3.86)),
            (0.7384, 0.3, Leader(((0, -0.9555),), weight=3.86)),
            (1.9, 1.2556, Leader(((0, 0.9556),), weight=3.86)),
            (1.9, 0.3, Leader(((0, -0.9556),), weight=3.86)),
            (2.7629, 2.799, Leader(((-1.9285, 0), (-1.9285, 1.4625)), weight=3.86)),
        ]),
    # image_36.png: LayOut page 'Structural triangles centered'
    36: dict(
        views=[
            ('Tilt up - add structural triangle (lower)', [0.2, 1.5099, 7.8, 4.0901], (57.691, 47.404, 134.757), (56.382, 144.786, 106.086), (-0.004, 0.282, 0.959), ('fov', 35.0)),
            ('Tilt up - add structural triangle (upper)', [0.2, 1.5099, 7.8, 4.0901], (57.691, 47.404, 134.757), (56.382, 144.786, 106.086), (-0.004, 0.282, 0.959), ('fov', 35.0)),
            ('Tools - centered blocks', [0.1989, 0.2, 1.2687, 1.1365], (901.231, 660.906, 11.97), (-271.421, 638.418, -33.097), (-0.038, -0.001, 0.999), ('height', 9.4215)),
            ('Tools - mis-centered blocks', [1.7313, 0.2, 1.2687, 1.1365], (900.943, 676.212, 11.813), (-271.708, 653.724, -33.254), (-0.038, -0.001, 0.999), ('height', 9.4215)),
        ],
        notes=[
            (0.8317, 0.7667, Icon('ptu_centered_blocks', 1.21, 1.0733)),  # Tools - centered blocks
            (2.365, 0.7667, Icon('ptu_mis_centered_blocks', 1.21, 1.0733)),  # Tools - mis-centered blocks
            (1.7313, 1.3365, Leader(((1.2638, 1.1365),), arrow=False, weight=9.65, color=(255, 0, 0))),
            (0.1989, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.7313, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (6.5771, 3.4426, Leader(((0, 1.1248), (-5.04, 1.1248)), weight=3.86)),
            (1.5371, 3.4426, Leader(((0, 1.1248),), weight=3.86)),
        ]),
    # image_37.png: LayOut page 'Structural triangles - screw'
    37: dict(
        views=[
            ('Tilt up - Structural triangle with screws', [0.2, 1.5, 7.8, 4.1], (56.927, 77.504, 129.537), (55.618, 174.886, 100.865), (-0.004, 0.282, 0.959), ('fov', 35.0)),
            ('Tools - long screw', [0.2, 0.2, 1.2687, 1.1365], (373.167, 492.594, 444.421), (-208.702, 471.939, -263.525), (-0.772, -0.027, 0.635), ('height', 2.7624)),
        ],
        notes=[
            (0.8333, 0.7667, Icon('ptu_long_screw', 1.2067, 1.0733)),  # Tools - long screw
            (0.2, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (0.9787, 1.0404, Label('x16', 0.119, attach=1)),
        ]),
    # image_38.png: LayOut page 'LHS Half Roof - step 1'
    38: dict(
        views=[
            ('ISO version - Tilt up - LHS Half Roof step 1', [0.2, 0.2, 7.8, 5.4], (-397.695, -289.989, 476.458), (153.017, 260.722, -74.253), (0.408, 0.408, 0.816), ('height', 300.2809)),
        ],
        notes=[
        ]),
    # image_39.png: LayOut page 'LHS Half Roof - step 2'
    39: dict(
        views=[
            ('ISO - Tilt up - LHS Roof step 2', [0.2, 0.2, 7.8, 5.4], (-363.6, -297.018, 440.983), (108.276, 174.858, -30.893), (0.408, 0.408, 0.816), ('height', 237.2933)),
        ],
        notes=[
        ]),
    # image_40.png: LayOut page 'LHS Half Roof - step 3'
    40: dict(
        views=[
            ('ISO - Tilt up - LHS Roof step 3', [0.2, 0.2, 7.8, 5.4], (-363.6, -297.018, 440.983), (108.276, 174.858, -30.893), (0.408, 0.408, 0.816), ('height', 237.2933)),
        ],
        notes=[
        ]),
    # image_42.png: LayOut page 'LHS Half Roof - align'
    42: dict(
        views=[
            ('ISO - Tilt up - Roof Assembly close up alignment of line', [0.2, 0.2, 7.8, 5.4], (410.203, -332.162, 464.519), (57.287, 20.753, 111.604), (-0.408, 0.408, 0.816), ('height', 20.6868)),
        ],
        notes=[
            (3.7, 2.19, Leader(((2.7638, 0),), weight=3.86)),  # (its head on the 1x6's pencil mark, at the triangle's face)
        ]),
    # image_43.png: LayOut page 'RHS Half Roof - step 1'
    43: dict(
        views=[
            ('ISO version - Tilt up - RHS half roof step 1', [0.2, 0.1954, 7.8, 5.4046], (486.112, -314.717, 446.38), (-53.594, 224.989, -93.326), (-0.408, 0.408, 0.816), ('height', 287.0263)),
        ],
        notes=[
        ]),
    # image_45.png: LayOut page 'RHS Half Roof - step 3'
    45: dict(
        views=[
            ('ISO - Tilt up - RHS half roof step 3', [0.2, 0.1951, 7.8, 5.4049], (461.804, -300.907, 431.283), (128.127, 32.77, 97.607), (-0.408, 0.408, 0.816), ('height', 246.0045)),
        ],
        notes=[
        ]),
    # image_46.png: LayOut page 'RHS Half Roof - step 4'
    46: dict(
        views=[
            ('ISO - Tilt up RHS Half Roof Step 4', [0.2, 0.2, 7.8, 5.4], (461.804, -300.907, 431.283), (128.127, 32.77, 97.607), (-0.408, 0.408, 0.816), ('height', 246.0045)),
        ],
        notes=[
        ]),
    # image_47.png: LayOut page 'RHS Half Roof - align'
    47: dict(
        views=[
            ('ISO - Tilt up - two roof assemblies joined', [0.2, 1.5, 7.8, 4.1], (437.203, -363.857, 498.142), (54.853, 18.493, 115.792), (-0.408, 0.408, 0.816), ('height', 13.9943)),
            ('Tools - horizontally aligned blocks', [0.2, 0.2, 1.2687, 1.1365], (624.694, 511.54, 11.861), (-277.534, 574.169, -35.713), (-0.052, 0.004, 0.999), ('height', 3.8075)),
            ('Tools - horizontally misaligned blocks', [1.6, 0.2, 1.2687, 1.1365], (627.071, 528.678, 15.364), (-277.663, 589.793, -37.418), (-0.058, 0.004, 0.998), ('height', 4.7944)),
        ],
        notes=[
            (0.8333, 0.7667, Icon('ptu_horizontally_aligned_blocks', 1.2067, 1.0733)),  # Tools - horizontally aligned blocks
            (2.2333, 0.7667, Icon('ptu_horizontally_misaligned_blocks', 1.2067, 1.0733)),  # Tools - horizontally misaligned blocks
            (0.2, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.6, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.6, 1.3365, Leader(((1.2638, 1.1365),), arrow=False, weight=9.65, color=(255, 0, 0))),
            (3.225, 3.265, Leader(((-0.1526, -0.0484), (-0.3748, -0.0161), (-0.5907, 0.0313), (-0.7994, 0.0931), (-1.0, 0.1688), (-1.1917, 0.2577), (-1.3736, 0.3592), (-1.5447, 0.4726), (-1.7044, 0.5974), (-1.8516, 0.7328), (-1.9855, 0.8784), (-2.1052, 1.0333), (-2.2099, 1.1971), (-2.2987, 1.369), (-2.3707, 1.5486), (-2.425, 1.735)), weight=3.86)),  # (its head where the page had it against the 1x6's end, which sits a little differently here)
        ]),
    # image_48.png: LayOut page 'Connect center beam - first bay'
    48: dict(
        views=[
            ('ISO - Tilt up - screw together roof assembliesh', [0.2, 1.5, 7.8, 4.1], (604.824, 564.668, 663.744), (-26.87, -67.026, 32.049), (-0.408, -0.408, 0.816), ('height', 12.7169)),
            ('Tools - short screw', [0.2, 0.1981, 1.2687, 1.1365], (405.101, 497.165, 428.868), (-229.632, 486.566, -259.523), (-0.735, -0.012, 0.678), ('height', 2.2231)),
            ('Tools - long screw', [1.6, 0.0346, 1.2687, 1.3818], (373.167, 492.594, 444.421), (-208.702, 471.939, -263.525), (-0.772, -0.027, 0.635), ('height', 2.7624)),
        ],
        notes=[
            (0.8333, 0.765, Icon('ptu_short_screw', 1.2067, 1.0767)),  # Tools - short screw
            (2.2333, 0.765, Icon('ptu_long_screw_2', 1.2067, 1.0767)),  # Tools - long screw
            (0.2, 0.1981, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.05, 0.9735, Label('x4', 0.119, attach=1)),
            (1.6, 0.1981, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.6, 1.3346, Leader(((1.2638, 1.1365),), arrow=False, weight=9.65, color=(255, 0, 0))),
        ]),
    # image_49.png: LayOut page 'Connect center beam - second bay'
    49: dict(
        views=[
            ('ISO - Tilt up screw together roof assemblies bay 2', [0.2, 1.5, 7.8, 4.1], (619.519, 595.957, 680.226), (-7.345, -30.907, 53.362), (-0.408, -0.408, 0.816), ('height', 16.4344)),
            ('Tools - short screw', [0.2, 0.2084, 1.2687, 1.1365], (405.101, 497.165, 428.868), (-229.632, 486.566, -259.523), (-0.735, -0.012, 0.678), ('height', 2.2231)),
            ('Tools - long screw', [1.5933, 0.0441, 1.2687, 1.3818], (373.167, 492.594, 444.421), (-208.702, 471.939, -263.525), (-0.772, -0.027, 0.635), ('height', 2.7624)),
        ],
        notes=[
            (0.8333, 0.775, Icon('ptu_short_screw', 1.2067, 1.0767)),  # Tools - short screw
            (2.225, 0.775, Icon('ptu_long_screw_2', 1.21, 1.0767)),  # Tools - long screw
            (0.2, 0.2084, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1364)), ((1.2687, -1.1364), (0, -1.1364)), ((0, -1.1364), (0, 0))), weight=7.72)),
            (1.05, 0.9837, Label('x4', 0.119, attach=1)),
            (5.1406, 4.7591, Leader(((0.5809, -0.3425),), weight=3.86, color=(255, 0, 0))),
            (5.7215, 5.1016, Leader(((-0.5809, 0.3425),), weight=3.86, color=(255, 0, 0))),
            (5.3038, 4.993, Label('4"', 0.119, attach=1)),
            (1.5933, 1.3441, Leader(((1.2638, 1.1364),), arrow=False, weight=9.65, color=(255, 0, 0))),
            (1.5933, 0.2077, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1364)), ((1.2687, -1.1364), (0, -1.1364)), ((0, -1.1364), (0, 0))), weight=7.72)),
        ]),
    # image_50.png: LayOut page 'Connect center beam alternate bays'
    50: dict(
        views=[
            ('Tilt up - all roof assembly bays', [0.4167, 1.5024, 7.5833, 4.0976], (55.087, 91.254, 343.441), (53.342, 91.252, 292.704), (0.999, 0.001, -0.034), ('fov', 35.0)),
            ('Tools - Clamp', [0.2, 0.2, 1.2687, 1.1365], (-28.979, 265.118, -14.995), (419.611, 277.919, 9.757), (-0.055, -0.002, 0.998), ('fov', 35.0)),
            ('Tools - short screw', [1.6038, 0.2, 1.2687, 1.1365], (405.101, 497.165, 428.868), (-229.632, 486.566, -259.523), (-0.735, -0.012, 0.678), ('height', 2.2231)),
        ],
        notes=[
            (0.8333, 0.7667, Icon('ptu_clamp', 1.2067, 1.0733)),  # Tools - Clamp
            (2.2367, 0.7667, Icon('ptu_short_screw', 1.2067, 1.0733)),  # Tools - short screw
            (0.2, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.6038, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (3.8862, 3.4597, Leader(((0, -0.0004), (0, -0.003), (0, -0.0101), (0, -0.024), (0, -0.0469), (0, -0.081), (0, -0.1287), (0, -0.1921), (0, -0.2735), (0, -0.3751), (0, -0.4993), (0, -0.6483), (0, -0.8242), (0, -1.0294), (0, -1.2661), (0, -1.5366)), weight=3.86)),
            (2.5383, 3.4488, Leader(((0, -0.0004), (0, -0.003), (0, -0.0101), (0, -0.024), (0, -0.0469), (0, -0.081), (0, -0.1287), (0, -0.1921), (0, -0.2735), (0, -0.3751), (0, -0.4993), (0, -0.6483), (0, -0.8242), (0, -1.0294), (0, -1.2661), (0, -1.5366)), weight=3.86)),
            (1.1625, 1.0308, Label('x2', 0.119, attach=1)),
            (2.5975, 1.0278, Label('x4', 0.119, attach=1)),
            (5.2917, 3.4597, Leader(((0, -0.0004), (0, -0.003), (0, -0.0101), (0, -0.024), (0, -0.0469), (0, -0.081), (0, -0.1287), (0, -0.1921), (0, -0.2735), (0, -0.3751), (0, -0.4993), (0, -0.6483), (0, -0.8242), (0, -1.0294), (0, -1.2661), (0, -1.5366)), weight=3.86)),
            (4.5333, 3.039, Leader(((0, 1.639),), weight=3.86)),
            (5.8333, 3.039, Leader(((0, 1.639),), weight=3.86)),
            (3.1, 3.039, Leader(((0, 1.639),), weight=3.86)),
        ]),
    # image_51.png: LayOut page 'Roof align + Clamp to wall'
    51: dict(
        views=[
            ('Tilt up - overhead for lag bolt installation', [0.2, 1.5, 7.8, 4.1], (55.087, 91.254, 343.441), (53.342, 91.252, 292.704), (0.999, 0.001, -0.034), ('fov', 35.0)),
            ('Tilt up - clamp roof to wall', [1.6313, 0.1859, 1.2687, 1.1365], (71.901, 80.448, 98.388), (298.54, -12.231, 84.071), (0.054, -0.022, 0.998), ('fov', 35.0)),
            ('Tilt up - aligning roof and wall', [0.1975, 0.1859, 1.2687, 1.1365], (87.289, 68.227, 96.648), (310.811, 70.962, 179.703), (-0.348, -0.004, 0.937), ('fov', 35.0)),  # (24" along from the page's view, onto the magic rafter)
        ],
        notes=[
            (4.4343, 1.7097, Lines((((0, 0), (0.5657, 0)), ((0.5657, 0), (0.5657, -0.581)), ((0.5657, -0.581), (0, -0.581)), ((0, -0.581), (0, 0))), weight=7.72)),
            (4.4343, 4.3222, Lines((((0, 0), (0.5657, 0)), ((0.5657, 0), (0.5657, -0.581)), ((0.5657, -0.581), (0, -0.581)), ((0, -0.581), (0, 0))), weight=7.72)),
            (1.6313, 0.1859, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (0.1975, 0.1859, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            # (the center lines on the rafter and the stud, lined up: ALIGN_X)
            (ALIGN_X + 0.2414, 0.416, Leader(((0, -0.8),), arrow=False, weight=3.86)),
            (ALIGN_X - 0.2474, 0.4092, Leader(((0, -0.8),), arrow=False, weight=3.86)),
            (ALIGN_X + 0.2414, 0.816, Leader(((0.3748, 0.0001),), weight=3.86)),
            (ALIGN_X - 0.2474, 0.8092, Leader(((-0.4051, 0.0001),), weight=3.86)),
            (ALIGN_X, 0.6704, Leader(((0, 0.4845),), arrow=False, weight=3.86)),
            (ALIGN_X, 0.8224, Leader(((0, -0.5),), arrow=False, weight=3.86)),
        ]),
    # image_52.png: LayOut page 'Roof lag bolt - first'
    52: dict(
        views=[
            ('Tilt up - overhead for lag bolt installation', [0.2, 1.5, 7.8, 4.1], (55.087, 91.254, 343.441), (53.342, 91.252, 292.704), (0.999, 0.001, -0.034), ('fov', 35.0)),
            ('Tilt up - lag bolt v2', [0.2, 0.2, 1.2687, 1.1365], (103.933, 73.626, 107.506), (19.022, -134.378, 9.098), (-0.152, -0.371, 0.916), ('fov', 35.0)),
        ],
        notes=[
            (4.4343, 1.7097, Lines((((0, 0), (0.5657, 0)), ((0.5657, 0), (0.5657, -0.581)), ((0.5657, -0.581), (0, -0.581)), ((0, -0.581), (0, 0))), weight=7.72)),
            (4.4343, 4.3222, Lines((((0, 0), (0.5657, 0)), ((0.5657, 0), (0.5657, -0.581)), ((0.5657, -0.581), (0, -0.581)), ((0, -0.581), (0, 0))), weight=7.72)),
            (0.2, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.5637, 1.1642, Label('x2', 0.119, attach=1)),
        ]),
    # image_53.png: LayOut page 'Add screws to roof brackets '
    53: dict(
        views=[
            ('Tilt up - overhead for lag bolt installation', [0.2, 1.5, 7.8, 4.1], (55.087, 91.254, 343.441), (53.342, 91.252, 292.704), (0.999, 0.001, -0.034), ('fov', 35.0)),
            ('Tools - hex bolt', [0.2, 0.2, 1.2687, 1.1365], (644.028, 613.597, 218.82), (-224.227, 619.459, -105.685), (-0.35, 0.002, 0.937), ('height', 1.673)),
            ('Tilt up - screw roof brackets close up', [1.9942, 0.2, 1.2687, 1.1365], (65.319, 14.619, 119.377), (16.146, 91.111, 59.277), (-0.298, 0.464, 0.834), ('fov', 35.0)),  # (re-aimed: a three-quarter view of the bracket from 9" off, up the slope; the page's camera sat in the ridge board)
        ],
        notes=[
            (0.8333, 0.7667, Icon('ptu_hex_bolt', 1.2067, 1.0733)),  # Tools - hex bolt
            (1.9942, 0.2, Lines((((0, 0), (1.2688, 0)), ((1.2688, 0), (1.2688, -1.1365)), ((1.2688, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (0.2, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.05, 1.0198, Label('x3', 0.119, attach=1)),
            (1.9942, 0.7682, Leader(((-0.5255, 0),), weight=3.86)),
            (3.3741, 1.1538, Label('x4', 0.119, attach=1)),
            (1.7298, 2.662, Lines((((0, 0), (0.6057, 0)), ((0.6057, 0), (0.6057, -0.581)), ((0.6057, -0.581), (0, -0.581)), ((0, -0.581), (0, 0))), weight=7.72)),
            (1.7298, 3.3786, Lines((((0, 0), (0.6057, 0)), ((0.6057, 0), (0.6057, -0.581)), ((0.6057, -0.581), (0, -0.581)), ((0, -0.581), (0, 0))), weight=7.72)),
            (5.8045, 2.662, Lines((((0, 0), (0.6057, 0)), ((0.6057, 0), (0.6057, -0.581)), ((0.6057, -0.581), (0, -0.581)), ((0, -0.581), (0, 0))), weight=7.72)),
            (5.8045, 3.3786, Lines((((0, 0), (0.6057, 0)), ((0.6057, 0), (0.6057, -0.581)), ((0.6057, -0.581), (0, -0.581)), ((0, -0.581), (0, 0))), weight=7.72)),
        ]),
    # image_54.png: LayOut page 'All lag bolts'
    54: dict(
        views=[
            ('Tilt up - overhead for lag bolt installation', [0.2, 1.4951, 7.8, 4.1049], (55.087, 91.254, 343.441), (53.342, 91.252, 292.704), (0.999, 0.001, -0.034), ('fov', 35.0)),
            ('Tilt up - lag bolt v2', [0.2185, 0.2, 1.2687, 1.1365], (103.933, 73.626, 107.506), (19.022, -134.378, 9.098), (-0.152, -0.371, 0.916), ('fov', 35.0)),
        ],
        notes=[
            (0.2185, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.6014, 1.1826, Label('x12', 0.119, attach=1)),
            (1.8714, 1.9101, Lines((((0, 0), (4.4572, 0)), ((4.4572, 0), (4.4572, -0.3075)), ((4.4572, -0.3075), (0, -0.3075)), ((0, -0.3075), (0, 0))), weight=11.57)),
            (1.8979, 4.3612, Lines((((0, 0), (4.4572, 0)), ((4.4572, 0), (4.4572, -0.3075)), ((4.4572, -0.3075), (0, -0.3075)), ((0, -0.3075), (0, 0))), weight=11.57)),
        ]),
    # image_56.png: LayOut page 'Bird block'
    56: dict(
        views=[
            ('Tilt up - insert bird block (lower)', [0.2, 1.5, 7.8, 4.1], (72.298, 35.123, 119.443), (161.597, 34.381, 51.698), (0.604, -0.005, 0.797), ('fov', 35.0)),
            ('Tilt up - insert bird block (upper)', [0.2, 1.5, 7.8, 4.1], (72.298, 35.123, 119.443), (161.597, 34.381, 51.698), (0.604, -0.005, 0.797), ('fov', 35.0)),
            ('Tilt up - Bird block', [0.2, 0.1951, 1.2687, 1.1365], (99.147, 52.923, 105.103), (51.693, -47.102, 87.573), (-0.067, -0.141, 0.988), ('fov', 35.0)),
        ],
        notes=[
            (4.2491, 2.6376, Leader(((0, -0.7167),), weight=3.86)),
            (5.5831, 2.6376, Leader(((0, -0.7167),), weight=3.86)),
            (2.6975, 2.6376, Leader(((0, -0.7167),), weight=3.86)),
            (5.5831, 2.6376, Leader(((0, -0.7167),), weight=3.86)),
            (0.2, 0.1951, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1364)), ((1.2687, -1.1364), (0, -1.1364)), ((0, -1.1364), (0, 0))), weight=7.72)),
        ]),
    # image_57.png: LayOut page 'Hammer bird block tight'
    57: dict(
        views=[
            ('Tilt up - bird block tight against roof', [0.2, 1.5, 7.8, 4.1], (92.615, 54.827, 114.999), (143.107, -27.589, 58.233), (0.265, -0.432, 0.862), ('fov', 35.0)),
            ('Tools - blocks without gap', [0.2, 0.2, 1.2687, 1.1365], (900.018, 716.268, 14.552), (-272.134, 679.313, -33.841), (-0.041, -0.001, 0.999), ('height', 8.7814)),
            ('Tools - blocks with gap', [1.7324, 0.2, 1.2687, 1.1365], (900.634, 691.967, 12.013), (-272.018, 669.478, -33.054), (-0.038, -0.001, 0.999), ('height', 8.7814)),
            ('Tools - mallet', [6.7313, 0.2, 1.2687, 1.1365], (18.469, 379.517, -16.188), (-311.117, 324.37, -7.569), (0.025, 0.004, 1.0), ('fov', 35.0)),
        ],
        notes=[
            (0.8333, 0.7667, Icon('ptu_blocks_without_gap', 1.2067, 1.0733)),  # Tools - blocks without gap
            (2.365, 0.7667, Icon('ptu_blocks_with_gap', 1.21, 1.0733)),  # Tools - blocks with gap
            (7.365, 0.7667, Icon('ptu_mallet', 1.21, 1.0733)),  # Tools - mallet
            (0.2, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.7324, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.7324, 1.3365, Leader(((1.2638, 1.1365),), arrow=False, weight=9.65, color=(255, 0, 0))),
            (6.7313, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (5.3, 3.2, Leader(((0.2576, 0.0762), (0.5005, 0.1591), (0.728, 0.2484), (0.9399, 0.3436), (1.1356, 0.4443), (1.3147, 0.5501), (1.4766, 0.6606), (1.621, 0.7754), (1.7473, 0.8941), (1.855, 1.0163), (1.9438, 1.1415), (2.0131, 1.2695), (2.0625, 1.3997), (2.0915, 1.5318), (2.0996, 1.6654), (2.0864, 1.8)), weight=3.86)),
            (4.6042, 3.1966, Leader(((-3.8042, -0.0034), (-3.7698, 1.8601)), weight=3.86)),
        ]),
    # image_58.png: LayOut page 'Screws in bird block'
    58: dict(
        views=[
            ('ISO - Tilt up - screws in bird block', [0.2, 1.5, 7.8, 4.1], (85.879, 51.846, 94.318), (123.767, 13.958, 113.262), (-0.236, 0.236, 0.943), ('fov', 35.0)),
            ('Tools - long screw', [0.202, 0.2, 1.2687, 1.1365], (373.167, 492.594, 444.421), (-208.702, 471.939, -263.525), (-0.772, -0.027, 0.635), ('height', 2.7624)),
        ],
        notes=[
            (0.835, 0.7667, Icon('ptu_long_screw', 1.21, 1.0733)),  # Tools - long screw
            (0.202, 0.2, Lines((((0, 0), (1.2687, 0)), ((1.2687, 0), (1.2687, -1.1365)), ((1.2687, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.5937, 1.1642, Label('x2', 0.119, attach=1)),
        ]),
    # image_59.png: LayOut page 'All bird block'
    59: dict(
        views=[
            ('Tilt up - overhead for lag bolt installation', [0.2, 1.5, 7.8, 4.1], (55.087, 91.254, 343.441), (53.342, 91.252, 292.704), (0.999, 0.001, -0.034), ('fov', 35.0)),
            ('Tilt up - Bird block', [0.2096, 0.2, 1.2687, 1.1365], (99.147, 52.923, 105.103), (51.693, -47.102, 87.573), (-0.067, -0.141, 0.988), ('fov', 35.0)),
        ],
        notes=[
            (0.2096, 0.2, Lines((((0, 0), (1.2688, 0)), ((1.2688, 0), (1.2688, -1.1365)), ((1.2688, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.6014, 1.1642, Label('x12', 0.119, attach=1)),
            (2.9809, 2.0798, Leader(((0, -0.819),), weight=3.86)),
            (3.7609, 2.0798, Leader(((0, -0.819),), weight=3.86)),
            (4.4294, 2.0798, Leader(((0, -0.819),), weight=3.86)),
            (5.098, 2.0798, Leader(((0, -0.819),), weight=3.86)),
            (5.7666, 2.0798, Leader(((0, -0.819),), weight=3.86)),
            (2.3123, 2.0798, Leader(((0, -0.819),), weight=3.86)),
            (5.0966, 4.5202, Leader(((0, 0.819),), weight=3.86)),
            (4.3166, 4.5202, Leader(((0, 0.819),), weight=3.86)),
            (3.648, 4.5202, Leader(((0, 0.819),), weight=3.86)),
            (2.9795, 4.5202, Leader(((0, 0.819),), weight=3.86)),
            (2.3109, 4.5202, Leader(((0, 0.819),), weight=3.86)),
            (5.7652, 4.5202, Leader(((0, 0.819),), weight=3.86)),
        ]),
    # image_60.png: LayOut page 'Add vent guide board'
    60: dict(
        views=[
            ('Tilt up - Add vent guide board (lower)', [0.2, 0.2, 7.7887, 5.4], (-96.556, 93.661, 242.5), (79.707, 93.869, 27.712), (0.773, 0.001, 0.634), ('fov', 35.0)),
            ('Tilt up - Add vent guide board (upper)', [0.2, 0.2, 7.7887, 5.4], (-96.556, 93.661, 242.5), (79.707, 93.869, 27.712), (0.773, 0.001, 0.634), ('fov', 35.0)),
        ],
        notes=[
        ]),
    # image_61.png: LayOut page 'Align vent'
    61: dict(
        views=[
            ('Tilt up - align vent lower', [0.2, 0.1951, 7.7887, 5.4049], (25.669, 150.468, 95.884), (262.294, 149.388, 241.521), (-0.524, 0.002, 0.852), ('fov', 35.0)),
            ('Tilt up - align vent upper', [0.2, 0.1951, 7.7887, 5.4049], (25.669, 150.468, 95.884), (262.294, 149.388, 241.521), (-0.524, 0.002, 0.852), ('fov', 35.0)),
        ],
        notes=[
            (2.9817, 1.9496, Leader(((-0.2225, -0.4048),), weight=3.86)),
            (5.3183, 1.9496, Leader(((0.2225, -0.4048),), weight=3.86)),
        ]),
    # image_62.png: LayOut page 'Attach vent'
    62: dict(
        views=[
            ('Tilt up - Screws in vent', [0.2, 0.1951, 7.8, 5.4049], (33.111, 150.884, 103.2), (269.736, 149.805, 248.837), (-0.524, 0.002, 0.852), ('fov', 35.0)),
        ],
        notes=[
        ]),
    # image_63.png: LayOut page 'All vents'
    63: dict(
        views=[
            ('Tilt up - add all vents', [0.2, 1.5, 7.8, 4.1], (55.087, 91.254, 343.441), (53.342, 91.252, 292.704), (0.999, 0.001, -0.034), ('fov', 35.0)),
            ('Tilt up - vent', [0.2096, 0.2, 1.2687, 1.1365], (23.904, 150.265, 81.692), (203.708, 150.458, 293.524), (-0.762, -0.001, 0.647), ('fov', 35.0)),
        ],
        notes=[
            (0.2096, 0.2, Lines((((0, 0), (1.2688, 0)), ((1.2688, 0), (1.2688, -1.1365)), ((1.2688, -1.1365), (0, -1.1365)), ((0, -1.1365), (0, 0))), weight=7.72)),
            (1.6014, 1.1642, Label('x12', 0.119, attach=1)),
            (5.098, 2.8988, Leader(((0, 0.819),), weight=3.86)),
            (4.318, 2.8988, Leader(((0, 0.819),), weight=3.86)),
            (3.6494, 2.8988, Leader(((0, 0.819),), weight=3.86)),
            (2.9809, 2.8988, Leader(((0, 0.819),), weight=3.86)),
            (2.3123, 2.8988, Leader(((0, 0.819),), weight=3.86)),
            (5.7666, 2.8988, Leader(((0, 0.819),), weight=3.86)),
            (2.9795, 3.7012, Leader(((0, -0.819),), weight=3.86)),
            (3.7595, 3.7012, Leader(((0, -0.819),), weight=3.86)),
            (4.428, 3.7012, Leader(((0, -0.819),), weight=3.86)),
            (5.0966, 3.7012, Leader(((0, -0.819),), weight=3.86)),
            (5.7652, 3.7012, Leader(((0, -0.819),), weight=3.86)),
            (2.3109, 3.7012, Leader(((0, -0.819),), weight=3.86)),
        ]),
}
