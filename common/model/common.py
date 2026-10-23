"""Helpers shared by every module of the model."""

from functools import cache

from build123d import *

from .hardware import *  # hand-modeled stand-ins for imported hardware meshes
from .lumber import *  # standard lumber sizes and sheet goods

from .dimensions import *

# Boxes and rectangles are placed by their minimum corner.
CORNER = Align.MIN

# Children whose tag starts with this are optional: jig tools and manual
# annotations that only belong in particular manuals' figures. They're left
# out unless the caller asks for one of the tag's words. A tag may hold
# several words, e.g. "manual:platform:1 manual:platform:3"; a figure for
# platform.md step 3 asks for {"manual:platform", "manual:platform:3"}.
OPTIONAL = "manual:"


def shown_by(tag, shown):
    """Whether an optional child's tag is asked for."""
    return any(word in shown for word in tag.split())


def spaced(first, step, count):
    """count positions, the first at `first` and each `step` further on."""
    return [first + i * step for i in range(count)]


def component(fn):
    """Make fn(), returning (solids, children), into a cached component."""
    fn = cache(fn)
    shapes = {}

    @cache
    def tags():
        """Every tag used anywhere inside this component."""
        out = set()
        for child, _, _, tag in fn()[1]:
            out |= set(tag.split()) | {tag} | child.tags()
        return frozenset(out)

    def include(tag, hidden, shown):
        if tag.startswith(OPTIONAL):
            return shown_by(tag, shown)
        return tag not in hidden

    def shape(hidden=frozenset(), mods=(), shown=frozenset()):
        """The component with children on `hidden` tags left out (and optional
        children in unless `shown` asks for them), then mirrored/scaled per
        `mods`. Cached (mirroring copies geometry), keyed only on the tags
        that occur inside it."""
        hidden, shown = frozenset(hidden) & tags(), frozenset(shown) & tags()
        k = (hidden, mods, shown)
        if k not in shapes:
            if mods:
                s = shape(hidden, (), shown)
                for mod in mods:
                    s = mirror(s, Plane.YZ) if mod == "mirror" else scale(s, by=mod[1])
            else:
                solids, children = fn()
                parts = list(solids)
                for child, loc, cmods, tag in children:
                    if include(tag, hidden, shown):
                        parts.append(loc * child.shape(hidden, key(cmods), shown))
                s = Compound(parts)
            shapes[k] = s
        return shapes[k]

    def notes(shown=frozenset(), hidden=frozenset()):
        """The annotations (see notes.py) in this component that `shown` asks
        for, as [(Location, Note)] in its frame. (Modifiers don't apply to
        annotations.)"""
        out = []
        for child, loc, _, tag in fn()[1]:
            if include(tag, hidden, shown):
                out += [(loc * l, note) for l, note in child.notes(shown, hidden)]
        return out

    fn.shape = shape
    fn.tags = tags
    fn.notes = notes
    return fn


def key(mods):
    """Hashable form of a modifiers list."""
    return tuple(m if m == "mirror" else (m[0], tuple(m[1])) for m in mods)
