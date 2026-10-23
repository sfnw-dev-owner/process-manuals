#!/usr/bin/env python3
"""Render the manuals' figures from the model (common/model) to SVG.

A manual embeds a figure as `model:<manual>/<figure>` (see
common/model/figures/__init__.py); render/model.lua asks this script for each
one's SVG. Runs inside the renderer container (render/Dockerfile), from any
directory:

  model2svg.py FIGURE ...         JSON {figure: {"svg": path, "deps": [paths]}},
                                  rendering any that aren't cached yet
  model2svg.py --deps FIGURE ...  the same, without rendering (for render/go's
                                  dependency pass)
  model2svg.py --all              render every figure any manual embeds (in
                                  parallel, a few of a manual's at a time) and
                                  drop cached figures no manual uses
                                  (render/all runs this first)

Paths are relative to the repo root, with a leading "/" (typst's --root).

Cache: .rendered-figures/<manual>-<figure>-<hash>.svg, where the hash covers
the figure's name and everything it's drawn from: the source files its
module imports from common/model (followed statically, so checking the
cache doesn't need build123d), this file, render/requirements.txt, and the
clipart. So a manual whose text changes, but not its figures' model code,
typesets without rendering anything, and a change to, say, walls.py only
re-renders the figures that import it.
"""

import ast
import base64
import functools
import hashlib
import json
import math
import os
import pathlib
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).resolve().parents[1]
MODEL = REPO / "common" / "model"
CLIPART = REPO / "common" / "clipart"
CACHE = REPO / ".rendered-figures"
REF = re.compile(r"model:([a-z0-9_-]+)/([a-z0-9_.-]+)")


# ── the cache (standard library only) ──────────────────────────────────────

@functools.cache
def registry():
    """(MODULES, FIGURES, SIZES) from model/figures/__init__.py, read
    without importing it."""
    tree = ast.parse((MODEL / "figures" / "__init__.py").read_text())
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("MODULES", "FIGURES", "SIZES"):
                found[node.targets[0].id] = ast.literal_eval(node.value)
    return found["MODULES"], found["FIGURES"], found["SIZES"]


def _module_file(name):
    """The file of a module under common/model ("model.walls"), or None."""
    parts = name.split(".")
    if parts[0] != "model":
        return None
    base = MODEL.joinpath(*parts[1:])
    for f in (base.with_suffix(".py"), base / "__init__.py"):
        if f.is_file():
            return f
    return None


def _package(f):
    """The package a file's module is in (a package's __init__.py: that
    package), as ["model", ...]."""
    return list(f.relative_to(MODEL.parent).with_suffix("").parts[:-1])


