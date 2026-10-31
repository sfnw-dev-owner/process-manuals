"""tilt-up/tilt-up.md figures: pages of views of the tilt-up (model/tilt_up.py).

Each page is an isometric view of the platform and the walls as they are
at that step (SCENES), from above one of the house's corners, framed on
what it shows; a close-up of a corner's clamps may sit in an inset. The
notes are the tool insets at the page's corners, arrows from them to where
the tool is used, and arrows for the walls' moves, all hung on points of
the model (the renderer projects them)."""

import math

from build123d import Plane, Pos, Rot, Vector

from model.house import house
from model.notes import Icon, Label, Leader, dashed_line
from model.platform_assembly import DECK, PLATFORM_LENGTH, PLATFORM_WIDTH, platform
from model import tilt_up as tu
from model.walls import SIDE_STUDS, STUD, WALL_DEPTH, WALL_HEIGHT

from . import Figure
from .pages import (
    GRAY, PAGE, RED, arrow_to, center_of, frame, inset, inset_edge, inset_rect, iso, main_rect, move_arrow,
    perspective, pointer_to, up_arrow, view,
)

MD = "tilt-up/tilt-up.md"
LOWER = main_rect(1.5)  # the main view under a row of insets
# Looking down the house from above its rear end: the front wall's corners
# and their clamps.
OVER_REAR = ((PLATFORM_WIDTH / 2, -5, DECK + 150), (PLATFORM_WIDTH / 2, PLATFORM_LENGTH + 85, DECK - 60))
NAILING_STEP = 16  # the nailer follows the mallet along the bottom plate, a stud bay at a time
NAILING_ARCS = 5  # how many more nailing points the dashed arcs show
MOVE_ARROW = 0.8  # an arrow for a wall's move, page inches
RAISE_ARROW = 1.4  # the arrow up for a wall tilting up


# ── what each page shows ────────────────────────────────────────────────────
# A scene is a list of what's in it: "platform"; ("wall", wall, stage);
# ("jig", wall); ("crew", group); "brace"; ("corner", corner); ("nails",
# corner); "brace_tools".

RHS = ("wall", "rhs", "upright")
BACK = ("wall", "back", "upright")
LHS = ("wall", "lhs", "upright")
BASE = ["platform", RHS, "brace"]  # after the first wall is up and braced
LHS_BASE = ["platform", RHS, BACK]  # the brace comes off before the second side wall goes up
FRONT_BASE = ["platform", RHS, BACK, LHS]

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
    "lhs_jig": LHS_BASE + [("jig", "lhs"), ("wall", "lhs", "on_jig"), ("crew", "lhs_jig"), ("crew", "lhs_platform")],
    "lhs_tilted": LHS_BASE + [("wall", "lhs", "tilted")],
    "lhs_clear_hands": LHS_BASE + [("wall", "lhs", "gap")],
    "lhs_slide": LHS_BASE + [LHS],
    "lhs_clamp": LHS_BASE + [LHS, ("corner", "back_lhs")],
    "lhs_mississippis": LHS_BASE + [LHS, ("corner", "back_lhs")],
    "lhs_side_nails": LHS_BASE + [LHS, ("corner", "back_lhs"), ("nails", "back_lhs")],
    "front_jig": FRONT_BASE + [("crew", "front_platform"), ("jig", "front"), ("wall", "front", "on_jig"),
                               ("crew", "front_jig")],
    "front_off_jig": FRONT_BASE + [("crew", "front_platform"), ("jig", "front"), ("wall", "front", "carried"),
                                   ("crew", "front_carried")],
    "front_to_platform": FRONT_BASE + [("crew", "front_platform"), ("jig", "front"), ("wall", "front", "at_platform"),
                                       ("crew", "front_at_platform")],
    "front_align": FRONT_BASE + [("wall", "front", "at_platform")],
    "front_tilted": FRONT_BASE + [("wall", "front", "tilted")],
    "front_upright": FRONT_BASE + [("wall", "front", "upright")],
    "front_clamp": FRONT_BASE + [("wall", "front", "upright"), ("corner", "front_lhs"), ("corner", "front_rhs")],
    "front_mississippis": FRONT_BASE + [("wall", "front", "upright"), ("corner", "front_lhs"), ("corner", "front_rhs")],
    "front_nail": FRONT_BASE + [("wall", "front", "upright"), ("corner", "front_lhs"), ("corner", "front_rhs"),
                                ("nails", "front_lhs"), ("nails", "front_rhs")],
}


def facing(direction):
    """How far to turn a cut-out person (about Z) to face a camera looking
    along `direction`."""
    dx, dy = -direction[0], -direction[1]
    return math.degrees(math.atan2(-dx, dy))


