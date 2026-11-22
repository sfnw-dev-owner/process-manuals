#!/usr/bin/env python3
"""See what a change to the model did to the manuals' figures.

Renders every figure the manuals embed (through render/model2svg.py), draws
each SVG to a PNG, and compares two such snapshots, writing a side-by-side
picture of every figure that changed. Runs inside the renderer container
(like model2svg.py), from the repo root:

  figdiff.py snapshot DIR            render every figure; its PNG (and SVG) go in DIR
  figdiff.py compare BEFORE AFTER OUT  for each figure that differs between the
                                     two snapshot DIRs, OUT/<figure>.png: the
                                     old and new side by side, and a summary in
                                     OUT/README.md

The PNGs come from a small rasterizer here (lines, arcs, circles, fills,
labels in the figures' fonts, clipped views, icons), good enough to spot
what moved; the SVGs are what the manuals get.
"""

import base64
import io
import math
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import model2svg  # noqa: E402

NS = "{http://www.w3.org/2000/svg}"
XLINK = "{http://www.w3.org/1999/xlink}href"
PIXELS = 1600  # across the longer side of a figure
FONTS = {  # family -> (regular, bold)
    "DejaVu Sans": (HERE / "DejaVu" / "DejaVuSans.ttf", HERE / "DejaVu" / "DejaVuSans-Bold.ttf"),
    "Carlito": (HERE / "Carlito" / "Carlito-Regular.ttf", HERE / "Carlito" / "Carlito-Bold.ttf"),
}


# ── snapshot ───────────────────────────────────────────────────────────────

def snapshot(out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(HERE / "model2svg.py"), "--all"], check=True)
    figures = model2svg.manuals_figures()
    seen = set()
    for fig, (svg, _) in sorted(model2svg.plan(figures).items()):
        name = fig.split("@")[0].replace("/", "-")  # (a figure embedded at two scales: its first)
        if name in seen:
            continue
        seen.add(name)
        (out / f"{name}.svg").write_bytes(svg.read_bytes())
        rasterize(svg, out / f"{name}.png")
        print(f"figdiff: {name}", file=sys.stderr)


# ── compare ────────────────────────────────────────────────────────────────

def compare(before, after, out):
    before, after, out = pathlib.Path(before), pathlib.Path(after), pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    names = sorted({p.stem for p in before.glob("*.png")} | {p.stem for p in after.glob("*.png")})
    rows = []
    for name in names:
        a, b = before / f"{name}.png", after / f"{name}.png"
        if not a.exists():
            rows.append((name, "new"))
            Image.open(b).save(out / f"{name}.png")
            continue
        if not b.exists():
            rows.append((name, "gone"))
            Image.open(a).save(out / f"{name}.png")
            continue
        ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
        if ia.size == ib.size and ia.tobytes() == ib.tobytes():
            continue
        rows.append((name, f"{differing_pixels(ia, ib)} px differ" if ia.size == ib.size else f"size {ia.size} -> {ib.size}"))
        side_by_side(ia, ib).save(out / f"{name}.png")
    with open(out / "README.md", "w") as f:
        f.write(f"# {len(rows)} of {len(names)} figures changed\n\n")
        for name, what in rows:
            f.write(f"- [{name}]({name}.png): {what}\n")
    print(f"figdiff: {len(rows)} of {len(names)} figures changed; see {out / 'README.md'}", file=sys.stderr)


def differing_pixels(a, b):
    import numpy as np
    return int((np.asarray(a) != np.asarray(b)).any(axis=2).sum())


def side_by_side(a, b, gap=20):
    """The old picture on the left, the new on the right, each boxed, at the same scale."""
    h = max(a.height, b.height)
    out = Image.new("RGB", (a.width + b.width + 3 * gap, h + 2 * gap), (200, 200, 200))
    out.paste(a, (gap, gap))
    out.paste(b, (2 * gap + a.width, gap))
    d = ImageDraw.Draw(out)
    d.rectangle([gap - 1, gap - 1, gap + a.width, gap + a.height], outline=(120, 0, 0))
    d.rectangle([2 * gap + a.width - 1, gap - 1, 2 * gap + a.width + b.width, gap + b.height], outline=(0, 100, 0))
    return out


# ── the rasterizer ─────────────────────────────────────────────────────────

def _mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _apply(m, x, y):
    return (m[0][0] * x + m[0][1] * y + m[0][2], m[1][0] * x + m[1][1] * y + m[1][2])


def _scale_of(m):
    """How much a transform magnifies lengths (the geometric mean of its axes)."""
    return math.sqrt(abs(m[0][0] * m[1][1] - m[0][1] * m[1][0])) or 1


