#!/usr/bin/env python3
"""Look at the model, or at a manual's figure, in an interactive 3D viewer
while editing the Python that defines it.

  ./render/view.py roof-blocking/vent_guide_board      a figure's parts, seen from its camera
  ./render/view.py 'post_tilt_up.ladders("right")'     what a model expression makes
  ./render/view.py --watch roof-blocking/vent_guide_board
                                                       ...and again every time common/model changes

A figure is named as the manuals embed it (manual/figure, see
model/figures/__init__.py FIGURES); it's shown with its parts colored by
their drawing style (gray, see-through context; the rest solid), and the
viewer's camera put where the figure's is. Anything else is a Python
expression evaluated with every model module imported by its name
(post_tilt_up, roof, house, ...): a shape, a component, or a list of
(component, placement, mods) entries as the model's placement functions
return them.

The viewer is the OCP CAD Viewer, which draws build123d parts in a browser
tab and takes new parts over a local socket. Install and start it once:

    uv pip install ocp_viewer           (in the same venv as build123d)
    python -m ocp_viewer                then open http://localhost:3939

(VS Code users can instead install its "OCP CAD Viewer" extension, which
opens the same viewer inside VS Code and provides the `ocp_vscode` package
this script also accepts.) Orbit, zoom, clip, explode and measure in the
viewer; --watch keeps the camera where you left it between shows.

--dry-run lists what would be shown instead of showing it (no viewer
needed): handy for checking a figure's parts and camera.
"""

import argparse
import importlib
import os
import pathlib
import pkgutil
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "common"))

FIGURE = re.compile(r"^([a-z0-9_-]+)/([a-z0-9_.-]+)$")  # manual/figure, as model2svg's REF

# A drawing style's look in the viewer: (color, opacity); None: the viewer's own palette
LOOKS = {
    "context": ("#9a9a9a", 0.35),
    "jig": ("#c8c8c8", 0.5),
    "covered": ("#6a6a6a", 0.6),
    "bare": ("#e0e0e0", 0.3),
    "hlr_light": ("#9a9a9a", 0.35),
}
WATCH_EVERY = 1.0  # seconds between looks at the model's files


def model_namespace():
    """{name: module} for every model module, and the model package itself."""
    import model
    ns = {"model": model}
    for info in pkgutil.iter_modules(model.__path__):
        ns[info.name] = importlib.import_module(f"model.{info.name}")
    return ns


def placed(entry):
    """A shape for a (component, placement, mods) entry (what the model's
    placement functions return), a (component, placement) pair, a component
    or a shape; (name, shape)."""
    from model.common import key
    if isinstance(entry, tuple) and len(entry) in (2, 3) and hasattr(entry[0], "shape"):
        comp, loc = entry[0], entry[1]
        mods = entry[2] if len(entry) == 3 else []
        return comp.__name__, loc * comp.shape(frozenset(), key(mods))
    if hasattr(entry, "shape") and callable(entry.shape):
        return entry.__name__, entry.shape()
    return type(entry).__name__, entry


def expression_parts(text):
    """[(name, shape, color, alpha)] for what a model expression makes."""
    value = eval(text, model_namespace())  # noqa: S307 (the user's own code)
    entries = list(value) if isinstance(value, (list, tuple)) and not (len(value) in (2, 3) and hasattr(value[0], "shape")) else [value]
    out = []
    for i, entry in enumerate(entries, 1):
        name, shape = placed(entry)
        out.append((f"{i:02d} {name}", shape, None, None))
    return out