@functools.cache
def _imports(f):
    """The files under common/model that file `f` imports (and the
    packages it's in, whose __init__ importing it runs); parsed once."""
    pkg = _package(f)
    found = [_module_file(".".join(pkg[:i])) for i in range(1, len(pkg) + 1)]
    for node in ast.walk(ast.parse(f.read_text())):
        if isinstance(node, ast.Import):
            found += [_module_file(a.name) for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = pkg[:len(pkg) - node.level + 1] if node.level > 1 else pkg
                base = ".".join(base + ([node.module] if node.module else []))
            else:
                base = node.module or ""
            found.append(_module_file(base))
            found += [_module_file(f"{base}.{a.name}") for a in node.names]  # submodules
    return [g for g in found if g is not None]


def sources(module):
    """Every file under common/model that `module` imports, transitively
    (including the packages they're in)."""
    todo, seen = [_module_file(module)], set()
    while todo:
        f = todo.pop()
        if f is None or f in seen:
            continue
        seen.add(f)
        todo += _imports(f)
    return sorted(seen)


def inputs(module):
    """Files a module's figures are drawn from (see the docstring)."""
    return sources(module) + [pathlib.Path(__file__).resolve(), REPO / "render" / "requirements.txt",
                              *sorted(CLIPART.iterdir())]


def rel(f):
    return "/" + str(f.relative_to(REPO))


def plan(figures):
    """{figure: (svg path, [input files])} for "manual/name" figures."""
    modules, names, _ = registry()
    out, digests = {}, {}
    for fig in figures:
        manual, name = fig.split("/")
        if manual not in modules or name not in names[manual]:
            sys.exit(f"model2svg: unknown figure {fig!r} (see common/model/figures/__init__.py)")
        module = f"model.figures.{modules[manual]}"
        if module not in digests:
            files = inputs(module)
            h = hashlib.sha1()
            for f in files:
                h.update(rel(f).encode() + b"\0" + f.read_bytes() + b"\0")
            digests[module] = (h, files)
        h, files = digests[module]
        h = h.copy()
        h.update(fig.encode())
        out[fig] = (CACHE / f"{manual}-{name}-{h.hexdigest()[:20]}.svg", files)
    return out


def manuals_figures():
    """Every figure any manual embeds."""
    found = []
    for md in sorted(REPO.rglob("*.md")):
        if ".git" in md.parts or "archived" in md.parts:
            continue
        for m in REF.finditer(md.read_text(errors="replace")):
            found.append(f"{m.group(1)}/{m.group(2)}")
    return list(dict.fromkeys(found))


def main(argv):
    deps_only = "--deps" in argv
    figures = manuals_figures() if "--all" in argv else [a for a in argv if not a.startswith("--")]
    todo = plan(figures)
    missing = [f for f, (svg, _) in todo.items() if not svg.exists()]
    if missing and not deps_only:
        render(missing, {f: todo[f][0] for f in missing})
    if "--all" in argv:
        keep = {svg for svg, _ in todo.values()}
        stale = [f for f in CACHE.glob("*.svg") if f not in keep] if CACHE.is_dir() else []
        for f in stale:  # no manual uses these (any more)
            f.unlink()
        print(f"model2svg: {len(todo)} figures, {0 if deps_only else len(missing)} rendered, {len(stale)} pruned",
              file=sys.stderr)
    else:
        print(json.dumps({f: {"svg": rel(svg), "deps": [rel(d) for d in files]} for f, (svg, files) in todo.items()}))


# ── rendering (build123d) ──────────────────────────────────────────────────

# Line weights, in inches on paper: QCAD printed the drawings' lines as
# hairlines whatever their scale, so a drawing's line weight is PAPER_LINE
# divided by its printed scale.
PAPER_LINE = 0.004
PAPER_HEAVY = 0.025  # a "heavy" outline: how the drawings emphasized a new part that can't be filled black
LINE = 0.12  # inches of drawing: the notes' line weights are defined relative to this at full size
# Labels: the drawings' were typeset in DejaVu Sans (QCAD's default); a page's
# (as LayOut's) in Carlito.
DRAWING_FONT = ("DejaVu Sans", REPO / "render" / "DejaVu" / "DejaVuSans.ttf", REPO / "render" / "DejaVu" / "DejaVuSans-Bold.ttf")
PAGE_FONT = ("Carlito", REPO / "render" / "Carlito" / "Carlito-Regular.ttf", REPO / "render" / "Carlito" / "Carlito-Bold.ttf")
# White around a drawing, in inches of drawing: QCAD's "print to PDF" cropped
# the manuals' drawings to their contents plus this much (render/dxf-export.js
# in git history, cropToContents: a 5-unit margin split between the sides).
MARGIN = 2.5
SVGNS = "{http://www.w3.org/2000/svg}"


JOB = 4  # figures per job: a job builds its manual's figures (just its own, where the module can) and writes them


def render(figures, paths):
    """Render figures ("manual/name") to their cache paths, in jobs of a
    few figures of one manual each, run in parallel processes (forked after
    the one import of build123d, which costs more than a small manual's
    figures do; one job runs in this process)."""
    sys.path.insert(0, str(REPO / "common"))
    CACHE.mkdir(exist_ok=True)
    by_manual = {}
    for fig in figures:
        manual, name = fig.split("/")
        by_manual.setdefault(manual, []).append(name)
    sizes = registry()[2]
    jobs = [(manual, names[i:i + JOB], {n: paths[f"{manual}/{n}"] for n in names[i:i + JOB]})
            # pages (3D views, which have no printed size) first, they take longest; then the big manuals
            for manual, names in sorted(by_manual.items(), key=lambda kv: (kv[0] in sizes, -len(kv[1])))
            for i in range(0, len(names), JOB)]
    if len(jobs) == 1:
        _render_job(jobs[0])
        return
    import multiprocessing
    _import_build123d()  # once, before forking
    with multiprocessing.get_context("fork").Pool(min(len(jobs), os.cpu_count() or 1)) as pool:
        for _ in pool.imap_unordered(_render_job, jobs):
            pass


def _import_build123d():
    """Import build123d for rendering, with its linear algebra
    single-threaded: the process then has one thread, so it forks cleanly
    (and nothing here needs more)."""
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    import build123d  # noqa: F401


def _render_job(job):
    manual, names, paths = job
    _import_build123d()
    from model.figures import manual_figures
    built = manual_figures(manual, names)
    for name in names:
        fd, tmp = tempfile.mkstemp(dir=CACHE, suffix=".svg.tmp")
        os.close(fd)
        write_svg(built[name], pathlib.Path(tmp))
        os.replace(tmp, paths[name])  # atomically: render/all runs manuals in parallel
        print(f"model2svg: rendered {manual}/{name}", file=sys.stderr)


def styles(line=LINE, heavy=4 * LINE):
    from model.figures import BLACK, DARK, EDGE, GRAY, LIGHT
    return {  # style -> (line color, line weight, fill); see model/figures/__init__.py
        "jig": (LIGHT, line, None),
        "context": (EDGE, line, GRAY),
        "covered": (DARK, line, None),
        "new": (BLACK, line, BLACK),
        "outline": (BLACK, line, None),
        "heavy": (BLACK, heavy, None),
        "bare": (None, 0, None),
        "hlr": (BLACK, line, None),
        "hlr_thin": (BLACK, line / 2, None),
    }


HLR = ("hlr", "hlr_thin")
FILLS = {"foam": "url(#foam)", "laid": "url(#laid)", "glass": "url(#glass)", "plywood": "url(#plywood)"}
SVG_DEFS = """<defs xmlns="http://www.w3.org/2000/svg">
  <pattern id="foam" patternUnits="userSpaceOnUse" width="4" height="0.5">
    <rect width="4" height="0.5" fill="white"/>
    <path d="M0 0.25 H4" stroke="rgb(185,185,185)" stroke-width="0.12"/>
  </pattern>
  <pattern id="laid" patternUnits="userSpaceOnUse" width="1.5" height="1.5">
    <rect width="1.5" height="1.5" fill="white"/>
    <path d="M-0.375 0.375 L0.375 -0.375 M0 1.5 L1.5 0 M1.125 1.875 L1.875 1.125" stroke="rgb(120,120,120)" stroke-width="0.1"/>
  </pattern>
  <pattern id="glass" patternUnits="userSpaceOnUse" width="2" height="2">
    <rect width="2" height="2" fill="white"/>
    <path d="M-0.5 0.5 L0.5 -0.5 M0 2 L2 0 M1.5 2.5 L2.5 1.5 M0 1.4 L1.4 0" stroke="rgb(120,120,120)" stroke-width="0.06"/>
  </pattern>
  <pattern id="plywood" patternUnits="userSpaceOnUse" width="3.5" height="3.5">
    <rect width="3.5" height="3.5" fill="white"/>
    <path d="M-1.75 1.75 L1.75 -1.75 M0 3.5 L3.5 0 M1.75 5.25 L5.25 1.75" stroke="rgb(150,150,150)" stroke-width="0.07" stroke-dasharray="2.2 0.9"/>
    <circle cx="0.9" cy="1.1" r="0.06" fill="rgb(150,150,150)"/><circle cx="2.6" cy="2.4" r="0.06" fill="rgb(150,150,150)"/>
  </pattern>
</defs>"""


def _parts(fig):
    """(shape, style, fill, clip) for each part: fill and clip (a box the
    part's own edges are cut to, like Figure.clip) are optional."""
    for p in fig.parts:
        yield p[0], p[1], (p[2] if len(p) > 2 else None), (p[3] if len(p) > 3 else None)


def _positions(e, fractions):
    """Points along an edge at fractions of its length: what build123d's
    Edge.position_at gives (the same OpenCASCADE calls, the same
    arithmetic), as (x, y, z) tuples, without the wrapper objects (a figure
    evaluates tens of thousands of points)."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GCPnts import GCPnts_AbscissaPoint
    from OCP.TopAbs import TopAbs_Orientation
    curve = BRepAdaptor_Curve(e.wrapped)
    length = GCPnts_AbscissaPoint.Length_s(curve)
    forward = e.wrapped.Orientation() == TopAbs_Orientation.TopAbs_FORWARD
    first = curve.FirstParameter()
    out = []
    for f in fractions:
        if not forward:
            f = 1 - f
        p = curve.Value(GCPnts_AbscissaPoint(curve, length * f, first).Parameter())
        out.append((p.X(), p.Y(), p.Z()))
    return out


def _length(e):
    """build123d's Edge.length."""
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    props = GProp_GProps()
    BRepGProp.LinearProperties_s(e.wrapped, props)
    return props.Mass()


def _ordered(edges):
    """Edges in a stable order (OpenCASCADE's projection returns them in an
    order that varies from run to run), so the same figure gives the same
    SVG. Degenerate edges (which the projection can produce from a part seen
    edge-on; their ends can't even be evaluated) are dropped."""
    keyed = []
    for e in edges:
        try:
            (ax, ay, _), (bx, by, _) = _positions(e, (0, 1))
            keyed.append((tuple(round(c, 4) for c in (ax, ay, bx, by, _length(e))), e))
        except Exception:
            continue
    return [e for _, e in sorted(keyed, key=lambda k: k[0])]


def _ordered_solids(shape):
    """A part's solids in a stable order, lowest first: OpenCASCADE lists
    the solids of a transformed compound in an order that varies from run
    to run, and where the faces of one fill overlap, the one drawn last
    covers the others (and their outlines), so a painter's order by height
    lets a part's higher solids hide its lower ones, as seen from above. A
    solid's own faces keep their order. A part without solids is yielded
    whole."""
    solids = shape.solids()
    if len(solids) < 2:
        return [shape]

    def key(s):
        bb = s.bounding_box()
        return tuple(round(v, 4) for v in (bb.max.Z, bb.min.Z, bb.min.X, bb.min.Y, s.volume))
    return sorted(solids, key=key)


def outline(shape):
    """A part's own edges seen from above. Like the manuals' drawings, parts
    don't hide one another: framing shows through the sheathing."""
    eye = (0, 0, shape.bounding_box().max.Z + 1000)
    return _ordered(shape.project_to_viewport(eye, (0, 1, 0), (0, 0, 0))[0])


def visible_outline(shapes):
    """The edges of these parts seen from above, each hiding what's behind
    it (for 3D views)."""
    from build123d import Compound
    c = Compound(shapes)
    eye = (0, 0, c.bounding_box().max.Z + 1000)
    return _ordered(c.project_to_viewport(eye, (0, 1, 0), (0, 0, 0))[0])


def clipped(edges, box):
    """The edges cut to a box (x0, y0, x1, y1), or all of them if there's no
    box: straight edges are shortened to it, others kept only if inside."""
    if box is None:
        return edges
    from build123d import Edge
    x0, y0, x1, y1 = box
    out = []
    for e in edges:
        a, b = e.position_at(0), e.position_at(1)
        if e.geom_type.name != "LINE":
            bb = e.bounding_box()
            if bb.min.X >= x0 and bb.max.X <= x1 and bb.min.Y >= y0 and bb.max.Y <= y1:
                out.append(e)
            continue
        t0, t1 = 0.0, 1.0  # Liang-Barsky
        for p, q in ((a.X - b.X, a.X - x0), (b.X - a.X, x1 - a.X), (a.Y - b.Y, a.Y - y0), (b.Y - a.Y, y1 - a.Y)):
            if p == 0:
                if q < 0:
                    t0, t1 = 1, 0
                    break
                continue
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
        if t0 < t1:
            out.append(e if (t0, t1) == (0, 1) else Edge.make_line(a + (b - a) * t0, a + (b - a) * t1))
    return out


def top_faces(shape):
    """The part's upward-facing flat faces, flattened onto the drawing: what
    gets filled."""
    from build123d import Face, GeomType, Location, Wire
    out = []
    for f in (f for solid in _ordered_solids(shape) for f in solid.faces()):
        try:
            n = f.normal_at()
        except Exception:
            continue
        if n.Z > 0.999:
            out.append(Location((0, 0, -f.center().Z)) * f)
        elif n.Z > 0.2 and f.geom_type == GeomType.PLANE:  # tilted: flatten its outline onto the drawing
            # (the corners in the wire's order: unordered, a rectangle fills as a bowtie)
            pts = [(e.position_at(0).X, e.position_at(0).Y, 0) for e in f.outer_wire().order_edges()]
            if len(pts) >= 3:
                out.append(Face(Wire.make_polygon(pts, close=True)))
    return out


def write_svg(fig, path):
    """The figure as SVG: geometry by build123d's ExportSVG (fills, then
    lines), then the annotations. Returns the drawing's edges, for comparing."""
    from build123d import ExportSVG
    if fig.page:
        return write_page_svg(fig, path)
    scale = fig.size or 1  # inches on paper per inch of drawing
    line = PAPER_LINE / scale
    STYLES = styles(line, PAPER_HEAVY / scale)
    svg = ExportSVG(margin=0)  # _add_notes adds MARGIN around everything
    fills = {}
    for shape, style, fill, _ in _parts(fig):
        if isinstance(fill, tuple):  # a plain color
            name, color = "rgb_%d_%d_%d" % fill, fill
        elif fill:  # a pattern
            name, color = fill, (255, 255, 255)
        else:
            name, color = style, STYLES[style][2]
        if color is not None:
            fills.setdefault(name, (color, []))[1].extend(top_faces(shape))
    edges = []
    # the jig's lines go under the fills (the drawings' solid hatches covered
    # them: a part laid on the jig hides it)
    svg.add_layer("jig", line_color=_hex(STYLES["jig"][0]), line_weight=STYLES["jig"][1])
    for shape, style, _, clip in _parts(fig):
        if style == "jig":
            es = clipped(clipped(outline(shape), fig.clip), clip)
            svg.add_shape(es, layer=style)
            edges += [(e, style) for e in es]
    for name, (color, faces) in sorted(fills.items(), key=lambda kv: kv[0] not in FILLS):  # patterns underneath
        if faces:
            svg.add_layer(f"fill_{name}", fill_color=_hex(color), line_weight=0.001)
            svg.add_shape(faces, layer=f"fill_{name}")
    for style, (color, weight, _) in STYLES.items():
        if color is not None and style != "jig":
            svg.add_layer(style, line_color=_hex(color), line_weight=weight)
    for shape, style, _, clip in _parts(fig):
        if STYLES[style][0] is None or style in HLR or style == "jig":
            continue
        es = clipped(clipped(outline(shape), fig.clip), clip)
        svg.add_shape(es, layer=style)
        edges += [(e, style) for e in es]
    for style in HLR:
        shapes = [shape for shape, s, _, _ in _parts(fig) if s == style]
        if shapes:
            es = clipped(visible_outline(shapes), fig.clip)
            svg.add_shape(es, layer=style)
            edges += [(e, style) for e in es]
    path.parent.mkdir(parents=True, exist_ok=True)
    svg.write(path)
    _add_notes(path, fig.notes, fig.size, margin=fig.frame or MARGIN, unit=line / LINE)
    return edges


PAGE_LINES = {"hlr_light": 0.012, "hlr": 0.012, "hlr_thin": 0.006}  # a page's stroke widths, inches (as SketchUp drew them)
PAGE_COLORS = {"hlr_light": "#8a8a8a"}  # (default black): "hlr_light" for background views (LayOut's gray)
PAGE_UNIT = 0.06  # notes' line weights on a page, relative to a drawing's


def write_page_svg(fig, path):
    """A page of viewports (see model/figures/__init__.py Viewport), then the
    page's notes."""
    w, h = fig.page
    root = ET.Element(f"{SVGNS}svg", {"width": f"{w}in", "height": f"{h}in", "viewBox": f"0 0 {w} {h}",
                                      "version": "1.1"})
    root.append(ET.fromstring(SVG_DEFS))
    edges = []
    projections = {}  # the page's views with the same camera share their projections
    for i, vp in enumerate(fig.viewports):
        project, scale, point = _viewport_projection(vp, projections)
        x, y, vw, vh = vp.rect
        clip = ET.SubElement(root, f"{SVGNS}clipPath", {"id": f"vp{i}"})
        ET.SubElement(clip, f"{SVGNS}rect", {"x": f"{x}", "y": f"{y}", "width": f"{vw}", "height": f"{vh}"})
        cx, cy = x + vw / 2 + vp.offset[0], y + vh / 2 + vp.offset[1]
        tx, ty = point(vp.target)
        g = ET.SubElement(root, f"{SVGNS}g", {"clip-path": f"url(#vp{i})"})
        inner = ET.SubElement(g, f"{SVGNS}g", {
            "transform": f"translate({cx:.4f},{cy:.4f}) scale({scale:.6f},{-scale:.6f}) translate({-tx:.4f},{-ty:.4f})",
            "fill": "none", "stroke": "black", "stroke-linecap": "round"})
        # the parts of the page's other views with this camera hide what's
        # behind them here too (LayOut stacked such views; the part drawn in
        # black on top hid the gray view's lines behind it)
        occluders = [p[0] for other in fig.viewports if other is not vp and _same_camera(other, vp) for p in other.parts]
        for style, visible in _page_edges(vp, project, occluders).items():
            edges += [(e, style) for e in visible]
            color = fig.light if style == "hlr_light" and fig.light else PAGE_COLORS.get(style, "black")
            layer = ET.SubElement(inner, f"{SVGNS}g", {"stroke-width": f"{PAGE_LINES[style] / scale:.5f}",
                                                       "stroke": color})
            layer.extend(_edge_elements(visible))
        def page_point(p):
            q = point(p)
            if q is None:
                return None
            return (cx + (q[0] - tx) * scale, cy - (q[1] - ty) * scale)
        from model.notes import Icon
        persons = []
        for px, py, pz, note in vp.notes:
            at = page_point((px, py, pz))
            if at:
                for el, _ in _note_svg(at[0], at[1], note, PAGE_UNIT, PAGE_FONT):
                    root.append(el)
                if isinstance(note, Icon) and note.name == "ptu_person":
                    persons.append(((px, py, pz), at, note))
        if persons:
            _occlude_persons(root, g, i, vp, persons, page_point)
    for x, y, note in fig.notes:
        for el, _ in _note_svg(x, y, note, PAGE_UNIT, PAGE_FONT):
            root.append(el)
    if fig.border:  # a hairline just inside the page's edge
        b = fig.border
        ET.SubElement(root, f"{SVGNS}rect", {"x": f"{b / 2:.4f}", "y": f"{b / 2:.4f}", "width": f"{w - b:.4f}",
                                             "height": f"{h - b:.4f}", "fill": "none", "stroke": "black",
                                             "stroke-width": f"{b:.4f}"})
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.ElementTree(root).write(path, xml_declaration=True, encoding="utf-8")
    return edges


PERSON_RAYS = (5, 9)  # rays through a silhouette's box (across, down), to find what's in front of it
PERSON_DEPTH_TOLERANCE = 1  # model inches: what's this close to a silhouette's plane doesn't hide it


def _occlude_persons(root, lines, i, vp, persons, page_point):
    """The crew's silhouettes (icons at points of the model, drawn over the
    lines) are hidden by the parts in front of them. A solid is in front of
    a silhouette when a ray from the eye through its box meets the solid
    before reaching the silhouette's plane; such a solid's projected outline,
    filled white, goes over the icon, and the view's lines go over that
    again, within those outlines."""
    import copy
    import numpy as np
    from build123d import Vector
    from OCP.gp import gp_Dir, gp_Lin, gp_Pnt
    from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
    eye = Vector(*vp.eye)
    fwd = (Vector(*vp.target) - eye).normalized()
    far = 1e4
    for k, (p, (ax, ay), note) in enumerate(persons):
        p = Vector(*p)
        x0, x1 = ax + note.dx - note.width / 2, ax + note.dx + note.width / 2
        y0, y1 = ay - note.dy - note.height / 2, ay - note.dy + note.height / 2
        # model offsets for page offsets at the silhouette (its plane faces the eye)
        J = np.array([[page_point((p.X + dx, p.Y + dy, p.Z + dz))[j] - (ax, ay)[j] for dx, dy, dz in ((1, 0, 0), (0, 1, 0), (0, 0, 1))] for j in (0, 1)])
        back = np.linalg.pinv(J)
        samples = []
        for u in np.linspace(x0, x1, PERSON_RAYS[0] + 2)[1:-1]:
            for v in np.linspace(y0, y1, PERSON_RAYS[1] + 2)[1:-1]:
                q = p + Vector(*(back @ np.array([u - ax, v - ay])))
                if vp.fov is None:
                    samples.append((q - fwd * far, fwd, far - PERSON_DEPTH_TOLERANCE))
                else:
                    d = q - eye
                    samples.append((eye, d.normalized(), d.length - PERSON_DEPTH_TOLERANCE))
        polys = []
        for shape, *_ in vp.parts:
            for s in shape.solids():
                b = s.bounding_box()
                corners = [page_point((x, y, z)) for x in (b.min.X, b.max.X) for y in (b.min.Y, b.max.Y) for z in (b.min.Z, b.max.Z)]
                corners = [q for q in corners if q]
                if len(corners) < 3 or max(q[0] for q in corners) < x0 or min(q[0] for q in corners) > x1 or max(q[1] for q in corners) < y0 or min(q[1] for q in corners) > y1:
                    continue
                inter = IntCurvesFace_ShapeIntersector()
                inter.Load(s.wrapped, 1e-6)
                hit = False
                for o, d, limit in samples:
                    inter.Perform(gp_Lin(gp_Pnt(o.X, o.Y, o.Z), gp_Dir(d.X, d.Y, d.Z)), 0, limit)
                    if inter.IsDone() and inter.NbPnt() > 0:
                        hit = True
                        break
                if not hit:
                    continue
                pts = [page_point(tuple(v)) for v in s.vertices()] if len(s.vertices()) >= 4 else corners
                polys.append(_hull([q for q in pts if q]))
        if not polys:
            continue
        clip = ET.SubElement(root, f"{SVGNS}clipPath", {"id": f"person{i}_{k}"})
        ET.SubElement(clip, f"{SVGNS}rect", {"x": f"{x0:.4f}", "y": f"{y0:.4f}", "width": f"{x1 - x0:.4f}", "height": f"{y1 - y0:.4f}"})
        grp = ET.SubElement(root, f"{SVGNS}g", {"clip-path": f"url(#person{i}_{k})"})
        hulls = ET.SubElement(root, f"{SVGNS}clipPath", {"id": f"person{i}_{k}_front", "clip-path": f"url(#person{i}_{k})"})
        for poly in polys:
            points = " ".join(f"{x:.4f},{y:.4f}" for x, y in poly)
            ET.SubElement(grp, f"{SVGNS}polygon", {"points": points, "fill": "white", "stroke": "none"})
            ET.SubElement(hulls, f"{SVGNS}polygon", {"points": points})
        again = copy.deepcopy(lines)
        again.set("clip-path", f"url(#person{i}_{k}_front)")
        root.append(again)


def _hull(pts):
    """The convex hull of 2D points (monotone chain), counterclockwise."""
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts
    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2 and (out[-1][0] - out[-2][0]) * (q[1] - out[-2][1]) - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0]) <= 0:
                out.pop()
            out.append(q)
        return out
    lower, upper = half(pts), half(reversed(pts))
    return lower[:-1] + upper[:-1]


