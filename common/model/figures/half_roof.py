"""Half_Roof/half_roof.md figures: a half-roof as built in its jig, seen from
above its top face, step by step. Drawing X runs down the slope from the
rafters' tips (the ridge board at X < 0), Y along the roof from the front
(the rear, the jig's "TOP", at the top of the drawing)."""

from build123d import Compound, Cylinder, Plane, Pos, Rot, extrude

from model.dimensions import (
    ANGLE_PLATE_FROM_TIP, CROSS_BLOCKS_FROM_TIP, FRONT_ROOF_OVERHANG, HALF_ROOF_LENGTH, RAFTER_LENGTH,
)
from model.lumber import width
from model.notes import (
    CIRCLED, SMALL, TITLE, Label, aimed, around, at, beside, callout, circled, dimension, icon, inches, line, next_to, pointer,
    title,
)
from model.roof import (
    ANGLE_PLATE_EDGES, EAVE_BOARD, LAG_COUNTERBORE, LAG_HOLE, RAFTER, RAFTER_DEPTH, RAFTER_Y,
    RIDGE_BOARD_BOTTOM, ROOF_Y, SLOPE, TAIL_U, TIP_U, TIP_X, UNBORED, angle_plate, bored_rafter, cross_block,
    eave_board, rafter, ridge_board
)

from . import Extent, Figure, break_box, camera, enlarged, extent, table, xy

MD = "Half_Roof/half_roof.md"

# The drawing: the slope frame (roof.py) seen from above the roof, turned so
# X runs down the slope from the rafters' tips and Y along the roof from the front.
HALF_ROOF_DRAWING = Pos(TIP_U, ROOF_Y + HALF_ROOF_LENGTH, 0) * Rot(Z=180) * SLOPE.inverse()
TO_DRAWING = HALF_ROOF_DRAWING

DETAIL_SCALE = 2  # the insets are drawn at twice size
DETAIL_OFF = 18  # an inset's center this far (drawing inches) right of the eave board
BRACKET_DETAIL_REACH = 13  # how much of the rafter step 2's inset shows, from the tip
BORE_DETAIL_REACH = (6, 8)  # step 7's: past the bore up the rafter, and along the white board either way
DOUBLING_SCREWS = 4  # along a doubled pair of rafters (step 4)
HOLE = 1/40  # a pre-drilled hole as drawn, paper inches


def top_edge(shape):
    """A part as just its top face's footprint, a thin slab. The ridge board
    is notched in plumb, so flat in the jig it leans by the roof's pitch and
    its face shows from above; the drawing shows only its 3/4" edge."""
    from build123d import Face, Wire
    top = max(shape.faces(), key=lambda f: f.normal_at().Z)
    z = top.center().Z
    pts = [(e.position_at(0).X, e.position_at(0).Y, z) for e in top.outer_wire().order_edges()]
    return extrude(Face(Wire.make_polygon(pts, close=True)), -0.1)


def disk(point, radius):
    """A white disk on the drawing at a point: a hole as seen from above."""
    return (Pos(*point, 50) * Cylinder(radius, 0.01), "outline", (255, 255, 255))


def bracket_detail(scale, at_):
    """Step 2's inset: a rafter's tip from the side, its angle plate's leg on
    its face, the plate's distance from the tip dimensioned. Returns its
    parts and notes, and its Extent."""
    plate = Pos(RAFTER_LENGTH - ANGLE_PLATE_FROM_TIP, RAFTER, 0) * angle_plate.shape()  # on the rafter's +Y face
    window = extrude(Plane.XZ * Pos(RAFTER_LENGTH - BRACKET_DETAIL_REACH, -1)
                     * break_box(BRACKET_DETAIL_REACH + 1, RAFTER_DEPTH + 2, ("left",)), RAFTER + 2, both=True)
    shape, to_drawing = enlarged(Compound([rafter.shape() & window, plate]), camera((0, 1, 0)), DETAIL_SCALE, at_)
    tip, edge = to_drawing((RAFTER_LENGTH, 0, RAFTER_DEPTH)), to_drawing((RAFTER_LENGTH - ANGLE_PLATE_FROM_TIP, 0, 0))
    notes = dimension((tip[0], edge[1]), edge, scale, inches(ANGLE_PLATE_FROM_TIP), offset=-3/16)
    return [(shape, "hlr_thin")], notes, Extent(shape)