def figure_parts(ref):
    """[(name, shape, color, alpha)] for a figure's parts, and its camera
    ((eye, target), or None for the viewer's default)."""
    from model.figures import manual_figures
    sys.path.insert(0, str(HERE))
    import model2svg
    manual, name = FIGURE.match(ref).groups()
    figs = manual_figures(manual, {name})
    if name not in figs:
        sys.exit(f"view: no figure {ref}; see model/figures/__init__.py FIGURES")
    fig = figs[name]
    viewports = fig.viewports if fig.page else [None]
    out, camera, seen = [], None, set()
    for i, vp in enumerate(viewports, 1):
        parts = vp.parts if vp else fig.parts
        for j, part in enumerate(parts, 1):
            shape, style = part[0], part[1]
            if id(shape) in seen:
                continue
            seen.add(id(shape))
            color, alpha = LOOKS.get(style, (None, None))
            label = f"v{i} {j:02d} {style}" if vp else f"{j:02d} {style}"
            out.append((label, shape, color, alpha))
        if vp and camera is None:  # the first view's camera
            fitted = model2svg._fitted(vp)
            if fitted.eye is not None and fitted.target is not None:
                camera = (tuple(fitted.eye), tuple(fitted.target))
    return out, camera


def show_parts(parts, camera, keep_camera, port):
    try:
        from ocp_viewer import Camera, show  # the standalone viewer
    except ImportError:
        try:
            from ocp_vscode import Camera, show  # VS Code's
        except ImportError:
            sys.exit("view: no viewer package: `uv pip install ocp_viewer` (or VS Code's OCP CAD Viewer extension)")
    kw = {}
    if port:
        kw["port"] = port
    if keep_camera:
        kw["reset_camera"] = Camera.KEEP
    elif camera:
        kw["position"], kw["target"] = camera
        kw["reset_camera"] = Camera.RESET
    shapes = [p[1] for p in parts]
    show(*shapes, names=[p[0] for p in parts], colors=[p[2] for p in parts], alphas=[p[3] for p in parts],
         ortho=False, black_edges=True, **kw)


def describe(parts, camera):
    for name, shape, color, alpha in parts:
        bb = shape.bounding_box()
        print(f"  {name:28s} {color or '-':8s} {alpha if alpha is not None else '-':<5} "
              f"({bb.min.X:.1f}, {bb.min.Y:.1f}, {bb.min.Z:.1f}) to ({bb.max.X:.1f}, {bb.max.Y:.1f}, {bb.max.Z:.1f})")
    if camera:
        print(f"  camera: eye {tuple(round(c, 1) for c in camera[0])}, target {tuple(round(c, 1) for c in camera[1])}")


def model_files():
    return sorted(p for p in (REPO / "common" / "model").rglob("*.py")) + [HERE / "view.py"]


def mtimes():
    return {p: p.stat().st_mtime for p in model_files()}


def once(targets, keep_camera, port, dry_run):
    for target in targets:
        if FIGURE.match(target):
            parts, camera = figure_parts(target)
        else:
            parts, camera = expression_parts(target), None
        print(f"view: {target}: {len(parts)} parts", file=sys.stderr)
        if dry_run:
            describe(parts, camera)
        else:
            show_parts(parts, camera, keep_camera, port)
        keep_camera = True  # the next target of the same run keeps the camera


def watch(args):
    """Show, then show again (keeping the camera) each time a model file
    changes: in a fresh process each time, so every module reloads."""
    cmd = [sys.executable, str(HERE / "view.py")] + [a for a in args if a != "--watch"]
    seen = mtimes()
    subprocess.run(cmd)
    cmd.append("--keep-camera")
    print("view: watching common/model (Ctrl-C to stop)", file=sys.stderr)
    while True:
        time.sleep(WATCH_EVERY)
        now = mtimes()
        if now != seen:
            seen = now
            changed = [p.name for p in now if p not in seen or now[p] != seen.get(p)]
            print(f"view: changed: {' '.join(changed) or 'files'}", file=sys.stderr)
            subprocess.run(cmd)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("targets", nargs="+", metavar="FIGURE|EXPR", help="manual/figure, or a model expression")
    ap.add_argument("--watch", action="store_true", help="show again whenever common/model changes")
    ap.add_argument("--keep-camera", action="store_true", help="leave the viewer's camera where it is")
    ap.add_argument("--port", type=int, help="the viewer's port, if not its default")
    ap.add_argument("--dry-run", action="store_true", help="list the parts and the camera instead of showing them")
    a = ap.parse_args(argv)
    if a.watch:
        watch(argv)
    else:
        os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
        once(a.targets, a.keep_camera, a.port, a.dry_run)


if __name__ == "__main__":
    main(sys.argv[1:])
