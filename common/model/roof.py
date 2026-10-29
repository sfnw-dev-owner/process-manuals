"""The roof: two half-roof assemblies meeting at a ridge beam, structural
triangles on the end walls, the plywood deck, shingles, ridge vent, fascia,
soffits, and the siding in the gables.

Per Half_Roof/half_roof.md and images/half_roof.dxf; Structural_Triangle/triangle.dxf;
post-tilt-up/frame-completion.md and roof-blocking.md; Roof/roof_manual.md.

Frame: the house's X (across) and Y (along); Z = 0 at the top of the walls.

Geometry, from the pitch outward: the rafters' underside rises at ROOF_PITCH
from the inside face of the side walls' top plates (the structural triangle's
sloped edge) to the ridge, where each rafter's plumb-cut tip butts against its
half's 1x6 ridge board. The two ridge boards meet on the center line.
"""

from functools import cache
from math import cos, radians, sin, tan

from .common import *
from .walls import SIDING, WALL_DEPTH, WRAP

T, C, S = tan(radians(ROOF_PITCH)), cos(radians(ROOF_PITCH)), sin(radians(ROOF_PITCH))

RAFTER = thickness("2x4")  # 1 1/2, along the house
RAFTER_DEPTH = width("2x4")  # 3 1/2, square to the slope
RIDGE_BOARD, EAVE_BOARD = "1x6", "1x8"  # the "white boards"
FASCIA = "1x6"
DECK = 3/4  # plywood
SHINGLES = 1/2  # total thickness of the roofing layers, for the ridge vent
SIDING_FACE = WRAP + SIDING  # siding's outer face, outside the framing

RIDGE_X = PLATFORM_WIDTH / 2
SEAT_X = WALL_DEPTH  # where the rafters' underside meets the top of the wall
TIP_X = RIDGE_X - thickness(RIDGE_BOARD)  # the rafters' plumb-cut tips


def underside(x):
    """Height of the rafters' underside above the wall top, at x (left half)."""
    return (x - SEAT_X) * T


PLUMB_DEPTH = RAFTER_DEPTH / C  # a rafter's depth, measured plumb
RIDGE_TOP = underside(TIP_X) + PLUMB_DEPTH  # top of the rafters' tips and of the ridge boards
RIDGE_BOARD_BOTTOM = RIDGE_TOP - width(RIDGE_BOARD)

# The slope frame (left half): X up the slope from the rafters' seat on the
# wall, Z square to the slope (0 = rafters' underside), Y along the house.
SLOPE = Pos(SEAT_X, 0, 0) * Rot(Y=-ROOF_PITCH)
TIP_U = (TIP_X - SEAT_X) / C + RAFTER_DEPTH * T  # the rafters' top-edge tip, along the slope
TAIL_U = TIP_U - RAFTER_LENGTH  # rafter tails, cut square
DECK_TOP_U = TAIL_U + width(EAVE_BOARD) + ROOF_DECK_SHEET[0]  # top edge of the plywood

# Birdsmouth: a horizontal seat on the wall's top plate, reaching out past the
# siding so the rafter clears it.
BIRDSMOUTH_SEAT = SEAT_X + SIDING_FACE

# Along the house: the half-roofs overhang the front wall's framing by
# FRONT_ROOF_OVERHANG (frame-completion.md:92), and run HALF_ROOF_LENGTH.
ROOF_Y = PLATFORM_LENGTH + FRONT_ROOF_OVERHANG - HALF_ROOF_LENGTH

# Rafters along the half-roof (half_roof.dxf): at both ends, doubled one slot
# in from each end, and on 24" centers in between.
RAFTER_Y = [ROOF_Y + y for y in (
    0, 8, 8 + RAFTER,
    *[c - RAFTER / 2 for c in spaced(30, 24, 5)],
    HALF_ROOF_LENGTH - 11, HALF_ROOF_LENGTH - 11 + RAFTER,
    HALF_ROOF_LENGTH - RAFTER,
)]
# The "magic" rafter (roof-blocking.md "Align Magic Rafters"): the one over
# the side walls' stud 48" from the front, pulled onto it (the jig lays it
# 1/4" off), as the roof is drawn from then on.
MAGIC_RAFTER = min(range(len(RAFTER_Y)), key=lambda i: abs(RAFTER_Y[i] + RAFTER / 2 - (PLATFORM_LENGTH - 48)))
RAFTER_Y[MAGIC_RAFTER] = PLATFORM_LENGTH - 48 - RAFTER / 2


def bays():
    """(start, end) of the open space between adjacent rafters."""
    edges = sorted(RAFTER_Y)
    return [(a + RAFTER, b) for a, b in zip(edges, edges[1:]) if b - (a + RAFTER) > 1]


def wall_bays():
    """Bays between the rafters above the walls (not the end bays over the gables)."""
    return [(a, b) for a, b in bays() if a > 0 and b < PLATFORM_LENGTH]


