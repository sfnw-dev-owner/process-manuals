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
        *half_roof_manual(),
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
    return solids, []


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
    return solids, []


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
    return [TwoByFour(CROSS_BLOCK_LENGTH, along="Y", wide="Z")], []


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


# ── Half_Roof/half_roof.md figures ─────────────────────────────────────────
# Tools and annotations, tagged "manual:half_roof:<step>". Positions are in
# the drawing's frame: the half-roof in its jig seen from above its top
# face, x down the slope from the ridge board (the rafters' tips at 4.54),
# y along the roof.

from .notes import Circle, Icon, Label, Leader, Lines, vertical_dimension  # noqa: E402

HALF_ROOF_DRAWING = (Pos(4.54 + TIP_U, ROOF_Y + HALF_ROOF_LENGTH, 0) * Rot(Z=180) * SLOPE.inverse())


def half_roof_manual():
    def at(x, y):
        return HALF_ROOF_DRAWING.inverse() * Pos(x, y, 0)

    def steps(*ns):
        return " ".join(f"manual:half_roof:{n}" for n in ns)

    every = "manual:half_roof"
    out = [
        (Label("TOP", 4, attach=1, rotation=90), at(-8.91, 84.45), [], every),
        (Label("BOTTOM", 4, attach=1, rotation=90), at(75.55, 80.05), [], every),
        (Label("Half Roof Assembly", 4, attach=1, rotation=90), at(96, 57), [], every),
    ]
    # Step 7: the overhang past the end rafters' bores
    out += [(n, at(-0.52, 0.09), [], steps(7)) for n in vertical_dimension(6.25, '6.25"')]
    out += [(n, at(1, 149.75), [], steps(7)) for n in vertical_dimension(6.25, '6.25"')]
    # Step 01
    t = steps('1')
    out += [
        (Icon('mallet', 7.68, 7.68), at(-0.15, 9.86), [], t),
        (Icon('mallet', 7.68, 7.68), at(-0.15, 143.86), [], t),
    ]
    # Step 02
    t = steps('2')
    out += [
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.4, 0.44), [], t),
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.4, 8.44), [], t),
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.4, 146.94), [], t),
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.4, 154.94), [], t),
        (Label('6"', 1.5, attach=1), at(77.3, 14.14), [], t),
        (Label('Note: Rafter bracket at other end\n  is on outside of rafter', 2.5, attach=1, rotation=90), at(82.9, 39.59), [], t),
        (Label('x2', 3, attach=3), at(-8, 2.5), [], t),
        (Label('x2', 3, attach=3), at(-8, 10.5), [], t),
        (Label('x2', 3, attach=3), at(-8, 149), [], t),
        (Label('x2', 3, attach=3), at(-8, 157), [], t),
        (Leader(((-3.25, 0),)), at(82.95, 13.32), [], t),
        (Leader(((3.54, 0),)), at(73.16, 13.32), [], t),
        (Circle(0.39), at(84.06, 20.03), [], t),
        (Circle(0.39), at(86.56, 20.03), [], t),
        (Circle(0.39), at(89.06, 20.03), [], t),
        (Circle(15), at(82.7, 22.04), [], t),
        (Circle(4.27), at(10.78, 7.46), [], t),
        (Lines((((14.98, -1.93), (14.98, 1.57)), ((14.98, -1.93), (21.98, -1.93)), ((21.98, -1.93), (21.98, 1.57)), ((21.98, 1.57), (14.98, 1.57)), ((2.7, 5.13), (27.96, 5.13)), ((5.04, -1.88), (28.21, -1.88)), ((5.04, -1.88), (2.7, 5.13)), ((27.96, 5.16), (27.96, 5.06)), ((27.96, 5.06), (27.86, 4.87)), ((27.86, 4.87), (27.76, 4.87)), ((27.76, 4.87), (27.66, 4.87)), ((27.66, 4.87), (27.66, 4.77)), ((27.66, 4.77), (27.57, 4.77)), ((27.57, 4.77), (27.47, 4.77)), ((27.47, 4.77), (27.47, 4.67)), ((27.47, 4.67), (27.18, 4.58)), ((27.18, 4.58), (27.08, 4.48)), ((27.08, 4.48), (26.89, 4.38)), ((26.89, 4.38), (26.79, 4.38)), ((26.79, 4.38), (26.59, 4.19)), ((26.59, 4.19), (26.4, 4.09)), ((26.4, 4.09), (26.21, 4.09)), ((26.21, 4.09), (26.11, 3.9)), ((26.11, 3.9), (25.82, 3.9)), ((25.82, 3.9), (25.82, 3.8)), ((25.82, 3.8), (25.82, 3.6)), ((25.82, 3.6), (25.82, 3.51)), ((25.82, 3.51), (25.82, 3.41)), ((25.82, 3.41), (25.91, 3.31)), ((25.91, 3.31), (25.91, 3.21)), ((25.91, 3.21), (26.11, 3.12)), ((26.11, 3.12), (26.3, 2.83)), ((26.3, 2.83), (26.3, 2.63)), ((26.3, 2.63), (26.4, 2.53)), ((26.4, 2.53), (26.5, 2.34)), ((26.5, 2.34), (26.59, 2.24)), ((26.59, 2.24), (26.69, 2.15)), ((26.69, 2.15), (26.79, 2.15)), ((26.79, 2.15), (26.89, 2.15)), ((26.89, 2.15), (26.89, 2.05)), ((26.89, 2.05), (26.89, 1.95)), ((26.89, 1.95), (26.98, 1.85)), ((26.98, 1.85), (27.18, 1.76)), ((27.18, 1.76), (27.37, 1.76)), ((27.37, 1.76), (27.47, 1.66)), ((27.47, 1.66), (27.57, 1.66)), ((27.57, 1.66), (27.66, 1.66)), ((27.66, 1.66), (27.66, 1.56)), ((27.66, 1.56), (27.76, 1.56)), ((27.76, 1.56), (27.76, 1.46)), ((27.76, 1.46), (27.76, 1.37)), ((27.76, 1.37), (27.86, 1.27)), ((27.86, 1.27), (27.86, 1.08)), ((27.86, 1.08), (27.86, 0.98)), ((27.86, 0.98), (27.86, 0.88)), ((27.86, 0.88), (27.86, 0.78)), ((27.86, 0.78), (27.86, 0.69)), ((27.86, 0.69), (27.86, 0.59)), ((27.86, 0.59), (27.86, 0.49)), ((27.86, 0.49), (27.86, 0.4)), ((27.86, 0.4), (27.86, 0.2)), ((27.86, 0.2), (27.86, 0.1)), ((27.86, 0.1), (27.86, 0.01)), ((27.86, 0.01), (27.86, -0.19)), ((27.86, -0.19), (27.86, -0.29)), ((27.86, -0.29), (27.86, -0.38)), ((27.86, -0.38), (27.86, -0.48)), ((27.86, -0.48), (27.86, -0.58)), ((27.86, -0.58), (27.86, -0.67)), ((27.86, -0.67), (27.76, -0.77)), ((27.76, -0.77), (27.66, -0.77)), ((27.66, -0.77), (27.57, -0.77)), ((27.57, -0.77), (27.57, -0.87)), ((27.57, -0.87), (27.57, -0.97)), ((27.57, -0.97), (27.66, -0.97)), ((27.66, -0.97), (27.76, -0.97)), ((27.76, -0.97), (27.86, -0.97)), ((27.86, -0.97), (27.86, -1.06)), ((27.86, -1.06), (27.96, -1.06)), ((27.96, -1.06), (28.05, -1.06)), ((28.05, -1.06), (28.15, -1.06)), ((28.15, -1.06), (28.15, -1.16)), ((28.15, -1.16), (28.25, -1.16)), ((28.25, -1.16), (28.34, -1.16)), ((28.34, -1.16), (28.54, -1.16)), ((28.54, -1.16), (28.54, -1.26)), ((28.54, -1.26), (28.54, -1.45)), ((28.54, -1.45), (28.54, -1.55)), ((28.54, -1.55), (28.34, -1.55)), ((28.34, -1.55), (28.34, -1.65)), ((28.34, -1.65), (28.25, -1.65)), ((28.25, -1.65), (28.21, -1.88)), ((5.13, -2.56), (5.13, -6.56)), ((14.98, -2.56), (14.98, -6.56)), ((0, 0), (-52.97, -10.21)))), at(67.97, 19.21), [], t),
    ]
    # Step 03
    t = steps('3')
    out += [
        (Icon('Screw', 4, 9.6, flip=True), at(17.71, 160.61), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(17.8, 141.9), [], t),
        (Icon('Screw', 4, 9.6, flip=True), at(17.94, 14.1), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(18.03, -4.61), [], t),
        (Icon('Screw', 4, 9.6, flip=True), at(31.17, 160.51), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(31.26, 142), [], t),
        (Icon('Screw', 4, 9.6, flip=True), at(31.39, 14), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(31.48, -4.51), [], t),
        (Icon('Screw', 4, 9.6, flip=True), at(44.52, 160.57), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(44.61, 141.93), [], t),
        (Icon('Screw', 4, 9.6, flip=True), at(44.74, 14.06), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(44.83, -4.58), [], t),
        (Label('CLAMP', 2.5, attach=3), at(32.32, 133.2), [], t),
        (Label('CLAMP', 2.5, attach=3), at(33.49, 25.06), [], t),
        (Label('x2', 3, attach=3), at(15.85, 162.69), [], t),
        (Label('x2', 3, attach=9), at(15.94, 139.82), [], t),
        (Label('x2', 3, attach=3), at(16.08, 16.18), [], t),
        (Label('x2', 3, attach=9), at(16.17, -6.69), [], t),
        (Label('x2', 3, attach=3), at(29.3, 162.59), [], t),
        (Label('x2', 3, attach=9), at(29.39, 139.92), [], t),
        (Label('x2', 3, attach=3), at(29.53, 16.08), [], t),
        (Label('x2', 3, attach=9), at(29.62, -6.59), [], t),
        (Label('x2', 3, attach=3), at(42.65, 162.65), [], t),
        (Label('x2', 3, attach=9), at(42.74, 139.85), [], t),
        (Label('x2', 3, attach=3), at(42.88, 16.14), [], t),
        (Label('x2', 3, attach=9), at(42.97, -6.66), [], t),
        (Leader(((0, 4.5),)), at(36, 156), [], t),
        (Leader(((0, -14.5), (-3, -14.5))), at(36.02, 146.48), [], t),
        (Leader(((0, 14.5), (-3, 14.5))), at(37.31, 9.5), [], t),
        (Leader(((0, -5),)), at(37.35, -0.08), [], t),
    ]
    # Step 04
    t = steps('4')
    out += [
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.18, 10.21), [], t),
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.18, 29.96), [], t),
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.18, 53.96), [], t),
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.18, 77.96), [], t),
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.18, 101.96), [], t),
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.18, 125.96), [], t),
        (Icon('Screw', 4, 9.6, rotation=90, flip=True), at(-1.18, 145.71), [], t),
        (Icon('Screw', 4, 9.6, flip=True), at(9.97, 15.46), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(10, 140.8), [], t),
        (Icon('Screw', 4, 9.6, flip=True), at(20.97, 15.46), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(21, 140.8), [], t),
        (Icon('Screw', 4, 9.6, flip=True), at(31.97, 15.46), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(32, 140.8), [], t),
        (Icon('Screw', 4, 9.6, flip=True), at(42.97, 15.46), [], t),
        (Icon('Screw', 4, 9.6, rotation=180), at(43, 140.8), [], t),
        (Label('x2', 3, attach=3), at(-8, 11.84), [], t),
        (Label('x2', 3, attach=3), at(-8, 31.59), [], t),
        (Label('x2', 3, attach=3), at(-8, 55.59), [], t),
        (Label('x2', 3, attach=3), at(-8, 79.59), [], t),
        (Label('x2', 3, attach=3), at(-8, 103.59), [], t),
        (Label('x2', 3, attach=3), at(-8, 127.59), [], t),
        (Label('x2', 3, attach=3), at(-8, 147.34), [], t),
    ]
    # Step 05
    t = steps('5')
    out += [
        (Icon('Screw', 4, 9.6, rotation=-90), at(66.62, 1.04), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(66.62, 10.04), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(66.62, 30.04), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(66.62, 54.04), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(66.62, 78.04), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(66.62, 102.04), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(66.62, 126.04), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(66.67, 155.08), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(66.72, 147.61), [], t),
        (Label('Flush\nthis end', 3, attach=1, rotation=90), at(77.25, 140.87), [], t),
        (Label('Rout off if board\nhangs over rafter', 3, attach=1, rotation=90), at(79.02, 2.25), [], t),
        (Label('x2', 3, attach=3), at(76.32, 149.5), [], t),
        (Label('x2', 3, attach=3), at(76.54, 11.93), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.81, 145.75), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.81, 147.23), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.83, 0.71), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.84, 10.33), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.85, 8.66), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.91, 29.93), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.91, 53.93), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.91, 77.93), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.91, 101.93), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.91, 125.93), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(59.95, 155.13), [], t),
    ]
    # Step 06
    t = steps('6')
    out += [
        (Icon('Screw', 4, 9.6, rotation=-90), at(67.04, 0.83), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(67.04, 9.83), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(67.04, 29.83), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(67.04, 53.83), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(67.04, 77.83), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(67.04, 101.83), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(67.04, 125.83), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(67.09, 154.87), [], t),
        (Icon('Screw', 4, 9.6, rotation=-90), at(67.14, 147.4), [], t),
        (Label('x2', 3, attach=3), at(76.92, 11.76), [], t),
        (Label('x2', 3, attach=3), at(77.02, 149.34), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.61, 145.84), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.62, 147.31), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.63, 0.79), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.64, 10.42), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.66, 8.75), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.71, 30.02), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.71, 54.02), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.71, 78.02), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.71, 102.02), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.71, 126.02), [], t),
        (Circle(0.5, fill=(255, 255, 255)), at(54.75, 155.22), [], t),
    ]
    # Step 07
    t = steps('7')
    out += [
        (Label('1', 4, attach=1, rotation=90), at(39.86, 14.1), [], t),
        (Label('1', 4, attach=1, rotation=90), at(44.82, 21.6), [], t),
        (Label('1', 4, attach=1, rotation=90), at(44.93, 45.45), [], t),
        (Label('1', 4, attach=1, rotation=90), at(45.02, 69.45), [], t),
        (Label('1', 4, attach=1, rotation=90), at(45.19, 93.49), [], t),
        (Label('1', 4, attach=1, rotation=90), at(45.44, 137.41), [], t),
        (Label('1', 4, attach=1, rotation=90), at(45.48, 117.52), [], t),
        (Label('1', 4, attach=1, rotation=90), at(64.36, 112.01), [], t),
        (Label('2', 4, attach=1, rotation=90), at(33.35, 13.84), [], t),
        (Label('2', 4, attach=1, rotation=90), at(38.43, 21.26), [], t),
        (Label('2', 4, attach=1, rotation=90), at(38.84, 45.27), [], t),
        (Label('2', 4, attach=1, rotation=90), at(38.84, 69.27), [], t),
        (Label('2', 4, attach=1, rotation=90), at(38.84, 93.27), [], t),
        (Label('2', 4, attach=1, rotation=90), at(38.84, 117.27), [], t),
        (Label('2', 4, attach=1, rotation=90), at(38.85, 136.83), [], t),
        (Label('2', 4, attach=1, rotation=90), at(76.98, 111.8), [], t),
        (Label('3', 4, attach=1, rotation=90), at(-7.11, 21.58), [], t),
        (Label('3', 4, attach=1, rotation=90), at(-5, 136.48), [], t),
        (Label('3', 4, attach=1, rotation=90), at(89.35, 112.07), [], t),
        (Label('Edge of bored hole \nshould be 1/2"\nabove white board', 3, attach=1, rotation=90), at(69.36, 34.71), [], t),
        (Label('Pencil mark at bottom\nof white board', 3, attach=1, rotation=90), at(89.41, 118.22), [], t),
        (Label('Spade bit,\nperpendicular to floor', 3, attach=1, rotation=90), at(64.2, 118.13), [], t),
        (Label('Straight bit,\nperpendicular to floor', 3, attach=1, rotation=90), at(77.4, 118.2), [], t),
        (Leader(((-3.12, -3.42),)), at(52.88, 27.74), [], t),
        (Leader(((-3.12, -3.42),)), at(52.88, 51.74), [], t),
        (Leader(((-3.12, -3.42),)), at(52.88, 75.74), [], t),
        (Leader(((-3.12, -3.42),)), at(52.88, 99.74), [], t),
        (Leader(((-3.12, -3.42),)), at(53.01, 123.73), [], t),
        (Leader(((-3.12, -3.42),)), at(53.12, 143.64), [], t),
        (Leader(((-4.16, 3.72), (-7.03, 3.51))), at(52, 12), [], t),
        (Leader(((-6.46, -6.58), (-6.46, -8.58))), at(3.46, 149.58), [], t),
        (Leader(((-8.75, 7.62), (-8.75, 13.62))), at(3.75, 6.38), [], t),
        (Circle(3.05), at(-5.06, 23.05), [], t),
        (Circle(3.05), at(-2.95, 137.95), [], t),
        (Circle(3.05), at(35.39, 15.31), [], t),
        (Circle(3.05), at(40.48, 22.73), [], t),
        (Circle(3.05), at(40.88, 46.74), [], t),
        (Circle(3.05), at(40.88, 70.74), [], t),
        (Circle(3.05), at(40.88, 94.74), [], t),
        (Circle(3.05), at(40.88, 118.74), [], t),
        (Circle(3.05), at(40.9, 138.31), [], t),
        (Circle(3.05), at(41.93, 15.28), [], t),
        (Circle(3.05), at(46.84, 22.64), [], t),
        (Circle(3.05), at(46.97, 46.63), [], t),
        (Circle(3.05), at(47.11, 70.62), [], t),
        (Circle(3.05), at(47.24, 94.61), [], t),
        (Circle(3.05), at(47.37, 118.59), [], t),
        (Circle(3.05), at(47.47, 138.5), [], t),
        (Circle(3.05), at(66.5, 113), [], t),
        (Circle(3.05), at(79.03, 113), [], t),
        (Circle(3.05), at(91.41, 113.27), [], t),
        (Lines((((17.15, -10.47), (0.01, -0.15)), ((17.23, -6.19), (0.09, 4.13)), ((17.02, -17.47), (17.41, 3.78)), ((25.34, -22.48), (25.73, -1.22)), ((26.82, -21.47), (27.21, -0.13)), ((13.89, -5.32), (13.74, -5.45)), ((13.74, -5.45), (13.62, -5.63)), ((13.62, -5.63), (13.54, -5.85)), ((13.54, -5.85), (13.52, -6.12)), ((13.52, -6.12), (13.53, -6.41)), ((13.53, -6.41), (13.6, -6.72)), ((13.6, -6.72), (13.86, -7.35)), ((13.86, -7.35), (14.25, -7.89)), ((14.25, -7.89), (14.48, -8.11)), ((14.48, -8.11), (14.71, -8.28)), ((14.71, -8.28), (14.95, -8.4)), ((14.95, -8.4), (15.18, -8.46)), ((15.18, -8.46), (15.4, -8.45)), ((15.4, -8.45), (15.59, -8.39)), ((15.59, -8.39), (15.74, -8.26)), ((15.74, -8.26), (15.86, -8.08)), ((15.86, -8.08), (15.94, -7.86)), ((15.94, -7.86), (15.96, -7.59)), ((15.96, -7.59), (15.95, -7.3)), ((15.95, -7.3), (15.88, -6.99)), ((15.88, -6.99), (15.62, -6.37)), ((15.62, -6.37), (15.23, -5.82)), ((15.23, -5.82), (15, -5.6)), ((15, -5.6), (14.77, -5.43)), ((14.77, -5.43), (14.53, -5.31)), ((14.53, -5.31), (14.3, -5.25)), ((14.3, -5.25), (14.08, -5.26)), ((14.08, -5.26), (13.89, -5.32)), ((14.8, -5.49), (14.59, -5.69)), ((14.59, -5.69), (14.46, -6.01)), ((14.46, -6.01), (14.44, -6.41)), ((14.44, -6.41), (14.51, -6.86)), ((14.51, -6.86), (14.68, -7.32)), ((14.68, -7.32), (14.93, -7.75)), ((14.93, -7.75), (15.24, -8.13)), ((15.24, -8.13), (15.59, -8.41)), ((14.97, -6.64), (14.91, -6.7)), ((14.91, -6.7), (14.89, -6.8)), ((14.89, -6.8), (14.96, -7.04)), ((14.96, -7.04), (15.13, -7.23)), ((15.13, -7.23), (15.22, -7.26)), ((15.22, -7.26), (15.3, -7.25)), ((15.3, -7.25), (15.36, -7.19)), ((15.36, -7.19), (15.38, -7.09)), ((15.38, -7.09), (15.31, -6.85)), ((15.31, -6.85), (15.14, -6.66)), ((15.14, -6.66), (15.05, -6.62)), ((15.05, -6.62), (14.97, -6.64)), ((27.11, -12.14), (30.08, -10.13)), ((26.96, -14.34), (29.93, -12.33)), ((30.08, -10.13), (27.06, -8.31)), ((17.3, -2.43), (3.76, 5.72)), ((27.15, -0.18), (25.66, -1.19)), ((25.73, -1.22), (17.35, 3.82)), ((17.35, 3.82), (18.83, 4.83)), ((27.21, -0.13), (18.83, 4.83)), ((29.93, -12.33), (30.08, -10.13)), ((0.13, 4.08), (0.19, 4.1)), ((0.19, 4.1), (0.21, 4.1)), ((0.21, 4.1), (0.37, 4.17)), ((0.37, 4.17), (0.44, 4.19)), ((0.44, 4.19), (0.54, 4.22)), ((0.54, 4.22), (0.56, 4.22)), ((0.56, 4.22), (0.65, 4.24)), ((0.65, 4.24), (0.71, 4.26)), ((0.71, 4.26), (0.82, 4.2)), ((0.82, 4.2), (0.85, 4.18)), ((0.85, 4.18), (0.87, 4.17)), ((0.87, 4.17), (0.93, 4.12)), ((0.93, 4.12), (1.04, 4.06)), ((1.04, 4.06), (1.09, 4.05)), ((1.09, 4.05), (1.19, 4.07)), ((1.19, 4.07), (1.3, 4.1)), ((1.3, 4.1), (1.32, 4.11)), ((1.32, 4.11), (1.34, 4.11)), ((1.34, 4.11), (1.36, 4.12)), ((1.36, 4.12), (1.4, 4.13)), ((1.4, 4.13), (1.4, 4.15)), ((1.4, 4.15), (1.43, 4.18)), ((1.43, 4.18), (1.49, 4.24)), ((1.49, 4.24), (1.5, 4.29)), ((1.5, 4.29), (1.49, 4.31)), ((1.49, 4.31), (1.51, 4.32)), ((1.51, 4.32), (1.52, 4.37)), ((1.52, 4.37), (1.52, 4.39)), ((1.52, 4.39), (1.53, 4.43)), ((1.53, 4.43), (1.56, 4.47)), ((1.56, 4.47), (1.6, 4.59)), ((1.6, 4.59), (1.64, 4.67)), ((1.64, 4.67), (1.66, 4.7)), ((1.66, 4.7), (1.65, 4.72)), ((1.65, 4.72), (1.67, 4.72)), ((1.67, 4.72), (1.71, 4.78)), ((1.71, 4.78), (1.74, 4.81)), ((1.74, 4.81), (1.77, 4.88)), ((1.77, 4.88), (1.81, 4.96)), ((1.81, 4.96), (1.86, 5.04)), ((1.86, 5.04), (1.91, 5.1)), ((1.91, 5.1), (1.96, 5.18)), ((1.96, 5.18), (2, 5.26)), ((2, 5.26), (2.04, 5.32)), ((2.04, 5.32), (2.03, 5.34)), ((2.03, 5.34), (2.07, 5.35)), ((2.07, 5.35), (2.12, 5.41)), ((2.12, 5.41), (2.14, 5.44)), ((2.14, 5.44), (2.18, 5.45)), ((2.18, 5.45), (2.27, 5.47)), ((2.27, 5.47), (2.32, 5.51)), ((2.32, 5.51), (2.39, 5.52)), ((2.39, 5.52), (2.41, 5.53)), ((2.41, 5.53), (2.47, 5.46)), ((2.47, 5.46), (2.52, 5.38)), ((2.52, 5.38), (2.58, 5.31)), ((2.58, 5.31), (2.79, 5.2)), ((2.79, 5.2), (2.92, 5.15)), ((2.92, 5.15), (2.99, 5.14)), ((2.99, 5.14), (3.05, 5.16)), ((3.05, 5.16), (3.12, 5.13)), ((3.12, 5.13), (3.15, 5.14)), ((3.15, 5.14), (3.19, 5.15)), ((3.19, 5.15), (3.21, 5.16)), ((3.21, 5.16), (3.22, 5.18)), ((3.22, 5.18), (3.28, 5.24)), ((3.28, 5.24), (3.3, 5.34)), ((3.3, 5.34), (3.36, 5.6)), ((3.36, 5.6), (3.38, 5.63)), ((3.38, 5.63), (3.43, 5.69)), ((3.43, 5.69), (3.46, 5.74)), ((3.46, 5.74), (3.6, 5.8)), ((3.6, 5.8), (3.72, 5.88)), ((0, 0), (0.04, 0.12)), ((0.04, 0.12), (0.04, 0.17)), ((0.04, 0.17), (0.09, 0.43)), ((0.09, 0.43), (0.12, 0.48)), ((0.12, 0.48), (0.15, 0.61)), ((0.15, 0.61), (0.18, 0.66)), ((0.18, 0.66), (0.33, 0.79)), ((0.33, 0.79), (0.37, 0.82)), ((0.37, 0.82), (0.48, 0.92)), ((0.48, 0.92), (0.51, 0.97)), ((0.51, 0.97), (0.5, 0.99)), ((0.5, 0.99), (0.47, 1.12)), ((0.47, 1.12), (0.37, 1.32)), ((0.37, 1.32), (0.28, 1.48)), ((0.28, 1.48), (0.18, 1.68)), ((0.18, 1.68), (0.1, 1.81)), ((0.1, 1.81), (0.04, 2.05)), ((0.04, 2.05), (0.02, 2.13)), ((0.02, 2.13), (0.07, 2.6)), ((0.07, 2.6), (0.08, 2.67)), ((0.08, 2.67), (0.09, 2.71)), ((0.09, 2.71), (0.1, 2.74)), ((0.1, 2.74), (0.21, 2.93)), ((0.21, 2.93), (0.24, 2.98)), ((0.24, 2.98), (0.25, 3.05)), ((0.25, 3.05), (0.22, 3.16)), ((0.22, 3.16), (0.12, 3.52)), ((0.12, 3.52), (0.08, 3.68)), ((0.08, 3.68), (0.06, 3.75)), ((0.06, 3.75), (0.05, 3.77)), ((0.05, 3.77), (0.05, 3.79)), ((25.14, -22.59), (25.06, -22.28)), ((25.06, -22.28), (24.78, -21.79)), ((24.78, -21.79), (24.76, -21.7)), ((24.76, -21.7), (24.71, -21.67)), ((24.71, -21.67), (24.63, -21.55)), ((24.63, -21.55), (24.58, -21.56)), ((24.58, -21.56), (24.43, -21.51)), ((24.43, -21.51), (24.37, -21.48)), ((24.37, -21.48), (23.99, -21.44)), ((23.99, -21.44), (23.9, -21.46)), ((23.9, -21.46), (23.79, -21.4)), ((23.79, -21.4), (23.65, -21.39)), ((23.65, -21.39), (23.29, -21.3)), ((23.29, -21.3), (23.09, -21.26)), ((23.09, -21.26), (22.84, -21.18)), ((22.84, -21.18), (22.66, -21.05)), ((22.66, -21.05), (22.24, -20.88)), ((22.24, -20.88), (21.68, -20.7)), ((21.68, -20.7), (21.47, -20.61)), ((21.47, -20.61), (21.4, -20.54)), ((21.4, -20.54), (21.2, -20.5)), ((21.2, -20.5), (20.89, -20.39)), ((20.89, -20.39), (20.79, -20.37)), ((20.79, -20.37), (20.41, -20.34)), ((20.41, -20.34), (20.22, -20.34)), ((20.22, -20.34), (19.95, -20.37)), ((19.95, -20.37), (19.67, -20.39)), ((19.67, -20.39), (19.57, -20.37)), ((19.57, -20.37), (19.36, -20.29)), ((19.36, -20.29), (19.25, -20.22)), ((19.25, -20.22), (19.14, -20.16)), ((19.14, -20.16), (19.09, -20.13)), ((19.09, -20.13), (19.05, -20)), ((19.05, -20), (19.02, -19.86)), ((19.02, -19.86), (18.87, -19.48)), ((18.87, -19.48), (18.8, -19.22)), ((18.8, -19.22), (18.78, -19.18)), ((18.78, -19.18), (18.77, -19.13)), ((18.77, -19.13), (18.65, -18.84)), ((18.65, -18.84), (18.52, -18.54)), ((18.52, -18.54), (18.4, -18.25)), ((18.4, -18.25), (18.34, -18.22)), ((18.34, -18.22), (18.25, -18.05)), ((18.25, -18.05), (18.09, -17.81)), ((18.09, -17.81), (18.05, -17.83)), ((18.05, -17.83), (17.95, -17.81)), ((17.95, -17.81), (17.78, -17.71)), ((17.78, -17.71), (17.49, -17.51)), ((17.49, -17.51), (17.45, -17.52)), ((17.45, -17.52), (17.44, -17.47)), ((17.44, -17.47), (17.28, -17.42)), ((17.28, -17.42), (17.24, -17.43)), ((17.24, -17.43), (17.23, -17.39)), ((17.23, -17.39), (17.14, -17.41)), ((25.24, -22.61), (25.32, -22.58)), ((25.32, -22.58), (25.37, -22.57)), ((25.37, -22.57), (25.41, -22.56)), ((25.41, -22.56), (25.51, -22.58)), ((25.51, -22.58), (25.69, -22.53)), ((25.69, -22.53), (25.76, -22.47)), ((25.76, -22.47), (25.79, -22.41)), ((25.79, -22.41), (25.87, -22.34)), ((25.87, -22.34), (25.86, -22.3)), ((25.86, -22.3), (26.09, -22.1)), ((26.09, -22.1), (26.15, -21.99)), ((26.15, -21.99), (26.27, -21.91)), ((26.27, -21.91), (26.31, -21.9)), ((26.31, -21.9), (26.4, -21.87)), ((26.4, -21.87), (26.44, -21.86)), ((26.44, -21.86), (26.53, -21.84)), ((26.53, -21.84), (26.67, -21.85)), ((26.67, -21.85), (26.72, -21.83)), ((26.72, -21.83), (26.76, -21.82)), ((26.76, -21.82), (26.81, -21.81)), ((26.81, -21.81), (26.79, -21.77)), ((26.79, -21.77), (26.78, -21.72)))), at(66.41, 23.57), [], t),
    ]
    return out
