"""Half_Roof/half_roof.md figures: a half-roof as built in its jig, seen from
above its top face. Drawing X runs down the slope from the ridge board (the
rafters' tips at 4.54), Y along the roof."""

from build123d import Compound, Plane, Pos, Rot, extrude

from model.dimensions import HALF_ROOF_LENGTH, RAFTER_LENGTH
from model.lumber import width
from model.notes import Circle, Leader, horizontal_dimension, inches
from model.roof import (
    CROSS_BLOCKS_FROM_TIP, EAVE_BOARD, LAG_BORE_AT, LAG_COUNTERBORE, LAG_HOLE, RAFTER, RAFTER_DEPTH, RAFTER_Y,
    RIDGE_BOARD_BOTTOM, ROOF_Y, SLOPE, TAIL_U, TIP_U, TIP_X, ANGLE_PLATE_FROM_TIP, UNBORED, angle_plate,
    bored_rafter, cross_block, eave_board, rafter, ridge_board, HALF_ROOF_DRAWING, half_roof,
)

from . import Figure, break_box, camera, enlarged, figure_names, optional_parts, placed_notes, title

MD = "Half_Roof/half_roof.md"
TO_DRAWING = HALF_ROOF_DRAWING

DETAIL_SCALE = 2  # the insets are drawn at twice size
BRACKET_DETAIL_AT = (83.59, 20.83)  # the center of step 2's inset, in the drawing
BRACKET_DETAIL_REACH = 13  # how much of the rafter it shows, from the tip
BORE_DETAIL_AT = (81.45, 15.21)  # step 7's
BORE_DETAIL_REACH = (6, 8)  # past the bore up the rafter, and along the white board either way


def bracket_detail():
    """Step 2's inset: a rafter's tip from the side, its angle plate's leg on
    its face, the plate's distance from the tip dimensioned; and the line
    pointing it out from the plate in the drawing."""
    plate = Pos(RAFTER_LENGTH - ANGLE_PLATE_FROM_TIP[0], RAFTER, 0) * angle_plate.shape()  # on the rafter's +Y face
    window = extrude(Plane.XZ * Pos(RAFTER_LENGTH - BRACKET_DETAIL_REACH, -1)
                     * break_box(BRACKET_DETAIL_REACH + 1, RAFTER_DEPTH + 2, ("left",)), RAFTER + 2, both=True)
    shape, at = enlarged(Compound([rafter.shape() & window, plate]), camera((0, 1, 0)), DETAIL_SCALE, BRACKET_DETAIL_AT)
    tip, edge = at((RAFTER_LENGTH, 0, RAFTER_DEPTH)), at((RAFTER_LENGTH - ANGLE_PLATE_FROM_TIP[0], 0, 0))
    gap = -4  # the dimension line this far under the rafter
    notes = [(min(tip[0], edge[0]), edge[1] + gap, n)
             for n in horizontal_dimension(abs(edge[0] - tip[0]), inches(ANGLE_PLATE_FROM_TIP[0]), -1.5, -gap)]
    return [(shape, "hlr_thin")], notes


def bore_detail():
    """Step 7's inset: a rafter crossing the 1x8 white board, with its lag
    bolt bore, in isometric."""
    x, y, _ = LAG_BORE_AT
    up, along = BORE_DETAIL_REACH
    board = Pos(0, y - along, RAFTER_DEPTH) * eave_board.shape()
    window = extrude(Plane.XY * Pos(-1, y - along) * break_box(x + up + 1, 2 * along, ("right", "top", "bottom"), tooth=1/4),
                     2 * RAFTER_DEPTH + 2, both=True)
    shape, _ = enlarged(Compound([bored_rafter.shape() & window, board & window]), camera((1, -1, 2)), DETAIL_SCALE,
                        BORE_DETAIL_AT)
    return [(shape, "hlr_thin")], []


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
    details = {2: bracket_detail(), 7: bore_detail()}
    out = []
    for i, (fig_name, parts) in enumerate(zip(figure_names(MD), steps), 1):
        shown = {"manual:half_roof", f"manual:half_roof:{i}"}
        parts = parts + optional_parts(TO_DRAWING, half_roof, shown, "outline", "laid")
        notes = placed_notes(TO_DRAWING, half_roof, shown) + [title(f"Step {i}", 102, 66, 3.5, 90)]
        if i == 7:
            notes += bores
        if i in details:
            detail_parts, detail_notes = details[i]
            parts, notes = parts + detail_parts, notes + detail_notes
        out.append(Figure(MD, fig_name, parts, notes))
    return out