# Cross blocks between the two rafters at each end, measured down the slope
# from the rafters' tips (half_roof.dxf: 17 1/8, 30 1/2, 43 7/8 from the
# drawing's origin, whose rafter tips are at 4.54).
CROSS_BLOCKS_FROM_TIP = [x - 4.54 for x in (17 + 1/8, 30 + 1/2, 43 + 7/8)]


@component
def roof():
    """Both halves of the roof and the structural triangles under them."""
    solids = []
    children = [
        (half_roof, Location(), [], ''),
        (half_roof, Pos(PLATFORM_WIDTH, 0, 0), ['mirror'], ''),
        (structural_triangle, Pos(RIDGE_X, 0, 0), [], ''),
        (structural_triangle, Pos(RIDGE_X, PLATFORM_LENGTH - WALL_DEPTH, 0), [], ''),
        (gable_skin, Pos(RIDGE_X, 0, 0) * Rot(Z=180), [], ''),
        (gable_skin, Pos(RIDGE_X, PLATFORM_LENGTH, 0), [], ''),
        (ridge_vent, Location(), [], ''),
        # Roofing on each side; the two sides use different start/end shingle sets.
        (roofing_a, Location(), [], 'Roofing'),
        (roofing_b, Pos(PLATFORM_WIDTH, 0, 0), ['mirror'], 'Roofing'),
        (cap_shingles, Location(), [], 'Roofing'),
    ]
    return solids, children


@component
def half_roof():
    """The left half-roof, as built in the half-roof jig and lifted on."""
    front_blocks, rear_blocks = RAFTER_Y[-2] + RAFTER, RAFTER_Y[0] + RAFTER
    solids = []
    children = [
        # Rafters: the inner ones are bored for lag bolts into the wall.
        *[(rafter if i in UNBORED else bored_rafter, SLOPE * Pos(TAIL_U, y, 0), [], '')
          for i, y in enumerate(RAFTER_Y)],
        # A35 angle plates on the rafters one slot in from each end, on the
        # side facing that end, bottom flush with the rafter's bottom.
        (angle_plate, SLOPE * Pos(TIP_U - ANGLE_PLATE_FROM_TIP[1], RAFTER_Y[1], 0) * Rot(Z=180), [], ''),
        (angle_plate, SLOPE * Pos(TIP_U - ANGLE_PLATE_FROM_TIP[0], RAFTER_Y[-2] + RAFTER, 0), [], ''),
        (ridge_board, Pos(TIP_X, ROOF_Y, RIDGE_BOARD_BOTTOM), [], ''),
        (eave_board, SLOPE * Pos(TAIL_U, ROOF_Y, RAFTER_DEPTH), [], ''),
        # Cross blocks between the pairs of rafters at each end.
        *[(cross_block, SLOPE * Pos(TIP_U - d - RAFTER, y, 0), [], '')
          for d in CROSS_BLOCKS_FROM_TIP for y in (rear_blocks, front_blocks)],
        # Bird blocks on the side wall's top plate and vent blocks against
        # the ridge board, in each bay above the walls.
        *[(bird_block(b - a), Pos(-SIDING_FACE, (a + b - bird_length(b - a)) / 2, 0), [], '')
          for a, b in wall_bays()],
        *[(vent_block(b - a), Pos(TIP_X - VENT_BLOCK_THICKNESS, (a + b - vent_length(b - a)) / 2,
                                  underside(TIP_X - VENT_BLOCK_THICKNESS) + PLUMB_DEPTH - VENT_BLOCK_HEIGHT), [], '')
          for a, b in wall_bays()],
        # Deck: two sheets, tight against the eave board.
        *[(deck_sheet, SLOPE * Pos(TAIL_U + width(EAVE_BOARD), y, RAFTER_DEPTH), [], '')
          for y in spaced(ROOF_Y, ROOF_DECK_SHEET[1], 2)],
        # Fascia on the end rafters, and soffits under the gable overhangs.
        (fascia, Pos(0, ROOF_Y - thickness(FASCIA), 0), [], ''),
        (fascia, Pos(0, ROOF_Y + HALF_ROOF_LENGTH, 0), [], ''),
        (soffit, Pos(0, PLATFORM_LENGTH + SIDING_FACE, 0), [], ''),
        (soffit, Pos(0, -SIDING_FACE - SOFFIT_WIDTH, 0), [], ''),
    ]
    return solids, children


@component
def rafter():
    """A 2x4 rafter, 56 3/4" along its top edge: square-cut tail at X = 0,
    birdsmouth over the wall, plumb cut at the tip. Z = 0 is its underside."""
    seat_u = -TAIL_U  # the seat's inner corner, from the tail
    a = (seat_u, 0)
    b = (seat_u - BIRDSMOUTH_SEAT * C, BIRDSMOUTH_SEAT * S)
    c = (seat_u - BIRDSMOUTH_SEAT / C, 0)
    tip = RAFTER_LENGTH
    solids = [
        TwoByFour(RAFTER_LENGTH, along="X", wide="Z")
        - extrude(Plane.XZ * (Polygon(c, a, b, align=None)
                              + Polygon((tip - RAFTER_DEPTH * T, 0), (tip, 0), (tip, RAFTER_DEPTH), align=None)),
                  -RAFTER),
    ]
    anchors = {  # on the top edge's center line
        "tip": Pos(tip, RAFTER / 2, RAFTER_DEPTH),
        "tail": Pos(0, RAFTER / 2, RAFTER_DEPTH),
    }
    return solids, [], anchors