def _same_camera(a, b):
    return (a.eye, a.target, a.up, a.height, a.fov) == (b.eye, b.target, b.up, b.height, b.fov)


def _page_edges(vp, project, occluders=()):
    """{style: visible edges} of a viewport's parts, every part (and every
    occluder, which isn't drawn) hiding what's behind it whatever its style,
    as SketchUp drew them: all the parts are projected together, and each
    visible edge is given the style of the part it lies on (the style whose
    parts, projected alone, come nearest its midpoint; the first such style
    on a tie)."""
    by_style = {}
    for shape, style, *_ in vp.parts:
        by_style.setdefault(style, []).append(shape)
    if occluders:
        by_style[None] = list(occluders)
    if len(by_style) == 1:
        style, shapes = next(iter(by_style.items()))
        return {style: project(shapes)}
    alone = {style: _Nearest(project(shapes)) for style, shapes in by_style.items()}
    out = {style: [] for style in by_style if style is not None}
    for e in project([s for shapes in by_style.values() for s in shapes]):
        mid = _positions(e, (0.5,))[0]
        best, best_distance = None, math.inf
        for style, near in alone.items():
            d = near.distance(mid, best_distance)
            if d < best_distance:
                best, best_distance = style, d
        if best is not None:
            out[best].append(e)
    return out