def _transform(s):
    m = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for name, args in re.findall(r"(\w+)\(([^)]*)\)", s or ""):
        a = [float(v) for v in re.split(r"[ ,]+", args.strip()) if v]
        if name == "translate":
            t = [[1, 0, a[0]], [0, 1, a[1] if len(a) > 1 else 0], [0, 0, 1]]
        elif name == "scale":
            t = [[a[0], 0, 0], [0, a[1] if len(a) > 1 else a[0], 0], [0, 0, 1]]
        elif name == "rotate":
            th = math.radians(a[0])
            c, s_ = math.cos(th), math.sin(th)
            t = [[c, -s_, 0], [s_, c, 0], [0, 0, 1]]
            if len(a) == 3:
                cx, cy = a[1], a[2]
                t = _mul([[1, 0, cx], [0, 1, cy], [0, 0, 1]], _mul(t, [[1, 0, -cx], [0, 1, -cy], [0, 0, 1]]))
        elif name == "matrix":
            t = [[a[0], a[2], a[4]], [a[1], a[3], a[5]], [0, 0, 1]]
        else:
            continue
        m = _mul(m, t)
    return m


def _color(c, default):
    if c in (None, "none"):
        return None
    if c.startswith("#"):
        c = c.lstrip("#")
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    if c.startswith("rgb"):
        return tuple(int(float(v)) for v in re.findall(r"[\d.]+", c)[:3])
    if c.startswith("url"):
        return (225, 225, 225)  # a hatch pattern
    return {"black": (0, 0, 0), "white": (255, 255, 255)}.get(c, default)


def _arc_points(x0, y0, rx, ry, rot, large, sweep, x1, y1):
    """An SVG elliptical arc as points (the endpoint-to-center conversion from
    the SVG spec), including both ends."""
    if rx == 0 or ry == 0:
        return [(x0, y0), (x1, y1)]
    phi = math.radians(rot)
    c, s = math.cos(phi), math.sin(phi)
    dx, dy = (x0 - x1) / 2, (y0 - y1) / 2
    x1p, y1p = c * dx + s * dy, -s * dx + c * dy
    rx, ry = abs(rx), abs(ry)
    lam = (x1p / rx) ** 2 + (y1p / ry) ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    k = math.sqrt(max(0, num / den)) if den else 0
    if large == sweep:
        k = -k
    cxp, cyp = k * rx * y1p / ry, -k * ry * x1p / rx
    cx, cy = c * cxp - s * cyp + (x0 + x1) / 2, s * cxp + c * cyp + (y0 + y1) / 2

    def angle(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a
    t0 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    n = max(4, int(abs(dt) * max(rx, ry) / 2) + 2)
    pts = []
    for i in range(n + 1):
        t = t0 + dt * i / n
        ex, ey = rx * math.cos(t), ry * math.sin(t)
        pts.append((c * ex - s * ey + cx, s * ex + c * ey + cy))
    return pts


def _dashed(pts, on, off):
    """A polyline's dashes, as (start, end) segments."""
    out, t, drawing = [], 0.0, True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        s = 0.0
        while s < length:
            span = (on if drawing else off) - t
            e = min(length, s + span)
            if drawing:
                out.append(((x0 + (x1 - x0) * s / length, y0 + (y1 - y0) * s / length),
                            (x0 + (x1 - x0) * e / length, y0 + (y1 - y0) * e / length)))
            t += e - s
            s = e
            if t >= (on if drawing else off) - 1e-9:
                t, drawing = 0.0, not drawing
    return out


def _path_polylines(d):
    """A path's subpaths as lists of points (curves approximated)."""
    toks = re.findall(r"[MmLlHhVvZzAaCcQqSsTt]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?", d or "")
    polys, cur, start, i, cmd = [], (0.0, 0.0), None, 0, None
    poly = []

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                if poly and start:
                    poly.append(start)
                    cur = start
                continue
        rel = cmd.islower()
        if cmd in "Mm":
            x, y = num(), num()
            if rel:
                x, y = cur[0] + x, cur[1] + y
            if poly:
                polys.append(poly)
            poly, cur, start = [(x, y)], (x, y), (x, y)
            cmd = "l" if rel else "L"
        elif cmd in "Ll":
            x, y = num(), num()
            if rel:
                x, y = cur[0] + x, cur[1] + y
            poly.append((x, y))
            cur = (x, y)
        elif cmd in "Hh":
            x = num()
            x = cur[0] + x if rel else x
            cur = (x, cur[1])
            poly.append(cur)
        elif cmd in "Vv":
            y = num()
            y = cur[1] + y if rel else y
            cur = (cur[0], y)
            poly.append(cur)
        elif cmd in "Aa":
            rx, ry, rot, large, sweep, x, y = (num() for _ in range(7))
            if rel:
                x, y = cur[0] + x, cur[1] + y
            poly += _arc_points(*cur, rx, ry, rot, bool(large), bool(sweep), x, y)[1:]
            cur = (x, y)
        elif cmd in "Qq":  # a quadratic curve, as a polyline
            x1, y1, x, y = (num() for _ in range(4))
            if rel:
                x1, y1, x, y = cur[0] + x1, cur[1] + y1, cur[0] + x, cur[1] + y
            x0, y0 = cur
            for k in range(1, 17):
                t = k / 16
                poly.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t * t * x,
                             (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t * t * y))
            cur = (x, y)
        elif cmd in "CcSsTt":
            n = {"c": 6, "s": 4, "t": 2}[cmd.lower()]
            vals = [num() for _ in range(n)]
            x, y = vals[-2], vals[-1]
            if rel:
                x, y = cur[0] + x, cur[1] + y
            poly.append((x, y))  # a straight approximation
            cur = (x, y)
        else:
            i += 1
    if poly:
        polys.append(poly)
    return polys


