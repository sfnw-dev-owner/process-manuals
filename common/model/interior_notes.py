"""Annotations for the interior manuals' figures: Interior_Panels/interior_panels.md,
Interior_Trim/interior_trim.md and Interior_Trim/vent_cap_install.md.

Tagged "manual:<manual>:<figure>" so they appear only in those figures.
Each function takes `at(x, y)`, the component's Location for a point of
the figure's drawing (the drawing's frame is the original QCAD drawing's,
in inches), and returns children for that component.
"""

from build123d import Location, Plane, Pos

from .notes import Circle, Icon, Label, Leader, Lines, crossed_box

# A wall seen from inside the house: drawing x = the wall frame's X (left to
# right as seen from inside), drawing y = Z.
INSIDE_VIEW = Location(Plane((0, 0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))).inverse()

# A sheet lying in XY seen from below, turned so its Y runs across the
# drawing: drawing x = Y, drawing y = X.
FLAT_VIEW = Location(Plane((0, 0, 0), x_dir=(0, 1, 0), z_dir=(0, 0, -1))).inverse()


def view_at(view):
    """at(x, y) for a component drawn through `view` (its frame -> drawing)."""
    inverse = view.inverse()
    return lambda x, y: inverse * Pos(x, y, 0)


def panels_tag(figure):
    return f"manual:interior_panels:{figure}"


# ── Interior_Panels/interior_panels.md ─────────────────────────────────────

# Where the figures draw each wall (wall frame -> drawing): its framing's
# inside-bottom corner at these points.
SIDE_PANELS_VIEW = Pos(20, -167) * INSIDE_VIEW
REAR_PANELS_VIEW = Pos(47, -143.5) * INSIDE_VIEW
FRONT_PANELS_VIEW = Pos(46.74, -155.26) * INSIDE_VIEW
TRIANGLE_PANELS_VIEW = Pos(49.74, -113.26) * INSIDE_VIEW  # the front wall

# Loose panels, laid out above each wall: (x, y) of the panel's lower-left corner.
LOOSE = {
    "A": (0, 0), "B": (0, -53), "C": (120, -53),
    "G": (47.38, 12.15), "H": (47.38, -37.85),
    "D": (47.38, 12.15), "E": (89, -37.85),
    "R1": (0, 0), "R2": (130, 0),
}

EDGE_SCREW_SPACING = 8


