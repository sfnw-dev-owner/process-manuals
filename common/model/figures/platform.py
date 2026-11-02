"""Platform/platform.md figures: the platform seen from above, the REAR at
the top of the drawing and the FRONT at the bottom."""

from build123d import Align, Box, Pos, Rot

from model.lumber import thickness, width
from model.dimensions import FOAM_LENGTH, JOIST_LENGTH, PLATFORM_LENGTH, PLATFORM_WIDTH, SKID, SKID_INSET
from model.notes import (
    ICONS, SMALL, Label, aimed, at, beside, callout, icon, line, next_to, pointer, title,
)
from model.platform_assembly import (
    FRAME_BOTTOM, FRAME_TOP, JOIST_Y, RIM, SKID_HEIGHT, bays, bracket_marks, foam, foam_width, platform_joist,
    platform_long_side, platform_plywood, save_blocks, skid,
)

from . import GRAY, Extent, break_box, extent, table, xy

MD = "Platform/platform.md"

# The model's rear is at Y = 0; the drawing puts it at the top: X across the
# platform (the drawing's X runs the other way), Y up it from the front.
TO_DRAWING = Pos(PLATFORM_WIDTH, PLATFORM_LENGTH, 0) * Rot(Z=180)

ROUTER_LINE = width("2x4")  # step 12's pencil line, in from the edges
NAILS_PER_END = 4  # through the doubled end joists (step 2)


