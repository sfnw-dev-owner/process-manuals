"""Helpers shared by every module of the model."""

from functools import cache

from build123d import *

from .hardware import *  # hand-modeled stand-ins for imported hardware meshes
from .lumber import *  # standard lumber sizes and sheet goods

from .dimensions import *

# Boxes and rectangles are placed by their minimum corner.
CORNER = Align.MIN

def spaced(first, step, count):
    """count positions, the first at `first` and each `step` further on."""
    return [first + i * step for i in range(count)]


def component(fn):
    """Make fn(), returning (solids, children) or (solids, children,
    anchors), into a cached component. Anchors are {name: Location} of the
    points other things are placed by (a rafter's tip, a stud's top), in the
    component's frame; figures hang their notes on them."""
    fn = cache(fn)
    shapes = {}

    def anchors():
        """{name: Location}: the component's named points, in its frame."""
        out = fn()
        return dict(out[2]) if len(out) > 2 else {}

    @cache
    def tags():
        """Every tag used anywhere inside this component."""
        out = set()
        for child, _, _, tag in fn()[1]:
            out |= set(tag.split()) | {tag} | child.tags()
        return frozenset(out)

    def shape(hidden=frozenset(), mods=()):
        """The component with children on `hidden` tags left out, then
        mirrored/scaled per `mods`. Cached (mirroring copies geometry), keyed
        only on the tags that occur inside it."""
        hidden = frozenset(hidden) & tags()
        k = (hidden, mods)
        if k not in shapes:
            if mods:
                s = shape(hidden, ())
                for mod in mods:
                    s = mirror(s, Plane.YZ) if mod == "mirror" else scale(s, by=mod[1])
            else:
                solids, children = fn()[:2]
                parts = list(solids)
                for child, loc, cmods, tag in children:
                    if tag not in hidden:
                        parts.append(loc * child.shape(hidden, key(cmods)))
                s = Compound(parts)
            shapes[k] = s
        return shapes[k]

    fn.shape = shape
    fn.tags = tags
    fn.anchors = anchors
    return fn


def key(mods):
    """Hashable form of a modifiers list."""
    return tuple(m if m == "mirror" else (m[0], tuple(m[1])) for m in mods)