NEAREST_SLACK = 1e-6  # drawing units: how far a lower bound may understate a distance


class _Nearest:
    """The least distance from a point to any of some edges (build123d's
    distance_to, i.e. OpenCASCADE's extrema), computed only for the edges
    that can be the nearest: every edge first gets a cheap lower bound on
    its distance (a line's exact segment distance, a curve's bounding box,
    for all the edges at once), and the exact distance is found in order of
    those, stopping once the bound can't beat what's been found."""

    def __init__(self, edges):
        import numpy as np
        from OCP.Bnd import Bnd_Box
        from OCP.BRepBndLib import BRepBndLib
        self.edges = edges
        n = len(edges)
        self.a, self.b = np.zeros((n, 3)), np.zeros((n, 3))  # lines: their ends
        self.lo, self.hi = np.zeros((n, 3)), np.zeros((n, 3))  # every edge: its box
        self.line = np.zeros(n, dtype=bool)
        for i, e in enumerate(edges):
            if e.geom_type.name == "LINE":
                self.a[i], self.b[i] = _positions(e, (0, 1))
                self.lo[i], self.hi[i] = np.minimum(self.a[i], self.b[i]), np.maximum(self.a[i], self.b[i])
                self.line[i] = True
            else:
                box = Bnd_Box()
                BRepBndLib.Add_s(e.wrapped, box, True)
                lo, hi = box.CornerMin(), box.CornerMax()
                self.lo[i], self.hi[i] = (lo.X(), lo.Y(), lo.Z()), (hi.X(), hi.Y(), hi.Z())
        self.ab = self.b - self.a
        self.ab2 = np.maximum((self.ab * self.ab).sum(1), 1e-300)

    def distance(self, point, limit=math.inf):
        """The least distance from `point` (x, y, z) to the edges if it's
        under `limit` (otherwise some distance that isn't); 1e9 if there are
        no edges."""
        import numpy as np
        if not self.edges:
            return 1e9
        p = np.array(point)
        gap = np.maximum(np.maximum(self.lo - p, p - self.hi), 0)
        bound = np.sqrt((gap * gap).sum(1))
        if self.line.any():
            ap = p - self.a[self.line]
            ab = self.ab[self.line]
            t = np.clip((ap * ab).sum(1) / self.ab2[self.line], 0, 1)
            off = ap - t[:, None] * ab
            bound[self.line] = np.maximum(bound[self.line], np.sqrt((off * off).sum(1)))
        bound -= NEAREST_SLACK
        best = 1e9
        for i in np.argsort(bound, kind="stable"):
            if bound[i] >= min(best, limit):
                break
            d = self.edges[i].distance_to(point)
            if d < best:
                best = d
        return best