class _Raster:
    def __init__(self, root, scale):
        vb = [float(v) for v in root.get("viewBox").split()]
        self.scale = scale
        self.size = (int(vb[2] * scale) + 1, int(vb[3] * scale) + 1)
        self.base = [[scale, 0, -vb[0] * scale], [0, scale, -vb[1] * scale], [0, 0, 1]]
        self.clips = {el.get("id"): el for el in root.iter(f"{NS}clipPath")}
        self.fonts = {}
        self.image = Image.new("RGB", self.size, "white")

    def font(self, family, size, bold):
        path = FONTS.get(family, FONTS["DejaVu Sans"])[1 if bold else 0]
        key = (path, size)
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(str(path), max(1, size))
        return self.fonts[key]

    def run(self, root):
        self.draw(root, self.base, {"stroke": None, "fill": None, "stroke-width": None, "font-family": None,
                                    "font-size": None, "font-weight": None}, self.image)
        return self.image

    def mask_for(self, clip_id, m):
        """A mask (L image) for a clipPath's shapes under transform m."""
        el = self.clips.get(clip_id)
        mask = Image.new("L", self.size, 0)
        if el is None:
            return None
        d = ImageDraw.Draw(mask)
        for child in el:
            tag = child.tag.replace(NS, "")
            if tag == "rect":
                x, y, w, h = (float(child.get(k, 0)) for k in ("x", "y", "width", "height"))
                d.polygon([_apply(m, x, y), _apply(m, x + w, y), _apply(m, x + w, y + h), _apply(m, x, y + h)], fill=255)
            elif tag == "polygon":
                pts = [tuple(map(float, p.split(","))) for p in child.get("points", "").split()]
                if len(pts) >= 3:
                    d.polygon([_apply(m, *p) for p in pts], fill=255)
        inner = el.get("clip-path")
        if inner:
            other = self.mask_for(inner[5:-1], m)
            if other is not None:
                from PIL import ImageChops
                mask = ImageChops.multiply(mask, other)
        return mask

    def draw(self, el, m, style, target):
        tag = el.tag.replace(NS, "")
        if tag in ("defs", "clipPath", "pattern"):
            return
        m = _mul(m, _transform(el.get("transform")))
        style = dict(style)
        for k in style:
            if el.get(k) is not None:
                style[k] = el.get(k)
        clip = el.get("clip-path")
        if clip:
            layer = Image.new("RGBA", self.size, (0, 0, 0, 0))
            self.draw_into(el, tag, m, style, layer)
            for child in el:
                self.draw(child, m, style, layer)
            mask = self.mask_for(clip[5:-1], self.base if clip.startswith("url(#vp") else m)
            if mask is not None:
                from PIL import ImageChops
                layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
            target.paste(layer, (0, 0), layer)
            return
        self.draw_into(el, tag, m, style, target)
        for child in el:
            self.draw(child, m, style, target)

    def draw_into(self, el, tag, m, style, target):
        d = ImageDraw.Draw(target)
        stroke = _color(style["stroke"], None)
        fill = _color(style["fill"], None)
        width = max(1, int(round(float(style["stroke-width"] or 0) * _scale_of(m)))) if style["stroke-width"] else 1
        if tag == "line":
            p0 = _apply(m, float(el.get("x1")), float(el.get("y1")))
            p1 = _apply(m, float(el.get("x2")), float(el.get("y2")))
            d.line([p0, p1], fill=stroke or (0, 0, 0), width=width)
        elif tag == "path":
            dashes = el.get("stroke-dasharray")
            for poly in _path_polylines(el.get("d")):
                pts = [_apply(m, *p) for p in poly]
                if fill and len(pts) > 2:
                    d.polygon(pts, fill=fill)
                if stroke or not fill:
                    if len(pts) > 1 and dashes:
                        on, off = (float(v) * _scale_of(m) for v in dashes.split()[:2])
                        for a, b in _dashed(pts, on, off):
                            d.line([a, b], fill=stroke or (0, 0, 0), width=width)
                    elif len(pts) > 1:
                        d.line(pts, fill=stroke or (0, 0, 0), width=width)
        elif tag == "circle":
            cx, cy = _apply(m, float(el.get("cx")), float(el.get("cy")))
            r = float(el.get("r")) * _scale_of(m)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=stroke or (0, 0, 0), fill=fill, width=width)
        elif tag == "rect" and el.get("width"):
            x, y, w, h = (float(el.get(k, 0)) for k in ("x", "y", "width", "height"))
            pts = [_apply(m, x, y), _apply(m, x + w, y), _apply(m, x + w, y + h), _apply(m, x, y + h)]
            d.polygon(pts, outline=stroke, fill=fill, width=width)
        elif tag == "polygon":
            pts = [_apply(m, *map(float, p.split(","))) for p in el.get("points", "").split()]
            if len(pts) > 2:
                d.polygon(pts, outline=stroke, fill=fill)
        elif tag == "image":
            self.image_into(el, m, target)
        elif tag == "text":
            self.text_into(el, m, style, target)

    def image_into(self, el, m, target):
        x, y, w, h = (float(el.get(k, 0)) for k in ("x", "y", "width", "height"))
        href = el.get("href") or el.get(XLINK, "")
        pts = [_apply(m, x, y), _apply(m, x + w, y), _apply(m, x + w, y + h), _apply(m, x, y + h)]
        try:
            icon = Image.open(io.BytesIO(base64.b64decode(href.split(",", 1)[1]))).convert("RGBA")
        except Exception:
            ImageDraw.Draw(target).polygon(pts, outline=(255, 0, 255))
            return
        # the icon's box under the transform: its axes' lengths and its rotation
        ax, ay = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        bx, by = pts[3][0] - pts[0][0], pts[3][1] - pts[0][1]
        bw, bh = int(math.hypot(ax, ay)), int(math.hypot(bx, by))
        if bw < 1 or bh < 1:
            return
        icon = icon.resize((bw, bh))
        angle = -math.degrees(math.atan2(ay, ax))
        if ax * by - ay * bx < 0:  # mirrored: flip it, and the x axis points the other way
            icon = icon.transpose(Image.FLIP_LEFT_RIGHT)
            angle += 180
        if abs(angle) > 0.1:
            icon = icon.rotate(angle, expand=True)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        target.paste(icon, (int(cx - icon.width / 2), int(cy - icon.height / 2)), icon)

    def text_into(self, el, m, style, target):
        family = style["font-family"] or "DejaVu Sans"
        x, y = float(el.get("x", 0)), float(el.get("y", 0))
        pen_x, baseline = x, y
        k = _scale_of(m)
        angle = math.degrees(math.atan2(m[1][0], m[0][0]))
        for span in el.iter(f"{NS}tspan"):
            size = float(span.get("font-size") or style["font-size"] or 1)
            bold = (span.get("font-weight") or style["font-weight"]) == "bold"
            if span.get("x") is not None:
                pen_x = float(span.get("x"))
            if span.get("dy") is not None:
                baseline += float(span.get("dy"))
            text = span.text or ""
            font = self.font(family, int(round(size * k)), bold)
            px, py = _apply(m, pen_x, baseline)
            if abs(angle) < 0.1:
                ImageDraw.Draw(target).text((px, py), text, fill=(0, 0, 0), font=font, anchor="ls")
            else:
                w = int(font.getlength(text)) + 4
                h = int(size * k * 1.5) + 4
                layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                ImageDraw.Draw(layer).text((0, int(size * k * 1.1)), text, fill=(0, 0, 0, 255), font=font, anchor="ls")
                rotated = layer.rotate(-angle, expand=True, resample=Image.BICUBIC)
                # where the pen's origin (0, baseline) lands after rotation about the layer's center
                ox, oy = 0 - w / 2, int(size * k * 1.1) - h / 2
                a = math.radians(-angle)
                rx, ry = ox * math.cos(a) + oy * math.sin(a), -ox * math.sin(a) + oy * math.cos(a)
                target.paste(rotated, (int(px - rx - rotated.width / 2), int(py - ry - rotated.height / 2)), rotated)
            pen_x += font.getlength(text) / k


def rasterize(svg, png, pixels=PIXELS):
    root = ET.parse(svg).getroot()
    vb = [float(v) for v in root.get("viewBox").split()]
    r = _Raster(root, pixels / max(vb[2], vb[3]))
    r.run(root).save(png)


def main(argv):
    if len(argv) == 2 and argv[0] == "snapshot":
        snapshot(argv[1])
    elif len(argv) == 4 and argv[0] == "compare":
        compare(*argv[1:])
    elif len(argv) == 3 and argv[0] == "png":
        rasterize(argv[1], argv[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
