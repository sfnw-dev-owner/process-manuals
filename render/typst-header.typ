// Typst header to apply uniform style to all documents.

#show heading.where(level: 1): it => {
  set text(size: 20pt, weight: "bold")
  align(center, block(above: .5em, below: 1.5em)[#it])
}

#show heading.where(level: 2): set text(size: 18pt, weight: "regular")

#show heading.where(level: 3): it => {
  set text(size: 16pt, weight: "regular")
  underline(offset: 2pt)[#it]
}

#show heading.where(level: 4): set text(size: 14pt, weight: "regular")

#set table(stroke: 0.5pt, inset: (x: 6pt, y: 4pt))

// See ../Front_Wall/front_wall_ada.md for example usage.
#let fullpage(path) = block(height: 100%, width: 100%)[#align(center + horizon)[#image(path)]]
#let ctrimage(path) = align(center)[#rect(stroke: none)[#image(path)]]