def _nudge(p):
    return (p[0] + 1e-3, p[1], p[2])


def _viewport_projection(vp, shared=None):
    """(project(shapes) -> visible edges in the view's plane, page inches per
    unit of those edges, point(p) -> where a point of the model lands in that
    plane, or None). `shared`, a dict, caches projections across the views of
    a page that share a camera (a view's parts occlude the others' too)."""
    from build123d import Compound, Edge, Vector
    from OCP.gp import gp_Ax1, gp_Ax2, gp_Pnt, gp_Pnt2d
    from OCP.HLRAlgo import HLRAlgo_Projector
    eye, target, up = vp.eye, vp.target, vp.up
    fwd = _unit([t - e for t, e in zip(target, eye)])
    d = math.dist(eye, target)
    if vp.fov is None:  # parallel: look along fwd from far off
        origin, focus = tuple(t - 1e5 * f for t, f in zip(target, fwd)), None
    else:
        focus = d / 2
        origin = tuple(e + focus * f for e, f in zip(eye, fwd))

    def hlr(shapes):
        return _ordered(Compound(shapes).project_to_viewport(origin, up, target, focus=focus)[0])

    camera = (origin, up, target, focus)

    def project(shapes):
        if shared is None:
            return hlr(shapes)
        k = (camera, tuple(id(s) for s in shapes))
        if k not in shared:
            shared[k] = hlr(shapes)
        return shared[k]

    # The projector build123d's project_to_viewport makes for this camera,
    # to project points with directly: it puts a point where the projection
    # of a tiny edge from it lands (bit for bit, checked across views; a
    # parallel view's are all offset by one constant, measured below).
    viewport_origin, look_at = Vector(origin), Vector(target)
    axes = gp_Ax2()
    axes.SetAxis(gp_Ax1(viewport_origin.to_pnt(), (viewport_origin - look_at).normalized().to_dir()))
    axes.SetYDirection(Vector(up).normalized().to_dir())
    projector = HLRAlgo_Projector(axes, focus) if focus else HLRAlgo_Projector(axes)

    def projected(p):
        q = gp_Pnt2d()
        projector.Project(gp_Pnt(*p), q)
        return q.X(), q.Y()

    def by_edge(p):
        """The old way: the projection of a tiny edge from p, which the
        hidden-line algorithm drops when it's seen end-on."""
        e = hlr([Edge.make_line(p, _nudge(p))])
        if not e:
            return None
        q = e[0].position_at(0)
        return q.X, q.Y
    anchor = by_edge(target)
    offset = (anchor[0] - projected(target)[0], anchor[1] - projected(target)[1])

    def point(p):
        a = projected(p)
        if math.dist(a, projected(_nudge(p))) < DEGENERATE_EDGE:
            return by_edge(p)  # let the hidden-line algorithm decide, as before
        return a[0] + offset[0], a[1] + offset[1]

    if vp.fov is None:
        return project, vp.rect[3] / vp.height, point
    # how long a unit across the view at the target comes out
    side = _unit(_cross(fwd, up))
    probe = hlr([Edge.make_line(target, tuple(t + s for t, s in zip(target, side)))])
    per_unit = probe[0].length if probe else 1
    seen = 2 * d * math.tan(math.radians(vp.fov) / 2)  # model inches top to bottom at the target
    return project, vp.rect[3] / (seen * per_unit), point


