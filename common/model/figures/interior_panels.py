"""Interior_Panels/interior_panels.md figures: each wall seen from inside
(framing and the installed panels, light gray), with its panels laid out
loose above it showing their preset screws; the ceiling's panels flattened
out of the slope.

The manual is a table of its figures: the parts, and the notes hung on the
panels' extents in the drawing."""

import math

from build123d import Pos

from model.common import key
from model.interior import (
    front_wall_interior, panel_a, panel_b, panel_c, panel_d, panel_e, panel_g, panel_h,
    rear_wall_interior, side_wall_interior_door_side,
)
from model.interior_roof import (
    CEILING_BOTTOM_U, END_INTERIOR_AT, HALF_TRIANGLE_BASE, HALF_TRIANGLE_NOTCH, ceiling_half, ceiling_panel_r1,
    ceiling_panel_r2, ceiling_rafter_screws, end_wall_interior, half_triangle_left, half_triangle_right,
)
from model.roof import SLOPE, T
from model.notes import Circle, Label, aimed, at, beside, callout, circled, title
from model.walls import front_wall_framing, rear_wall_framing, side_wall_framing

from . import TYVEK, Extent, camera, extent, table, xy

MD = "Interior_Panels/interior_panels.md"
PANEL_FILL = TYVEK  # the drawings' light gray (ACI 9)

# A wall seen from inside the house (its frame: X along the wall left to
# right as seen from inside, Z up): drawing x = X, y = Z.
INSIDE_VIEW = camera((0, -1, 0))
# A sheet lying in XY seen from below, turned so its Y runs across the
# drawing: drawing x = Y, y = X.
FLAT_VIEW = camera((0, 0, -1), up=(1, 0, 0))
# The ceiling's panels, flattened out of the slope: x along the house from
# the rear, y up the slope.
CEILING_FLAT = FLAT_VIEW * SLOPE.inverse()

LOOSE_GAP = 12  # drawing inches between the loose panels, and above the wall
EDGE_SCREWS = 8  # a loose panel's preset screws, about this far apart along its edges
SCREW_IN = 4  # the first screw this far from the panel's bottom end (the last at the top)
SCREW = 0.7  # the screw icon, scaled down
LETTER = 1/4  # a panel's letter, paper inches
LETTERS = {panel_a: "A", panel_b: "B", panel_c: "C", panel_d: "D", panel_e: "E", panel_g: "G", panel_h: "H",
           ceiling_panel_r1: "R1", ceiling_panel_r2: "R2"}
TRIM_TAGS = frozenset({
    "baseboards", "rear_shelf", "rear_window_trim", "top_trim", "vertical_trim", "horizontal_trim",
    "front_baseboard", "front_shelf", "front_window_trim", "front_trim_a", "front_trim_b", "final_trim",
})


