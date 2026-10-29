"""Interior_Trim/interior_trim.md figures: the walls seen from inside, as they
are at each trim step: panels outlined, trim from earlier steps light gray,
this step's black; details of the window shelves in plan.

The manual is a table of its figures: each figure's walls (one under the
other), and its notes hung on the trim pieces' extents in the drawing."""

import math

from build123d import Align, Box, Location, Pos

from model.common import key
from model.interior import (
    BASEBOARD_TOP, DOOR_SIDE_WALL_AT, END_INSIDE, FAR_SIDE_WALL_AT, FRONT_WALL_AT, PANEL, SHELF_TOP, SHELF_Z, TOP_TRIM_Z,
    W, front_wall_interior, rear_wall_interior, side_wall_interior_door_side, side_wall_interior_far_side,
)
from model.interior_roof import END_INTERIOR_AT, end_wall_interior
from model.notes import (
    CIRCLED, SMALL, TITLE, Label, Leader, aimed, around, at, beside, callout, cross, line, next_to, numbered, numbered_row,
    pointer, title,
)
from model.walls import WINDOW_WIDTH, WINDOW_X, WINDOW_Z, front_wall_framing, rear_wall_framing, window_unit_at

from . import TYVEK, Extent, extent, table
from .interior_panels import INSIDE_VIEW

MD = "Interior_Trim/interior_trim.md"
ORDER = [
    "baseboards", "rear_shelf", "rear_window_trim", "top_trim", "vertical_trim", "horizontal_trim",
    "triangle_trim", "front_baseboard", "front_shelf", "front_window_trim", "front_trim_a", "front_trim_b",
    "final_trim",
]
PANELS = {"panels", "panel_d", "panel_e2"}
SHELVES = {"rear_shelf", "front_shelf"}  # drawn outlined, even when new
DONE = TYVEK  # the drawings' light gray for trim already in place
SCREW = 0.7  # the screw icon, scaled down
STRIP_GAP = 8  # a side wall's corner trim, unfolded beside the front wall, this far off it
PLAN_GAP = 16  # a shelf's plan this far right of its wall
BLOCK_MARK_IN = 2  # a support block's end screws this far in from its ends
BLOCK_MARK_DOWN = 3/4  # and from its top

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


def wall_parts(component, step, new, loc=Location(), hide=(), also=()):
    """A wall interior component's pieces as they are at `step` (those tagged
    in `hide` left out, those in `also` drawn as done though later), seen
    from inside."""
    tags = {t for t in component.tags() if t}
    out = []
    for tag in sorted(tags):
        style = None if tag in hide else styled(tag, step, new, also)
        if style:
            shape = component.shape(frozenset(tags - {tag}))
            if shape.solids():
                out.append((INSIDE_VIEW * loc * shape, *style))
    return out


def pieces(component, tag, loc=Location()):
    """The extents, in the drawing, of a wall's pieces tagged `tag`, in order
    left to right (then bottom to top)."""
    out = []
    for c, l, mods, t in component()[1]:
        if t == tag:
            out += [Extent(s) for s in (INSIDE_VIEW * loc * l * c.shape(frozenset(), key(mods))).solids()]
    return sorted(out, key=lambda e: (e.x0, e.y0))


def tall(exts):
    return [e for e in exts if e.height > e.width]


def wide(exts):
    return [e for e in exts if e.width >= e.height]


def window():
    comp, loc, mods, _ = window_unit_at()
    x, z, w, h = GLASS
    glass = Pos(x, -1, z) * Box(w, 1, h, align=Align.MIN)
    return [(INSIDE_VIEW * glass, "bare", "glass"), (INSIDE_VIEW * loc * comp.shape(frozenset(), key(mods)), "outline")]


def gable_trim():
    """An end wall's triangle trim, in the wall's frame."""
    tags = set(end_wall_interior.tags())
    return END_INTERIOR_AT * end_wall_interior.shape(frozenset(tags - {"triangle_trim"}), key(["mirror"]))


def gable(triangle_trim):
    """The end wall's gable: its panels outlined, and its trim too, or black
    ("new") in the step that installs it, or left out before that."""
    panels = END_INTERIOR_AT * end_wall_interior.shape(frozenset({"triangle_trim"}), key(["mirror"]))
    out = [(INSIDE_VIEW * panels, "outline")]
    if triangle_trim == "new":
        out.append((INSIDE_VIEW * gable_trim(), "new"))
    elif triangle_trim:
        out.append((INSIDE_VIEW * gable_trim(), "outline"))
    return out


