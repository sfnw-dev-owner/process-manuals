// Typst template to apply uniform style to all documents. Replaces pandoc's typst template.

#set page("us-letter")

#let title-page(body) = {
  align(center + horizon)[
    #image("/common/SoundFoundationsNW_logo.png")
    #v(4em)
    #body
  ]
  counter(page).update(0)
  pagebreak()
}

#if "$title$" != "" and "$no-title-page$" == "" {
  title-page(text(24pt, weight: "bold", [$title$]))
}

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

$header-includes$

$body$

