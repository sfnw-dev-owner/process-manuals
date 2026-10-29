"""Roofing: tar paper, a starter course, the shingle courses, the ridge vent
and the cap shingles over it, per Roof/roof_manual.md.

Frame: the roof's (roof.py); a side's roofing is built in the slope frame of
the left half-roof and mirrored for the right.
"""

from math import ceil

from build123d import Box, Plane, Polygon, Pos, extrude

from .lumber import thickness
from .dimensions import (
    CAP_SHINGLE, HALF_ROOF_LENGTH, RAKE_STARTER_OVERLAP, RIDGE_VENT_OVERHANG, ROW_9_TRIM, SHINGLE_EXPOSURE,
    SHINGLE_FIRST_TRIM, SHINGLE_LENGTH, SHINGLE_OVERHANG, SHINGLE_WIDTH, START_END_PAIR, TAR_PAPER_LENGTH,
    TAR_PAPER_WIDTH
)
from .common import CORNER, component, spaced
from .roof import (
    C, DECK, DECK_TOP_U, FASCIA, RAFTER_DEPTH, RIDGE_X, ROOF_Y, SEAT_X, SHINGLES, SLOPE, TAIL_U, underside
)


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
    per_half = ceil((middle - y0) / SHINGLE_EXPOSURE)  # enough to reach the middle from either end
    solids = []
    for i, y in enumerate(spaced(y0, SHINGLE_EXPOSURE, per_half)):  # from the rear
        if y + CAP_SHINGLE > middle + SHINGLE_EXPOSURE:
            break
        solids.append(Pos(0, y, (i % 2) * SHINGLE) * extrude(cap, -CAP_SHINGLE))
    for i, y in enumerate(spaced(y1 - CAP_SHINGLE, -SHINGLE_EXPOSURE, per_half)):  # from the front
        if y < middle - SHINGLE_EXPOSURE:
            break
        solids.append(Pos(0, y, (i % 2) * SHINGLE) * extrude(cap, -CAP_SHINGLE))
    short = CAP_SHINGLE / 2  # cut just below the adhesive line
    solids.append(Pos(0, middle - short / 2, 2 * SHINGLE) * extrude(cap, -short))
    return solids, []