def gable_trim_pieces():
    """The triangle trim's pieces in the drawing: the left and right angled
    pieces, and the center piece."""
    exts = [Extent(s) for s in (INSIDE_VIEW * gable_trim()).solids()]
    center = min(exts, key=lambda e: e.width)
    angled = sorted((e for e in exts if e is not center and e.height > 4), key=lambda e: e.x0)
    return angled[0], angled[-1], center


def door():
    from model.house import house
    out = []
    for comp, loc, mods, _ in house()[1]:
        if comp.__module__ == "model.doors":
            out.append((INSIDE_VIEW * FRONT_WALL_AT.inverse() * loc * comp.shape(frozenset(), key(mods)), "outline"))
    return out


def rear(step, new=None, hide=(), also=()):
    new = new or {step}
    tri = "new" if step == "triangle_trim" else ORDER.index(step) > ORDER.index("triangle_trim")
    return wall_parts(rear_wall_interior, step, new, hide=hide, also=also) + window() + gable(tri)


def front(step, new=None):
    new = new or {step}
    tri = "new" if step == "front_trim_b" else ORDER.index(step) > ORDER.index("front_trim_b")
    in_front = FRONT_WALL_AT.inverse()
    sides = (wall_parts(side_wall_interior_door_side, step, new & {"front_trim_a"}, in_front * DOOR_SIDE_WALL_AT)
             + wall_parts(side_wall_interior_far_side, step, new & {"front_trim_b"}, in_front * FAR_SIDE_WALL_AT))
    sides = [p for p in sides if p[1] == "new"]  # only the corner trim seen edge on
    return wall_parts(front_wall_interior, step, new) + window() + gable(tri) + door() + sides


def side_strip(side):
    """A side wall's 2" corner trim as the front-wall drawings showed it: a
    hatched strip beside the wall (the trim's face, unfolded)."""
    x = END_INSIDE[0] - STRIP_GAP - W if side == "left" else END_INSIDE[1] + STRIP_GAP
    strip = Pos(x, -PANEL, BASEBOARD_TOP) * Box(W, 0.5, TOP_TRIM_Z - BASEBOARD_TOP, align=Align.MIN)
    return (INSIDE_VIEW * strip, "outline", "laid")


def side(step, new=None):
    parts = wall_parts(side_wall_interior_far_side, step, new or {step})
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


def shelf_plan(component, framing, step):
    """A plan of the shelf and what it's against, cut at the shelf: x along
    the wall, y into the house (the room at the bottom); and the framing's
    sections' extents."""
    half = WINDOW_WIDTH / 2 + 14  # as far as the detail's circle
    cut = Pos(WINDOW_X + WINDOW_WIDTH / 2 - half, -50, SHELF_Z) * Box(2 * half, 100, SHELF_TOP - SHELF_Z - 0.01, align=Align.MIN)
    parts, studs = [], []
    for shape, is_framing in ((component.shape(frozenset({t for t in component.tags() if t not in PANELS | {step}})), False),
                              (framing.shape(), True)):
        section = shape & cut
        if section.solids():
            section = Pos(0, 0, -SHELF_Z) * section
            parts.append((section, "outline"))
            if is_framing:
                studs += [Extent(s) for s in section.solids()]
    return parts, studs


def studs_behind(framing, x0, x1, margin=5):
    """The x (wall frame) of the framing's stud lines between x0 and x1,
    `margin` in from them (a pair of studs side by side counts once)."""
    xs = []
    for s in framing.shape().solids():
        bb = s.bounding_box()
        if bb.size.Z > 40 and bb.size.X < 4 and x0 + margin < bb.center().X < x1 - margin:
            xs.append(bb.center().X)
    out = []
    for x in sorted(xs):
        if out and x - out[-1][-1] < 4:
            out[-1].append(x)
        else:
            out.append([x])
    return [sum(pair) / len(pair) for pair in out]


def moved(parts, dx, dy):
    return [(Pos(dx, dy, 0) * p[0], *p[1:]) for p in parts]


