"""Platform/platform.md figures: the platform seen from above, FRONT at the
bottom (the drawing's Y = 0 is the front)."""

from build123d import Align, Box, Pos, Rot

from model.lumber import thickness
from model.dimensions import FOAM_LENGTH, JOIST_LENGTH, PLATFORM_LENGTH, PLATFORM_WIDTH, SKID, SKID_INSET
from model.platform import (
    FRAME_BOTTOM, FRAME_TOP, JOIST_Y, RIM, SKID_HEIGHT, bays, foam, foam_width, platform, platform_joist,
    platform_long_side, platform_plywood, skid,
)

from . import GRAY, Figure, figure_names, optional_parts, placed_notes, title

MD = "Platform/platform.md"

# The model's front is at +Y; the drawings put it at the bottom.
TO_DRAWING = Pos(PLATFORM_WIDTH, PLATFORM_LENGTH, 0) * Rot(Z=180)


def place(component, x, y, z):
    return TO_DRAWING * Pos(x, y, z) * component.shape()


def figures():
    sides = [place(platform_long_side, x, 0, FRAME_BOTTOM) for x in (0, PLATFORM_WIDTH - RIM)]
    joists = {y: place(platform_joist, RIM, y, FRAME_BOTTOM) for y in JOIST_Y}
    ends = [joists[JOIST_Y[0]], joists[JOIST_Y[-1]]]
    doubled = [joists[JOIST_Y[1]], joists[JOIST_Y[-2]]]
    inner = [joists[y] for y in JOIST_Y[2:-2]]
    skids = [place(skid, x, 0, 0) for x in (SKID_INSET, PLATFORM_WIDTH - SKID_INSET - thickness(SKID))]
    foams = [place(foam(b - a), RIM + (JOIST_LENGTH - FOAM_LENGTH) / 2, (a + b) / 2 - foam_width(b - a) / 2, SKID_HEIGHT)
             for a, b in bays()]
    ply = [place(platform_plywood, 0, y, FRAME_TOP) for y in (0, 48, 96)]  # "Panel 1" first, at the rear

    frame = sides + ends + doubled + inner

    def uncovered(shapes, deck):
        """What of these parts shows beyond the plywood laid so far (the
        drawings show framing through the deck, but not foam or skids)."""
        if not deck:
            return shapes
        y0 = min(p.bounding_box().min.Y for p in deck)
        out = []
        for sh in shapes:
            bb = sh.bounding_box()
            if bb.max.Y <= y0 + 1e-6:
                out.append(sh)
            elif bb.min.Y < y0:
                out.append(sh & Pos(bb.min.X - 1, bb.min.Y - 1, bb.min.Z - 1)
                           * Box(bb.size.X + 2, y0 - bb.min.Y + 1, bb.size.Z + 2, align=Align.MIN))
        return out

    def covered(shapes, deck):
        """What of these parts is under the plywood laid so far."""
        y0 = min(p.bounding_box().min.Y for p in deck)
        out = []
        for sh in shapes:
            bb = sh.bounding_box()
            if bb.max.Y > y0 + 1e-6:
                out.append(sh & Pos(bb.min.X - 1, y0, bb.min.Z - 1) * Box(bb.size.X + 2, bb.max.Y - y0 + 1, bb.size.Z + 2, align=Align.MIN))
        return out

    jig = [(s, "jig") for s in frame]
    cov = lambda xs: [(s, "covered") for s in xs]
    ctx = lambda xs, fill=None: [(s, "context") if fill is None else (s, "context", fill) for s in xs]
    new = lambda xs, fill=None: [(s, "new") if fill is None else (s, "new", fill) for s in xs]
    foam_of = lambda xs, style="bare": [(s, style, "foam") for s in xs]
    ply_of = lambda xs: [(s, "outline", GRAY) for s in xs]
    base = ctx(skids) + ctx(frame)  # the platform on its skids (Step_04-Framing)
    steps = [
        jig + new(sides + ends),                                   # 1: perimeter
        jig + ctx(sides + ends) + new(doubled),                    # 2: doubled ends
        jig + ctx(sides + ends + doubled) + new(inner),            # 3: inner joists
        base,                                                      # 4: onto the skids
        base,                                                      # 5: bracket marks
        base,                                                      # 6: brackets
        base,                                                      # 7: spacer blocks
        base + foam_of(foams, "heavy"),                            # 8: foam
        ctx(uncovered(skids, ply[:1])) + ctx(uncovered(frame, ply[:1])) + foam_of(uncovered(foams, ply[:1]))
        + ply_of(ply[:1]) + cov(covered(frame, ply[:1])),          # 9: panel 1 (framing shows through the deck)
        ctx(uncovered(skids, ply[:2])) + ctx(uncovered(frame, ply[:2])) + foam_of(uncovered(foams, ply[:2]))
        + ply_of(ply[:2]) + cov(covered(frame, ply[:2])),          # 10: panel 2
        ply_of(ply) + cov(frame),                                  # 11: panel 3
        ply_of(ply),                                               # 12: router the edges
    ]
    out = []
    for i, (fig_name, parts) in enumerate(zip(figure_names(MD), steps), 1):
        shown = {"manual:platform", f"manual:platform:{i}"}
        parts = parts + optional_parts(TO_DRAWING, platform, shown, "new")
        notes = placed_notes(TO_DRAWING, platform, shown) + [
            title(f"Step {i}", 42.47, -11.63, runs=(("Step", 2.5), (f" {i}", 3)))]  # "Step" smaller, as drawn
        out.append(Figure(MD, fig_name, parts, notes))
    return out