# Lag bolt bores (Half_Roof/half_roof.md Step 7): vertical, a 13/16" spade-bit
# counterbore whose lower edge is 1/2" above the 1x8 eave board, then a
# straight bit down through the rafter. (half_roof.dxf draws the bores
# ~4" further up the rafter, where they would miss the wall's top plate; the
# text wins.) The rafters at the ends and those carrying angle plates aren't bored.
UNBORED = {0, 1, len(RAFTER_Y) - 2, len(RAFTER_Y) - 1}
LAG_COUNTERBORE = 13/16  # diameter
LAG_COUNTERBORE_DEPTH = 1 + 1/4  # as modeled in SketchUp
LAG_HOLE = 1/2  # the "larger straight drill bit"; size not given in the manual


LAG_BORE_AT = (width(EAVE_BOARD) + 1/2 + LAG_COUNTERBORE / 2 / C, RAFTER / 2, RAFTER_DEPTH)  # the bore's center on the rafter's top face


@component
def bored_rafter():
    """A rafter with its vertical lag bolt bore."""
    r = LAG_COUNTERBORE / 2
    x = LAG_BORE_AT[0]
    up = (S, 0, C)  # plumb, in the rafter's frame
    top = Location(Plane(origin=LAG_BORE_AT, x_dir=(C, 0, -S), z_dir=up))
    solids = [
        rafter.shape()
        - top * Cylinder(r, LAG_COUNTERBORE_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX))
        - top * Cylinder(LAG_HOLE / 2, 2 * PLUMB_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX)),
    ]
    return solids, [], {**rafter.anchors(), "bore": Pos(*LAG_BORE_AT)}


# A35 angle plates (Half_Roof/half_roof.md Step 2; placed per half_roof.dxf,
# Step 02: 3 1/2" long, starting 4 1/2" down the slope from the rafters' tips,
# reaching 1 3/4" out from the rafter).
ANGLE_PLATE = (3 + 1/2, 1 + 3/4, 1 + 1/2)  # length along the rafter, out, up the rafter's face
ANGLE_PLATE_GAUGE = 0.05  # 18 ga
ANGLE_PLATE_FROM_TIP = (9 - 4.54, 9 - 4.54 + ANGLE_PLATE[0])  # (near, far) edges, from the tip
ANGLE_PLATE_HOLE = 0.39  # diameter (half_roof.dxf)
ANGLE_PLATE_HOLES = (1/2, 1 + 3/4, 3)  # along the flat leg, from its near end
ANGLE_PLATE_HOLE_OUT = 1.4  # out from the rafter's face