DEGENERATE_EDGE = 1e-5  # a projected edge shorter than this may be dropped by the hidden-line algorithm (it drops 1e-8, keeps 1e-6)


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _edge_elements(edges):
    """SVG paths for projected edges (in the view plane's coordinates)."""
    out = []
    for e in edges:
        n = 2 if e.geom_type.name == "LINE" else max(4, min(48, int(_length(e) * 4)))
        pts = _positions(e, [i / (n - 1) for i in range(n)])
        d = "M " + " L ".join(f"{x:.3f} {y:.3f}" for x, y, _ in pts)
        out.append(ET.Element(f"{SVGNS}path", {"d": d}))
    return out


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def _hex(rgb):
    return "#%02x%02x%02x" % rgb


def _add_notes(path, notes, size=None, margin=MARGIN, unit=1):
    """Add the notes and the pattern fills, fit the view box (the drawing's
    geometry and notes plus `margin`, in drawing units, all around or (left,
    top, right, bottom)), and set the printed size."""
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.parse(path)
    root = tree.getroot()
    root.insert(0, ET.fromstring(SVG_DEFS))
    for g in root.iter(f"{SVGNS}g"):
        name = (g.get("id") or "").removeprefix("fill_")
        if name in FILLS:
            g.set("fill", FILLS[name])
    vx, vy, vw, vh = map(float, root.get("viewBox").split())
    box = [vx, vy, vx + vw, vy + vh]
    group = ET.SubElement(root, f"{SVGNS}g", {"id": "notes"})
    for x, y, note in notes:
        for el, bb in _note_svg(x, -y, note, unit):
            group.append(el)
            box = [min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3])]
    ml, mt, mr, mb = margin if isinstance(margin, tuple) else (margin,) * 4
    vx, vy, vw, vh = box[0] - ml, box[1] - mt, box[2] - box[0] + ml + mr, box[3] - box[1] + mt + mb
    root.set("viewBox", f"{vx:.3f} {vy:.3f} {vw:.3f} {vh:.3f}")
    if isinstance(size, dict):  # {"width": inches}
        w = size["width"]
        h = w * vh / vw
    else:  # inches on paper per inch of drawing (default: full size)
        w, h = vw * (size or 1), vh * (size or 1)
    root.set("width", f"{w:.3f}in")
    root.set("height", f"{h:.3f}in")
    tree.write(path, xml_declaration=True, encoding="utf-8")