def edge_screws(at, x0, y0, w, h, t, size=(4, 9.6)):
    """Screws preset along a loose panel's two short (left and right) edges,
    about 8" apart, drawn slanting toward the edge."""
    n = int(h // EDGE_SCREW_SPACING) + 1
    ys = [y0 + 4 + i * (h - 4) / (n - 1) for i in range(n)]
    return ([(Icon("Screw", *size, rotation=-60), at(x0 + 4.33, y), [], t) for y in ys]
            + [(Icon("Screw", *size, rotation=60), at(x0 + w - 5, y), [], t) for y in ys])


def loose_panel(at, name, size, t, label=(20, 40)):
    """A loose panel's screws and its letter, at (dx, dy) in it."""
    x0, y0 = LOOSE[name]
    w, h = size
    return edge_screws(at, x0, y0, w, h, t) + [(Label(name, 8, attach=1), at(x0 + label[0], y0 + label[1]), [], t)]


def factory_edge_notes(at, t, points):
    return [(Label("Factory edge (paint mark)", 3, attach=1), at(*p), [], t) for p in points]


def side_panels_notes(at, sizes):
    t = panels_tag("side")
    a, b, c = sizes
    return [
        *loose_panel(at, "A", a, t),
        *loose_panel(at, "B", b, t, (19.53, 30.39)),
        *loose_panel(at, "C", c, t, (15.19, 73.32)),
        *factory_edge_notes(at, t, [(109.31, 57.74), (109.85, -57.19)]),
        (Label('8" spacing', 2.5, attach=1), at(117.22, 42.51), [], t),
        (Leader(((10.65, 16), (16.02, 16))), at(92, 39.99), [], t),
        (Leader(((10.65, -16), (16.02, -16))), at(92.25, -42.77), [], t),
        (Leader(((15, 31.75), (23, 31.75))), at(92, 8.25), [], t),
        (Leader(((15, 60),)), at(92, -20), [], t),
        (Leader(((-13.05, 13.28),)), at(120.05, 26.72), [], t),
        # installed
        (Label("A", 8, attach=1), at(50, -87), [], t),
        (Label("B", 8, attach=1), at(49.02, -133.79), [], t),
        (Label("C", 8, attach=1), at(125.46, -89), [], t),
        *circled(at, t, [("1", 82, -143), ("2", 80.95, -102.1), ("3", 150.23, -103.22)], 4.47, 6),
        (Label("Line up factory edges of A and B\nwith centerline of stud", 3, attach=1), at(132.17, -66.98), [], t),
        (Leader(((6.24, 12.08), (13.73, 12.08))), at(116, -80.5), [], t),
        (Label("Rear", 3, attach=1), at(0, -117), [], t),
        (Label("Front", 3, attach=1), at(170, -117), [], t),
        (Label("Side Wall Panels", 6, attach=1), at(64.31, -184.87), [], t),
    ]


def circled(at, t, numbers, radius, height):
    """Circled step numbers: (text, circle center x, y)."""
    out = []
    for text, x, y in numbers:
        out += [(Circle(radius), at(x, y), [], t), (Label(text, height), at(x, y), [], t)]
    return out


def end_panels_notes(at, figure, upper, lower, sizes, title, installed_labels):
    t = panels_tag(figure)
    return [
        *loose_panel(at, upper, sizes[0], t, (41.98, 33.91) if upper == "G" else (42.62, 27.85)),
        *loose_panel(at, lower, sizes[1], t, (42.62 if lower == "H" else 21, 27.85)),
        (Label('8" spacing', 3, attach=1), at(150.95, 6.5), [], t),
        (Leader(((7.5, -17), (13.5, -17))), at(135.5, 22), [], t),
        (Leader(((7.87, 11.5),)), at(135.13, -6.5), [], t),
        *[(Label(name, 8, attach=1), at(x, y), [], t) for name, x, y in installed_labels],
        (Label(title, 6, attach=1), at(64.31, -184.87), [], t),
    ]


def rear_panels_notes(at, sizes):
    return end_panels_notes(at, "rear", "G", "H", sizes, "Rear Wall Panels",
                            [("G", 75.43, -75.84), ("H", 75.84, -118.29)])


def front_panels_notes(at, sizes):
    return end_panels_notes(at, "front", "D", "E", sizes, "Front Wall Panels",
                            [("D", 100.65, -86.51), ("E", 103.17, -128.95)])


def triangle_panels_notes(at):
    """Screws preset around the loose half-triangles: along the bottom, the
    sloping edge and the short edge (at the peak)."""
    t = panels_tag("triangle")
    s = (3, 7.2)
    out = []
    for i in range(5):
        out += [
            (Icon("Screw", *s, rotation=-150), at(44.5 + 8 * i, 10.02), [], t),
            (Icon("Screw", *s, rotation=30), at(47.29 + 7.585 * i, 17.48 + 2.5375 * i), [], t),
            (Icon("Screw", *s, rotation=150, flip=True), at(119.1 + 8 * i, 10.4), [], t),
            (Icon("Screw", *s, rotation=-30, flip=True), at(117.97 + 7.585 * i, 28.02 - 2.54 * i), [], t),
        ]
    for dy in (-4.86, 0, 5):
        out += [
            (Icon("Screw", *s, rotation=-60, flip=True), at(85.18, 19 + dy), [], t),
            (Icon("Screw", *s, rotation=60), at(110.42, 19.51 + dy), [], t),
        ]
    return out


def ceiling_panels_notes(at, rafter_screws):
    """rafter_screws: [(x, y)] in the drawing, the screws into the rafters
    through the installed panels."""
    t = panels_tag("ceiling")
    return [
        *loose_panel(at, "R1", (92, 43.5), t),
        *loose_panel(at, "R2", (44, 43.5), t, (15.49, 39.99)),
        *factory_edge_notes(at, t, [(109.31, 57.74), (127.72, -17.03)]),
        *[(Label('8" spacing', 2.5, attach=1), at(x, 24.42), [], t) for x in (106.45, 188.58)],
        (Leader(((10.65, 16), (16.02, 16))), at(92, 39.99), [], t),
        (Leader(((6.88, 13), (12.88, 13))), at(92, 10), [], t),
        (Leader(((6.88, 13), (12.88, 13))), at(174.12, 10), [], t),
        (Leader(((-14.69, -24.71), (-5.53, -24.71))), at(129.79, 6.3), [], t),
        # installed: R1, then R2, then the screws into the rafters
        (Label("R1", 8, attach=1), at(55.75, -55.5), [], t),
        (Label("R2", 8, attach=1), at(127.07, -130.13), [], t),
        (Label("Factory Edge", 3, attach=1), at(141.56, -99.08), [], t),
        (Leader(((9.7, -15.18), (16.92, -15.18))), at(122.3, -85.61), [], t),
        (Label("Factory Edge", 3, attach=1), at(121.6, -108.64), [], t),
        (Leader(((-11.23, 22.29), (-2.42, 22.29))), at(121.23, -132.29), [], t),
        *[(Label("Back", 5, attach=1), at(0, y), [], t) for y in (-60, -138.16, -225.95)],
        *[(Label("Front", 5, attach=1), at(177.6, y), [], t) for y in (-60.34, -137.99, -225.78)],
        *[(Circle(0.32), at(x, y), [], t) for x, y in rafter_screws],
        (Label("Drill & countersink, then use\nLONG screws into rafters\n(5 screws into each rafter)", 3.5, attach=1),
         at(40, -260), [], t),
        (Label("Ceiling Panels", 8, attach=1), at(64.32, -284.43), [], t),
    ]


# ── Interior_Trim/interior_trim.md ─────────────────────────────────────────
# Each figure draws a wall or two from inside at these places (wall frame ->
# drawing); the end walls' notes are the rear wall's (figures up to the
# triangle trim) or the front wall's (the rest).

def trim_tag(figure):
    return f"manual:interior_trim:{figure}"


REAR_TRIM_VIEWS = {
    "baseboards": Pos(20, 9.5) * INSIDE_VIEW,
    "rear_shelf": Pos(30, -20.5) * INSIDE_VIEW,
    "rear_window_trim": Pos(30, -20.5) * INSIDE_VIEW,
    "top_trim": Pos(20, 9.5) * INSIDE_VIEW,
    "vertical_trim": Pos(20, 9.5) * INSIDE_VIEW,
    "horizontal_trim": Pos(30, 200) * INSIDE_VIEW,
    "triangle_trim": Pos(23.67, 112.05) * INSIDE_VIEW,
}
FRONT_TRIM_VIEWS = {
    "front_window": Pos(-4.22, 0.35) * INSIDE_VIEW,
    "front_trim_a": Pos(12.4, 132.91) * INSIDE_VIEW,
    "front_trim_b": Pos(12.4, 132.91) * INSIDE_VIEW,
    "final_trim": Pos(31.82, 49.26) * INSIDE_VIEW,
}
# The far side wall ("left side wall (facing rear)"), front to the left: its
# panels' front bottom corner (3.97, 1/2) at the outline's corner.
SIDE_TRIM_VIEWS = {
    "baseboards": Pos(-3.97, 219.5) * INSIDE_VIEW,
    "top_trim": Pos(-3.97, 219.5) * INSIDE_VIEW,
    "vertical_trim": Pos(-3.97, 219.5) * INSIDE_VIEW,
    "horizontal_trim": Pos(0.17 - 3.97, 98.37) * INSIDE_VIEW,
    "final_trim": Pos(6.32 - 3.97, 230.76) * INSIDE_VIEW,
}
FRONT_WINDOW_LOWER_VIEW = Pos(-3.92, -131.62) * INSIDE_VIEW  # the front window figure's second view
# The shelf details: plans from above at the shelf, the room at the bottom:
# the window's opening's left side at x, the framing's inside face at y.
REAR_SHELF_PLAN = Pos(75.44, -61.14)
FRONT_SHELF_PLAN = Pos(74.69, 43.18)


def rear_trim_notes():
    return [c for fig, view in REAR_TRIM_VIEWS.items() for c in TRIM_NOTES[fig](view_at(view))]


def front_trim_notes():
    return [c for fig, view in FRONT_TRIM_VIEWS.items() for c in TRIM_NOTES[fig](view_at(view))]


def trim_baseboards_notes(at):
    t = trim_tag("baseboards")
    return [
        (Label('1', 8, attach=1), at(84.37, 244.96), [], t),
        (Label('2', 8, attach=1), at(-17.14, 178.47), [], t),
        (Label('3', 8, attach=1), at(58.86, 37.44), [], t),
        (Label('Baseboards', 8, attach=1), at(40, 0), [], t),
        (Label('Front', 5, attach=1), at(-25.38, 273.86), [], t),
        (Label('Interior Trim', 10, attach=1), at(40, -20), [], t),
        (Label('Left side wall (facing rear)', 8, attach=1), at(0, 200), [], t),
        (Label('Rear', 5, attach=1), at(145.32, 274.77), [], t),
        (Label('Repeat for door-side sidewall', 8, attach=1), at(0, 178), [], t),
        (Label('Use spacers', 5, attach=1), at(139.6, 214.6), [], t),
        (Label('rear wall', 5, attach=1), at(-40, 90), [], t),
        (Leader(((0, 13.11),)), at(61.22, 13.57), [], t),
        (Leader(((0, 9.7),)), at(86.74, 224.5), [], t),
        (Leader(((4.5, -7.5), (16, -7.5))), at(122.5, 219), [], t),
        (Circle(6.63), at(-14.78, 174.34), [], t),
        (Circle(6.63), at(61.22, 33.31), [], t),
        (Circle(6.63), at(86.74, 240.83), [], t),
    ]


def trim_rear_shelf_notes(at):
    t = trim_tag("rear_shelf")
    return [
        # the support block's screws, marked on it
        *[(Lines((((-0.6, 0), (0.6, 0)), ((0, -0.6), (0, 0.6)))), at(x, y), [], t) for x, y in ((76.26, 22.93), (76.26, 21.43), (101.76, 22.93), (101.76, 21.43))],
        (Icon('Screw', 3, 7.2, rotation=180), at(75.99, 15.82), [], t),
        (Icon('Screw', 3, 7.2, rotation=180, flip=True), at(101.53, 16.05), [], t),
        (Icon('Screw', 3, 7.2), at(119.58, -59.04), [], t),
        (Icon('Screw', 3, 7.2), at(125.21, -55.87), [], t),
        (Icon('Screw', 3, 7.2), at(134.21, -55.87), [], t),
        (Icon('Screw', 3, 7.2), at(143.21, -55.87), [], t),
        (Icon('Screw', 3, 7.2), at(148.58, -59.04), [], t),
        (Label('1', 4, attach=1), at(133.06, -39.79), [], t),
        (Label('2', 4, attach=1), at(75.62, 6.58), [], t),
        (Label('2x', 3, attach=1), at(69.51, 13.43), [], t),
        (Label('2x', 3, attach=1), at(103.51, 13.43), [], t),
        (Label('3', 4, attach=1), at(111.13, -47.48), [], t),
        (Label('3', 4, attach=1), at(154.67, -47.52), [], t),
        (Label('Interior Trim', 8, attach=1), at(50, -140), [], t),
        (Label('Long screws', 4, attach=1), at(117.08, -76.64), [], t),
        (Label('Mount support block\n   with 1/2" shelf overhang\n   on each end', 2.5, attach=1), at(58.55, -5.89), [], t),
        (Label('Rear Window Shelf and Frame', 5, attach=1), at(34.21, 113.97), [], t),
        (Label('Shelf', 4, attach=1), at(127.08, -62.64), [], t),
        (Label('Use long screws', 2.5, attach=1), at(83.08, 5.51), [], t),
        (Leader(((-10.09, -13.16),)), at(89.26, 20.43), [], t),
        (Leader(((-28.15, -29.43), (-14.83, -29.43))), at(71.25, 22.25), [], t),
        (Leader(((-3.39, 3.84),)), at(118.26, -56.08), [], t),
        (Leader(((-6.78, 8.28),)), at(143.08, -52.64), [], t),
        (Leader(((0, 7.49),)), at(134.08, -52.64), [], t),
        (Leader(((4.03, 3.84),)), at(149.51, -55.9), [], t),
        (Leader(((6.34, 8.17),)), at(125.59, -52.58), [], t),
        (Circle(3.51), at(77.03, 4.47), [], t),
        (Circle(3.51), at(112.55, -49.6), [], t),
        (Circle(3.51), at(134.08, -41.64), [], t),
        (Circle(3.51), at(156.08, -49.64), [], t),
        (Circle(31.11), at(133.19, -62.64), [], t),
    ]


def trim_rear_window_trim_notes(at):
    t = trim_tag("rear_window_trim")
    return [
        (Label('1', 4, attach=2), at(62.04, 56.97), [], t),
        (Label('2" plywood trim', 2.5, attach=1), at(112.57, 77.46), [], t),
        (Label('2" plywood trim', 2.5, attach=1), at(122.05, 29.8), [], t),
        (Label('2', 4, attach=2), at(109.47, 56.84), [], t),
        (Label('3', 4, attach=2), at(58.19, 37), [], t),
        (Label('3', 4, attach=2), at(123.02, 37.76), [], t),
        (Label('3-1/2" plywood liner', 2.5, attach=1), at(118.09, 56.13), [], t),
        (Label('3-1/2" plywood liners', 2.5, attach=1), at(35.5, 61.62), [], t),
        (Label('4', 4, attach=2), at(106.68, 77.79), [], t),
        (Label('Interior Trim', 8, attach=1), at(50, -140), [], t),
        (Label('Rear Window Shelf and Frame', 5, attach=1), at(34.21, 113.97), [], t),
        (Leader(((-13.31, 0),)), at(75.04, 35), [], t),
        (Leader(((-6.14, 6.4), (-34.36, 6.4))), at(100, 48.5), [], t),
        (Leader(((-9.52, -0.06), (-13.03, 5.64))), at(77, 46.3), [], t),
        (Leader(((10.82, 10.96),)), at(93.29, 62.49), [], t),
        (Leader(((16.47, 0),)), at(103, 35.81), [], t),
        (Leader(((4.85, -4.94), (11.41, -4.89))), at(94.57, 59.82), [], t),
        (Circle(3.51), at(58.22, 35), [], t),
        (Circle(3.51), at(62.13, 54.93), [], t),
        (Circle(3.51), at(106.58, 75.95), [], t),
        (Circle(3.51), at(109.48, 54.95), [], t),
        (Circle(3.51), at(122.98, 35.81), [], t),
    ]


def trim_top_trim_notes(at):
    t = trim_tag("top_trim")
    return [
        (Label('1', 8, attach=1), at(88.64, 289.11), [], t),
        (Label('2', 8, attach=3), at(22.37, 289.13), [], t),
        (Label('3', 8, attach=3), at(-47.63, 138.76), [], t),
        (Label('4', 8, attach=3), at(-27.63, 139.13), [], t),
        (Label('5', 8, attach=1), at(118.26, 87.84), [], t),
        (Label('Front', 5, attach=1), at(-25.38, 273.86), [], t),
        (Label('Interior Trim', 10, attach=1), at(40, -20), [], t),
        (Label('Left side wall (facing rear)', 8, attach=1), at(0, 200), [], t),
        (Label('Rear', 5, attach=1), at(145.32, 274.77), [], t),
        (Label('Repeat 1 & 2 for door-side sidewall', 8, attach=3), at(165.61, 140.04), [], t),
        (Label('Top Trim', 8, attach=1), at(49.24, -6.48), [], t),
        (Label('rear wall', 5, attach=1), at(-40, 90), [], t),
        (Leader(((0, -12.37),)), at(20, 304), [], t),
        (Leader(((0, -12.97),)), at(91, 304.58), [], t),
        (Leader(((3, -9), (13, -9))), at(101, 93), [], t),
        (Circle(6.63), at(-50, 134.63), [], t),
        (Circle(6.63), at(-30, 135), [], t),
        (Circle(6.63), at(20, 285), [], t),
        (Circle(6.63), at(91, 284.98), [], t),
        (Circle(6.63), at(120.62, 83.71), [], t),
    ]


def trim_vertical_trim_notes(at):
    t = trim_tag("vertical_trim")
    return [
        (Label('1', 8, attach=1), at(64.04, 244.13), [], t),
        (Label('1', 8, attach=1), at(155.25, 244.13), [], t),
        (Label('2', 8, attach=3), at(-24.09, 165.17), [], t),
        (Label('3', 8, attach=3), at(-1.18, 67.92), [], t),
        (Label('3', 8, attach=1), at(127.28, 67.83), [], t),
        (Label('Front', 5, attach=1), at(-25.38, 273.86), [], t),
        (Label('Front', 5, attach=1), at(-25.38, 313.86), [], t),
        (Label('Interior Trim', 10, attach=1), at(40, -20), [], t),
        (Label('Left side wall (facing rear)', 8, attach=1), at(0, 200), [], t),
        (Label('Rear', 5, attach=1), at(145.32, 274.77), [], t),
        (Label('Rear', 5, attach=1), at(145.32, 314.77), [], t),
        (Label('Repeat on other side sidewall', 8, attach=3), at(142.64, 166.41), [], t),
        (Label('Vertical Trim', 8, attach=1), at(44.32, -8.16), [], t),
        (Label('rear wall', 5, attach=1), at(-40, 90), [], t),
        (Leader(((-4.93, -6.14), (-17.11, -6.14))), at(19.82, 70.01), [], t),
        (Leader(((4.93, -6.14), (17.11, -6.14))), at(106.32, 70.01), [], t),
        (Leader(((5.76, -11), (14.77, -11))), at(45, 251), [], t),
        (Leader(((5.76, -11), (14.77, -11))), at(136.21, 251), [], t),
        (Circle(6.63), at(-26.46, 161.03), [], t),
        (Circle(6.63), at(-3.92, 63.87), [], t),
        (Circle(6.63), at(66.4, 240), [], t),
        (Circle(6.63), at(130.05, 63.87), [], t),
        (Circle(6.63), at(157.62, 240), [], t),
    ]


def trim_horizontal_trim_notes(at):
    t = trim_tag("horizontal_trim")
    return [
        (Label('1', 8, attach=1), at(85.17, 233.02), [], t),
        (Label('2', 8, attach=1), at(116.76, 131.95), [], t),
        (Label('3', 8, attach=3), at(-23.16, 90.2), [], t),
        (Label('Do this FIRST', 8, attach=1), at(130, 250), [], t),
        (Label('Front', 5, attach=1), at(-25.21, 152.73), [], t),
        (Label('Horizontal Trim', 8, attach=1), at(40.36, -6.12), [], t),
        (Label('Interior Trim', 10, attach=1), at(40, -20), [], t),
        (Label('Rear', 5, attach=1), at(145.49, 153.64), [], t),
        (Label('Repeat for door-side sidewall', 8, attach=1), at(0, 90), [], t),
        (Label('rear wall', 5, attach=3), at(-5.78, 279.65), [], t),
        (Label('side wall', 5, attach=1), at(-39.83, 168.87), [], t),
        (Label('use a  level, cover seam', 2.5, attach=1), at(71.17, 142.94), [], t),
        (Label('use a  level', 2.5, attach=1), at(47.38, 244.23), [], t),
        (Leader(((8.4, -8.5), (16.97, -8.5))), at(64.68, 237.56), [], t),
        (Leader(((8.4, -8.5), (16.97, -8.5))), at(95.52, 136.32), [], t),
        (Circle(6.63), at(-25.53, 86.07), [], t),
        (Circle(6.63), at(88, 229.2), [], t),
        (Circle(6.63), at(119.12, 127.82), [], t),
    ]


def trim_triangle_trim_notes(at):
    t = trim_tag("triangle_trim")
    return [
        (Label('4', 8, attach=1), at(85.06, 224.01), [], t),
        (Label('5', 8, attach=1), at(38.93, 187.81), [], t),
        (Label('Interior Trim', 10, attach=1), at(40, -20), [], t),
        (Label('Triangle Trim', 8, attach=1), at(40, 0), [], t),
        (Label('Triangle Trim', 8, attach=1), at(101.65, 224.09), [], t),
        (Label('rear wall', 5, attach=3), at(-12.1, 191.69), [], t),
        (Leader(((-7.6, -17), (-17.0, -17))), at(65.54, 200.65), [], t),
        (Leader(((4.04, 4.7),)), at(80.69, 209.67), [], t),
        (Leader(((6.61, 11.08), (28.15, 11.08))), at(53.39, 208.92), [], t),
        (Circle(6.63), at(41.77, 183.73), [], t),
        (Circle(6.63), at(88.17, 220.05), [], t),
    ]


BLOCK_SCREWS_DX = 1.75  # the front window's support block's screw marks, along from where the drawing had them


def trim_front_window_notes(at):
    t = trim_tag("front_window")
    return [
        # the support block's screws, marked on it
        # (shifted BLOCK_SCREWS_DX along from the drawing: the block sits that much further along here)
        *[(Lines((((-0.6, 0), (0.6, 0)), ((0, -0.6), (0, 0.6)))), at(x + BLOCK_SCREWS_DX, y), [], t) for x, y in ((42.83, 42.36), (65.36, 42.47), (65.36, 40.97), (77.69, 42.4))],
        (Icon('Screw', 3, 7.2, rotation=180, flip=True), at(42.72 + BLOCK_SCREWS_DX, 36.25), [], t),
        (Icon('Screw', 3, 7.2, rotation=180, flip=True), at(65.4 + BLOCK_SCREWS_DX, 36.18), [], t),
        (Icon('Screw', 3, 7.2, rotation=180, flip=True), at(77.72 + BLOCK_SCREWS_DX, 36.22), [], t),
        (Icon('Screw', 3, 7.2, rotation=180, flip=True), at(123.72, 38.22), [], t),
        (Icon('Screw', 3, 7.2), at(124.47, 48.44), [], t),
        (Icon('Screw', 3, 7.2), at(133.47, 48.44), [], t),
        (Icon('Screw', 3, 7.2), at(142.47, 48.44), [], t),
        (Icon('Screw', 3, 7.2, rotation=180, flip=True), at(144.53, 38.58), [], t),
        (Icon('Screw', 3, 7.2, rotation=180, flip=True), at(158.53, 38.58), [], t),
        (Label('1', 4, attach=1), at(88.73, 14.83), [], t),
        (Label('2', 4, attach=1), at(132.38, 64.84), [], t),
        (Label('2x', 2.5, attach=1), at(66.47 + BLOCK_SCREWS_DX, 37.67), [], t),
        (Label('3', 4, attach=1), at(54.44, 27.71), [], t),
        (Label('4', 4, attach=1), at(143.82, 24.68), [], t),
        (Label('5', 4, attach=1), at(91.36, -65.02), [], t),
        (Label('6', 4, attach=1), at(72.17, -55.94), [], t),
        (Label('Front Window Shelf and Frame', 5, attach=1), at(31.11, 113.11), [], t),
        (Label('LONG Screws', 3, attach=1), at(41.38, 11.37), [], t),
        (Label('LONG Screws', 3, attach=1), at(112.03, 23.89), [], t),
        (Label('LONG Screws', 3, attach=1), at(138.62, 64.49), [], t),
        (Label('Mount support block\n  flush with left edge\n  of shelf', 2.5, attach=1), at(41.03, 21.18), [], t),
        (Leader(((-18.09 - BLOCK_SCREWS_DX, -6.41),)), at(77.03 + BLOCK_SCREWS_DX, 33.18), [], t),
        (Leader(((-5.8 - BLOCK_SCREWS_DX, -5.23),)), at(64.03 + BLOCK_SCREWS_DX, 33.18), [], t),
        (Leader(((-6.78, 8.28),)), at(142.33, 51.68), [], t),
        (Leader(((-9.46, -10.08),)), at(157.03, 35.18), [], t),
        (Leader(((0, 7.49),)), at(133.33, 51.68), [], t),
        (Leader(((0, -9.12),)), at(145.03, 35.18), [], t),
        (Leader(((17.16, -10.77),)), at(125.03, 35.18), [], t),
        (Leader(((28.5, 0),)), at(79.53, 43.85), [], t),
        (Leader(((4.85, -4.94), (11.41, -4.89))), at(58.39, -52.87), [], t),
        (Leader(((2.6, -5.27),)), at(66.83, -61.73), [], t),
        (Leader(((6.34, 8.17),)), at(124.84, 51.73), [], t),
        (Leader(((6.81, 8.17), (16.92, 8.17))), at(69.47, 4.55), [], t),
        (Leader(((6.67, -10), (45.53, -10))), at(43.33, -57), [], t),
        (Leader(((8.65, -5.66),)), at(44.03, 33.18), [], t),
        (Circle(3.51), at(55.62, 25.6), [], t),
        (Circle(3.51), at(73.31, -57.74), [], t),
        (Circle(3.51), at(89.9, 12.72), [], t),
        (Circle(3.51), at(92.37, -67.19), [], t),
        (Circle(3.51), at(133.33, 62.68), [], t),
        (Circle(3.51), at(145.16, 22.54), [], t),
        (Circle(31.11), at(139.13, 43.85), [], t),
    ]


def trim_front_trim_a_notes(at):
    t = trim_tag("front_trim_a")
    return [
        (Label('#4 trim board goes on first, because it is wider and less flexible.\n Then #5 trim is nailed onto the sidewall.\n This does not match the other corners, but is correct.', 6, attach=1, bold=("first",)), at(-60, 60), [], t),
        (Label('1', 8, attach=1), at(93.05, 236.14), [], t),
        (Label('2', 8, attach=1), at(-10.22, 125.52), [], t),
        (Label('3', 8, attach=1), at(69.88, 155.55), [], t),
        (Label('4', 8, attach=1), at(-7.47, 209.05), [], t),
        (Label('5', 8, attach=1), at(-41, 171), [], t),
        (Label('Add 2" trim to sidewall\n  in this corner', 5, attach=1), at(-73.38, 152.56), [], t),
        (Label('Baseboards', 5, attach=1), at(1.83, 122.33), [], t),
        (Label('Front Wall Trim', 8, attach=1), at(40, 0), [], t),
        (Label('Interior Trim', 10, attach=1), at(40, -20), [], t),
        (Leader(((-11.68, 8.12),)), at(12.02, 193), [], t),
        (Leader(((-11.93, -12.91), (-34.83, -12.98))), at(3.4, 179.62), [], t),
        (Leader(((-15.2, -9.91),)), at(12.9, 134.91), [], t),
        (Leader(((-60.59, -10.61),)), at(59.27, 133.14), [], t),
        (Leader(((7.43, 7.1),)), at(83.16, 220.36), [], t),  # (its head above the top trim, not in it)
        (Leader(((9.88, -6.56),)), at(57.15, 161.8), [], t),
        (Circle(6.63), at(-38.06, 166.62), [], t),
        (Circle(6.63), at(-7.86, 121.39), [], t),
        (Circle(6.63), at(-5.1, 204.91), [], t),
        (Circle(6.63), at(72.55, 151.58), [], t),
        (Circle(6.63), at(95.41, 232.01), [], t),
    ]


def trim_front_trim_b_notes(at):
    t = trim_tag("front_trim_b")
    return [
        (Label('1', 8, attach=1), at(13.12, 238.78), [], t),
        (Label('2', 8, attach=1), at(90.27, 238.71), [], t),
        (Label('3', 8, attach=1), at(127.37, 218.23), [], t),
        (Label('4', 8, attach=1), at(115.34, 178.23), [], t),
        (Label('5', 8, attach=1), at(71.38, 263.07), [], t),
        (Label('Front Wall Trim', 8, attach=1), at(40, 0), [], t),
        (Label('Install 2" trim to side wall\n  in this corner before\n  front-wall corner trim,\n  unless there is not enough\n  space between side trim and\n  shelf edge.  In this case, install\n  front-wall corner trim first,\n  and then side-wall trim.', 5, attach=1), at(100, 120), [], t),
        (Label('Interior Trim', 10, attach=1), at(40, -20), [], t),
        (Leader(((-8.99, 13.79),)), at(28.09, 215.3), [], t),
        (Leader(((12.68, -7.45),)), at(99.42, 185.23), [], t),
        (Leader(((13.98, 21.0),)), at(56.89, 232.31), [], t),
        (Leader(((14.33, 28.51), (23.68, 28.83))), at(43.45, 230.22), [], t),
        (Leader(((15.43, 29.37), (9.11, 29.37))), at(71.27, 229.91), [], t),
        (Leader(((17.34, 15.72),)), at(70.39, 214.41), [], t),
        (Leader(((17.89, 10.79),)), at(106.98, 199.73), [], t),
        (Leader(((7.72, 28.75),)), at(83.2, 199.42), [], t),
        (Circle(6.63), at(15.48, 234.65), [], t),
        (Circle(6.63), at(73.75, 259.28), [], t),
        (Circle(6.63), at(92.64, 234.58), [], t),
        (Circle(6.63), at(117.81, 174.42), [], t),
        (Circle(6.63), at(130.54, 213.95), [], t),
    ]


def trim_final_trim_notes(at):
    t = trim_tag("final_trim")
    return [
        (Label('1', 8, attach=1), at(-9.97, 254.36), [], t),
        (Label('2', 8, attach=1), at(-10.24, 207.01), [], t),
        (Label('3', 8, attach=1), at(139.13, 107.88), [], t),
        (Label('4', 8, attach=1), at(4.91, 106.95), [], t),
        (Label('5', 8, attach=1), at(-7.79, 18.94), [], t),
        (Label('Cover ceiling seams with 2" trim', 8, attach=1), at(8.56, 18.03), [], t),
        (Label('Final Trim', 8, attach=1), at(52.72, -7.38), [], t),
        (Label('Front', 5, attach=1), at(-19.06, 285.12), [], t),
        (Label('Interior Trim', 10, attach=1), at(40, -20), [], t),
        (Label('Rear', 5, attach=1), at(151.64, 286.03), [], t),
        (Label('Repeat on other sidewall', 10, attach=1), at(6.12, 206.11), [], t),
        (Label('side wall', 5, attach=1), at(-33.68, 301.26), [], t),
        (Label('use a  level', 4, attach=1), at(136.32, 91.26), [], t),
        (Leader(((-17.91, 12),)), at(31.82, 87.26), [], t),
        (Leader(((-21.72, -15.05),)), at(19.57, 269.05), [], t),
        (Leader(((20.09, 12.9),)), at(115.82, 87.26), [], t),
        (Circle(6.63), at(-7.87, 202.88), [], t),
        (Circle(6.63), at(-7.6, 250.22), [], t),
        (Circle(6.63), at(-5.43, 14.8), [], t),
        (Circle(6.63), at(8.4, 102.96), [], t),
        (Circle(6.63), at(141.49, 103.74), [], t),
    ]


TRIM_NOTES = {name.removeprefix("trim_").removesuffix("_notes"): f for name, f in list(globals().items())
              if name.startswith("trim_") and name.endswith("_notes")}


def _with_stud_sections(notes, figure, corners):
    """The shelf details' window studs, cut: a crossed box each (1 1/2 x 3 1/2)."""
    def f(at):
        t = trim_tag(figure)
        return notes(at) + [(n, at(x, y), [], t) for x, y in corners for n in crossed_box(1.5, 3.5)]
    return f


TRIM_NOTES["rear_shelf"] = _with_stud_sections(TRIM_NOTES["rear_shelf"], "rear_shelf", [(120.69, -61.14), (146.19, -61.14)])
TRIM_NOTES["front_window"] = _with_stud_sections(TRIM_NOTES["front_window"], "front_window", [(119.94, 43.18), (145.44, 43.18)])


# ── Interior_Trim/vent_cap_install.md ──────────────────────────────────────

ARROW = 1.0  # a dimension's arrowhead, inches (the drawings' dimstyle)


def dimension(at, t, x0, x1, y, text, text_at, height=2.5, vertical=False):
    """A dimension from x0 to x1 (along X, or along Y with `vertical`, at x =
    y) at height y, arrows at both ends, its text at text_at. A dimension too
    short for its arrowheads has them outside, pointing in, as QCAD drew it."""
    v = (lambda a, b: (b, a)) if vertical else (lambda a, b: (a, b))
    d = x1 - x0
    if abs(d) < 3 * ARROW:
        lines = [(Leader((v(-3 * ARROW, 0),)), at(*v(x0, y)), [], t), (Leader((v(3 * ARROW, 0),)), at(*v(x1, y)), [], t),
                 (Leader((v(d, 0),), arrow=False), at(*v(x0, y)), [], t)]
    else:
        lines = [(Leader((v(d, 0),)), at(*v(x0, y)), [], t), (Leader((v(-d, 0),)), at(*v(x1, y)), [], t)]
    return lines + [(Label(text, height, attach=8), at(*text_at), [], t)]


def vent_cap_notes(at, short):
    """short: the short piece's length (cut to fit); it's drawn from x = 93.4."""
    t = "manual:interior_trim:vent_cap"
    end = 93.4 + short  # the short piece's front end, in the drawing
    centerlines = [((38.5, 103.5), (104, 0)), ((38.5, 106), (104, 0)), ((88.9, 67.59), (end - 85.4, 0)),
                   ((88.9, 70.09), (end - 85.4, 0))]
    centerlines += [((x, 96.5), (0, 16.5)) for x in (43.75, 90, 137.25)] + [((x, 60.59), (0, 16.5)) for x in (94.15, end - 1.75)]
    return [
        # the block, with its two screws preset
        (Icon("Screw", 4, 9.6), at(64.77, 168.08), [], t),
        (Icon("Screw", 4, 9.6), at(69.13, 170.79), [], t),
        (Label("Block preparation", 5, attach=1), at(95.24, 167.42), [], t),
        # the pieces' screw holes: centerlines and dimensions
        *[(Leader((d,), arrow=False), at(*p), [], t) for p, d in centerlines],
        # (where Images/vent_cap.dxf's dimensions were)
        *dimension(at, t, 42, 90, 114.5, '48"', (66, 116)),
        *dimension(at, t, 42, 43.75, 111, '1.75"', (38, 113.25)),
        *dimension(at, t, 137.25, 138, 113, '0.75"', (138.5, 116)),
        *dimension(at, t, 93.4, 94.15, 77.09, '0.75"', (92.9, 80.2)),
        *dimension(at, t, end - 1.75, end, 75.84, '1.75"', (end + 2.3, 79)),
        *dimension(at, t, 70.09, 73.59, end + 3, '3.5"', (end + 11.38, 72.5), vertical=True),  # the holes' rows, from the edges
        *dimension(at, t, 64.09, 67.59, end + 2, '3.5"', (end + 11.48, 65), vertical=True),
        (Label("REAR", 3, attach=1), at(36.44, 93.24), [], t),
        (Label("SEAM", 3, attach=1), at(132.7, 93.42), [], t),
        (Label("SEAM", 3, attach=1), at(88.73, 57.45), [], t),
        (Label("FRONT", 3, attach=1), at(end - 4.67, 57.27), [], t),
        (Label("Vent Cap Details", 7, attach=1), at(59.24, 15.8), [], t),
    ]
