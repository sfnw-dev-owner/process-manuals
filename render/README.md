# Rendering the manuals

`render/go <manual>.md` typesets one manual to a PDF beside it; `render/all`
typesets every manual. Both run pandoc and typst inside the renderer
container named in `render/.container` (built from `render/Dockerfile`; a
change to it or to `requirements.txt` on `main` rebuilds and pushes the
image), so nothing but docker or podman and git needs installing. The
templates are `pandoc-defaults.yaml` and `typst-header.typ`; the manuals'
text is set in [Carlito](https://fonts.google.com/specimen/Carlito), an open
alternative to Calibri.

## Figures drawn from the model

The figures are not images in the repo: they're drawn, at render time, from
the build123d model of the house in [common/model](../common/model/__init__.py),
by `render/model2svg.py`. A manual embeds one as

```
![](model:platform/step_03@1:20)
```

or, where a typst macro takes an image path, as
`` `#fullpage("model:platform/step_03@1:20")`{=typst} ``. The name is
`<manual>/<figure>`: the manual's file name, lowercased, and a figure name
from `FIGURES` in [common/model/figures/__init__.py](../common/model/figures/__init__.py).
`@1:20` is the scale to print the drawing at, chosen by the manual (an
overview at 1:20, a detail of it at 1:10; the same figure can appear at two
scales). The pages of 3D views (tilt-up, post-tilt-up, the iron-cart
extraction) have a page size of their own and take no scale.
`render/model.lua` is the pandoc filter that swaps these references for the
rendered SVGs, and `render/example-model.md` shows the forms.

## Values from the model

A dimension a manual states is written as the name of the value in
`common/model/dimensions.py`, in double braces:

```
Place {{STUD_LENGTH}} 2x4s (studs) in the designated spots
```

prints `Place 84” 2x4s (studs)...`, and a change to `STUD_LENGTH` changes
the manual. `render/model.lua` fills them in, from `render/values.py`, which
writes a number as the shop does: whole inches and a fraction (`93½”`,
`77¾”`, `¹⁵⁄₃₂”`), or a decimal when it isn't a sixty-fourth. The unit
comes from the model: a number is a length in inches, as the model is
built; an angle is marked there as `Degrees(18.5)` and prints `18½°`, and a
count of things as `Count(5)` prints `5`. `{{TAR_PAPER_LENGTH:ft}}` prints
a length in feet and inches (`13’4”`). A value from another model module is
`{{walls.AC_SIDE_BLOCK}}`, an element of a pair `{{WINDOW_OPENING[0]}}`, and
a small expression is allowed (`{{RIDGE_VENT_OVERHANG-SHINGLE_OVERHANG}}`).
A name the model doesn't have fails the render. A value's module counts as
a dependency of the manual for the revision date in its footer, like a
figure's sources.

The SVGs are cached in `.rendered-figures/`, keyed by everything a figure is
drawn from (its name and scale, the model modules its figure module imports,
`model2svg.py`, `requirements.txt` and the clipart), so editing a manual's
text re-renders nothing, and a change to, say, `walls.py` only re-renders
the figures that use it. `render/all` renders every figure first, in
parallel, and prunes cached figures no manual uses any more.

### Where things live

- `common/model/dimensions.py`: every dimension the manuals state, named.
  The manuals print these values (`{{NAME}}`, above) rather than repeating
  them, so this file is where a dimension is changed; `render/all` fails if
  a name there is used by no manual and no model module
  (`render/values.py --unused`).
- `common/model/<assembly>.py` (`platform_assembly`, `walls`, `roof`, `roofing`,
  `gables`, `interior`, `interior_roof`, `doors`, `flooring`, `exterior_trim`,
  `house`): the parts,
  as `@component` functions returning their solids and their placed children.
  Anything derived from the geometry is computed there (stud positions, bay
  widths, where a fastener goes: `common.driven(head, direction)` places a
  nail or screw by its head and the direction it's driven).
- `common/model/tilt_up.py`, `post_tilt_up.py`, `iron_carts.py`: the jigs,
  clamps, braces, equipment and crew of the assembly manuals' scenes.
- `common/model/figures/<manual>.py`: the manual's figures. A drawing's
  module has one table, one row per figure: the parts to show and how to
  style them (`"new"` filled black, `"context"` gray, `"covered"` showing
  through sheathing...), the jig tools laid on, and the notes. A page's
  module (`figures/pages.py` helpers) says which parts are in the scene and
  which way to look at them: `iso("rear lhs")` for the standard isometric
  from above a named corner of the house, or a camera from the `CAMERAS`
  table, fitted to the parts, with tool insets in the page's corners.
- `common/model/notes.py`: the annotations. A note is anchored to a point of
  the model (a stud's end, a nail's head, the middle of an arrow) and
  everything about the note itself (its size, its stand-off, a leader's
  length) is in inches on paper, so it looks the same at any scale. Helpers
  place them: `beside()`, `callout()`, `aimed()` (a tool icon pointing at a
  joint), `dimension()`, `numbered()`, `title()`.
- `common/clipart/`: the tool icons; `notes.ICONS` gives each one's size on
  paper and where its nose is.

### Editing a figure

Change the model (or the figure's row), then render the manual. To see
exactly what a change did, `render/figdiff.py` snapshots every figure the
manuals embed and compares two snapshots, writing a side-by-side picture of
each figure that changed and a summary README:

```
docker run --rm -v "$PWD":/s:z -w /s --entrypoint=/bin/bash "$(head -1 render/.container)" \
    -c "python3 render/figdiff.py snapshot /tmp/before"
# ...edit the model...
docker run --rm -v "$PWD":/s:z -w /s --entrypoint=/bin/bash "$(head -1 render/.container)" \
    -c "python3 render/figdiff.py snapshot /tmp/after && python3 render/figdiff.py compare /tmp/before /tmp/after /tmp/diff"
```

A change meant to touch one figure shouldn't change the others, and a
refactor shouldn't change any: `compare` says "0 of N figures changed".

To render a single figure while iterating, run `model2svg.py` the same way
with the figure's name (`python3 render/model2svg.py platform/step_03@1:20`);
it prints the SVG's path (as JSON). Delete the cached SVG to force a redraw.

## Visual diffs of PDFs

`render/visual-diff/` builds the image the `render-pdfs` workflow uses to
compare a pull request's PDFs against the latest release's.