def layout(groups, gap):
    """Groups of parts drawn one under the other (the first at the top),
    centered, `gap` apart: the (dx, dy) moving each group, and its extent
    once moved."""
    offsets, exts, y = [], [], 0
    for parts in groups:
        e = extent(parts)
        dx, dy = -e.center[0], y - e.y1
        offsets.append((dx, dy))
        exts.append(Extent.box(e.x0 + dx, e.y0 + dy, e.x1 + dx, e.y1 + dy))
        y -= e.height + gap
    return offsets, exts


def shifted(ext, dx, dy):
    return Extent.box(ext.x0 + dx, ext.y0 + dy, ext.x1 + dx, ext.y1 + dy)


def toward(circle_center, point, scale, radius=CIRCLED):
    """A leader from a circled number's edge to a point (as numbered() draws,
    for a second piece the number also marks)."""
    dx, dy = (circle_center[0] - point[0]) * scale, (circle_center[1] - point[1]) * scale
    d = math.hypot(dx, dy)
    return pointer(point, dx * (d - radius) / d, dy * (d - radius) / d)


def circle_of(notes):
    """The center of the circle in notes numbered() returned, in the drawing."""
    x, y, c = notes[0]
    return (x + c.dx / SCALE[0], y + c.dy / SCALE[0])


SCALE = [1/40]  # the scale the figures are being built at (for circle_of)