_ICONS = {}


def _icon_href(name):
    if name not in _ICONS:
        _ICONS[name] = "data:image/png;base64," + base64.b64encode((CLIPART / f"{name}.png").read_bytes()).decode()
    return _ICONS[name]


_ANCHOR = {1: ("start", 0), 2: ("middle", 0), 3: ("end", 0), 4: ("start", 0.5), 5: ("middle", 0.5),
           6: ("end", 0.5), 7: ("start", 1), 8: ("middle", 1), 9: ("end", 1)}

_FONTS = {}


def _font(font, bold=False):
    """(PIL font at size 1000, its ascent, its cap height as a fraction of
    the font size, glyph(ch) -> (advance, left bearing, right extent) in em)
    of a font (family, regular file, bold file), regular or bold."""
    path = font[2] if bold else font[1]
    if path not in _FONTS:
        from PIL import ImageFont
        from fontTools.ttLib import TTFont
        # Basic layout (no kerning) whether or not Pillow finds libraqm on
        # this machine, so the measurements, and the frames fitted to them,
        # are the same everywhere.
        f = ImageFont.truetype(str(path), 1000, layout_engine=ImageFont.Layout.BASIC)
        ascent = f.getmetrics()[0]
        tt = TTFont(str(path))
        cmap, glyf, hmtx, upm = tt.getBestCmap(), tt["glyf"], tt["hmtx"], tt["head"].unitsPerEm

        def glyph(ch):
            g = cmap.get(ord(ch)) or cmap.get(ord("?"))
            adv, lsb = hmtx[g]
            return adv / upm, lsb / upm, getattr(glyf[g], "xMax", adv) / upm
        _FONTS[path] = (f, ascent, (ascent - f.getbbox("H")[1]) / 1000, glyph)
    return _FONTS[path]


def _text_extent(line, size, font, bold=False):
    """(advance width, ink above the baseline, ink below it, ink left, ink
    right) of a line at font size `size`, in drawing units, from the pen's
    origin: what typst draws, so a figure's frame fits its labels exactly
    and they can be anchored by their ink (as QCAD anchored MTEXT)."""
    f, ascent, _, glyphs = _font(font, bold)
    if not line.strip():
        return f.getlength(line) * size / 1000, 0, 0, 0, f.getlength(line) * size / 1000
    _, top, _, bottom = f.getbbox(line)
    adv = f.getlength(line) * size / 1000
    first, last = glyphs(line[0]), glyphs(line[-1])
    left = first[1] * size
    right = adv - (last[0] - last[2]) * size
    return adv, (ascent - top) * size / 1000, (bottom - ascent) * size / 1000, left, right


def _bold_pieces(line, size, bold):
    """A line as (text, size, bold) pieces: all bold, none, or the words in
    `bold` (a tuple of substrings) set bold."""
    if bold is True or not bold:
        return [(line, size, bool(bold))]
    pieces, rest = [], line
    while rest:
        hits = [(rest.index(w), w) for w in bold if w in rest]
        if not hits:
            pieces.append((rest, size, False))
            break
        i, w = min(hits)
        if i:
            pieces.append((rest[:i], size, False))
        pieces.append((w, size, True))
        rest = rest[i + len(w):]
    return pieces


