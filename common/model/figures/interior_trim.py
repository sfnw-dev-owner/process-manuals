"""Interior_Trim/interior_trim.md figures: the walls seen from inside, as they
are at each trim step: panels outlined, trim from earlier steps light gray,
this step's black; details of the window shelves in plan."""

from build123d import Align, Box, Location, Pos

from model.common import OPTIONAL, key
from model.interior import (
    DOOR_SIDE_WALL_AT, FAR_SIDE_WALL_AT, FRONT_WALL_AT, SHELF_TOP, SHELF_Z, front_wall_interior,
    rear_wall_interior, side_wall_interior_door_side, side_wall_interior_far_side,
)
from model.interior_notes import (
    FRONT_SHELF_PLAN, FRONT_TRIM_VIEWS, FRONT_WINDOW_LOWER_VIEW, REAR_SHELF_PLAN, REAR_TRIM_VIEWS, SIDE_TRIM_VIEWS,
)
from model.interior_roof import END_INTERIOR_AT, end_wall_interior
from model.walls import WINDOW_WIDTH, WINDOW_X, WINDOW_Z, front_wall_framing, rear_wall_framing, window_unit_at

from . import TYVEK, Figure, figure_names, placed_notes

MD = "Interior_Trim/interior_trim.md"
ORDER = [
    "baseboards", "rear_shelf", "rear_window_trim", "top_trim", "vertical_trim", "horizontal_trim",
    "triangle_trim", "front_baseboard", "front_shelf", "front_window_trim", "front_trim_a", "front_trim_b",
    "final_trim",
]
PANELS = {"panels", "panel_d", "panel_e2"}
SHELVES = {"rear_shelf", "front_shelf"}  # drawn outlined, even when new
DONE = TYVEK  # the drawings' light gray for trim already in place

# The lower sash's glass, hatched in the drawings (the window unit is
# SketchUp's, without its panes): in the wall's frame.
GLASS = (WINDOW_X + 1/2, WINDOW_Z + 1/2, WINDOW_WIDTH - 1, 16 + 3/8)


# The window liners: drawn (black) in the step that installs them, left out
# of later views (their edges just cluttered the window there).
LINERS = {"rear_window_liner": "rear_window_trim", "front_window_liner": "front_window_trim"}


def styled(tag, step, new, also=()):
    if tag in PANELS:
        return ("outline",)
    if tag in LINERS:
        return ("new",) if LINERS[tag] in new else None
    if tag in new:
        return ("outline",) if tag in SHELVES else ("new",)
    if tag in also or (tag in ORDER and ORDER.index(tag) < ORDER.index(step)):
        return ("outline", DONE)
    return None


def wall_parts(view, component, step, new, loc=Location(), hide=(), also=()):
    """A wall interior component's pieces as they are at `step` (those tagged
    in `hide` left out, those in `also` drawn as done though later)."""
    tags = {t for t in component.tags() if not t.startswith(OPTIONAL) and t}
    out = []
    for tag in sorted(tags):
        style = None if tag in hide else styled(tag, step, new, also)
        if style:
            shape = component.shape(frozenset(tags - {tag}))
            if shape.solids():
                out.append((view * loc * shape, *style))
    return out


def window(view):
    comp, loc, mods, _ = window_unit_at()
    x, z, w, h = GLASS
    glass = Pos(x, -1, z) * Box(w, 1, h, align=Align.MIN)
    return [(view * glass, "bare", "glass"), (view * loc * comp.shape(frozenset(), key(mods)), "outline")]


def gable(view, triangle_trim):
    """The end wall's gable: its panels outlined, and its trim too, or black
    ("new") in the step that installs it, or left out before that."""
    tags = {t for t in end_wall_interior.tags() if not t.startswith(OPTIONAL)}
    panels = END_INTERIOR_AT * end_wall_interior.shape(frozenset({"triangle_trim"}), key(["mirror"]))
    out = [(view * panels, "outline")]
    if triangle_trim == "new":
        trim = END_INTERIOR_AT * end_wall_interior.shape(frozenset(tags - {"triangle_trim"}), key(["mirror"]))
        out.append((view * trim, "new"))
    elif triangle_trim:
        trim = END_INTERIOR_AT * end_wall_interior.shape(frozenset(tags - {"triangle_trim"}), key(["mirror"]))
        out.append((view * trim, "outline"))
    return out


def door(view):
    from model.house import house
    out = []
    for comp, loc, mods, _ in house()[1]:
        if comp.__module__ == "model.doors":
            out.append((view * FRONT_WALL_AT.inverse() * loc * comp.shape(frozenset(), key(mods)), "outline"))
    return out


def rear(view, step, new=None, hide=(), also=()):
    new = new or {step}
    tri = "new" if step == "triangle_trim" else ORDER.index(step) > ORDER.index("triangle_trim")
    return wall_parts(view, rear_wall_interior, step, new, hide=hide, also=also) + window(view) + gable(view, tri)


