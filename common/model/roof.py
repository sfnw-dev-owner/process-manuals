"""The roof framing: two half-roof assemblies (rafters, ridge and eave boards,
angle plates, cross blocks, fascia and soffits) meeting at the ridge, the
plywood deck, and the bird blocks and vent blocks between the rafters. The roofing is in
roofing.py, the gable ends (structural triangles and gable siding) in
gables.py, and the assembled roof in house.py.

Per Half_Roof/half_roof.md; post-tilt-up/frame-completion.md and
roof-blocking.md; Roof/roof_manual.md.

Frame: the house's X (across) and Y (along); Z = 0 at the top of the walls.

Geometry, from the pitch outward: the rafters' underside rises at ROOF_PITCH
from the inside face of the side walls' top plates (the structural triangle's
sloped edge) to the ridge, where each rafter's plumb-cut tip butts against its
half's 1x6 ridge board. The two ridge boards meet on the center line.
"""

from functools import cache
from math import cos, radians, sin, tan

from build123d import Align, Box, Cylinder, Location, Plane, Polygon, Pos, Rot, extrude

from .lumber import OneByEight, OneBySix, Sheet, TwoByFour, thickness, width
from .dimensions import (
    ANGLE_PLATE_FROM_TIP, BIRD_BLOCK_END_LENGTH, BIRD_BLOCK_LENGTH, CROSS_BLOCKS_FROM_TIP, CROSS_BLOCK_LENGTH,
    DOUBLED_RAFTER_FROM_FRONT, DOUBLED_RAFTER_FROM_REAR, END_BAY, FIRST_INNER_RAFTER, FRONT_ROOF_OVERHANG,
    HALF_ROOF_LENGTH, INNER_RAFTERS, PLATFORM_LENGTH, PLATFORM_WIDTH, RAFTER_LENGTH, RAFTER_SPACING,
    ROOF_DECK_SHEET, ROOF_PITCH, VENT_BLOCK_END_LENGTH, VENT_BLOCK_HEIGHT, VENT_BLOCK_LENGTH,
    VENT_SPACER_LENGTH
)
from .common import CORNER, component, spaced
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
# FRONT_ROOF_OVERHANG (frame-completion.md), and run HALF_ROOF_LENGTH.
ROOF_Y = PLATFORM_LENGTH + FRONT_ROOF_OVERHANG - HALF_ROOF_LENGTH

# Rafters along the half-roof: at both ends, doubled one slot in from each
# end, and on RAFTER_SPACING centers in between.
RAFTER_Y = [ROOF_Y + y for y in (
    0, DOUBLED_RAFTER_FROM_REAR, DOUBLED_RAFTER_FROM_REAR + RAFTER,
    *[c - RAFTER / 2 for c in spaced(FIRST_INNER_RAFTER, RAFTER_SPACING, INNER_RAFTERS)],
    HALF_ROOF_LENGTH - DOUBLED_RAFTER_FROM_FRONT, HALF_ROOF_LENGTH - DOUBLED_RAFTER_FROM_FRONT + RAFTER,
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


def middle_bay(bay):
    """Whether a bay this wide is one of the middle bays (the end bays, over
    the gables, are narrower and take shorter blocks and batts)."""
    return bay > END_BAY



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
        (angle_plate, SLOPE * Pos(TIP_U - ANGLE_PLATE_EDGES[1], RAFTER_Y[1], 0) * Rot(Z=180), [], ''),
        (angle_plate, SLOPE * Pos(TIP_U - ANGLE_PLATE_EDGES[0], RAFTER_Y[-2] + RAFTER, 0), [], ''),
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
# straight bit down through the rafter. (The old drawing had the bores
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


# A35 angle plates (Half_Roof/half_roof.md Step 2: 3 1/2" long, starting
# ANGLE_PLATE_FROM_TIP down the slope from the rafters' tips, reaching 1 3/4"
# out from the rafter).
ANGLE_PLATE = (3 + 1/2, 1 + 3/4, 1 + 1/2)  # length along the rafter, out, up the rafter's face
ANGLE_PLATE_GAUGE = 0.05  # 18 ga
ANGLE_PLATE_EDGES = (ANGLE_PLATE_FROM_TIP, ANGLE_PLATE_FROM_TIP + ANGLE_PLATE[0])  # (near, far) edges, from the tip
ANGLE_PLATE_HOLE = 0.39  # diameter
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
    for x in ANGLE_PLATE_HOLES:  # the flat leg's screw holes
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


# The deck's two options (Roof/roof_manual.md "Plywood Deck"): two equal
# sheets (Panel_Saw_Operation.md), or three
# unequal pieces whose seams miss the rafters, joined by three hurricane
# (H-) clips on each seam, evenly spaced up the slope.
ROOF_DECK_PIECES = (18 + 1/4, 96, 41 + 1/4)  # the 3-piece option, from the front
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
    return BIRD_BLOCK_LENGTH if middle_bay(bay) else BIRD_BLOCK_END_LENGTH


def bird_block(bay):
    return _bird_block(bird_length(bay))


@cache
def _bird_block(length):
    """A 2x4 on edge on the wall's top plate between two rafters, its outer
    face flush with the siding, its top ripped at ROOF_PITCH to meet the roof
    deck on the rafters (Back_Saw_Cut_List.md: "band saw for 18.5 deg angle
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
    return VENT_BLOCK_LENGTH if middle_bay(bay) else VENT_BLOCK_END_LENGTH


def vent_block(bay):
    return _vent_block(vent_length(bay))


@cache
def _vent_block(length):
    """A ridge vent block: a solid topper, with spacer strips at both ends and
    in the middle on the side against the ridge board."""
    @component
    def vent_block_():
        spacer = VENT_SPACER_LENGTH
        solids = [Box(VENT_TOPPER, length, VENT_BLOCK_HEIGHT, align=CORNER)]
        for y in (0, (length - spacer) / 2, length - spacer):
            for i in range(3):  # three 1/2" strips, stacked against the topper
                solids.append(Pos(VENT_TOPPER + i * VENT_SPACERS / 3, y, 0) * Box(VENT_SPACERS / 3, spacer, VENT_BLOCK_HEIGHT, align=CORNER))
        return solids, []
    return vent_block_


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