def edge_screws(ext, edges=("left", "right"), toward=None):
    """Screws preset along a loose panel's edges, slanting in toward the
    edge from the panel's face (as the manual has them drilled)."""
    out = []
    n = int(ext.height // EDGE_SCREWS) + 1
    ys = [ext.y0 + SCREW_IN + i * (ext.height - SCREW_IN) / (n - 1) for i in range(n)]
    for edge in edges:
        x = ext.x0 if edge == "left" else ext.x1
        angle = 210 if edge == "left" else 330  # from the screw to the edge: down and out
        out += [aimed((x, y), "Screw", angle, SCREW) for y in ys]
    return out


def spacing_callout(ext):
    """'8" spacing', pointing at a screw on the panel's right edge."""
    n = int(ext.height // EDGE_SCREWS) + 1
    y = ext.y0 + SCREW_IN + (n // 2) * (ext.height - SCREW_IN) / (n - 1)
    return callout((ext.x1, y), '8" spacing', "right", lead=5/8, height=0.1)


def letter(ext, text, fx=0.5, fy=0.5, height=LETTER):
    return at(ext.point(fx, fy), Label(text, height))


def installed(component, view, hidden=frozenset()):
    """A wall's installed panels, each as (component, shape in the drawing)."""
    return [(c, view * loc * c.shape()) for c, loc, mods, tag in component()[1]
            if tag in ("panels", "panel_d", "panel_e2") and tag not in hidden]


def stacked(shapes, x, top, gap=LOOSE_GAP):
    """Shapes laid out one under the other from `top` down, left edges at x:
    returns them moved."""
    out, y = [], top
    for s in shapes:
        e = Extent(s)
        out.append(Pos(x - e.x0, y - e.y1, 0) * s)
        y -= e.height + gap
    return out


def wall_figure(wall, framing, loose_panels, numbers=(), fractions=None, hidden=frozenset(), gap=LOOSE_GAP):
    """A wall's panels figure: its framing with the panels installed, the
    loose panels laid out above it in columns, their edges screwed, lettered.
    Returns the parts, the notes, the wall's extent and the loose panels'."""
    frame = INSIDE_VIEW * framing.shape()
    wall_ext = Extent(frame)
    parts = [(frame, "outline")]
    notes = []
    in_place = dict(installed(wall, INSIDE_VIEW, hidden))
    for comp, shape in in_place.items():
        parts.append((shape, "outline", PANEL_FILL))
        if comp in LETTERS:
            fx, fy = (fractions or {}).get(comp, (0.5, 0.5))
            notes.append(letter(Extent(shape), LETTERS[comp], fx, fy))
    for n, comp in enumerate(numbers, 1):
        e = Extent(in_place[comp])
        notes += circled((e.center[0] + 10, e.center[1] - 12), str(n))
    # the loose panels: columns of them, above the wall
    x, shapes = wall_ext.x0, {}
    for column in loose_panels:
        stack = stacked([INSIDE_VIEW * c.shape() for c in column], x, 0)
        shapes.update(zip(column, stack))
        x += max(Extent(s).width for s in stack) + LOOSE_GAP
    lift = wall_ext.y1 + gap - min(Extent(s).y0 for s in shapes.values())
    loose_ext = {}
    for comp, s in shapes.items():
        s = Pos(0, lift, 0) * s
        e = loose_ext[comp] = Extent(s)
        parts.append((s, "outline"))
        notes += edge_screws(e) + [letter(e, LETTERS[comp])]
    return parts, notes, wall_ext, loose_ext


def figures(scale=1/30):
    rows = {}
    whole = {}

    # Side wall: B, A over it, then C; the loose A over B, C beside them.
    side = side_wall_interior_door_side
    parts, notes, wall, loose_ext = wall_figure(side, side_wall_framing, [[panel_a, panel_b], [panel_c]],
                                                numbers=(panel_b, panel_a, panel_c), hidden=TRIM_TAGS, gap=2.5 * LOOSE_GAP)
    a, b, c = loose_ext[panel_a], loose_ext[panel_b], loose_ext[panel_c]
    notes += callout(a.point(1, 0.9), "Factory edge (paint mark)", "above right", lead=1/2)
    notes += callout(b.point(1, 0.2), "Factory edge (paint mark)", "below right", lead=3/8)
    notes += spacing_callout(c)
    seam = Extent(dict(installed(side, INSIDE_VIEW, TRIM_TAGS))[panel_a])
    notes += callout(seam.top_right, "Line up factory edges of A and B\nwith centerline of stud", "above left", lead=3/8)
    notes += [beside(wall.left, "left", Label("Rear"), 1/4), beside(wall.right, "right", Label("Front"), 1/4)]
    notes.append(title(wall.bottom, "Side Wall Panels", gap=1/2))
    rows["side_panels"] = (parts, [], notes)

    # Rear wall: H, G over it (its window to be routed out later).
    parts, notes, wall, loose_ext = wall_figure(rear_wall_interior, rear_wall_framing, [[panel_g, panel_h]],
                                                fractions={panel_g: (0.3, 0.5), panel_h: (0.3, 0.5)}, hidden=TRIM_TAGS)
    notes += spacing_callout(loose_ext[panel_g])
    notes.append(title(wall.bottom, "Rear Wall Panels", gap=1/2))
    rows["rear_panels"] = (parts, [], notes)

    # Front wall: E beside the door, D over it and the door.
    parts, notes, wall, loose_ext = wall_figure(front_wall_interior, front_wall_framing, [[panel_d, panel_e]],
                                                fractions={panel_d: (0.6, 0.5), panel_e: (0.35, 0.5)}, hidden=TRIM_TAGS | {"panel_e2"})
    notes += spacing_callout(loose_ext[panel_d])
    notes.append(title(wall.bottom, "Front Wall Panels", gap=1/2))
    rows["front_panels"] = (parts, [], notes)

    rows["ceiling_panels"] = ceiling_figure(scale)
    rows["triangle_panels"] = triangle_figure()
    return table(MD, rows)


def ceiling_figure(scale):
    """The left half's ceiling, flattened: R1 installed, then R2 against it,
    then the screws into the rafters through both; the loose panels above."""
    rest = {"", "ceiling_trim"}  # the batts and the seam trim, never shown
    views = [CEILING_FLAT * ceiling_half.shape(rest | {"ceiling_r2"}), CEILING_FLAT * ceiling_half.shape(rest),
             CEILING_FLAT * ceiling_half.shape(rest)]
    views = stacked(views, 0, 0, gap=25)
    exts = [Extent(v) for v in views]
    parts = [(v, "outline", PANEL_FILL) for v in views]
    notes = []
    for e in exts:
        notes += [beside(e.left, "left", Label("Back", 3/16), 1/2), beside(e.right, "right", Label("Front", 3/16), 1/2)]
    r1, r1r2, screwed = exts
    r1_in_r1r2 = Extent(Pos(0, r1r2.y0 - r1.y0, 0) * views[0])  # where R1 is in the second view
    notes += [letter(r1, "R1"), letter(Extent.box(r1_in_r1r2.x1, r1r2.y0, r1r2.x1, r1r2.y1), "R2")]
    notes += callout(r1.point(1, 0.15), "Factory Edge", "below right", lead=3/8)
    notes += callout((r1_in_r1r2.x1, r1r2.point(0, 0.85)[1]), "Factory Edge", "above right", lead=3/8)
    # the screws into the rafters, in the third view
    shift = screwed.y0 - Extent(CEILING_FLAT * ceiling_half.shape(rest)).y0
    for along, u in ceiling_rafter_screws():
        p = xy(CEILING_FLAT * SLOPE * Pos(u, along, 0))
        notes.append(at((p[0], p[1] + shift), Circle(1/60, fill=(0, 0, 0))))
    notes.append(beside((screwed.x0 + 10, screwed.y0), "below right",
                        Label("Drill & countersink, then use\nLONG screws into rafters\n(5 screws into each rafter)"), 1/4))
    # the loose panels above, their long edges screwed (the short edges go on the rafters' ends)
    loose_shapes = [FLAT_VIEW * ceiling_panel_r1.shape(), FLAT_VIEW * ceiling_panel_r2.shape()]
    x = r1.x0
    for comp, s in zip((ceiling_panel_r1, ceiling_panel_r2), loose_shapes):
        e = Extent(s)
        s = Pos(x - e.x0, r1.y1 + 2 * LOOSE_GAP - e.y0, 0) * s
        e = Extent(s)
        parts.append((s, "outline"))
        notes += edge_screws(e) + [letter(e, LETTERS[comp])]
        if comp is ceiling_panel_r1:
            notes += callout(e.point(1, 0.5), "Factory edge (paint mark)", "above right", lead=3/4)
        else:
            notes += callout(e.point(0, 0.1), "Factory edge (paint mark)", "below left", lead=1/2)
            notes += spacing_callout(e)
        x += e.width + 3 * LOOSE_GAP
    notes.append(title(screwed.bottom, "Ceiling Panels", gap=1))
    return parts, [], notes


def triangle_figure():
    """The half-triangle panels on the front wall, and loose above it with
    their screws preset along the bottom, the slope and the short edge."""
    frame = INSIDE_VIEW * front_wall_framing.shape()
    triangle_at = INSIDE_VIEW * END_INTERIOR_AT
    parts = [(frame, "outline"), (triangle_at * end_wall_interior.shape(frozenset({"triangle_trim"}), key(["mirror"])), "new")]
    wall = extent(parts)
    notes = []
    b, (nw, nh) = HALF_TRIANGLE_BASE, HALF_TRIANGLE_NOTCH
    rise = b * T
    slope = math.degrees(math.atan2(rise, b))
    y0 = wall.y1 + 2 * LOOSE_GAP
    for comp, sign, x0 in ((half_triangle_left, -1, wall.x0), (half_triangle_right, 1, wall.x0 + b + 2.5 * LOOSE_GAP)):
        s = INSIDE_VIEW * comp.shape()
        e = Extent(s)
        s = Pos(x0 - e.x0, y0 - e.y0, 0) * s
        parts.append((s, "outline"))
        foot = (x0 if sign < 0 else x0 + b, y0)  # the triangle's outer corner
        peak_x = x0 + b if sign < 0 else x0  # the short edge (at the center of the wall)

        def along(p, q, n, inset=SCREW_IN):
            d = math.hypot(q[0] - p[0], q[1] - p[1])
            return [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t) for t in [(inset + i * (d - 2 * inset) / (n - 1)) / d for i in range(n)]]
        notes += [aimed(p, "Screw", "below", SCREW) for p in along(foot, (peak_x, y0), round(b / EDGE_SCREWS))]
        top = (peak_x, y0 + rise - nh)
        n = round(math.hypot(b, rise) / EDGE_SCREWS)
        # from outside the sloping edge, in toward it
        notes += [aimed(p, "Screw", slope - 90 if sign < 0 else 270 - slope, SCREW) for p in along(foot, (peak_x, y0 + rise), n, inset=6)]
        notes += [aimed(p, "Screw", 180 if sign < 0 else 0, SCREW) for p in along((peak_x, y0), top, 3, inset=2)]
    return parts, [], notes
