"""The house's dimensions, as the construction manuals state them.

A manual prints a value from here rather than repeating it ({{STUD_LENGTH}}"
in its text; see render/README.md), so a dimension is changed in this file.
A citation says where a value is used (the manual's line, when it was
named) or where it came from: the SketchUp model and the QCAD drawings
(*.dxf) this package was bootstrapped from, not to be trusted where the
manuals differed. Those files were removed in commit 1492ff3; a citation of
one is read with `git show 1492ff3^:<path>`.
"""

# Platform: Platform/platform.md and Platform/images/platform.dxf.
PLATFORM_LENGTH = 144  # 2x6 long sides; Cut_Lists/Back_Saw_Cut_List.md:12
JOIST_LENGTH = 93  # 2x6; Cut_Lists/Back_Saw_Cut_List.md:11
PLATFORM_WIDTH = 96  # joist + two long sides; platform.dxf
JOIST_SPACING = 16  # joist centers; platform.dxf
SKID = "4x6"  # on edge; Platform/platform.md:55
SKID_INSET = 12 + 1/2  # platform edge to skid; platform.dxf
SUBFLOOR = 3/4  # CDX plywood, 48 x 96 sheets; Platform/platform.md:113
FOAM_WIDTH = 14  # 7 of these; Platform/platform.md:100
FOAM_END_WIDTH = 11 + 1/2  # 2 of these, in the end bays; Platform/platform.md:99
FOAM_LENGTH = 92 + 1/2  # Platform/platform.md:99

# Walls: Side_Walls/sidewall_1.md, Front_Wall/front_wall_ada.md,
# Rear_Wall/rear_wall.md and their images/*.dxf.
STUD_LENGTH = 84  # 2x4; Side_Walls/sidewall_1.md:32, Rear_Wall/rear_wall.md:33
SIDE_WALL_PLATE_LENGTH = 144  # 2x4; Side_Walls/sidewall_1.md:31
END_WALL_PLATE_LENGTH = 89  # 2x4; Cut_Lists/Front_Saw_Cut_List.md:11
STUD_SPACING = 24  # side wall stud centers; Side_Walls/images/side_wall.dxf
SIDING_HEIGHT = 93 + 1/2  # T1-11, flush with the top plate; Panel_Cutting/Panel_Saw_Operation.md:69
SIDING_PANEL_WIDTH = 48
DOOR_OPENING = 38  # rough opening; Front_Wall/images/front_wall_ada.dxf
WINDOW_OPENING = (24, 36)  # rough opening; front_wall_ada.dxf, rear_wall.dxf
AC_OPENING = 20 + 1/2  # between the A/C blocks; Rear_Wall/rear_wall.md:77