def _rotated_box(x0, y0, x1, y1, cx, cy, degrees):
    """The bounds of a box rotated by SVG's rotate(degrees, cx, cy)."""
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    pts = [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c)
           for x in (x0, x1) for y in (y0, y1)]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def _note_svg(x, y, note, unit=1, font=DRAWING_FONT):
    """SVG elements for a note at SVG coordinates (x, y), with its bounds.
    Line weights are for drawings in model inches; `unit` scales them (for a
    drawing's line weight, or a page in paper inches); arrowheads are sized
    for a page when `unit` is a page's."""
    head = unit if unit == PAGE_UNIT else 1
    from model.notes import Circle, Icon, Label, Leader, Lines
    if isinstance(note, Icon):
        cx, cy = x + note.dx, y - note.dy
        g = ET.Element(f"{SVGNS}g", {"transform": f"translate({cx:.3f},{cy:.3f}) rotate({-note.rotation:.1f})"
                                                  + (" scale(-1,1)" if note.flip else "")})
        ET.SubElement(g, f"{SVGNS}image", {"href": _icon_href(note.name), "x": f"{-note.width / 2:.3f}",
                                            "y": f"{-note.height / 2:.3f}", "width": f"{note.width:.3f}",
                                            "height": f"{note.height:.3f}", "preserveAspectRatio": "none"})
        w, h = note.width / 2, note.height / 2
        return [(g, _rotated_box(cx - w, cy - h, cx + w, cy + h, cx, cy, -note.rotation))]
    if isinstance(note, Label):
        anchor, frac = _ANCHOR[note.attach]
        cap = _font(font)[2]
        # each line: its pieces (text, font size, bold)
        if note.runs:
            lines = [[(r[0], r[1] / cap, bool(r[2]) if len(r) > 2 else note.bold is True) for r in note.runs]]
        else:
            lines = [_bold_pieces(line, note.height / cap, note.bold) for line in note.text.split("\n")]
        tx, ty = x + note.dx, y - note.dy
        gap = note.height * 5 / 3  # MTEXT line spacing
        total = note.height + gap * (len(lines) - 1)  # cap top of the first line to baseline of the last
        top = ty - frac * total  # top of the text block
        g = ET.Element(f"{SVGNS}g", {"transform": f"rotate({-note.rotation:.1f},{tx:.3f},{ty:.3f})"})
        t = ET.SubElement(g, f"{SVGNS}text", {"x": f"{tx:.3f}", "y": f"{top + note.height:.3f}", "font-family": font[0],
                                               "fill": "black", "{http://www.w3.org/XML/1998/namespace}space": "preserve"})
        box = None
        for i, pieces in enumerate(lines):
            # the line's ink, from its pen origin, to anchor it as MTEXT is (by its ink, not its advance)
            extents = [_text_extent(s, size, font, bold) for s, size, bold in pieces]
            adv = sum(e[0] for e in extents)
            left, right = extents[0][3], adv - extents[-1][0] + extents[-1][4]
            x0 = tx - {"start": left, "middle": (left + right) / 2, "end": right}[anchor]
            for j, ((s, size, bold), e) in enumerate(zip(pieces, extents)):
                attrs = {"font-size": f"{size:.3f}"}
                if bold:
                    attrs["font-weight"] = "bold"
                if j == 0:
                    attrs["x"] = f"{x0:.3f}"
                    attrs["dy"] = "0" if i == 0 else f"{gap:.3f}"
                span = ET.SubElement(t, f"{SVGNS}tspan", attrs)
                span.text = s
            y0 = top + note.height - max(e[1] for e in extents) if i == 0 else box[1]
            y1 = top + note.height + gap * i + max(e[2] for e in extents)
            b = (x0 + left, y0, x0 + right, y1)
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
        return [(g, _rotated_box(*box, tx, ty, -note.rotation))]
    if isinstance(note, Lines):
        ox, oy = x + note.dx, y - note.dy
        pts = [(ox + a, oy - b) for seg in note.segments for a, b in seg]
        d = " ".join(f"M {ox + a0:.3f} {oy - b0:.3f} L {ox + a1:.3f} {oy - b1:.3f}" for (a0, b0), (a1, b1) in note.segments)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return [(ET.Element(f"{SVGNS}path", {"d": d, "fill": "none", "stroke": _hex(note.color),
                                              "stroke-width": f"{LINE * unit * note.weight / 2:.4f}"}),
                 (min(xs), min(ys), max(xs), max(ys)))]
    if isinstance(note, Circle):
        cx, cy, r = x + note.dx, y - note.dy, note.radius
        fill = "none" if note.fill is None else _hex(note.fill)
        return [(ET.Element(f"{SVGNS}circle", {"cx": f"{cx:.3f}", "cy": f"{cy:.3f}", "r": f"{r:.3f}", "fill": fill,
                                                "stroke": "black", "stroke-width": f"{LINE * unit * note.weight:.4f}"}),
                 (cx - r, cy - r, cx + r, cy + r))]
    if isinstance(note, Leader):
        pts = [(x + note.dx, y - note.dy)] + [(x + note.dx + px, y - note.dy - py) for px, py in note.points]
        d = "M " + " L ".join(f"{a:.3f} {b:.3f}" for a, b in pts)
        els = [ET.Element(f"{SVGNS}path", {"d": d, "fill": "none", "stroke": _hex(note.color),
                                           "stroke-width": f"{LINE * unit * note.weight:.4f}"})]
        if note.arrow and len(pts) > 1:
            (ax, ay), (bx, by) = pts[0], pts[1]
            L = math.hypot(bx - ax, by - ay) or 1
            ux, uy = (bx - ax) / L, (by - ay) / L
            s = 1.2 * head * note.weight ** 0.5 * note.head
            p1 = (ax + ux * s - uy * s * 0.3, ay + uy * s + ux * s * 0.3)
            p2 = (ax + ux * s + uy * s * 0.3, ay + uy * s - ux * s * 0.3)
            els.append(ET.Element(f"{SVGNS}path", {"d": f"M {ax:.3f} {ay:.3f} L {p1[0]:.3f} {p1[1]:.3f} "
                                                        f"L {p2[0]:.3f} {p2[1]:.3f} Z", "fill": _hex(note.color)}))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return [(el, (min(xs), min(ys), max(xs), max(ys))) for el in els]
    return []


if __name__ == "__main__":
    main(sys.argv[1:])
