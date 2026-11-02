"""The house's dimensions, as the construction manuals state them.

A manual prints a value from here rather than repeating it ({{STUD_LENGTH}}
in its text prints 84”; see render/README.md), so a dimension is changed in
this file, and every name here is used by a manual or a model module
(render/all checks: `render/values.py --unused`). A number is a length in
inches, as the model is built; an angle is marked Degrees and a count of
things Count, so a manual prints their units right too.
"""


class Degrees(float):
    """An angle (a bare number is a length in inches)."""


class Count(int):
    """How many of something, not a length."""


# Platform
PLATFORM_LENGTH = 144  # 2x6 long sides
JOIST_LENGTH = 93  # 2x6
PLATFORM_WIDTH = 96  # joist + two long sides
JOIST_SPACING = 16  # joist centers
SKID = "4x6"  # on edge
SKID_INSET = 12 + 1/2  # platform edge to skid
SUBFLOOR = 3/4  # CDX plywood, 48 x 96 sheets
FOAM_WIDTH = 14  # 7 of these
FOAM_END_WIDTH = 11 + 1/2  # 2 of these, in the end bays
FOAM_LENGTH = 92 + 1/2

# Walls
STUD_LENGTH = 84  # 2x4
SIDE_WALL_PLATE_LENGTH = 144  # 2x4
END_WALL_PLATE_LENGTH = 89  # 2x4
STUD_SPACING = 24  # side wall stud centers
SIDING_HEIGHT = 93 + 1/2  # T1-11, flush with the top plate
SIDING_PANEL_WIDTH = 48
DOOR_OPENING = 38  # rough opening
WINDOW_OPENING = (24, 36)  # rough opening
AC_OPENING = 20 + 1/2  # between the A/C blocks

# Roof
ROOF_PITCH = Degrees(18.5)
RAFTER_LENGTH = 56 + 3/4  # 2x4, along its top edge
HALF_ROOF_LENGTH = 156
FRONT_ROOF_OVERHANG = 6 + 1/4  # past the front triangle
CROSS_BLOCK_LENGTH = 6 + 1/2  # 2x4
RAFTER_SPACING = 24  # inner rafter centers
INNER_RAFTERS = Count(5)  # on those centers, between the doubled rafters
FIRST_INNER_RAFTER = 30  # its center, from the half-roof's rear end
DOUBLED_RAFTER_FROM_REAR = 8  # the doubled rafters' slots ("one slot in from each end"), from the ends
DOUBLED_RAFTER_FROM_FRONT = 11
ANGLE_PLATE_FROM_TIP = 4 + 1/2  # down the slope from the rafter's tip
CROSS_BLOCKS_FROM_TIP = (12 + 5/8, 26, 39 + 3/8)  # the three cross blocks, down the slope from the tips
END_BAY = 20  # a rafter bay this wide or narrower is an end bay (over a gable); the wider ones take the longer blocks and batts
ROOF_DECK_SHEET = (48, 77 + 3/4)  # 3/4" CDX, up the slope x along the roof
BIRD_BLOCK_LENGTH = 22 + 1/4  # 2x4
BIRD_BLOCK_END_LENGTH = 18  # end bays
VENT_BLOCK_LENGTH = 21 + 7/8
VENT_BLOCK_END_LENGTH = 18 + 1/8  # end bays
VENT_BLOCK_HEIGHT = 4  # per the shop (not in the manuals)
VENT_SPACER_LENGTH = 2  # per the shop
SHINGLE_OVERHANG = 1  # past the eave and the fascia
SHINGLE_LENGTH = 39 + 3/8  # standard metric shingle
SHINGLE_WIDTH = 13 + 1/4
SHINGLE_EXPOSURE = 5 + 5/8
START_END_PAIR = 42  # a start plus an end shingle
SHINGLE_FIRST_TRIM = 3  # "Cut 3 inches off a shingle to start"
ROW_9_TRIM = 1 + 1/2  # off the top of row 9
RAKE_STARTER_OVERLAP = 1 + 1/2  # over the eave starters
TAR_PAPER_LENGTH = 13 * 12 + 4  # 13'4"
TAR_PAPER_WIDTH = 36  # standard roll (not stated in the manual)
CAP_SHINGLE = 13  # 13" x 13"
RIDGE_VENT_OVERHANG = 2  # past the fascia

# Interior roof
CEILING_R1 = (43 + 1/2, 92)  # up the slope x along the roof
CEILING_R2 = (43 + 1/2, 44)
ROOF_BATT_WIDTH = 24  # middle bays
ROOF_BATT_END_WIDTH = 18  # end bays
ROOF_BATT_LENGTH = 45 + 1/2
CEILING_TRIM_LENGTH = 42  # 1/2 x 2 ceiling seam trim
TRIANGLE_TRIM_LENGTH = 42  # 1/2 x 2, left and right
TRIANGLE_CENTER_TRIM_LENGTH = 12
VENT_CAP_WIDTH = 9 + 1/2
VENT_CAP_LENGTH = 96  # the long piece
VENT_CAP_BLOCK_LENGTH = 6 + 1/2  # half of a 13" block
