#set table(stroke: 0.5pt, inset: (x: 6pt, y: 4pt))

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
