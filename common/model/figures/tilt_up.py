"""tilt-up/tilt-up.md figures: pages of views of the tilt-up (model/tilt_up.py),
laid out as the manual's LayOut document (SketchUp/Tilt-up-isometric-a5.layout)
had them: each page's viewports with their cameras, tool insets, and arrows
and notes (PAGES, transcribed from it).

Cameras are as LayOut had them, in the SketchUp model's frame; view()
converts them to the house's (SKP_HOUSE: the SketchUp model had the house
turned half around, its deck 2 5/8" higher).
"""

import math

from build123d import Location, Plane, Pos, Rot

from model.house import house
from model.notes import Icon, Label, Leader, dashed_arc, dashed_line
from model.notes import legacy_box as box
from model.platform import platform
from model import tilt_up as tu

from . import Figure, Viewport, vertical_fov

MD = "tilt-up/tilt-up.md"
PAGE = (8.203125, 5.796875)  # inches (LayOut's A5 landscape)
SKP_HOUSE = (103.73, 164.15, 2.63)  # where the house's origin was in SketchUp (turned 180°)


def to_house(p):
    return (SKP_HOUSE[0] - p[0], SKP_HOUSE[1] - p[1], p[2] - SKP_HOUSE[2])


def view(scene, rect, eye, target, up, height=None, fov=None):
    """A LayOut viewport: its SketchUp scene's name (for reference), page
    rect, and camera in SketchUp's frame."""
    return dict(scene=scene, rect=rect, eye=to_house(eye), target=to_house(target), up=(-up[0], -up[1], up[2]),
                height=height, fov=vertical_fov(fov, rect) if fov else None)


# ── what each page shows ────────────────────────────────────────────────────
# A scene is a list of what's in it: "platform"; ("wall", wall, stage);
# ("jig", wall); ("crew", group); "brace"; ("corner", corner); ("nails",
# corner); "brace_tools".

def raising(wall, stage, *more):
    return [("wall", wall, stage), *more]


RHS = ("wall", "rhs", "upright")
BACK = ("wall", "back", "upright")
LHS = ("wall", "lhs", "upright")
BASE = ["platform", RHS, "brace"]  # after the first wall is up and braced
FRONT_BASE = ["platform", RHS, BACK, LHS]  # the brace is off once three walls stand

SCENES = {
    "rhs_jig": ["platform", ("jig", "rhs"), ("wall", "rhs", "on_jig"), ("crew", "rhs_jig"), ("crew", "rhs_platform")],
    "rhs_tilting": ["platform", ("wall", "rhs", "tilted")],
    "rhs_upright": ["platform", RHS],
    "rhs_brace": ["platform", RHS, "brace", "brace_tools"],
    "rhs_mississippis": BASE,
    "back_jig": BASE + [("crew", "back_platform"), ("jig", "back"), ("wall", "back", "on_jig"), ("crew", "back_jig")],
    "back_off_jig": BASE + [("crew", "back_platform"), ("jig", "back"), ("wall", "back", "carried"), ("crew", "back_carried")],
    "back_to_platform": BASE + [("crew", "back_platform"), ("jig", "back"), ("wall", "back", "at_platform"),
                                ("crew", "back_at_platform")],
    "back_raise": BASE + [("wall", "back", "tilted")],
    "back_clear_hands": BASE + [("wall", "back", "gap")],
    "back_slide": BASE + [BACK],
    "back_clamp": BASE + [BACK, ("corner", "back_rhs")],
    "back_mississippis": BASE + [BACK, ("corner", "back_rhs")],
    "back_nail": BASE + [BACK, ("corner", "back_rhs"), ("nails", "back_rhs")],
    "lhs_jig": BASE + [BACK, ("jig", "lhs"), ("wall", "lhs", "on_jig"), ("crew", "lhs_jig"), ("crew", "lhs_platform")],
    "lhs_tilted": BASE + [BACK, ("wall", "lhs", "tilted")],
    "lhs_clear_hands": BASE + [BACK, ("wall", "lhs", "gap")],
    "lhs_slide": BASE + [BACK, LHS],
    "lhs_clamp": BASE + [BACK, LHS, ("corner", "back_lhs")],
    "lhs_mississippis": BASE + [BACK, LHS, ("corner", "back_lhs")],
    "lhs_side_nails": BASE + [BACK, LHS, ("corner", "back_lhs"), ("nails", "back_lhs")],
    "front_jig": FRONT_BASE + [("crew", "front_platform"), ("jig", "front"), ("wall", "front", "on_jig"),
                         ("crew", "front_jig")],
    "front_off_jig": FRONT_BASE + [("crew", "front_platform"), ("jig", "front"), ("wall", "front", "carried"),
                             ("crew", "front_carried")],
    "front_to_platform": FRONT_BASE + [("crew", "front_platform"), ("jig", "front"), ("wall", "front", "at_platform"),
                                 ("crew", "front_at_platform")],
    "front_align": FRONT_BASE + [("wall", "front", "at_platform")],
    "front_tilted": FRONT_BASE + [("wall", "front", "tilted")],
    "front_upright": ["platform", RHS, BACK, LHS, ("wall", "front", "upright")],
    "front_clamp": ["platform", RHS, BACK, LHS, ("wall", "front", "upright"), ("corner", "front_lhs"), ("corner", "front_rhs")],
    "front_mississippis": ["platform", RHS, BACK, LHS, ("wall", "front", "upright"), ("corner", "front_lhs"),
                           ("corner", "front_rhs")],
    "front_nail": ["platform", RHS, BACK, LHS, ("wall", "front", "upright"), ("corner", "front_lhs"), ("corner", "front_rhs"),
                   ("nails", "front_lhs"), ("nails", "front_rhs")],
}