def parts(scene, direction):
    """[shape] for a scene, seen along `direction` (the people face it)."""
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
            turn = facing(direction)
            for x, y, z, mirror in tu.CREW[item[1]]:
                s = kind.shape()
                if mirror:
                    s = s.mirror(Plane.YZ)
                out.append(Pos(x, y, z) * Rot(Z=turn) * s)
        elif item[0] == "corner":
            out += [loc * c.shape() for c, loc in tu.CORNERS[item[1]] if c in (tu.bar_clamp, tu.door_clamp)]
        elif item[0] == "nails":
            out += [loc * c.shape() for c, loc in tu.CORNERS[item[1]] if c is tu.nail]
    return out


def clamps(corner):
    return [loc * c.shape() for c, loc in tu.CORNERS[corner] if c in (tu.bar_clamp, tu.door_clamp)]


def nails(corner):
    return [loc * c.shape() for c, loc in tu.CORNERS[corner] if c is tu.nail]


def top_nail(corner):
    """Where the highest of a corner's nails is."""
    return max((loc.position for c, loc in tu.CORNERS[corner] if c is tu.nail), key=lambda p: p.Z)


def wall_box(wall, stage):
    comp, loc = tu.wall_at(wall, stage)
    return (loc * comp.shape()).bounding_box()