# Roof: Half_Roof/half_roof.md + images/half_roof.dxf, Structural_Triangle/triangle.dxf,
# post-tilt-up/*.md, Roof/roof_manual.md.
ROOF_PITCH = 18.5  # degrees; Cut_Lists/Back_Saw_Cut_List.md:34, Roof/roof_manual.md:113
RAFTER_LENGTH = 56 + 3/4  # 2x4, along its top edge; Back_Saw_Cut_List.md:34
HALF_ROOF_LENGTH = 156  # Half_Roof/images/half_roof.dxf
FRONT_ROOF_OVERHANG = 6 + 1/4  # past the front triangle; post-tilt-up/frame-completion.md:92
CROSS_BLOCK_LENGTH = 6 + 1/2  # 2x4; Half_Roof/half_roof.md:50
RAFTER_SPACING = 24  # inner rafter centers; Half_Roof/images/half_roof.dxf
INNER_RAFTERS = 5  # on those centers, between the doubled rafters; half_roof.dxf
FIRST_INNER_RAFTER = 30  # its center, from the half-roof's rear end; half_roof.dxf
DOUBLED_RAFTER_FROM_REAR = 8  # the doubled rafters' slots ("one slot in from each end", half_roof.md:28), from the ends; half_roof.dxf
DOUBLED_RAFTER_FROM_FRONT = 11
ANGLE_PLATE_FROM_TIP = 4 + 1/2  # down the slope from the rafter's tip; half_roof.dxf (Step 02)
CROSS_BLOCKS_FROM_TIP = (12 + 5/8, 26, 39 + 3/8)  # the three cross blocks, down the slope from the tips; half_roof.dxf (Step 03)
END_BAY = 20  # a rafter bay this wide or narrower is an end bay (over a gable); the wider ones take the longer blocks and batts
ROOF_DECK_SHEET = (48, 77 + 3/4)  # 3/4" CDX, up the slope x along the roof; Panel_Saw_Operation.md:46
BIRD_BLOCK_LENGTH = 22 + 1/4  # 2x4; Back_Saw_Cut_List.md:23
BIRD_BLOCK_END_LENGTH = 18  # end bays; Back_Saw_Cut_List.md:24
VENT_BLOCK_LENGTH = 21 + 7/8  # Back_Saw_Cut_List.md:42
VENT_BLOCK_END_LENGTH = 18 + 1/8  # end bays; Back_Saw_Cut_List.md:43
VENT_BLOCK_HEIGHT = 4  # per the shop (not in the manuals)
VENT_SPACER_LENGTH = 2  # the plywood spacer blocks at a vent block's ends and middle (roof-blocking.md:101); per the shop
SHINGLE_OVERHANG = 1  # past the eave and the fascia; Roof/roof_manual.md (Shingles)
SHINGLE_LENGTH = 39 + 3/8  # standard metric shingle; see roof.py
SHINGLE_WIDTH = 13 + 1/4
SHINGLE_EXPOSURE = 5 + 5/8
START_END_PAIR = 42  # a start plus an end shingle; Roof/roof_manual.md:31
SHINGLE_FIRST_TRIM = 3  # "Cut 3 inches off a shingle to start"; Roof/roof_manual.md:43
ROW_9_TRIM = 1 + 1/2  # off the top of row 9; Roof/roof_manual.md:63
RAKE_STARTER_OVERLAP = 1 + 1/2  # over the eave starters; Roof/roof_manual.md (Starter Row)
TAR_PAPER_LENGTH = 13 * 12 + 4  # 13'4"; Roof/roof_manual.md:17
TAR_PAPER_WIDTH = 36  # standard roll (not stated in the manual)
CAP_SHINGLE = 13  # 13" x 13"; Roof/roof_manual.md:259
RIDGE_VENT_OVERHANG = 2  # past the fascia; Roof/roof_manual.md (Ridge Vent)

# Interior roof: Cut_Lists/Interior_Panels_Cut_List.md, Cut_Lists/Insulation.md,
# Cut_Lists/Interior_Trim_Items.md, Interior_Trim/vent_cap_install.md.
CEILING_R1 = (43 + 1/2, 92)  # up the slope x along the roof; Interior_Panels_Cut_List.md:43
CEILING_R2 = (43 + 1/2, 44)  # Interior_Panels_Cut_List.md:41
ROOF_BATT_WIDTH = 24  # middle bays; Cut_Lists/Insulation.md:25
ROOF_BATT_END_WIDTH = 18  # end bays; Cut_Lists/Insulation.md:26
ROOF_BATT_LENGTH = 45 + 1/2
CEILING_TRIM_LENGTH = 42  # 1/2 x 2 ceiling seam trim; Interior_Trim_Items.md:18
TRIANGLE_TRIM_LENGTH = 42  # 1/2 x 2, left and right; Interior_Trim_Items.md:19-20
TRIANGLE_CENTER_TRIM_LENGTH = 12  # Interior_Trim_Items.md:21
VENT_CAP_WIDTH = 9 + 1/2  # Interior_Trim/Images/vent_cap.dxf
VENT_CAP_LENGTH = 96  # the long piece; vent_cap_install.md step 7
VENT_CAP_BLOCK_LENGTH = 6 + 1/2  # half of a 13" block; vent_cap_install.md step 1, Interior_Trim_Items.md