def facing(eye, target):
    """How far to turn a cut-out person (about Z) to face the camera."""
    dx, dy = eye[0] - target[0], eye[1] - target[1]
    return math.degrees(math.atan2(-dx, dy))


def parts(scene, v):
    """[(shape, style)] for a scene, seen from viewport v (the people face it)."""
    out = []
    for item in scene:
        if item == "platform":
            out.append(platform.shape())
        elif item == "brace":
            out.append(tu.BRACE_AT * tu.wall_brace.shape())
        elif item == "brace_tools":
            out += [loc * c.shape() for c, loc in tu.BRACE_NAILS]
        elif item[0] == "wall":
            comp, loc = tu.wall_at(item[1], item[2])
            out.append(loc * comp.shape())
            if item[1] == "front":
                out.append(tu.STAGES["front"][item[2]] * tu.FUNKY_BOARD_16 * tu.funky_board_16.shape())
        elif item[0] == "jig":
            comp, loc = tu.jig_at(item[1])
            out.append(loc * comp.shape())
        elif item[0] == "crew":
            kind = tu.CREW_KIND[item[1]]
            turn = facing(v["eye"], v["target"])
            for x, y, z, mirror in tu.CREW[item[1]]:
                s = kind.shape()
                if mirror:
                    s = s.mirror(Plane.YZ)
                out.append(Pos(x, y, z) * Rot(Z=turn) * s)
        elif item[0] == "corner":
            out += [loc * c.shape() for c, loc in tu.CORNERS[item[1]] if c in (tu.bar_clamp, tu.door_clamp)]
        elif item[0] == "nails":
            out += [loc * c.shape() for c, loc in tu.CORNERS[item[1]] if c is tu.nail]
    return [(s, "hlr") for s in out]


# Notes at points of the model (for the brace close-up: the impact driver)
MODEL_NOTES = {
    "rhs_brace": [(*tu.IMPACT_DRIVER_AT, Icon("drill_icon", 0.6, 0.56, rotation=30, dx=-0.35, dy=0.57))],  # (nosed up to the top screw)
}


def figures(only=None):
    """The figures (just those named by `only`, if given)."""
    out = []
    for name, (_, views, notes) in PAGES.items():
        if only is not None and name not in only:
            continue
        vps = []
        for v in views:
            scene = SCENES[name]
            if v["scene"].endswith("LHS clamp close up") and ("corner", "back_lhs") not in scene:
                scene = scene + [("corner", "back_lhs")]
            vps.append(Viewport(v["rect"], v["eye"], v["target"], v["up"], parts(scene, v),
                                height=v["height"], fov=v["fov"],
                                notes=MODEL_NOTES.get(name, []) if v is views[0] else []))
        out.append(Figure(MD, name, page=PAGE, viewports=vps, notes=notes))
    return out


# ── the pages (transcribed from the LayOut document) ───────────────────────

