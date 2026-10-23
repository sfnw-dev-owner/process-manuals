"""Half_Roof/half_roof.md figures: a half-roof as built in its jig, seen from
above its top face. Drawing X runs down the slope from the ridge board (the
rafters' tips at 4.54), Y along the roof."""

from build123d import Pos, Rot

from model.dimensions import HALF_ROOF_LENGTH
from model.notes import Circle
from model.roof import (
    CROSS_BLOCKS_FROM_TIP, EAVE_BOARD, LAG_BORE_AT, LAG_COUNTERBORE, LAG_HOLE, RAFTER, RAFTER_DEPTH, RAFTER_Y,
    RIDGE_BOARD_BOTTOM, ROOF_Y, SLOPE, TAIL_U, TIP_U, TIP_X, ANGLE_PLATE_FROM_TIP, UNBORED, angle_plate,
    cross_block, eave_board, rafter, ridge_board, HALF_ROOF_DRAWING, half_roof,
)

from . import Figure, figure_names, optional_parts, placed_notes, title

MD = "Half_Roof/half_roof.md"
TO_DRAWING = HALF_ROOF_DRAWING


def top_edge(shape):
    """A part as just its top face's footprint, a thin slab. The ridge board
    is notched in plumb, so flat in the jig it leans by the roof's pitch and
    its face shows from above; the drawing showed only its 3/4" edge."""
    from build123d import Face, Wire, extrude
    top = max(shape.faces(), key=lambda f: f.normal_at().Z)
    z = top.center().Z
    pts = [(e.position_at(0).X, e.position_at(0).Y, z) for e in top.outer_wire().order_edges()]
    return extrude(Face(Wire.make_polygon(pts, close=True)), -0.1)


def figures():
    at = lambda loc, comp: TO_DRAWING * (loc * comp.shape())
    rafters = {i: at(SLOPE * Pos(TAIL_U, y, 0), rafter) for i, y in enumerate(RAFTER_Y)}
    # The lag bolt bores (step 7), drawn as the drawing did: the counterbore
    # around the hole, white, at the bore's center (the bores are plumb, so
    # the model's, seen square to the rafters, would show the counterbore's
    # floor off to one side).
    bores = []
    for i, y in enumerate(RAFTER_Y):
        if i in UNBORED:
            continue
        c = (TO_DRAWING * SLOPE * Pos(TAIL_U, y, 0) * Pos(*LAG_BORE_AT)).position
        bores += [(c.X, c.Y, Circle(LAG_COUNTERBORE / 2, fill=(255, 255, 255))), (c.X, c.Y, Circle(LAG_HOLE / 2, fill=(255, 255, 255)))]
    last = len(RAFTER_Y) - 1
    ridge = [top_edge(at(Pos(TIP_X, ROOF_Y, RIDGE_BOARD_BOTTOM), ridge_board))]
    plates = [at(SLOPE * Pos(TIP_U - ANGLE_PLATE_FROM_TIP[1], RAFTER_Y[1], 0) * Rot(Z=180), angle_plate),
              at(SLOPE * Pos(TIP_U - ANGLE_PLATE_FROM_TIP[0], RAFTER_Y[-2] + RAFTER, 0), angle_plate)]
    blocks = [at(SLOPE * Pos(TIP_U - d - RAFTER, y, 0), cross_block)
              for d in CROSS_BLOCKS_FROM_TIP for y in (RAFTER_Y[0] + RAFTER, RAFTER_Y[-2] + RAFTER)]
    eave = [at(SLOPE * Pos(TAIL_U, ROOF_Y, RAFTER_DEPTH), eave_board)]

    ends = [rafters[0], rafters[1], rafters[last - 1], rafters[last]]  # end rafters and the ones one slot in
    inner = [rafters[i] for i in range(2, last - 1)]
    ctx = lambda xs: [(s, "context") for s in xs]
    new = lambda xs: [(s, "new") for s in xs]
    outl = lambda xs: [(s, "outline") for s in xs]
    jig = [(s, "jig") for s in ridge + ends + plates + blocks + inner + eave]
    steps = [
        jig + new(ridge),                                              # 1: 1x6 in the jig
        jig + ctx(ridge) + new(ends) + outl(plates),                   # 2: notched rafters with angle plates
        jig + ctx(ridge + ends) + outl(plates) + new(blocks),                # 3: cross blocks
        jig + ctx(ridge + ends + blocks) + outl(plates) + new(inner),        # 4: the doubled and inner rafters
        ctx(ridge + ends + blocks + inner) + outl(plates) + new(eave),       # 5: 1x8 at the bottom
        ctx(ridge + ends + blocks + inner + eave) + outl(plates),            # 6: second screws
        ctx(ridge + ends + blocks + eave + inner),                           # 7: lag bolt bores (drawn as notes; the plates, under the rafters, left out)
    ]
    out = []
    for i, (fig_name, parts) in enumerate(zip(figure_names(MD), steps), 1):
        shown = {"manual:half_roof", f"manual:half_roof:{i}"}
        parts = parts + optional_parts(TO_DRAWING, half_roof, shown, "outline", "laid")
        notes = placed_notes(TO_DRAWING, half_roof, shown) + [title(f"Step {i}", 102, 66, 3.5, 90)]
        if i == 7:
            notes += bores
        out.append(Figure(MD, fig_name, parts, notes))
    return out