@component
def angle_plate():
    """An A35 framing angle: one leg against the rafter's face (at Y = 0,
    the plate reaching toward +Y) and one flat along the rafter's bottom,
    reaching out over the structural triangle. X runs down the slope."""
    length, out, up = ANGLE_PLATE
    g = ANGLE_PLATE_GAUGE
    flat = Pos(-length, 0, 0) * Box(length, out, g, align=CORNER)
    for x in ANGLE_PLATE_HOLES:  # the flat leg's screw holes (as half_roof.dxf drew them)
        flat -= Pos(-length + x, ANGLE_PLATE_HOLE_OUT, -1) * Cylinder(ANGLE_PLATE_HOLE / 2, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    vertical = Pos(-length, 0, 0) * Box(length, g, up, align=CORNER)
    for x in ANGLE_PLATE_HOLES:  # and the leg on the rafter's face
        vertical -= Pos(-length + x, -1, up / 2) * Rot(X=-90) * Cylinder(ANGLE_PLATE_HOLE / 2, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return [vertical, flat], []


@component
def ridge_board():
    """A half's 1x6 white board; with the other half's, the ridge beam."""
    return [OneBySix(HALF_ROOF_LENGTH, along="Y", wide="Z")], []


@component
def eave_board():
    """The 1x8 white board on the rafter tails, flush with their ends."""
    return [OneByEight(HALF_ROOF_LENGTH, along="Y", wide="X")], []


@component
def cross_block():
    """Between two rafters, along Y; its ends' centers are its anchors."""
    ends = {"rear": Pos(RAFTER / 2, 0, RAFTER_DEPTH), "front": Pos(RAFTER / 2, CROSS_BLOCK_LENGTH, RAFTER_DEPTH)}
    return [TwoByFour(CROSS_BLOCK_LENGTH, along="Y", wide="Z")], [], ends


@component
def deck_sheet():
    width_, length_ = ROOF_DECK_SHEET
    return [Sheet(DECK, width_, length_, facing="Z")], []


# The deck's two options (Roof/roof_manual.md "Plywood Deck"; images/
# panel_options.dxf): two equal sheets (Panel_Saw_Operation.md), or three
# unequal pieces whose seams miss the rafters, joined by three hurricane
# (H-) clips on each seam, evenly spaced up the slope.
ROOF_DECK_PIECES = (18 + 1/2, 96, 41)  # the 3-piece option, from the front (panel_options.dxf)
H_CLIPS_PER_SEAM = 3
H_CLIP = (1 + 1/2, 1, 1/16)  # along the seam, across it, thick


@cache
def deck_piece(length):
    """A 48"-wide piece of deck plywood, `length` along the roof."""
    def piece():
        return [Sheet(DECK, ROOF_DECK_SHEET[0], length, facing="Z")], []
    piece.__name__ = f"deck_piece_{length:g}"
    return component(piece)


@component
def h_clip():
    """Holds two sheets' edges level; sits in the seam, flush with the top."""
    along, across, t = H_CLIP
    return [Box(along, across, t, align=(Align.MIN, Align.CENTER, Align.MAX))], []


def roof_deck(option):
    """[(component, location)] of a half-roof's deck, in its frame: option 2
    (two sheets) or 3 (three pieces and their clips)."""
    lengths = [ROOF_DECK_SHEET[1]] * 2 if option == 2 else list(reversed(ROOF_DECK_PIECES))  # from the rear
    u0 = TAIL_U + width(EAVE_BOARD)  # tight against the eave board
    out, y = [], ROOF_Y
    for i, length in enumerate(lengths):
        out.append((deck_piece(length), SLOPE * Pos(u0, y, RAFTER_DEPTH)))
        y += length
        if option == 3 and i < len(lengths) - 1:
            out += [(h_clip, SLOPE * Pos(u0 + ROOF_DECK_SHEET[0] * (k + 1/2) / H_CLIPS_PER_SEAM, y, RAFTER_DEPTH + DECK))
                    for k in range(H_CLIPS_PER_SEAM)]
    return out


# ── bird blocks and vent blocks ────────────────────────────────────────────

def bird_length(bay):
    return BIRD_BLOCK_LENGTH if bay > 20 else BIRD_BLOCK_END_LENGTH


def bird_block(bay):
    return _bird_block(bird_length(bay))


@cache
def _bird_block(length):
    """A 2x4 on edge on the wall's top plate between two rafters, its outer
    face flush with the siding, its top ripped at ROOF_PITCH to meet the roof
    deck on the rafters (Back_Saw_Cut_List.md:23: "band saw for 18.5 deg angle
    cut"). X in from the siding, Y along the wall, Z up from the plate."""
    @component
    def bird_block_():
        t = thickness("2x4")
        top = lambda x: underside(x - SIDING_FACE) + PLUMB_DEPTH  # the rafters' top edge, under the deck
        profile = Polygon((0, 0), (t, 0), (t, top(t)), (0, top(0)), align=None)
        return [extrude(Plane.XZ * profile, -length)], []
    return bird_block_


VENT_TOPPER = 3/8
VENT_SPACERS = 3 * (1/2)  # three 1/2" spacer strips, against the ridge board
VENT_BLOCK_THICKNESS = VENT_TOPPER + VENT_SPACERS


def vent_length(bay):
    return VENT_BLOCK_LENGTH if bay > 20 else VENT_BLOCK_END_LENGTH


def vent_block(bay):
    return _vent_block(vent_length(bay))


@cache
def _vent_block(length):
    """A ridge vent block: a solid topper, with spacer strips at both ends and
    in the middle on the side against the ridge board."""
    @component
    def vent_block_():
        spacer = 2
        solids = [Box(VENT_TOPPER, length, VENT_BLOCK_HEIGHT, align=CORNER)]
        for y in (0, (length - spacer) / 2, length - spacer):
            for i in range(3):  # three 1/2" strips, stacked against the topper
                solids.append(Pos(VENT_TOPPER + i * VENT_SPACERS / 3, y, 0) * Box(VENT_SPACERS / 3, spacer, VENT_BLOCK_HEIGHT, align=CORNER))
        return solids, []
    return vent_block_


# ── roofing ────────────────────────────────────────────────────────────────

# Roofing, per Roof/roof_manual.md: tar paper, a starter course along the
# eave and up the rakes, ten courses of shingles, and cap shingles over the
# ridge vent. Shingles are standard metric-size architectural shingles (not
# stated in the manual, but a course of start + end (42") + 3 full shingles
# spans the roof with the manual's 1" overhangs only for 39 3/8" shingles, and
# row 9 trimmed by 1 1/2" then tops out at the deck's edge at a 5 5/8" exposure).

TAR_PAPER = 1/32
STARTER = 1/8  # single-layer starter shingle
SHINGLE = 1/4  # double-layer shingle
COURSE_RISE = 1/16  # each course over the one below

EAVE_U = TAIL_U  # the eave edge: rafter tails and eave board, along the slope
ROOFING_BASE = RAFTER_DEPTH + DECK  # top of the deck, in the slope frame
FRONT_EDGE = ROOF_Y + HALF_ROOF_LENGTH + thickness(FASCIA)  # outer face of the front fascia
REAR_EDGE = ROOF_Y - thickness(FASCIA)  # outer face of the rear fascia
SHINGLE_FRONT = FRONT_EDGE + SHINGLE_OVERHANG
SHINGLE_REAR = REAR_EDGE - SHINGLE_OVERHANG
SHINGLE_BOTTOM_U = EAVE_U - SHINGLE_OVERHANG
SHINGLE_TOP_U = DECK_TOP_U  # rows 9 and 10 top out at the deck's top edge


def start_shingles(side):
    """Start-shingle lengths for courses 1..10 on one side of the roof, from
    the manual's cutting procedure ("First 8 Rows"): trim 3" off a shingle;
    each cut then makes a start/end pair totaling 42", alternating between
    the two sides, and the sequence restarts after five pairs per side. The
    last two pairs cut go to rows 9 and 10."""
    starts, rest = [], SHINGLE_LENGTH - SHINGLE_FIRST_TRIM
    while len(starts) < 20:
        for _ in range(10):
            starts.append(rest)
            rest = SHINGLE_LENGTH - (START_END_PAIR - rest)
        rest = SHINGLE_LENGTH - SHINGLE_FIRST_TRIM
    return starts[side::2][:10]


def course(start, height):
    """One course along the roof, from the front: a start piece, three full
    shingles, and an end piece filling the rest. Returns (y0, length) pieces."""
    pieces, y = [], SHINGLE_FRONT
    for length in [start] + [SHINGLE_LENGTH] * 3:
        pieces.append((y - length, length))
        y -= length
    pieces.append((SHINGLE_REAR, y - SHINGLE_REAR))
    return pieces


def roofing(side):
    rows = []
    for k, start in enumerate(start_shingles(side), 1):
        if k <= 8:
            bottom, height = SHINGLE_BOTTOM_U + (k - 1) * SHINGLE_EXPOSURE, SHINGLE_WIDTH
        else:  # row 9 loses 1 1/2" off the top; row 10 its top half
            height = SHINGLE_WIDTH - ROW_9_TRIM if k == 9 else SHINGLE_WIDTH / 2
            bottom = SHINGLE_TOP_U - height
        # Each course lies over the one below it, a little higher, so its
        # butt edge shows.
        z = ROOFING_BASE + TAR_PAPER + STARTER + (k - 1) * COURSE_RISE
        rows += [SLOPE * Pos(bottom, y0, z) * Box(height, length, SHINGLE, align=CORNER)
                 for y0, length in course(start, height)]

    # Tar paper: the lower sheet 1" below the eave, the upper up to the deck's
    # top edge; both 13'4" long, centered on the roof.
    y0 = (FRONT_EDGE + REAR_EDGE - TAR_PAPER_LENGTH) / 2
    paper = [SLOPE * Pos(u, y0, ROOFING_BASE) * Box(TAR_PAPER_WIDTH, TAR_PAPER_LENGTH, TAR_PAPER, align=CORNER)
             for u in (SHINGLE_BOTTOM_U, SHINGLE_TOP_U - TAR_PAPER_WIDTH)]

    # Starter course: half-width single-layer pieces along the eave, 1" past
    # the eave and the fascia at each end...
    z = ROOFING_BASE + TAR_PAPER
    starter_w = SHINGLE_WIDTH / 2
    eave = [(SHINGLE_FRONT - (i + 1) * SHINGLE_LENGTH, SHINGLE_LENGTH) for i in range(3)]
    eave.append((SHINGLE_REAR, SHINGLE_LENGTH))  # the 4th from the rear; scrap fills the gap
    gap0, gap1 = SHINGLE_REAR + SHINGLE_LENGTH, SHINGLE_FRONT - 3 * SHINGLE_LENGTH
    if gap1 > gap0:
        eave.append((gap0, gap1 - gap0))
    starters = [SLOPE * Pos(SHINGLE_BOTTOM_U, y, z) * Box(starter_w, length, STARTER, align=CORNER)
                for y, length in eave]
    # ...and up each rake, overlapping the eave row by 1 1/2", to the peak.
    u, top = SHINGLE_BOTTOM_U + starter_w - RAKE_STARTER_OVERLAP, (RIDGE_X - SEAT_X) / C
    while u < top:
        length = min(SHINGLE_LENGTH, top - u)
        for y in (SHINGLE_REAR, SHINGLE_FRONT - starter_w):
            starters.append(SLOPE * Pos(u, y, z) * Box(length, starter_w, STARTER, align=CORNER))
        u += length
    return paper + starters + rows


@component
def roofing_a():
    """Tar paper, starters and shingles on the left side of the roof."""
    return roofing(0), []


@component
def roofing_b():
    """The same on the right side (mirrored into place), with the other set of
    start/end shingles."""
    return roofing(1), []


RIDGE_VENT_HALF_WIDTH = 4 + 7/8  # as modeled in SketchUp
RIDGE_VENT_THICKNESS = 1/2


@component
def ridge_vent():
    """The ridge vent, centered on the ridge over the shingles, 2" past the
    fascia at each end (Roof/roof_manual.md: 161 1/2" long)."""
    def roof_top(x):  # top of the shingles, extended to the ridge
        return underside(x) + (RAFTER_DEPTH + DECK + SHINGLES) / C
    x0 = RIDGE_X - RIDGE_VENT_HALF_WIDTH
    lo = [(x0, roof_top(x0)), (RIDGE_X, roof_top(RIDGE_X)), (2 * RIDGE_X - x0, roof_top(x0))]
    hi = [(x, z + RIDGE_VENT_THICKNESS) for x, z in reversed(lo)]
    y0 = ROOF_Y - thickness(FASCIA) - RIDGE_VENT_OVERHANG
    length_ = HALF_ROOF_LENGTH + 2 * (thickness(FASCIA) + RIDGE_VENT_OVERHANG)
    solids = [Pos(0, y0, 0) * extrude(Plane.XZ * Polygon(*lo, *hi, align=None), -length_)]
    return solids, []


@component
def cap_shingles():
    """13" x 13" cap shingles over the ridge vent, from each end toward the
    middle, each covering the adhesive strip of the one before, plus a short
    piece over the seam in the middle (Roof/roof_manual.md, Cap Shingles)."""
    def vent_top(x):
        return underside(x) + (RAFTER_DEPTH + DECK + SHINGLES) / C + RIDGE_VENT_THICKNESS / C
    half = CAP_SHINGLE / 2
    lo = [(RIDGE_X - half, vent_top(RIDGE_X - half)), (RIDGE_X, vent_top(RIDGE_X)),
          (RIDGE_X + half, vent_top(RIDGE_X - half))]
    cap = Plane.XZ * Polygon(*lo, *[(x, z + SHINGLE) for x, z in reversed(lo)], align=None)
    y0 = ROOF_Y - thickness(FASCIA) - RIDGE_VENT_OVERHANG
    y1 = y0 + HALF_ROOF_LENGTH + 2 * (thickness(FASCIA) + RIDGE_VENT_OVERHANG)
    middle = (y0 + y1) / 2
    solids = []
    for i, y in enumerate(spaced(y0, SHINGLE_EXPOSURE, 99)):  # from the rear
        if y + CAP_SHINGLE > middle + SHINGLE_EXPOSURE:
            break
        solids.append(Pos(0, y, (i % 2) * SHINGLE) * extrude(cap, -CAP_SHINGLE))
    for i, y in enumerate(spaced(y1 - CAP_SHINGLE, -SHINGLE_EXPOSURE, 99)):  # from the front
        if y < middle - SHINGLE_EXPOSURE:
            break
        solids.append(Pos(0, y, (i % 2) * SHINGLE) * extrude(cap, -CAP_SHINGLE))
    short = CAP_SHINGLE / 2  # cut just below the adhesive line
    solids.append(Pos(0, middle - short / 2, 2 * SHINGLE) * extrude(cap, -short))
    return solids, []


# ── fascia and soffits ─────────────────────────────────────────────────────

SOFFIT_WIDTH = width("1x6")


@component
def fascia():
    """A fascia board on an end rafter: its top flush with the top of the
    deck, square at the eave, plumb-cut at the ridge's center line."""
    top, bottom = RAFTER_DEPTH + DECK, RAFTER_DEPTH + DECK - width(FASCIA)

    def at_ridge(h):  # slope position where the ridge center line crosses height h
        return (RIDGE_X - SEAT_X + h * S) / C
    profile = Polygon((TAIL_U, bottom), (at_ridge(bottom), bottom), (at_ridge(top), top), (TAIL_U, top), align=None)
    return [SLOPE * extrude(Plane.XZ * profile, -thickness(FASCIA))], []


@component
def soffit():
    """A 1x6 soffit under a gable overhang, from the siding out, running from
    the ridge beam down to the rafter tails."""
    top_at_ridge = (TIP_X - SEAT_X) / C
    profile = Polygon((TAIL_U, -thickness("1x6")), (top_at_ridge - thickness("1x6") * T, -thickness("1x6")),
                      (top_at_ridge, 0), (TAIL_U, 0), align=None)
    return [SLOPE * extrude(Plane.XZ * profile, -SOFFIT_WIDTH)], []


# ── structural triangles and gables ────────────────────────────────────────

# Structural_Triangle/triangle.dxf. Frame: X along the end wall from its
# center, Y through it (3 1/2", flush with the wall framing), Z up from the top
# of the wall. Its sloped top edges carry the rafters' underside.
TRI_HALF = END_WALL_PLATE_LENGTH / 2
TRI_BASE = thickness("2x4")  # the base 2x4 lies flat on the wall's top plate
TRI_SIDE_FOOT = 5  # the sides' feet on the base (triangle.dxf)
TRI_NOTCH_HALF = 1 + 1/8  # the notch at the peak for the ridge beam
# Studs, by the distance of their inner edge from the center (triangle.dxf):
# the center stud C is centered; E studs beside it; D studs further out.
TRI_E = thickness("2x4") / 2
TRI_D = 16 + 1/2


def tri_top(x):
    """The triangle's sloped top edge (= rafters' underside), x from center."""
    return (TRI_HALF - abs(x)) * T


def tri_inner(x):
    """The underside of the triangle's sloped sides."""
    foot = TRI_HALF - TRI_BASE / T - TRI_SIDE_FOOT
    return TRI_BASE + (foot - abs(x)) * T


# Its parts, labeled as in Cut_Lists/Structural_Triangle_Parts.md: the base
# B (2x4 flat, both ends cut at the pitch), the sloped sides A, the center
# stud C, and the studs E beside it and D further out, their tops cut at the
# pitch (E's tip then cut off under the ridge beam). Each part is placed in
# the triangle's frame; the right-hand A, D and E are mirrored.
TRI_BASE_END = TRI_HALF - TRI_BASE / T  # where the base's top meets the sides
TRI_FOOT = TRI_BASE_END - TRI_SIDE_FOOT  # the sides' inner foot on the base
TRI_PEAK = RIDGE_BOARD_BOTTOM  # the studs stop under the ridge beam


def triangle_part_label(letter):
    from .notes import Label
    return (Label(letter, 2), None, [], "manual:structural_triangle_parts")


def _flat(face):
    return extrude(Plane.XZ * face, -WALL_DEPTH)


@component
def triangle_base():
    """B: 89" at the bottom."""
    face = Polygon((-TRI_HALF, 0), (TRI_HALF, 0), (TRI_BASE_END, TRI_BASE), (-TRI_BASE_END, TRI_BASE), align=None)
    label = triangle_part_label("B")
    return [_flat(face)], [(label[0], Pos(-6.6, WALL_DEPTH, -1.7), [], label[3])]


@component
def triangle_side():
    """A: the left side, from its foot on the base up to the ridge notch."""
    n = TRI_NOTCH_HALF
    face = Polygon((-TRI_BASE_END, TRI_BASE), (-TRI_FOOT, TRI_BASE), (-n, tri_inner(n)), (-n, tri_top(n)), align=None)
    label = triangle_part_label("A")
    return [_flat(face)], [(label[0], Pos(-10.8, WALL_DEPTH, 13.3), [], label[3])]


@component
def triangle_center_stud():
    """C: square cut, up to the ridge beam."""
    stud = thickness("2x4")
    label = triangle_part_label("C")
    return ([_flat(Pos(-stud / 2, TRI_BASE) * Rectangle(stud, TRI_PEAK - TRI_BASE, align=CORNER))],
            [(label[0], Pos(-0.2, WALL_DEPTH, TRI_PEAK + 3.1), [], label[3])])


def triangle_stud(x0, letter, label_dx):
    """A stud from x0 (its inner edge) outward, its top cut at the pitch to
    follow the sides' underside (the first cut), then flat where that would
    reach above the ridge beam (the second cut)."""
    x1 = x0 + thickness("2x4")
    top0, top1 = tri_inner(x0), tri_inner(x1)
    top = [(x1, min(top1, TRI_PEAK)), (x0, min(top0, TRI_PEAK))]
    if top1 < TRI_PEAK < top0:  # the pitch cut crosses the ridge beam's underside within the stud
        top.insert(1, (x0 + (top0 - TRI_PEAK) / T, TRI_PEAK))
    face = Polygon((x0, TRI_BASE), (x1, TRI_BASE), *top, align=None)
    label = triangle_part_label(letter)
    return [_flat(face)], [(label[0], Pos(x0 + label_dx, WALL_DEPTH, TRI_BASE + 3.5), [], label[3])]


@component
def triangle_stud_e():
    """E: beside C."""
    return triangle_stud(TRI_E, "E", 2.85)


@component
def triangle_stud_d():
    """D: further out."""
    return triangle_stud(TRI_D, "D", -1.9)


def triangle_parts():
    """{label: [(component, location, mods)]} in the triangle's frame."""
    return {
        "B": [(triangle_base, Location(), [])],
        "A": [(triangle_side, Location(), []), (triangle_side, Location(), ['mirror'])],
        "C": [(triangle_center_stud, Location(), [])],
        "E": [(triangle_stud_e, Location(), []), (triangle_stud_e, Location(), ['mirror'])],
        "D": [(triangle_stud_d, Location(), []), (triangle_stud_d, Location(), ['mirror'])],
    }


@component
def structural_triangle():
    return [], [(c, loc, mods, '') for parts in triangle_parts().values() for c, loc, mods in parts]


# The gable skin (Exterior_Trim/exterior_trim.md, "Exterior Triangles"):
# pre-cut Tyvek stapled to the structural triangle, Z-flashing over the top
# of the wall's siding, then T1-11 in two pieces: a large triangle and a small
# one at the left corner (as seen from outside; images/triangles.dxf).
# Frame: X along the wall from its center, Y outward from the framing, Z up
# from the wall top. Seen from outside, the left is +X.
GABLE_NOTCH = thickness(RIDGE_BOARD)  # half-width of the notch around the ridge boards
Z_FLASHING = 1/32  # sheet metal
Z_FLASHING_SHORT_LEG = 1/2  # down over the wall's siding
Z_FLASHING_LONG_LEG = 2  # up behind the gable siding
GABLE_SIDING_LIFT = 1/2  # "a pencil-width above the Z-flashing fold"
GABLE_SMALL_PIECE = 8 + 1/2  # the small triangle's length at the bottom (triangles.dxf)


def gable_outline(bottom=0):
    """The gable up to the rafters' underside, notched for the ridge boards,
    from `bottom` up."""
    half = TRI_HALF - bottom / T
    n = GABLE_NOTCH
    return Polygon((-half, bottom), (half, bottom), (n, tri_top(n)), (n, RIDGE_BOARD_BOTTOM),
                   (-n, RIDGE_BOARD_BOTTOM), (-n, tri_top(n)), align=None)


@component
def gable_wrap():
    return [extrude(Plane.XZ * gable_outline(), -WRAP)], []


@component
def z_flashing():
    """Centered on the wall, its long leg's ends cut to the roof pitch."""
    half, t = TRI_HALF, Z_FLASHING
    long_leg = Polygon((-half, 0), (half, 0), (half - Z_FLASHING_LONG_LEG / T, Z_FLASHING_LONG_LEG),
                       (-half + Z_FLASHING_LONG_LEG / T, Z_FLASHING_LONG_LEG), align=None)
    solids = [
        Pos(0, WRAP, t) * extrude(Plane.XZ * long_leg, -t),
        Pos(-half, WRAP, 0) * Box(2 * half, SIDING + t, t, align=CORNER),  # resting on the siding's top edge
        Pos(-half, WRAP + SIDING, -Z_FLASHING_SHORT_LEG) * Box(2 * half, t, Z_FLASHING_SHORT_LEG + t, align=CORNER),
    ]
    return solids, []


def gable_siding_piece(x0, x1):
    """The gable's T1-11 between x0 and x1 (along the wall from its center)."""
    face = gable_outline(GABLE_SIDING_LIFT) & Pos(x0, 0) * Rectangle(x1 - x0, RIDGE_TOP, align=CORNER)
    return Pos(0, WRAP + Z_FLASHING, 0) * extrude(Plane.XZ * face, -SIDING)


SMALL_PIECE_X = TRI_HALF - GABLE_SIDING_LIFT / T - GABLE_SMALL_PIECE  # the seam


@component
def gable_siding_large():
    return [gable_siding_piece(-TRI_HALF, SMALL_PIECE_X)], []


@component
def gable_siding_small():
    return [gable_siding_piece(SMALL_PIECE_X, TRI_HALF)], []


@component
def gable_skin():
    """House wrap, Z-flashing and T1-11 in a gable, above the end wall's siding."""
    children = [
        (gable_wrap, Location(), [], ''),
        (z_flashing, Location(), [], ''),
        (gable_siding_large, Location(), [], ''),
        (gable_siding_small, Location(), [], ''),
        *gable_manual(),
    ]
    return [], children


# Exterior_Trim/exterior_trim.md's triangle figures show the gable from
# outside, one view per step, tagged "manual:exterior_trim:<view>". Note
# positions are in a view's drawing frame: x to the right from the gable's
# center, y up from the wall top.
GABLE_VIEWS = ["tyvek", "z_flashing", "siding_large", "siding_small"]


def gable_manual():
    from .notes import Circle, Label, Leader

    def at(x, y):
        return Pos(-x, WRAP + SIDING, y)

    def views(*vs):
        return " ".join(f"manual:exterior_trim:{v}" for v in vs)

    return [
        # (where the drawing had it, which differed between its upper and lower views)
        (Label("Existing T1-11 Siding", 3, attach=1), at(-18.39, -15.7), [], views("tyvek", "siding_large")),
        (Label("Existing T1-11 Siding", 3, attach=1), at(-20.41, -11.1), [], views("z_flashing", "siding_small")),
        (Label("Tyvek", 3, attach=1), at(-5.55, 10.55), [], views("tyvek")),
        (Label("Z-flashing", 3, attach=1), at(15.63, -5.38), [], views("z_flashing")),
        (Leader(((6.31, -6.44), (9.31, -6.44))), at(4.85, -0.47), [], views("z_flashing")),
        (Label("3.1", 4, attach=1), at(23.05, -6.14), [], views("siding_large")),
        (Circle(5.85), at(26.68, -8.47), [], views("siding_large")),
        (Leader(((6.47, -9.05), (9.83, -9.05))), at(11, GABLE_SIDING_LIFT), [], views("siding_large")),
        (Label("3.2", 4, attach=1), at(-32.86, -5.8), [], views("siding_small")),
        (Circle(5.85), at(-29.23, -8.13), [], views("siding_small")),
        (Leader(((3, -8.51), (5.06, -8.51))), at(-40.15, 0.41), [], views("siding_small")),
    ]