def front(view, step, new=None):
    new = new or {step}
    tri = "new" if step == "front_trim_b" else ORDER.index(step) > ORDER.index("front_trim_b")
    in_front = FRONT_WALL_AT.inverse()
    sides = (wall_parts(view, side_wall_interior_door_side, step, new & {"front_trim_a"}, in_front * DOOR_SIDE_WALL_AT)
             + wall_parts(view, side_wall_interior_far_side, step, new & {"front_trim_b"}, in_front * FAR_SIDE_WALL_AT))
    sides = [p for p in sides if p[1] == "new"]  # only the corner trim seen edge on
    return wall_parts(view, front_wall_interior, step, new) + window(view) + gable(view, tri) + door(view) + sides


def side_strip(x0, y0, x1, y1):
    """The side wall's 2" corner trim as the front-wall drawings showed it: a
    hatched strip beside the wall (the trim's face, unfolded), in the
    drawing's frame."""
    return (Pos(x0, y0, 0) * Box(x1 - x0, y1 - y0, 0.5, align=Align.MIN), "outline", "laid")


def side(view, step, new=None):
    parts = wall_parts(view, side_wall_interior_far_side, step, new or {step})
    if step == "top_trim":  # the short front piece hatched, as the drawing told the two pieces apart
        out = []
        for shape, style, *rest in parts:
            solids = shape.solids() if style == "new" else []
            if len(solids) == 2:
                short = min(solids, key=lambda s: s.bounding_box().size.X)
                out += [(s, "new") if s is not short else (s, "outline", "laid") for s in solids]
            else:
                out.append((shape, style, *rest))
        return out
    return parts


def shelf_plan(plan, component, framing, step):
    """A plan of the shelf and what it's against, cut at the shelf."""
    half = WINDOW_WIDTH / 2 + 14  # as far as the detail's circle
    cut = Pos(WINDOW_X + WINDOW_WIDTH / 2 - half, -50, SHELF_Z) * Box(2 * half, 100, SHELF_TOP - SHELF_Z - 0.01, align=Align.MIN)
    parts = []
    for shape, style in ((component.shape(frozenset({t for t in component.tags() if t not in PANELS | {step}})), "outline"),
                         (framing.shape(), "outline")):
        section = shape & cut
        if section.solids():
            parts.append((plan * Pos(0, 0, -SHELF_Z) * section, style))
    return parts


def notes(figure):
    component, view = ((rear_wall_interior, REAR_TRIM_VIEWS[figure]) if figure in REAR_TRIM_VIEWS
                       else (front_wall_interior, FRONT_TRIM_VIEWS[figure]))
    return placed_notes(view, component, {"manual:interior_trim", f"manual:interior_trim:{figure}"})


def figures():
    r, s, f = REAR_TRIM_VIEWS, SIDE_TRIM_VIEWS, FRONT_TRIM_VIEWS
    steps = [
        # (the drawing showed the rear shelf, though it comes later)
        ("baseboards", rear(r["baseboards"], "baseboards", also={"rear_shelf"}) + side(s["baseboards"], "baseboards")),
        # (the rear window's drawings left the baseboards out)
        ("rear_shelf", rear(r["rear_shelf"], "rear_shelf", hide={"baseboards"})
         + shelf_plan(REAR_SHELF_PLAN, rear_wall_interior, rear_wall_framing, "rear_shelf")),
        ("rear_window_trim", rear(r["rear_window_trim"], "rear_window_trim", hide={"baseboards"})),
        ("top_trim", rear(r["top_trim"], "top_trim") + side(s["top_trim"], "top_trim")),
        ("vertical_trim", rear(r["vertical_trim"], "vertical_trim") + side(s["vertical_trim"], "vertical_trim")),
        ("horizontal_trim", rear(r["horizontal_trim"], "horizontal_trim") + side(s["horizontal_trim"], "horizontal_trim")),
        ("triangle_trim", rear(r["triangle_trim"], "triangle_trim")),
        ("front_window", front(f["front_window"], "front_shelf", {"front_baseboard", "front_shelf"})
         + shelf_plan(FRONT_SHELF_PLAN, front_wall_interior, front_wall_framing, "front_shelf")
         + front(FRONT_WINDOW_LOWER_VIEW, "front_window_trim")),
        ("front_trim_a", front(f["front_trim_a"], "front_trim_a") + [side_strip(3.4, 133.91, 4.9, 214.91)]),
        ("front_trim_b", front(f["front_trim_b"], "front_trim_b") + [side_strip(105.48, 133.65, 106.98, 214.65)]),
        ("final_trim", front(f["final_trim"], "final_trim") + side(s["final_trim"], "final_trim")),
    ]
    out = []
    for fig_name, (name, parts) in zip(figure_names(MD), steps):
        out.append(Figure(MD, fig_name, parts, notes(name)))
    return out