def figures(scale=1/40):
    SCALE[0] = scale
    gap = 1.5 / scale  # between walls drawn one under the other: room for a row of notes
    rows = {}
    k = 1 / scale  # a paper inch, in drawing inches

    def side_labels(ext):
        return [beside(ext.left, "left", Label("Front"), 1/4), beside(ext.right, "right", Label("Rear"), 1/4)]

    def side_title(ext):
        return title(ext.bottom, "Left side wall (facing rear)", height=3/16, gap=3/16)

    def rear_label(ext):
        return beside(ext.point(0, 0.8), "left", Label("rear wall"), 1/4)

    def repeat_row(ext, numbers, text):
        return numbered_row((ext.x0, ext.y0 - 0.7 * k), numbers, text)

    def block_marks(block, stud_xs, dx, dy, ends=True):
        """A support block's preset screws: marks on it (two in a line at a
        stud marker, and one near each end if `ends`), and the screws below it."""
        notes, screws = [], []
        marks = []
        if ends:
            marks = [(block.x0 + BLOCK_MARK_IN, block.y1 - BLOCK_MARK_DOWN), (block.x1 - BLOCK_MARK_IN, block.y1 - BLOCK_MARK_DOWN)]
            screws = [aimed((block.x0 + BLOCK_MARK_IN, block.y0), "Screw", "below", SCREW),
                      aimed((block.x1 - BLOCK_MARK_IN, block.y0), "Screw", "below", SCREW)]
        for x in stud_xs:
            marks += [(x + dx, block.y1 - BLOCK_MARK_DOWN), (x + dx, block.y1 - BLOCK_MARK_DOWN - 1.5)]
        notes += [at(p, cross(1/40)) for p in marks]
        for x in stud_xs:
            screw = aimed((x + dx, block.y0), "Screw", "below", SCREW)
            screws += [screw, next_to(screw, "right", Label("2x", SMALL), gap=1/10)]
        return notes + screws

    # ── baseboards ──
    groups = [side("baseboards"), rear("baseboards", also={"rear_shelf"})]
    offsets, (s, r) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0]) + moved(groups[1], *offsets[1])
    base = shifted(max(wide(pieces(side_wall_interior_far_side, "baseboards")), key=lambda e: e.width), *offsets[0])
    notes = numbered(base.point(0.5, 1), "1", "above", lead=1/2)
    notes += callout(base.point(1, 0.2), "Use spacers", "right", lead=3/8)
    notes += side_labels(s) + [side_title(s)] + repeat_row(s, "2", "Repeat for door-side sidewall")
    base = shifted(max(wide(pieces(rear_wall_interior, "baseboards")), key=lambda e: e.width), *offsets[1])
    notes += numbered(base.point(0.5, 1), "3", "above", lead=1/2) + [rear_label(r), title(r.bottom, "Baseboards")]
    rows["baseboards"] = (parts, [], notes)

    # ── rear window shelf ──
    groups = [rear("rear_shelf", hide={"baseboards"})]
    offsets, (r,) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0])
    shelf_pieces = pieces(rear_wall_interior, "rear_shelf")
    shelf = shifted(min(shelf_pieces, key=lambda e: e.height), *offsets[0])
    block = shifted(max(shelf_pieces, key=lambda e: e.height), *offsets[0])
    studs = studs_behind(rear_wall_framing, block.x0 - offsets[0][0], block.x1 - offsets[0][0])
    notes = [title(r.top, "Rear Window Shelf and Frame", "above", gap=1/2)]
    notes += block_marks(block, studs, offsets[0][0], offsets[0][1], ends=False)
    two = numbered(block.point(0.5, 0), "2", "below", lead=3/4)
    notes += two + [next_to(two[0], "right", Label("Use long screws"), gap=1/8)]
    notes += callout(block.bottom_left, 'Mount support block\nwith 1/2" shelf overhang\non each end', "below left", lead=3/4)
    plan, studs_cut = shelf_plan(rear_wall_interior, rear_wall_framing, "rear_shelf")
    notes += shelf_plan_notes(plan, studs_cut, r, shelf, scale, parts, ("1", "3"), rear=True)
    rows["rear_shelf"] = (parts, [], notes)

    # ── rear window trim ──
    groups = [rear("rear_window_trim", hide={"baseboards"})]
    offsets, (r,) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0])
    liners = [shifted(e, *offsets[0]) for e in pieces(rear_wall_interior, "rear_window_liner")]
    trims = [shifted(e, *offsets[0]) for e in pieces(rear_wall_interior, "rear_window_trim")]
    left_liner, right_liner, top_liner = tall(liners)[0], tall(liners)[-1], wide(liners)[0]
    left_trim, right_trim, top_trim = tall(trims)[0], tall(trims)[-1], wide(trims)[0]
    notes = [title(r.top, "Rear Window Shelf and Frame", "above", gap=1/2)]
    one = numbered(left_liner.point(0.5, 1), "1", "above", lead=5/8)
    notes += one + [next_to(one[0], "left", Label('3-1/2" plywood liners'), gap=1/8)]
    two = numbered(top_liner.point(0.8, 0.5), "2", "right", lead=1)
    notes += two + [next_to(two[0], "right", Label('3-1/2" plywood liner'), gap=1/8)]
    notes += numbered(left_trim.point(0.5, 0.4), "3", "left", lead=3/4)
    three = numbered(right_trim.point(0.5, 0.4), "3", "right", lead=3/4)
    notes += three + [next_to(three[0], "below", Label('2" plywood trim'), gap=1/8)]
    four = numbered(top_trim.point(0.75, 1), "4", "above right", lead=1/2)
    notes += four + [next_to(four[0], "right", Label('2" plywood trim'), gap=1/8)]
    rows["rear_window_trim"] = (parts, [], notes)

    # ── top trim ──
    groups = [side("top_trim"), rear("top_trim")]
    offsets, (s, r) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0]) + moved(groups[1], *offsets[1])
    long_, short = sorted((shifted(e, *offsets[0]) for e in pieces(side_wall_interior_far_side, "top_trim")), key=lambda e: -e.width)
    notes = numbered(long_.point(0.5, 0), "1", "below", lead=5/8) + numbered(short.point(0.5, 0), "2", "below", lead=5/8)
    notes += side_labels(s) + [side_title(s)] + repeat_row(s, ["3", "4"], "Repeat 1 & 2 for door-side sidewall")
    top = shifted(pieces(rear_wall_interior, "top_trim")[0], *offsets[1])
    notes += numbered(top.point(0.9, 0), "5", "below right", lead=1/2) + [rear_label(r), title(r.bottom, "Top Trim")]
    rows["top_trim"] = (parts, [], notes)

    # ── vertical trim ──
    groups = [side("vertical_trim"), rear("vertical_trim")]
    offsets, (s, r) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0]) + moved(groups[1], *offsets[1])
    notes = []
    for e in tall(pieces(side_wall_interior_far_side, "vertical_trim")):
        notes += numbered(shifted(e, *offsets[0]).point(0.5, 0.3), "1", "below right", lead=5/8)
    notes += side_labels(s) + [side_title(s)] + repeat_row(s, "2", "Repeat on other side sidewall")
    left, right = [shifted(e, *offsets[1]) for e in tall(pieces(rear_wall_interior, "vertical_trim"))]
    notes += numbered(left.point(0.5, 0.5), "3", "left", lead=5/8) + numbered(right.point(0.5, 0.5), "3", "right", lead=5/8)
    notes += [rear_label(r), title(r.bottom, "Vertical Trim")]
    rows["vertical_trim"] = (parts, [], notes)

    # ── horizontal trim ──
    groups = [rear("horizontal_trim"), side("horizontal_trim")]
    offsets, (r, s) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0]) + moved(groups[1], *offsets[1])
    trim = shifted(pieces(rear_wall_interior, "horizontal_trim")[0], *offsets[0])
    notes = numbered(trim.point(0.6, 0), "1", "below right", lead=5/8)
    notes += [beside(trim.point(0.4, 1), "above", Label("use a level", SMALL)), rear_label(r),
              beside(r.point(1, 0.6), "right", Label("Do this FIRST", 3/16), 1/2)]
    trim = shifted(pieces(side_wall_interior_far_side, "horizontal_trim")[0], *offsets[1])
    notes += numbered(trim.point(0.6, 0), "2", "below right", lead=5/8)
    notes += [beside(trim.point(0.5, 1), "above", Label("use a level, cover seam", SMALL)),
              beside(s.point(0, 0.85), "left", Label("side wall"), 1/4)]
    notes += side_labels(s) + repeat_row(s, "3", "Repeat for door-side sidewall") + [title(s.bottom, "Horizontal Trim", gap=1.1)]
    rows["horizontal_trim"] = (parts, [], notes)

    # ── triangle trim ──
    groups = [rear("triangle_trim")]
    offsets, (r,) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0])
    left, right, center = [shifted(e, *offsets[0]) for e in gable_trim_pieces()]
    four = numbered(right.point(0.5, 1), "4", "above right", lead=1/2)
    notes = four + [toward(circle_of(four), left.point(0.5, 1), scale)]
    notes += numbered(center.point(0, 0.5), "5", "above left", lead=1) + [rear_label(r), title(r.bottom, "Triangle Trim")]
    rows["triangle_trim"] = (parts, [], notes)

    # ── front window: the shelf, then the liners ──
    groups = [front("front_shelf", {"front_baseboard", "front_shelf"}), front("front_window_trim")]
    offsets, (f1, f2) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0]) + moved(groups[1], *offsets[1])
    base = shifted(max(wide(pieces(front_wall_interior, "front_baseboard")), key=lambda e: e.width), *offsets[0])
    shelf_pieces = pieces(front_wall_interior, "front_shelf")
    shelf = shifted(min(shelf_pieces, key=lambda e: e.height), *offsets[0])
    block = shifted(max(shelf_pieces, key=lambda e: e.height), *offsets[0])
    studs = studs_behind(front_wall_framing, block.x0 - offsets[0][0], block.x1 - offsets[0][0])
    notes = [title(f1.top, "Front Window Shelf and Frame", "above", gap=1/2)]
    notes += numbered(base.bottom_right, "1", "below right", lead=1/2)
    notes += block_marks(block, studs, offsets[0][0], offsets[0][1])
    # the block's screws numbered from below them, with their notes
    three_at = (block.center[0], block.y0 - 0.6 * k)
    notes += [at(three_at, n) for _, _, n in numbered(three_at, "3", "right", lead=0)[:2]]
    for x in [block.x0 + BLOCK_MARK_IN, block.x1 - BLOCK_MARK_IN] + [x + offsets[0][0] for x in studs]:
        notes.append(toward(three_at, (x, block.y0 - 0.5 * k), scale))
    notes += [beside((three_at[0] + CIRCLED * k, three_at[1]), "right", Label("LONG Screws"), 1/8),
              beside((f1.x0, f1.y0 - 0.3 * k), "below right", Label("Mount support block\nflush with left edge\nof shelf"), 0)]
    plan, studs_cut = shelf_plan(front_wall_interior, front_wall_framing, "front_shelf")
    notes += shelf_plan_notes(plan, studs_cut, f1, shelf, scale, parts, ("2", "4"), rear=False, gap=2.2 * k)
    liners = [shifted(e, *offsets[1]) for e in pieces(front_wall_interior, "front_window_liner")]
    left_liner, right_liner, top_liner = tall(liners)[0], tall(liners)[-1], wide(liners)[0]
    five = numbered(right_liner.point(0.5, 0.4), "5", "right", lead=3/4)
    notes += five + [toward(circle_of(five), left_liner.point(0.5, 0.6), scale)]
    notes += numbered(top_liner.point(0.8, 0.5), "6", "above right", lead=1/2)
    rows["front_window"] = (parts, [], notes)

    # ── front wall trim, part I ──
    groups = [front("front_trim_a") + [side_strip("left")]]
    offsets, (f,) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0])
    exts = [shifted(e, *offsets[0]) for e in pieces(front_wall_interior, "front_trim_a") if e.width > 3 or e.height > 3]
    top = max(exts, key=lambda e: e.width)  # the top trim
    base = min(exts, key=lambda e: e.y1)  # the short baseboard behind the door
    narrow, wide_ = sorted((e for e in exts if e.height > 50), key=lambda e: e.x0)  # the boards behind and beside the door
    strip = shifted(Extent(side_strip("left")[0]), *offsets[0])
    notes = numbered(top.point(0.8, 1), "1", "above right", lead=1/2)
    two = numbered(base.point(0, 0.5), "2", "left", lead=3/4)
    notes += two + [next_to(two[0], "below", Label("Baseboards"), gap=1/8)]
    notes += numbered(wide_.point(1, 0.25), "3", "right", lead=1/2)
    notes += numbered(narrow.point(0, 0.85), "4", "above left", lead=5/8)
    five = numbered(strip.point(0, 0.6), "5", "left", lead=1/2)
    notes += five + [next_to(five[0], "below", Label('Add 2" trim to sidewall\nin this corner'), gap=1/8)]
    notes.append(beside((f.x0, f.y0 - 0.8 * k), "below right",
                        Label("#4 trim board goes on first, because it is wider and less flexible.\n"
                              "Then #5 trim is nailed onto the sidewall.\n"
                              "This does not match the other corners, but is correct.", bold=("first",)), 0))
    notes.append(title(f.bottom, "Front Wall Trim", gap=1.8))
    rows["front_trim_a"] = (parts, [], notes)

    # ── front wall trim, part II ──
    groups = [front("front_trim_b") + [side_strip("right")]]
    offsets, (f,) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0])
    exts = [shifted(e, *offsets[0]) for e in pieces(front_wall_interior, "front_trim_b")]
    over_door = max(wide(exts), key=lambda e: e.width)
    window_top = min(wide(exts), key=lambda e: e.width)
    corner, window_side = sorted(tall(exts), key=lambda e: -e.x0)[:2]
    strip = shifted(Extent(side_strip("right")[0]), *offsets[0])
    left_angled, right_angled, _ = [shifted(e, *offsets[0]) for e in gable_trim_pieces()]
    notes = numbered(over_door.point(0.3, 1), "1", "above left", lead=1/2)
    two = numbered(window_top.point(0.6, 1), "2", "above right", lead=5/8)
    notes += two + [toward(circle_of(two), window_side.point(0.5, 0.8), scale)]
    notes += numbered(strip.point(1, 0.8), "3", "above right", lead=1/2)
    notes += numbered(corner.point(1, 0.5), "4", "below right", lead=1/2)
    five = numbered(left_angled.point(0.6, 1), "5", "above right", lead=3/4)
    notes += five + [toward(circle_of(five), right_angled.point(0.4, 1), scale)]
    notes.append(beside((f.center[0], f.y0 - 0.5 * k), "below right",
                        Label('Install 2" trim to side wall\nin this corner before\nfront-wall corner trim,\n'
                              'unless there is not enough\nspace between side trim and\nshelf edge.  In this case, install\n'
                              'front-wall corner trim first,\nand then side-wall trim.'), 0))
    notes.append(title(f.bottom, "Front Wall Trim", gap=2.6))
    rows["front_trim_b"] = (parts, [], notes)

    # ── final trim ──
    groups = [side("final_trim"), front("final_trim")]
    offsets, (s, f) = layout(groups, gap)
    parts = moved(groups[0], *offsets[0]) + moved(groups[1], *offsets[1])
    trim = shifted(pieces(side_wall_interior_far_side, "final_trim")[0], *offsets[0])
    notes = numbered(trim.point(0.3, 0), "1", "below left", lead=5/8)
    notes += [beside(s.point(0, 0.85), "left", Label("side wall"), 1/4)] + side_labels(s)
    notes += repeat_row(s, "2", "Repeat on other sidewall")
    behind_door, under_shelf = sorted((shifted(e, *offsets[1]) for e in pieces(front_wall_interior, "final_trim")), key=lambda e: e.x0)
    three = numbered(under_shelf.point(1, 0.5), "3", "right", lead=1/2)
    notes += three + [next_to(three[0], "below", Label("use a level", SMALL), gap=1/8)]
    notes += numbered(behind_door.point(0, 0.5), "4", "left", lead=1/2)
    notes += numbered_row((f.x0, f.y0 - 0.7 * k), "5", 'Cover ceiling seams with 2" trim')
    notes.append(title(f.bottom, "Final Trim", gap=1.2))
    rows["final_trim"] = (parts, [], notes)

    return table(MD, rows)