def wall_top(wall, stage):
    """The middle of a wall's top edge at a stage."""
    bb = wall_box(wall, stage)
    return ((bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, bb.max.Z)


def wall_center(wall, stage):
    return tuple(wall_box(wall, stage).center())


# ── the pages ──────────────────────────────────────────────────────────────

def mississippis(corner, wall_point, along, mallet_at, gun_at):
    """The mallet-and-nail-gun page: the mallet inset and the nail gun inset
    (corners of the page), arrows from them to the first strike at the
    bottom plate's end, and dashed arcs on to the nailing points along it."""
    mallet, gun = inset_rect(*mallet_at), inset_rect(*gun_at)
    notes = inset("tu_mallet", *mallet_at, count="x3") + inset("tu_nail_gun", *gun_at, count="x1")
    mallet_side = "right" if "left" in mallet_at[0] else "left"
    gun_side = "right" if "left" in gun_at[0] else "left"
    view_notes = [arrow_to(wall_point, mallet, mallet_side, curve=0.2), arrow_to(wall_point, gun, gun_side, curve=-0.15)]
    for k in range(1, NAILING_ARCS + 1):
        p = tuple(w + a * NAILING_STEP * k for w, a in zip(wall_point, along))
        view_notes.append(arrow_to(p, gun, gun_side, curve=-0.15, weight=1.5, color=GRAY, dash=(0.08, 0.06), head=1.2))
    return notes, view_notes


def clamp_inset(corner, corner_name, at=("top left", 0)):
    """A close-up of a corner's upper clamp in an inset, framed."""
    rect = inset_rect(*at)
    upper = max(clamps(corner_name), key=lambda s: s.bounding_box().max.Z)
    return view(rect, corner, clamps(corner_name) + [platform.shape()] + [loc * c.shape() for c, loc in
                [tu.wall_at(w, "upright") for w in ("rhs", "back", "lhs")]], fit=[upper], margin=0.15), [frame(rect)]


def nail_page(corner, corner_name, icon):
    """A corner's nailing page: a close-up on the corner's clamps and nails,
    the angled nail and nail gun insets at the left, the blocks-in-line
    insets at the right, the gun's arrow to the top nail."""
    angled, gun = inset_rect("top left"), inset_rect("top left", row=1)
    notes = inset(icon, "top left") + inset("tu_nail_gun", "top left", row=1, count="x5")
    notes += inset("tu_blocks_in_line", "top right", 1) + inset("tu_blocks_not_in_line", "top right", 0, struck=True)
    # the toe-nailing angle, drawn on the angled nail's picture: dashed red up along the nail, then the arrow
    x, y, w, h = angled
    a, b = (x + 0.22 * w, y + 0.65 * h), (x + 0.97 * w, y + 0.33 * h)
    notes += [(a[0], a[1], dashed_line(b[0] - a[0], -(b[1] - a[1]), weight=3, color=RED)),
              (b[0], b[1], Leader(((a[0] - b[0], -(a[1] - b[1])),), weight=2, color=RED))]
    fit = clamps(corner_name) + nails(corner_name)
    scene = parts(SCENES[f"{corner_name.split('_')[0]}_nail" if corner_name == "back_rhs" else "lhs_side_nails"], iso(corner))
    main = view(LOWER, corner, scene, fit=fit, margin=0.1, notes=[arrow_to(tuple(top_nail(corner_name)), gun, "right", curve=-0.2)])
    return [main], notes


def figures(only=None):
    rhs_rear = (0, 0, DECK)  # where the rhs wall's bottom plate meets the platform's rear end
    pages = {}

    def page(name, corner, fit=None, margin=0.05, view_notes=(), notes=(), rect=None, views=()):
        if only is not None and name not in only:
            return
        main = view(rect or main_rect(), corner, parts(SCENES[name], iso(corner)), fit=fit, margin=margin, notes=view_notes)
        pages[name] = ([main] + list(views), list(notes))

    # ── the rhs wall ──
    # the platform's edge where the wall comes to: the arrow from the jig to it
    page("rhs_jig", "rear rhs", view_notes=[move_arrow(wall_center("rhs", "on_jig"), (0, PLATFORM_LENGTH / 2, DECK), "rear rhs", MOVE_ARROW)])
    page("rhs_tilting", "rear rhs", view_notes=[up_arrow(wall_top("rhs", "tilted"), RAISE_ARROW)])
    page("rhs_upright", "rear rhs")
    brace = tu.BRACE_AT * tu.wall_brace.shape()
    brace_top = max((loc.position for _, loc in tu.BRACE_NAILS), key=lambda p: p.Z)
    driver = (*brace_top, Icon("drill_icon", 0.6, 0.56, rotation=30, dx=-0.35, dy=0.57))
    page("rhs_brace", "front lhs", fit=[brace], margin=0.3, view_notes=[driver])
    notes, view_notes = mississippis("rear lhs", (0, 2, DECK), (0, 1, 0), ("middle left", 0), ("top right", 0))
    page("rhs_mississippis", "rear lhs", view_notes=view_notes, notes=notes)

    # ── the back wall ──
    crews = {"A": tu.CREW["back_jig"][1], "B": tu.CREW["back_jig"][4]}
    labels = [(x, y, z + 75, Label(letter, 0.11)) for letter, (x, y, z, _) in crews.items()]
    page("back_jig", "rear lhs", view_notes=labels + [move_arrow(wall_center("back", "on_jig"), (PLATFORM_WIDTH, 40, DECK), "rear lhs", MOVE_ARROW)])
    page("back_off_jig", "rear lhs", view_notes=[move_arrow(wall_center("back", "carried"), wall_center("back", "at_platform"), "rear lhs", MOVE_ARROW, at=0.4)])
    page("back_to_platform", "rear lhs")
    page("back_raise", "rear lhs", view_notes=[up_arrow(wall_top("back", "tilted"), RAISE_ARROW)])
    hand = inset_rect("middle left")
    gap = (tu.STAGES["back"]["gap"].position.X / 2, 2, DECK + WALL_HEIGHT / 2)  # between the back wall's end and the rhs wall
    page("back_clear_hands", "rear lhs", notes=inset("tu_hand", "middle left", struck=True), view_notes=[arrow_to(gap, hand, "right", curve=0.15)])
    over = DECK + WALL_HEIGHT + 8  # the arrow just over the wall's top
    page("back_slide", "rear lhs", view_notes=[move_arrow((tu.STAGES["back"]["gap"].position.X, 0, over), (0, 0, over), "rear lhs", 1.2)])
    close, close_notes = clamp_inset("front lhs", "back_rhs")
    upper_clamp = max((loc for c, loc in tu.CORNERS["back_rhs"] if c is tu.bar_clamp), key=lambda l: l.position.Z)
    page("back_clamp", "front lhs", rect=LOWER, views=[close], notes=close_notes,
         view_notes=[arrow_to(tuple(upper_clamp.position), inset_rect("top left"), "bottom", curve=-0.2)])
    notes, view_notes = mississippis("front lhs", (6, 0, DECK), (1, 0, 0), ("top left", 0), ("bottom left", 0))
    page("back_mississippis", "front lhs", view_notes=view_notes, notes=notes)
    if only is None or "back_nail" in only:
        pages["back_nail"] = nail_page("front lhs", "back_rhs", "tu_angled_nail_rhs")

    # ── the lhs wall ──
    crews = {"A": tu.CREW["lhs_jig"][1], "B": tu.CREW["lhs_jig"][3]}
    labels = [(x, y, z + 75, Label(letter, 0.11)) for letter, (x, y, z, _) in crews.items()]
    page("lhs_jig", "front lhs", view_notes=labels + [move_arrow(wall_center("lhs", "on_jig"), (PLATFORM_WIDTH, PLATFORM_LENGTH / 2, DECK), "front lhs", MOVE_ARROW)])
    page("lhs_tilted", "front lhs", view_notes=[up_arrow(wall_top("lhs", "tilted"), RAISE_ARROW)])
    gap = (PLATFORM_WIDTH - 2, tu.STAGES["lhs"]["gap"].position.Y / 2, DECK + WALL_HEIGHT / 2)
    page("lhs_clear_hands", "front lhs", notes=inset("tu_hand", "middle left", struck=True), view_notes=[arrow_to(gap, hand, "right", curve=0.15)])
    page("lhs_slide", "front lhs", view_notes=[move_arrow((PLATFORM_WIDTH, tu.STAGES["lhs"]["gap"].position.Y, over), (PLATFORM_WIDTH, 0, over), "front lhs", 1.2)])
    close, close_notes = clamp_inset("front rhs", "back_lhs")
    page("lhs_clamp", "front rhs", views=[close], notes=close_notes)
    notes, view_notes = mississippis("front rhs", (PLATFORM_WIDTH, 2, DECK), (0, 1, 0), ("middle left", 0), ("bottom right", 0))
    page("lhs_mississippis", "front rhs", view_notes=view_notes, notes=notes)
    if only is None or "lhs_side_nails" in only:
        pages["lhs_side_nails"] = nail_page("front rhs", "back_lhs", "tu_angled_nail_lhs")

    # ── the front wall ──
    crews = {"A": tu.CREW["front_jig"][1], "B": tu.CREW["front_jig"][4]}
    page("front_jig", "front rhs", view_notes=[move_arrow(wall_center("front", "on_jig"), wall_center("front", "carried"), "front rhs", MOVE_ARROW, at=0.6)])
    page("front_off_jig", "front rhs", view_notes=[move_arrow(wall_center("front", "carried"), wall_center("front", "at_platform"), "front rhs", MOVE_ARROW, at=0.4)])
    page("front_to_platform", "front rhs")
    page("front_align", "front rhs")
    page("front_upright", "front rhs")
    carry = inset_rect("bottom left")
    tilted = tu.STAGES["front"]["tilted"] * tu.FUNKY_BOARD_16
    ends = [tuple((tilted * Pos(x, 0, 0)).position) for x in (12, 84)]  # funky board #16's ends, under the tilted wall
    page("front_tilted", "front rhs", notes=inset("tu_plywood_carry", "bottom left"),
         view_notes=[arrow_to(p, carry, "right", curve=c) for p, c in zip(ends, (0.2, -0.1))])
    # looking down the house from over its rear: the front corners
    eye, target = OVER_REAR
    corners = [(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, DECK + WALL_HEIGHT), (PLATFORM_WIDTH - WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, DECK + WALL_HEIGHT)]

    def front_page(name, notes=(), view_notes=(), views=()):
        if only is not None and name not in only:
            return
        main = perspective(LOWER, eye, target, parts(SCENES[name], (0, 1, -1)), notes=list(view_notes))
        pages[name] = ([main] + list(views), list(notes))

    close, close_notes = clamp_inset("front rhs", "back_lhs")
    both = [pointer_to(c, (PAGE[0] / 2, 1.35)) for c in corners]  # the clamps go at both corners
    front_page("front_clamp", notes=close_notes, views=[close], view_notes=both)
    notes, view_notes = mississippis("front rhs", (WALL_DEPTH + 4, PLATFORM_LENGTH - WALL_DEPTH, DECK), (1, 0, 0), ("top left", 0), ("top right", 0))
    front_page("front_mississippis", notes=notes, view_notes=view_notes)
    gun = inset_rect("top left", row=1)
    notes = inset("tu_angled_nail_lhs", "top left") + inset("tu_nail_gun", "top left", row=1, count="x5")
    notes += inset("tu_blocks_in_line", "top right", 1) + inset("tu_blocks_not_in_line", "top right", 0, struck=True)
    x, y, w, h = inset_rect("top left")
    a, b = (x + 0.22 * w, y + 0.65 * h), (x + 0.97 * w, y + 0.33 * h)
    notes += [(a[0], a[1], dashed_line(b[0] - a[0], -(b[1] - a[1]), weight=3, color=RED)),
              (b[0], b[1], Leader(((a[0] - b[0], -(a[1] - b[1])),), weight=2, color=RED))]
    front_page("front_nail", notes=notes, view_notes=[arrow_to(tuple(top_nail(c)), gun, "right", curve=k)
                                                      for c, k in (("front_lhs", -0.15), ("front_rhs", 0.15))])

    return [Figure(MD, name, page=PAGE, viewports=views, notes=notes) for name, (views, notes) in pages.items()]