def figures(scale=1/20, only=None):
    place = lambda comp, x, y, z: TO_DRAWING * Pos(x, y, z) * comp.shape()
    sides = [place(platform_long_side, x, 0, FRAME_BOTTOM) for x in (0, PLATFORM_WIDTH - RIM)]
    joist_at = {y: Pos(RIM, y, FRAME_BOTTOM) for y in JOIST_Y}
    joists = {y: TO_DRAWING * loc * platform_joist.shape() for y, loc in joist_at.items()}
    ends = [joists[JOIST_Y[0]], joists[JOIST_Y[-1]]]
    doubled = [joists[JOIST_Y[1]], joists[JOIST_Y[-2]]]
    inner = [joists[y] for y in JOIST_Y[2:-2]]
    skids = [place(skid, x, 0, 0) for x in (SKID_INSET, PLATFORM_WIDTH - SKID_INSET - thickness(SKID))]
    foams = [place(foam(b - a), RIM + (JOIST_LENGTH - FOAM_LENGTH) / 2, (a + b) / 2 - foam_width(b - a) / 2, SKID_HEIGHT)
             for a, b in bays()]
    ply = [place(platform_plywood, 0, y, FRAME_TOP) for y in (0, 48, 96)]  # "Panel 1" first, at the rear
    frame = sides + ends + doubled + inner
    whole = extent(frame)

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

    # ── the notes, by points of the frame ──
    def end_of(y, side):
        """Where a joist meets the rim on this side, on the rim's outer face."""
        x = whole.x0 if side == "left" else whole.x1
        return x, xy(TO_DRAWING * joist_at[y] * platform_joist.anchors()["left"])[1]

    def nail_through_rims(ys, count="x3"):
        """A nail gun at each end of these joists, nailing through the rims."""
        out = []
        for y in ys:
            for side in ("left", "right"):
                gun = aimed(end_of(y, side), "NailGun", side)
                out += [gun, next_to(gun, side, Label(count))]
        return out

    rear, front = max(JOIST_Y), min(JOIST_Y)  # the doubled end joists' y (model)
    rear_edge, front_edge = whole.y1, whole.y0  # the frame's ends in the drawing

    def across(fraction):
        return whole.x0 + fraction * whole.width

    # Step 2: clamp and nail the doubled end joists, mark the inner joists' lines on the rims.
    step2 = []
    for edge, side in ((rear_edge, "above"), (front_edge, "below")):
        for k in range(NAILS_PER_END):
            step2.append(aimed((across((k + 1/2) / NAILS_PER_END), edge), "NailGun", side))
        for k in (1, 3):
            step2 += callout((across(k / 4), edge), "CLAMP", "above" if side == "below" else "below", lead=1/2)
    step2 += nail_through_rims([JOIST_Y[1], JOIST_Y[-2]])
    for y in JOIST_Y[2:-2]:
        for side, sign in (("left", -1), ("right", 1)):
            mark = end_of(y, side)
            step2 += [pointer(mark, sign * 1/8, 0, arrow=False), aimed((mark[0] + sign / 8 / scale, mark[1]), "Pencil", side)]

    # Steps 5-6: the bracket marks, and step 6's inset of a bracket with its screws.
    marks = [at(xy(TO_DRAWING * Pos(x, y, 0)), Label("x", SMALL)) for x, y in bracket_marks()]
    bracket = beside(whole.bottom_left, "below left", icon("Hurricane_Bracket"), gap=1/4)
    w, h = ICONS["Hurricane_Bracket"][0]
    bx, by = whole.x0 + bracket[2].dx / scale, whole.y0 + bracket[2].dy / scale  # the icon's center, in the drawing
    step6 = [bracket]
    for dy in (h / 4, -h / 4):
        screw = aimed((bx + w / 2 / scale, by + dy / scale), "Screw", "right")
        step6 += [screw, next_to(screw, "right", Label("x3"))]

    # Step 7: the spacer blocks on the skids, with an end bay's and an inner bay's called out.
    blocks = [(block, TO_DRAWING * loc) for block, loc in save_blocks()]
    block_ext = {k: Extent(block.shape().moved(loc)) for k, (block, loc) in enumerate(blocks)}
    bay_centers = [xy(TO_DRAWING * Pos(PLATFORM_WIDTH / 2, (a + b) / 2, 0)) for a, b in bays()]
    step7 = (callout(block_ext[0].right, 'Blocks labeled "SAVE END"', "above right", lead=1/2)
             + callout(block_ext[4].right, 'Blocks labeled "SAVE"', "above right", lead=1/2)
             + [at(bay_centers[-4], Label("DO NOT NAIL BLOCKS"))])

    # Step 8: the foam, sealed.
    foam_ext = {k: Extent(f) for k, f in enumerate(foams)}
    step8 = (callout(foam_ext[0].bottom, "Foam Sealant (Great Stuff) all 4 sides\nof each bay", "below right", lead=1/2)
             + callout(foam_ext[-1 % len(foams)].top, "Install insulation silver side up", "above right", lead=1/2))
    insulation = [at(bay_centers[len(bay_centers) // 2], Label("RIGID INSULATION", height=3/16))]

    # Step 12: the pencil line in from the edges, and the pencil.
    m = ROUTER_LINE
    corners = [(whole.x0 + m, whole.y0 + m), (whole.x1 - m, whole.y0 + m), (whole.x1 - m, whole.y1 - m), (whole.x0 + m, whole.y1 - m)]
    step12 = [line(a, b, scale, weight=1) for a, b in zip(corners, corners[1:] + corners[:1])]
    step12.append(aimed(corners[2], "Pencil", "above right"))

    rows = {
        "step_01": (jig + new(sides + ends), [], nail_through_rims([rear, front])),
        "step_02": (jig + ctx(sides + ends) + new(doubled), [], step2),
        "step_03": (jig + ctx(sides + ends + doubled) + new(inner), [], nail_through_rims(JOIST_Y[1:-1])),
        "step_04": (base, [], []),
        "step_05": (base, [], marks + [aimed(xy(TO_DRAWING * Pos(*bracket_marks()[0], 0)), "Pencil", "above right"),
                                      *callout(xy(TO_DRAWING * Pos(*bracket_marks()[0], 0)), "Start Here", "below right", lead=3/8)]),
        "step_06": (base, [], marks + step6),
        "step_07": (base, blocks, step7),
        "step_08": (base + foam_of(foams, "heavy"), [], step8 + insulation),
        "step_09": (ctx(uncovered(skids, ply[:1])) + ctx(uncovered(frame, ply[:1])) + foam_of(uncovered(foams, ply[:1]))
                    + ply_of(ply[:1]) + cov(covered(frame, ply[:1])), [], insulation),  # panel 1 (framing shows through the deck)
        "step_10": (ctx(uncovered(skids, ply[:2])) + ctx(uncovered(frame, ply[:2])) + foam_of(uncovered(foams, ply[:2]))
                    + ply_of(ply[:2]) + cov(covered(frame, ply[:2])), [], []),
        "step_11": (ply_of(ply) + cov(frame), [], []),
        "step_12": (ply_of(ply), [], step12),
    }
    figs = table(MD, rows)
    for fig in figs:
        step = int(fig.name[-2:])
        if step >= 4:  # which end is which
            fig.notes += [beside(whole.top, "above", Label("REAR", 3/16), 1/4), beside(whole.bottom, "below", Label("FRONT", 3/16), 1/4)]
        if 9 <= step <= 11:
            for n, sheet in enumerate(ply[:step - 8], 1):
                fig.notes.append(at(Extent(sheet).center, Label(f"Panel {n}", 3/16)))
        fig.notes.append(title(whole.bottom, f"Step {step}", gap=1 if step <= 3 or step == 6 else 5/8))
    return figs
