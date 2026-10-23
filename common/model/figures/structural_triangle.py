"""Structural_Triangle/triangle.md: building the structural triangle from
its cut parts (model/roof.py triangle_parts), seen face on, step by step:
B and the A sides, then C and the E studs, nailing them, then the D studs."""

from model.common import key
from model.notes import Icon, Label, Leader
from model.roof import triangle_parts

from . import Figure, camera, figure_names

MD = "Structural_Triangle/triangle.md"
VIEW = camera((0, -1, 0))  # face on: X to the right, Z up

# step -> (the parts it adds, the parts it's still working on); earlier
# parts are drawn gray
STEPS = {1: ("BA", ""), 2: ("CE", ""), 3: ("", "CE"), 4: ("", "CE"), 5: ("D", "")}

# The notes, in the drawing (inches, X from the triangle's center, Y up from
# the bottom of B)
NOTES = {
    1: [(-33.6, 6.09, Icon("Screw", 2.4, 5.76, rotation=-30, flip=True)),
        (34.52, 5.89, Icon("Screw", 2.4, 5.76, rotation=30)),
        (-36, -6, Label("CLAMP", 3, attach=1)), (21.16, -5.44, Label("CLAMP", 3, attach=1)),
        (-31, 10, Label("x3", 2, attach=1)), (29, 10, Label("x3", 2, attach=1)),
        (-39.52, 1.87, Leader(((0, 6.22),))), (-39.5, 0, Leader(((0, -7.5), (2.5, -7.5)))),
        (38.98, 1.87, Leader(((0, 6.22),))), (39, 0, Leader(((0, -7.5), (-2.5, -7.5))))],
    2: [(-3.89, -3.5, Icon("NailGun", 7.25, 7, rotation=180, flip=True)),
        (3.71, -3.52, Icon("NailGun", 7.25, 7, rotation=180)),
        (-6.72, -6.42, Label("x2", 2, attach=1)), (3.82, -6.42, Label("x2", 2, attach=1))],
    3: [(-5.92, 2.4, Icon("NailGun", 7.25, 7, rotation=90)),
        (-5.92, 10.58, Icon("NailGun", 7.25, 7, rotation=90, flip=True)),
        (5.92, 2.4, Icon("NailGun", 7.25, 7, rotation=-90, flip=True)),
        (5.92, 10.58, Icon("NailGun", 7.25, 7, rotation=-90))],
    4: [(-3.89, 18.08, Icon("NailGun", 7.25, 7)),
        (-2.07, -3.81, Icon("NailGun", 7.25, 7, rotation=180, flip=True)),
        (3.71, 18.1, Icon("NailGun", 7.25, 7, flip=True)),
        (-11, 21, Label("x2", 2, attach=1)), (-4.59, -7.01, Label("x2", 2, attach=1)),
        (8, 21, Label("x2", 2, attach=1))],
    5: [(-19.46, 13, Icon("NailGun", 7.25, 7)),
        (-19.31, -3.61, Icon("NailGun", 7.25, 7, rotation=180, flip=True)),
        (19.14, 13.1, Icon("NailGun", 7.25, 7, flip=True)),
        (19.3, -3.54, Icon("NailGun", 7.25, 7, rotation=180)),
        (-22.01, 15.82, Label("x2", 2, attach=7)), (-21.84, -6.44, Label("x2", 2, attach=1)),
        (19.24, 16, Label("x2", 2, attach=7)), (19.4, -6.44, Label("x2", 2, attach=1))],
}


def figures():
    shapes = {letter: [VIEW * loc * comp.shape(frozenset(), key(mods)) for comp, loc, mods in instances]
              for letter, instances in triangle_parts().items()}
    everything = [s for ss in shapes.values() for s in ss]
    out, done = [], ""
    for (step, (adds, working)), name in zip(STEPS.items(), figure_names(MD)):
        parts = [(s, "jig") for s in everything]
        parts += [(s, "context") for letter in done if letter not in working for s in shapes[letter]]
        parts += [(s, "new") for letter in adds + working for s in shapes[letter]]
        out.append(Figure(MD, name, parts, NOTES[step]))
        done += adds
    return out
