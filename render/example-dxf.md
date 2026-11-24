---
no-title-page: true
---

# An example incorporating .dxf sources

<!-- Markdown style -->
![](../Interior_Trim/Images/rear_wall.dxf){layers="1_Paneling,3_Shelf"}

<!-- typst macro style -->
`#fullpage("../Interior_Trim/Images/rear_wall.dxf", layers:"1_Paneling,3_Shelf")`{=typst}

# Hello

<!-- typst macro demonstrating extra param (vspace) -->
`#horizontal-center("../Interior_Trim/Images/rear_wall.dxf", vspace:1em, layers:"1_Paneling,3_Shelf")`{=typst}

# Goodbye