PAGES = {  # figure -> (LayOut page, [viewport...], [page note...])
    'rhs_jig': ('RHS Wall - Step 1 - jig', [
        view('ISO - Tilt up - RHS Jig', (0.2, 0.2, 7.8, 5.4), (2671.73, 2590.9, 2520.02), (129.91, 49.08, -21.8),
             (-0.408, -0.408, 0.816), height=258.95),
    ], [
        (4.523, 2.500, Leader(((-0.523, -0.3),), arrow=True, weight=3.858)),
    ]),
    'rhs_tilting': ('RHS Wall - Step 2 - tilting', [
        view('ISO - Tilt Up - RHS Tilted', (0.2, 0.2, 7.8, 5.4), (983.78, 1013.82, 942.89), (143.67, 173.7, 102.78),
             (-0.408, -0.408, 0.816), height=181.37),
    ], [
        (4.345, 3.488, Leader(((0, -1.627),), arrow=True, weight=3.858)),
    ]),
    'rhs_upright': ('RHS Wall - Step 3 upright', [
        view('ISO - RHS Upright', (0.2, 0.2, 7.8, 5.4), (983.78, 1013.82, 942.89), (143.67, 173.7, 102.78),
             (-0.408, -0.408, 0.816), height=181.37),
    ], [
    ]),
    'rhs_brace': ('RHS Wall - Brace', [
        view('ISO - Tilt up - RHS Brace', (0.2, 0.2, 7.8, 5.4), (-307.25, -362.21, 425.22), (86.78, 31.82, 31.19),
             (0.408, 0.408, 0.816), height=72.4),
    ], [
    ]),
    'rhs_mississippis': ('RHS Wall - Mississippis', [
        view('ISO - Tilt Up - RHS Mississippis', (0.2, 0.2, 7.8, 5.4), (-518.85, 682.63, 636.59), (128.47, 35.31, -10.73),
             (0.408, -0.408, 0.816), height=190.04),
    ], [
        (6.761, 1.687, Icon('tu_nail_gun', 1.199, 1.041)),
        (1.034, 2.723, Icon('tu_mallet', 1.199, 1.066)),
        (1.800, 3.887, Leader(((-0.075, 0.018), (-0.148, 0.04), (-0.22, 0.067), (-0.289, 0.098), (-0.357, 0.133), (-0.423, 0.172), (-0.487, 0.215), (-0.548, 0.262), (-0.607, 0.313), (-0.663, 0.368), (-0.716, 0.426), (-0.766, 0.487)), arrow=True, weight=3.858)),
        (1.532, 3.435, Label('x3', 0.107, attach=1)),
        (5.670, 1.368, Label('x1', 0.107, attach=1)),
        (0.400, 2.155, box(1.269, 1.136, weight=3.858)),
        (6.126, 1.131, box(1.269, 1.136, weight=3.858)),
        (2.371, 3.936, Leader(((0.169, 0.369), (0.375, 0.712), (0.614, 1.025), (0.883, 1.308), (1.179, 1.558), (1.499, 1.774), (1.841, 1.953), (2.2, 2.094), (2.574, 2.196), (2.96, 2.255), (3.355, 2.271), (3.755, 2.242)), arrow=True, weight=3.858)),
        (5.889, 5.050, dashed_arc(3.351, 86.0, 155.6, weight=2.3, color=(109, 109, 109))),
        (2.839, 3.666, Leader(((0.153, 0.305),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (5.887, 4.540, dashed_arc(2.838, 85.2, 156.3, weight=2.3, color=(109, 109, 109))),
        (3.294, 3.404, Leader(((0.122, 0.262),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (5.888, 4.034, dashed_arc(2.331, 84.2, 157.3, weight=2.3, color=(109, 109, 109))),
        (3.748, 3.141, Leader(((0.091, 0.219),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (5.895, 3.585, dashed_arc(1.881, 83.0, 158.3, weight=2.3, color=(109, 109, 109))),
        (4.167, 2.899, Leader(((0.062, 0.179),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (5.968, 3.116, dashed_arc(1.405, 83.6, 160.1, weight=2.3, color=(109, 109, 109))),
        (4.663, 2.643, Leader(((0.039, 0.135),), weight=0.579, head=3.5, color=(109, 109, 109))),
    ]),
    'back_jig': ('Back Wall - Step 1 - jig', [
        view('ISO - Tilt up - Back Jig step 1', (0.2, 0.2, 7.8, 5.4), (-582.8, 667.36, 567.16), (11.11, 73.45, -26.75),
             (0.408, -0.408, 0.816), height=352.75),
    ], [
        (4.200, 4.600, Leader(((0.68, 0.513),), arrow=True, weight=3.858)),
        (4.936, 2.134, Label('A', 0.107, attach=1)),
        (5.331, 1.984, Label('B', 0.107, attach=1)),
    ]),
    'back_off_jig': ('Back Wall - Step 2 - Jig', [
        view('ISO - Tilt up back jig step 2', (0.2, 0.2, 7.8, 5.4), (-582.8, 667.36, 567.16), (11.11, 73.45, -26.75),
             (0.408, -0.408, 0.816), height=352.75),
    ], [
        (2.000, 2.900, Leader(((0.986, -0.613),), arrow=True, weight=3.858)),
    ]),
    'back_to_platform': ('Back Wall - Step 3 - Jig', [
        view('ISO - Tilt up - Back jig step 3', (0.2, 0.2, 7.8, 5.4), (-582.8, 667.36, 567.16), (11.11, 73.45, -26.75),
             (0.408, -0.408, 0.816), height=352.75),
    ], [
    ]),
    'back_raise': ('Back Wall - Raise', [
        view('ISO - Tilt up - back tilted', (0.2, 0.2, 7.8, 5.4), (-511.52, 701.54, 625.41), (135.93, 54.09, -22.04),
             (0.408, -0.408, 0.816), height=226.62),
    ], [
        (3.999, 3.980, Leader(((0, -1.094),), arrow=True, weight=3.858)),
    ]),
    'back_clear_hands': ('Back Wall - Clear hands', [
        view('ISO - Tilt up - back with 1ft gap', (0.2, 0.2, 7.8, 5.4), (-511.52, 701.54, 625.41), (135.93, 54.09, -22.04),
             (0.408, -0.408, 0.816), height=226.62),
    ], [
        (1.037, 2.568, Icon('tu_hand', 1.194, 1.066)),
        (0.400, 2.000, box(1.269, 1.136, weight=3.858)),
        (0.405, 3.136, Leader(((1.264, 1.136),), arrow=False, weight=9.645, color=(255, 0, 0))),
        (3.000, 2.580, Leader(((-0.096, 0.059), (-0.193, 0.112), (-0.291, 0.157), (-0.39, 0.195), (-0.49, 0.226), (-0.59, 0.25), (-0.691, 0.267), (-0.793, 0.277), (-0.895, 0.279), (-0.996, 0.274), (-1.098, 0.262), (-1.2, 0.243)), arrow=True, weight=3.858)),
    ]),
    'back_slide': ('Back Wall - Slide', [
        view('ISO - Tilt up - back upright', (0.2, 0.195, 7.8, 5.405), (-511.52, 701.54, 625.41), (135.93, 54.09, -22.04),
             (0.408, -0.408, 0.816), height=226.62),
    ], [
        (2.400, 4.200, Leader(((1.651, -0.967),), arrow=True, weight=3.858)),
    ]),
    'back_clamp': ('Back Wall - Clamp', [
        view('ISO - Tilt up - back joined', (0.2, 1.5, 7.8, 4.1), (-375.68, -321.65, 480.19), (185.57, 239.6, -81.06),
             (0.408, 0.408, 0.816), height=196.25),
        view('ISO - Tilt up - back clamp close up', (0.2, 0.2, 1.269, 1.136), (-320.87, -258.44, 515.38), (99.01, 161.45, 95.49),
             (0.408, 0.408, 0.816), height=16.59),
    ], [
        (0.200, 0.200, box(1.269, 1.136, weight=3.858)),
        (3.862, 1.663, Leader(((-0.057, 0.113), (-0.146, 0.222), (-0.265, 0.324), (-0.411, 0.42), (-0.583, 0.508), (-0.778, 0.588), (-0.995, 0.659), (-1.231, 0.721), (-1.485, 0.772), (-1.755, 0.812), (-2.038, 0.84), (-2.333, 0.856)), arrow=True, weight=3.858)),
    ]),
    'back_mississippis': ('Back Wall - Mississippis', [
        view('ISO - Tilt up - back joined', (0.2, 0.2, 7.8, 5.4), (-375.68, -321.65, 480.19), (185.57, 239.6, -81.06),
             (0.408, 0.408, 0.816), height=196.25),
    ], [
        (0.835, 0.768, Icon('tu_mallet', 1.199, 1.066)),
        (0.835, 5.02, Icon('tu_nail_gun', 1.199, 1.041)),
        (0.200, 0.200, box(1.269, 1.136, weight=3.858)),
        (0.200, 4.464, box(1.269, 1.136, weight=3.858)),
        (2.000, 2.398, Leader(((-0.126, -0.006), (-0.25, 0.006), (-0.371, 0.037), (-0.488, 0.085), (-0.6, 0.15), (-0.706, 0.23), (-0.805, 0.325), (-0.896, 0.435), (-0.979, 0.557), (-1.052, 0.693), (-1.114, 0.84), (-1.166, 0.998)), arrow=True, weight=3.858)),
        (1.644, 2.000, Label('x3', 0.107, attach=1)),
        (1.700, 4.400, Label('x1', 0.107, attach=1)),
        (2.446, 3.423, Leader(((0, -0.163), (-0.017, -0.324), (-0.05, -0.481), (-0.098, -0.634), (-0.162, -0.783), (-0.239, -0.925), (-0.331, -1.061), (-0.435, -1.189), (-0.553, -1.309), (-0.683, -1.419), (-0.825, -1.52), (-0.978, -1.609)), arrow=True, weight=3.858)),
        (0.841, 2.970, dashed_arc(2.109, -73.1, -6.0, weight=2.3, color=(109, 109, 109))),
        (2.897, 3.184, Leader(((0.008, -0.167),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (1.033, 2.704, dashed_arc(2.366, -79.4, -4.8, weight=2.3, color=(109, 109, 109))),
        (3.393, 2.903, Leader(((-0.037, -0.261),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (1.507, 2.710, dashed_arc(2.322, -90.9, 1.4, weight=2.3, color=(109, 109, 109))),
        (3.828, 2.652, Leader(((-0.001, -0.158),), weight=0.579, head=3.5, color=(109, 109, 109))),
    ]),
    'back_nail': ('Back Wall - nail', [
        view('ISO - Tilt up - back clamped and nailed', (0.2, 1.504, 7.8, 4.096), (-335.6, -270.47, 492.85), (89.01, 154.14, 68.24),
             (0.408, 0.408, 0.816), height=79.3),
    ], [
        (0.835, 0.76, Icon('tu_angled_nail_rhs', 1.199, 1.066)),
        (0.835, 2.032, Icon('tu_nail_gun', 1.199, 1.066)),
        (5.963, 0.765, Icon('tu_blocks_in_line', 1.199, 1.066)),
        (7.362, 0.765, Icon('tu_blocks_not_in_line', 1.199, 1.066)),
        (0.200, 0.192, box(1.269, 1.136, weight=3.858)),
        (0.200, 1.464, box(1.269, 1.136, weight=3.858)),
        (0.997, 2.272, Label('x5', 0.107, attach=1)),
        (0.478, 0.931, dashed_line(0.95, 0.367, weight=3.858, color=(255, 0, 0))),
        (1.428, 0.565, Leader(((-0.95, -0.367),), weight=1.929, color=(255, 0, 0))),
        (4.100, 1.504, Leader(((-0.137, 0.107), (-0.291, 0.208), (-0.461, 0.3), (-0.645, 0.386), (-0.842, 0.462), (-1.052, 0.531), (-1.273, 0.591), (-1.503, 0.641), (-1.742, 0.682), (-1.989, 0.713), (-2.242, 0.734), (-2.5, 0.744)), arrow=True, weight=3.858)),
        (6.728, 1.334, Leader(((1.264, 1.136),), arrow=False, weight=9.645, color=(255, 0, 0))),
        (5.328, 0.197, box(1.269, 1.136, weight=3.858)),
        (6.728, 0.197, box(1.269, 1.136, weight=3.858)),
    ]),
    'lhs_jig': ('LHS Wall - Step 1 - Jig', [
        view('ISO - Tilt up - LHS on Jig', (0.2, 0.2, 7.8, 5.4), (-398.77, -287.84, 408.07), (-2.77, 108.16, 12.08),
             (0.408, 0.408, 0.816), height=293.28),
    ], [
        (1.045, 2.143, Label('A', 0.107, attach=1)),
        (1.465, 1.993, Label('B', 0.107, attach=1)),
        (4.000, 2.900, Leader(((-0.6, -0.4),), arrow=True, weight=3.858)),
    ]),
    'lhs_tilted': ('LHS Wall - Step 2 - Tilted', [
        view('ISO - Tilt up - LHS angled', (0.2, 0.2, 7.8, 5.4), (-363.24, -297.14, 452.13), (176.34, 242.44, -87.45),
             (0.408, 0.408, 0.816), height=212.79),
    ], [
        (4.957, 3.725, Leader(((0, -1.6),), arrow=True, weight=3.858)),
    ]),
    'lhs_clear_hands': ('LHS Wall - Clear hands', [
        view('ISO - Tilt up - LHS upright with 1ft gap', (0.2, 0.2, 7.8, 5.4), (-363.24, -297.14, 452.13), (176.34, 242.44, -87.45),
             (0.408, 0.408, 0.816), height=212.79),
    ], [
        (1.068, 2.568, Icon('tu_hand', 1.194, 1.066)),
        (0.431, 2.000, box(1.269, 1.136, weight=3.858)),
        (0.436, 3.136, Leader(((1.264, 1.136),), arrow=False, weight=9.645, color=(255, 0, 0))),
        (2.800, 2.414, Leader(((-0.09, 0.009), (-0.179, 0.014), (-0.269, 0.013), (-0.357, 0.009), (-0.445, -0.001), (-0.531, -0.014), (-0.616, -0.032), (-0.699, -0.055), (-0.779, -0.081), (-0.856, -0.112), (-0.93, -0.147), (-1, -0.186)), arrow=True, weight=3.858)),
    ]),
    'lhs_slide': ('LHS Wall - Slide', [
        view('ISO - Tilt up - LHS upright', (0.2, 0.2, 7.8, 5.4), (-363.24, -297.14, 452.13), (176.34, 242.44, -87.45),
             (0.408, 0.408, 0.816), height=212.79),
    ], [
        (2.700, 4.200, Leader(((1.4, -0.861),), arrow=True, weight=3.858)),
    ]),
    'lhs_clamp': ('LHS Wall - Clamp', [
        view('ISO - Tilt up - LHS missippis', (0.2, 0.164, 7.8, 5.436), (453.45, -310.32, 454.54), (-84.62, 227.75, -83.54),
             (-0.408, 0.408, 0.816), height=187.5),
        view('ISO - Tilt up - LHS clamp close up', (0.2, 0.164, 1.269, 1.136), (430.82, -259.94, 515.66), (10.97, 159.91, 95.81),
             (-0.408, 0.408, 0.816), height=16.64),
    ], [
        (0.200, 0.164, box(1.269, 1.136, weight=3.858)),
    ]),
    'lhs_mississippis': ('LHS Wall - Mississippis', [
        view('ISO - Tilt up - LHS missippis', (0.2, 0.2, 7.8, 5.4), (453.45, -310.32, 454.54), (-84.62, 227.75, -83.54),
             (-0.408, 0.408, 0.816), height=187.5),
    ], [
        (0.936, 2.707, Icon('tu_mallet', 1.199, 1.066)),
        (6.755, 4.741, Icon('tu_nail_gun', 1.199, 1.066)),
        (0.302, 2.139, box(1.269, 1.136, weight=3.858)),
        (6.120, 4.173, box(1.269, 1.136, weight=3.858)),
        (1.570, 3.867, Leader(((-0.058, 0.019), (-0.116, 0.04), (-0.172, 0.064), (-0.226, 0.092), (-0.279, 0.121), (-0.331, 0.154), (-0.38, 0.189), (-0.428, 0.226), (-0.474, 0.266), (-0.518, 0.309), (-0.56, 0.353), (-0.6, 0.4)), arrow=True, weight=3.858)),
        (1.215, 3.399, Label('x3', 0.107, attach=1)),
        (5.497, 4.824, Label('x1', 0.107, attach=1)),
        (2.187, 3.847, Leader(((0.248, -0.092), (0.512, -0.181), (0.791, -0.268), (1.085, -0.353), (1.393, -0.435), (1.716, -0.515), (2.053, -0.592), (2.403, -0.666), (2.767, -0.737), (3.143, -0.806), (3.532, -0.872), (3.933, -0.934)), arrow=True, weight=3.858)),
        (8.285, -8.792, dashed_arc(13.744, -99.1, -113.6, weight=2.3, color=(109, 109, 109))),
        (2.522, 3.686, Leader(((0.2, -0.092),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (8.971, -5.860, dashed_arc(11.016, -105.0, -121.3, weight=2.3, color=(109, 109, 109))),
        (3.010, 3.404, Leader(((0.185, -0.119),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (8.578, -2.002, dashed_arc(7.214, -109.9, -132.7, weight=2.3, color=(109, 109, 109))),
        (3.499, 3.122, Leader(((0.157, -0.154),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (8.121, 0.443, dashed_arc(4.776, -114.8, -146.3, weight=2.3, color=(109, 109, 109))),
        (3.988, 2.840, Leader(((0.112, -0.189),), weight=0.579, head=3.5, color=(109, 109, 109))),
        (8.003, 1.658, dashed_arc(3.644, -121.1, -161.2, weight=2.3, color=(109, 109, 109))),
        (4.469, 2.562, Leader(((0.058, -0.212),), weight=0.579, head=3.5, color=(109, 109, 109))),
    ]),
    'lhs_side_nails': ('LHS Wall - side nails', [
        view('ISO - Tilt up - LHS nails', (0.2, 1.505, 7.8, 4.095), (436.37, -276.73, 487.25), (18.99, 140.65, 69.87),
             (-0.408, 0.408, 0.816), height=85.6),
    ], [
        (0.835, 0.786, Icon('tu_angled_nail_lhs', 1.199, 1.066)),
        (0.835, 2.032, Icon('tu_nail_gun', 1.199, 1.066)),
        (5.966, 0.793, Icon('tu_blocks_in_line', 1.199, 1.066)),
        (7.365, 0.793, Icon('tu_blocks_not_in_line', 1.199, 1.066)),
        (0.200, 0.218, box(1.269, 1.136, weight=3.858)),
        (0.200, 1.464, box(1.269, 1.136, weight=3.858)),
        (1.054, 2.272, Label('x5', 0.107, attach=1)),
        (1.335, 0.935, dashed_line(-0.768, 0.314, weight=3.858, color=(255, 0, 0))),
        (0.554, 0.616, Leader(((0.781, -0.32),), weight=1.929, color=(255, 0, 0))),
        (4.300, 1.600, Leader(((-0.122, 0.109), (-0.27, 0.212), (-0.44, 0.307), (-0.633, 0.396), (-0.846, 0.477), (-1.077, 0.55), (-1.326, 0.615), (-1.589, 0.67), (-1.866, 0.716), (-2.155, 0.752), (-2.455, 0.777), (-2.763, 0.791)), arrow=True, weight=3.858)),
        (6.731, 1.361, Leader(((1.264, 1.136),), arrow=False, weight=9.645, color=(255, 0, 0))),
        (5.331, 0.225, box(1.269, 1.136, weight=3.858)),
        (6.731, 0.225, box(1.269, 1.136, weight=3.858)),
    ]),
    'front_jig': ('Front Wall - Step 1 - Jig', [
        view('ISO - Tilt up - front jig step 1', (0.2, 0.2, 7.8, 5.4), (490.02, -320.58, 391.29), (112.05, 57.39, 13.32),
             (-0.408, 0.408, 0.816), height=334.29),
    ], [
        (4.000, 4.900, Leader(((0.807, 0.602),), arrow=True, weight=3.858)),
    ]),
    'front_off_jig': ('Front Wall - Step 2 - Jig', [
        view('ISO - Tilt up - front jig step 2', (0.2, 0.2, 7.8, 5.4), (490.02, -320.58, 391.29), (112.05, 57.39, 13.32),
             (-0.408, 0.408, 0.816), height=334.29),
    ], [
        (2.300, 3.000, Leader(((0.909, -0.571),), arrow=True, weight=3.858)),
    ]),
    'front_to_platform': ('Front Wall - Step 3 - Jig', [
        view('ISO - Tilt up - front jig step 3', (0.2, 0.2, 7.8, 5.4), (490.02, -320.58, 391.29), (112.05, 57.39, 13.32),
             (-0.408, 0.408, 0.816), height=334.29),
    ], [
    ]),
    'front_align': ('Front Wall - Align', [
        view('ISO - Tilt up - front jig step 5h', (0.2, 0.2, 7.8, 5.4), (435.12, -323.93, 442.84), (57.16, 54.04, 64.87),
             (-0.408, 0.408, 0.816), height=211.25),
    ], [
    ]),
    'front_tilted': ('Front Wall - Tilted', [
        view('ISO - Tilt up - front tilted', (0.2, 0.2, 7.8, 5.4), (435.12, -323.93, 442.84), (57.16, 54.04, 64.87),
             (-0.408, 0.408, 0.816), height=211.25),
    ], [
        (0.918, 4.948, Icon('tu_plywood_carry', 1.199, 1.066)),
        (0.284, 4.380, box(1.269, 1.136, weight=3.858)),
        (2.795, 5.097, Leader(((-0.101, -0.045), (-0.205, -0.08), (-0.311, -0.106), (-0.418, -0.122), (-0.526, -0.129), (-0.634, -0.126), (-0.742, -0.113), (-0.847, -0.092), (-0.951, -0.061), (-1.052, -0.02), (-1.149, 0.029), (-1.243, 0.088)), arrow=True, weight=3.858)),
        (2.236, 4.719, Leader(((-0.013, -0.041), (-0.029, -0.081), (-0.047, -0.119), (-0.067, -0.155), (-0.089, -0.189), (-0.113, -0.22), (-0.138, -0.249), (-0.166, -0.275), (-0.195, -0.299), (-0.225, -0.32), (-0.257, -0.338), (-0.29, -0.353), (-0.324, -0.364), (-0.358, -0.372), (-0.392, -0.376), (-0.426, -0.378), (-0.46, -0.375), (-0.494, -0.37), (-0.528, -0.361), (-0.561, -0.349), (-0.593, -0.334), (-0.624, -0.315), (-0.654, -0.293), (-0.684, -0.268)), arrow=True, weight=3.858)),
    ]),
    'front_upright': ('Front Wall - Upright', [
        view('ISO - Tilt up - front upright', (0.2, 0.2, 7.8, 5.4), (435.12, -323.93, 442.84), (57.16, 54.04, 64.87),
             (-0.408, 0.408, 0.816), height=211.25),
    ], [
    ]),
    'front_clamp': ('Front Wall - Clamp', [
        view('ISO version - Tilt up - front clamps', (0.2, 1.5, 7.8, 4.1), (56.63, 169.31, 167.66), (55.32, -86.11, -43.53),
             (-0.003, -0.637, 0.771), fov=35),
        view('ISO - Tilt up - LHS clamp close up', (0.231, 0.2, 1.269, 1.136), (430.82, -259.94, 515.66), (10.97, 159.91, 95.81),
             (-0.408, 0.408, 0.816), height=16.64),
    ], [
        (0.231, 0.200, box(1.269, 1.136, weight=3.858)),
        (6.020, 1.495, Leader(((0, 0.6), (-3.8, 0.6), (-3.8, 0)), arrow=True, weight=3.858)),
        (2.220, 1.495, Leader(((0, 0.6),), weight=3.858)),
    ]),
    'front_mississippis': ('Front Wall - Mississippis', [
        view('ISO version - Tilt up - front clamps', (0.195, 1.499, 7.805, 4.101), (56.63, 169.31, 167.66), (55.32, -86.11, -43.53),
             (-0.003, -0.637, 0.771), fov=35),
    ], [
        (0.865, 0.768, Icon('tu_mallet', 1.199, 1.066)),
        (7.096, 1.227, Icon('tu_nail_gun', 1.199, 1.066)),
        (0.231, 0.200, box(1.269, 1.136, weight=3.858)),
        (6.462, 0.659, box(1.269, 1.136, weight=3.858)),
        (6.044, 1.078, Label('x1', 0.107, attach=1)),
        (1.004, 1.477, Label('x3', 0.107, attach=1)),
        (3.900, 3.700, Leader(((-0.128, 0.298), (-0.268, 0.589), (-0.421, 0.873), (-0.585, 1.147), (-0.762, 1.414), (-0.95, 1.671), (-1.149, 1.918), (-1.359, 2.156), (-1.579, 2.384), (-1.81, 2.6), (-2.05, 2.806), (-2.3, 3)), arrow=True, weight=3.858)),
        (4.453, 4.300, Leader(((0.035, 0.312), (0.097, 0.617), (0.183, 0.914), (0.294, 1.201), (0.428, 1.478), (0.585, 1.743), (0.763, 1.994), (0.962, 2.23), (1.181, 2.45), (1.419, 2.653), (1.674, 2.837), (1.947, 3)), arrow=True, weight=3.858)),
        (8.355, 3.818, dashed_arc(3.182, 127.8, 182.7, weight=2.3, color=(109, 109, 109))),
        (5.195, 4.258, Leader(((-0.022, 0.219),), weight=0.579, head=3.5, color=(109, 109, 109))),
    ]),
    'front_nail': ('Front Wall - Nail', [
        view('ISO version - Tilt up - front nail', (0.201, 1.504, 7.799, 4.096), (56.63, 169.31, 167.66), (55.32, -86.11, -43.53),
             (-0.003, -0.637, 0.771), fov=35),
    ], [
        (0.835, 0.768, Icon('tu_angled_nail_lhs', 1.199, 1.066)),
        (0.835, 2.072, Icon('tu_nail_gun', 1.199, 1.066)),
        (5.966, 0.768, Icon('tu_blocks_in_line', 1.199, 1.066)),
        (7.365, 0.768, Icon('tu_blocks_not_in_line', 1.199, 1.066)),
        (1.055, 2.313, Label('x5', 0.107, attach=1)),
        (1.335, 0.918, dashed_line(-0.768, 0.314, weight=3.858, color=(255, 0, 0))),
        (0.554, 0.598, Leader(((0.781, -0.32),), weight=1.929, color=(255, 0, 0))),
        (0.200, 0.200, box(1.269, 1.136, weight=3.858)),
        (0.201, 1.504, box(1.269, 1.136, weight=3.858)),
        (2.200, 1.600, Leader(((-0.008, 0.072), (-0.025, 0.144), (-0.053, 0.216), (-0.09, 0.287), (-0.137, 0.358), (-0.194, 0.428), (-0.26, 0.498), (-0.335, 0.566), (-0.42, 0.634), (-0.515, 0.701), (-0.618, 0.767), (-0.731, 0.832)), arrow=True, weight=3.858)),
        (5.800, 1.600, Leader(((-0.28, 0.112), (-0.578, 0.216), (-0.893, 0.314), (-1.225, 0.404), (-1.572, 0.486), (-1.933, 0.561), (-2.307, 0.627), (-2.693, 0.686), (-3.089, 0.735), (-3.495, 0.776), (-3.91, 0.809), (-4.331, 0.832)), arrow=True, weight=3.858)),
        (6.731, 1.336, Leader(((1.264, 1.136),), arrow=False, weight=9.645, color=(255, 0, 0))),
        (5.331, 0.200, box(1.269, 1.136, weight=3.858)),
        (6.731, 0.200, box(1.269, 1.136, weight=3.858)),
    ]),
}