def shelf_plan_notes(plan, studs_cut, wall, shelf, scale, parts, numbers, rear, gap=PLAN_GAP):
    """Place a shelf's plan (parts, in the wall's frame) to the right of
    the wall, level with the shelf, circled, and note it: the screws through
    the tab into the sill, and those down through the shelf into its block
    next to the wall. Appends the plan to `parts`; returns the notes."""
    k = 1 / scale
    e = extent(plan)
    dx, dy = wall.x1 + gap + e.width / 2 - e.center[0], shelf.center[1] - e.center[1]
    parts += moved(plan, dx, dy)
    plan_ext = shifted(e, dx, dy)
    studs_cut = [shifted(s, dx, dy) for s in studs_cut]
    radius = math.hypot(plan_ext.width, plan_ext.height) / 2 * scale + 0.25
    notes = [around(plan_ext.center, radius)]
    for s in studs_cut:  # lumber in section: crossed
        notes += [line(s.bottom_left, s.top_right, scale), line(s.top_left, s.bottom_right, scale)]
    # the tab, in the opening: its screws next to the window, from above
    tab_x0, tab_x1 = WINDOW_X + 1/8 + dx, WINDOW_X + WINDOW_WIDTH - 1/8 + dx
    tab_y = (plan_ext.y1 + (dy - PANEL)) / 2  # between the panel face and the tab's end
    tab_screws = [(tab_x0 + (tab_x1 - tab_x0) * f, tab_y) for f in (0.25, 0.5, 0.75)]
    notes += [aimed(p, "Screw", "above", SCREW) for p in tab_screws]
    circle = (tab_screws[1][0], plan_ext.y1 + 0.55 * k)
    notes += [at(circle, n) for _, _, n in numbered(circle, numbers[0], "right", lead=0)[:2]]
    notes += [toward(circle, (x, y + 0.5 * k), scale) for x, y in tab_screws]
    wall_y = dy - PANEL  # the panel's face, in the plan
    the_shelf = max((Extent(p[0]) for p in moved(plan, dx, dy)), key=lambda e: e.width)  # the plan's widest piece
    if rear:
        down = [(the_shelf.x0 + 2, wall_y), (the_shelf.x1 - 2, wall_y)]
        notes += [aimed(p, "Screw", "below", SCREW) for p in down]
        for p, side in zip(down, ("left", "right")):
            n = numbered((p[0], p[1] - 0.5 * k), numbers[1], side, lead=1/2)
            notes += n
        notes += [at(the_shelf.point(0.5, 0.1), Label("Shelf")), beside(plan_ext.bottom, "below", Label("Long screws"), 1/4)]
    else:
        # the front shelf's block runs from the door-side end of the shelf: screws 2" in from its ends and at the middle
        x0, x1 = the_shelf.x0 + 2, the_shelf.x1 - 1/2 - 2
        down = [(x0, wall_y), ((x0 + x1) / 2, wall_y), (x1, wall_y)]
        notes += [aimed(p, "Screw", "below", SCREW) for p in down]
        circle = (down[1][0], plan_ext.y0 - 0.55 * k)
        notes += [at(circle, n) for _, _, n in numbered(circle, numbers[1], "right", lead=0)[:2]]
        notes += [toward(circle, (x, y - 0.5 * k), scale) for x, y in down]
        notes.append(beside((circle[0] - CIRCLED * k, circle[1]), "left", Label("LONG Screws"), 1/8))
        notes.append(beside((tab_screws[1][0] + CIRCLED * k, plan_ext.y1 + 0.55 * k), "right", Label("LONG Screws"), 1/8))
    return notes