def bore_detail(at_):
    """Step 7's inset: a rafter crossing the 1x8 white board, with its lag
    bolt bore, in isometric."""
    x, y, _ = bored_rafter.anchors()["bore"].position
    up, along = BORE_DETAIL_REACH
    board = Pos(0, y - along, RAFTER_DEPTH) * eave_board.shape()
    window = extrude(Plane.XY * Pos(-1, y - along) * break_box(x + up + 1, 2 * along, ("right", "top", "bottom"), tooth=1/4),
                     2 * RAFTER_DEPTH + 2, both=True)
    shape, _ = enlarged(Compound([bored_rafter.shape() & window, board & window]), camera((1, -1, 2)), DETAIL_SCALE, at_)
    return [(shape, "hlr_thin")], Extent(shape)


def figures(scale=1/20, only=None):
    place = lambda loc, comp: TO_DRAWING * (loc * comp.shape())
    rafter_at = {i: SLOPE * Pos(TAIL_U, y, 0) for i, y in enumerate(RAFTER_Y)}
    rafters = {i: place(loc, rafter) for i, loc in rafter_at.items()}
    point = lambda i, anchor: xy(TO_DRAWING * rafter_at[i] * rafter.anchors()[anchor])
    tips = {i: point(i, "tip") for i in rafter_at}
    tails = {i: point(i, "tail") for i in rafter_at}
    bores = {i: xy(TO_DRAWING * rafter_at[i] * bored_rafter.anchors()["bore"]) for i in rafter_at if i not in UNBORED}
    last = len(RAFTER_Y) - 1
    ridge = [top_edge(place(Pos(TIP_X, ROOF_Y, RIDGE_BOARD_BOTTOM), ridge_board))]
    plate_at = SLOPE * Pos(TIP_U - ANGLE_PLATE_FROM_TIP, RAFTER_Y[last - 1] + RAFTER, 0)
    plates = [place(SLOPE * Pos(TIP_U - ANGLE_PLATE_EDGES[1], RAFTER_Y[1], 0) * Rot(Z=180), angle_plate),
              place(plate_at, angle_plate)]
    # Cross blocks between the pairs of rafters at each end: (block, the pair's outer and inner rafters)
    blocks = [(place(SLOPE * Pos(TIP_U - d - RAFTER, y, 0), cross_block), outer, inner)
              for d in CROSS_BLOCKS_FROM_TIP
              for y, outer, inner in ((RAFTER_Y[0] + RAFTER, 0, 1), (RAFTER_Y[last - 1] + RAFTER, last, last - 1))]
    eave = [place(SLOPE * Pos(TAIL_U, ROOF_Y, RAFTER_DEPTH), eave_board)]

    ends = [rafters[0], rafters[1], rafters[last - 1], rafters[last]]  # end rafters and the ones one slot in
    doubled = {2: 1, last - 2: last - 1}  # step 4's third rafters, beside the inner rafter of each end pair
    inner = [rafters[i] for i in range(2, last - 1)]
    ctx = lambda xs: [(s, "context") for s in xs]
    new = lambda xs: [(s, "new") for s in xs]
    outl = lambda xs: [(s, "outline") for s in xs]
    block_shapes = [b for b, _, _ in blocks]
    jig = [(s, "jig") for s in ridge + ends + plates + block_shapes + inner + eave]

    ridge_ext, eave_ext = extent(ridge), extent(eave)
    whole = Extent(*ridge, *ends, *inner, *eave)
    across = lambda s: Extent(s)  # a rafter's or block's box

    def every(step):
        """The notes every step has: which end of the jig is which (the
        ridge is its top), and the caption."""
        return [
            beside((ridge_ext.center[0], whole.y0), "below", Label("TOP", TITLE), gap=5/8),
            beside((eave_ext.center[0], whole.y0), "below", Label("BOTTOM", TITLE), gap=5/8),
            title(whole.bottom, f"Half Roof Assembly\nStep {step}", gap=1),
        ]

    def ridge_screws(indexes):
        """Two screws through the ridge board into each of these rafters' tips."""
        out = []
        for i in indexes:
            screw = aimed((ridge_ext.x0, tips[i][1]), "Screw", "left")
            out += [screw, next_to(screw, "left", Label("x2"))]
        return out

    def eave_screws(second=False):
        """A screw through the white board into each rafter's tail (the
        doubled pairs: one screw drawn, "x2"), and the holes drilled for
        them: a second row, up the board, for step 6."""
        out, holes, screws = [], [], {}
        hole_x = eave_ext.x1 - (0.6 if second else 1.5)  # in from the board's lower edge, or near its upper one
        done = set()
        for i in rafter_at:
            pair = doubled.get(i) or next((j for j, k in doubled.items() if k == i), None)
            y = tails[i][1] if pair is None else (tails[i][1] + tails[pair][1]) / 2
            if pair is not None and pair in done:
                continue
            done.add(i)
            screws[i] = screw = aimed((eave_ext.x1, y), "Screw", "right")
            out.append(screw)
            if pair is not None:
                out.append(next_to(screw, "right", Label("x2")))
            holes.append(disk((hole_x, y), HOLE / scale))
        return out, holes, screws

    # step 2: the plate on the drawing circled, and the inset, with a line between them
    plate_ext = Extent(plates[1])
    plate_r = max(plate_ext.width, plate_ext.height) / 2 * scale + 1/16
    plate_ring = around(plate_ext.center, plate_r)
    bracket_r = (BRACKET_DETAIL_REACH + 1) * DETAIL_SCALE / 2 * scale + 1/8  # (the inset's width, with the plate)
    bracket_parts, bracket_notes, bracket_ext = bracket_detail(
        scale, (eave_ext.x1 + DETAIL_OFF, whole.y0 + bracket_r / scale + 10))
    bracket_ring = around(bracket_ext.center, bracket_r)
    step2 = [
        plate_ring, bracket_ring, *bracket_notes,
        line(plate_ext.center, bracket_ext.center, scale, short=(plate_r, bracket_r)),
        beside((bracket_ext.center[0], bracket_ext.center[1] - bracket_r / scale), "below",
               Label("Note: Rafter bracket at other end\nis on outside of rafter", SMALL), 1/8),
    ]
    # step 3: screws through the end pairs into each cross block, and the pairs clamped below each block
    step3 = []
    for block, outer, inner_ in blocks:
        bx = across(block).center[0]
        outer_ext, inner_ext = across(rafters[outer]), across(rafters[inner_])
        outside = "above" if outer_ext.y0 > inner_ext.y0 else "below"
        inside = "below" if outside == "above" else "above"
        for side, ext_ in ((outside, outer_ext), (inside, inner_ext)):
            edge = (bx, ext_.y1 if side == "above" else ext_.y0)
            screw = aimed(edge, "Screw", side)
            step3 += [screw, next_to(screw, "left", Label("x2"))]
    for outer, inner_ in ((0, 1), (last, last - 1)):
        x = across(blocks[2][0]).center[0] + 7  # just below the middle block (down the slope)
        outer_ext, inner_ext = across(rafters[outer]), across(rafters[inner_])
        up = outer_ext.y0 > inner_ext.y0
        step3.append(pointer((x, outer_ext.y1 if up else outer_ext.y0), 0, 1/4 if up else -1/4))
        step3 += callout((x, inner_ext.y0 if up else inner_ext.y1), "CLAMP", "below right" if up else "above right", lead=5/8)
    # step 4: the doubled rafters screwed together from inside, and the inner rafters' tips screwed
    step4 = ridge_screws(range(2, last - 1))
    bottom_block = max(CROSS_BLOCKS_FROM_TIP) + RAFTER
    for third, second in doubled.items():
        pair = Extent(rafters[third], rafters[second])
        bay_side = "below" if pair.y0 > whole.center[1] else "above"  # the open bay the screws are driven from
        edge_y = pair.y0 if bay_side == "below" else pair.y1
        for k in range(DOUBLING_SCREWS):
            x = 3 + (bottom_block - 6) * (k + 1/2) / DOUBLING_SCREWS
            step4.append(aimed((x, edge_y), "Screw", bay_side))
    # steps 5 and 6: the white board screwed to the rafter tails
    screws5, holes5, _ = eave_screws()
    screws6, holes6, by_rafter = eave_screws(second=True)
    step5 = screws5 + [beside(eave_ext.top_right, "above right", Label("Flush\nthis end", SMALL), 1/8)]
    step6 = screws6 + [next_to(by_rafter[last], "right", Label("Rout off if board\nhangs over rafter", SMALL), 1/8)]
    # step 7: the lag bolt bores, the pencil marks on the ridge board, and the inset
    bore_disks = [disk(p, r / 2) for p in bores.values() for r in (LAG_COUNTERBORE, LAG_HOLE)]
    step7 = []
    for p in bores.values():
        two = (p[0] - 6, p[1] - 6)
        step7 += circled((two[0] - 2 * CIRCLED / scale - 1, two[1]), "1") + circled(two, "2")
        step7.append(pointer(p, (two[0] - p[0]) * scale, (two[1] - p[1]) * scale))
    marks = []
    for end, sign in ((ridge_ext.y1, -1), (ridge_ext.y0, 1)):
        y = end + sign * FRONT_ROOF_OVERHANG
        marks.append(line((ridge_ext.x0, y), (ridge_ext.x1, y), scale, weight=1))
        step7 += dimension((ridge_ext.x0, end), (ridge_ext.x0, y), scale, offset=-1/4)
        step7 += circled((ridge_ext.x0 - 12, y), "3") + [pointer((ridge_ext.x0, y), -12 * scale + 1/8, 0)]
    step7 += marks
    bore_parts, bore_ext = bore_detail((eave_ext.x1 + DETAIL_OFF, 24))
    step7.append(beside(bore_ext.bottom, "below", Label('Edge of bored hole\nshould be 1/2"\nabove white board', SMALL), 1/8))
    legend_x = eave_ext.x1 + 6
    for k, text in enumerate(("Spade bit,\nperpendicular to floor", "Straight bit,\nperpendicular to floor",
                              "Pencil mark at bottom\nof white board")):
        p = (legend_x, whole.y1 - 24 - 12 * k)
        step7 += circled(p, str(k + 1)) + [beside(p, "right", Label(text, SMALL), 1/8 + 1/16)]

    rows = {
        "step_01": (jig + new(ridge), [], [
            aimed((ridge_ext.x0, ridge_ext.point(0, 11/12)[1]), "mallet", "left"),
            aimed((ridge_ext.x0, ridge_ext.point(0, 1/12)[1]), "mallet", "left"),
        ]),
        "step_02": (jig + ctx(ridge) + new(ends) + outl(plates) + bracket_parts, [], ridge_screws([0, 1, last - 1, last]) + step2),
        "step_03": (jig + ctx(ridge + ends) + outl(plates) + new(block_shapes), [], step3),
        "step_04": (jig + ctx(ridge + ends + block_shapes) + outl(plates) + new(inner), [], step4),
        "step_05": (ctx(ridge + ends + block_shapes + inner) + outl(plates) + new(eave) + holes5, [], step5),
        "step_06": (ctx(ridge + ends + block_shapes + inner + eave) + outl(plates) + holes5 + holes6, [], step6),
        "step_07": (ctx(ridge + ends + block_shapes + eave + inner) + bore_disks + bore_parts, [], step7),
    }
    figs = table(MD, rows)
    for fig in figs:
        fig.notes += every(int(fig.name[-1]))
    return figs
