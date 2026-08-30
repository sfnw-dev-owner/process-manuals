---
no-title-page: true
---

# An example incorporating .dxf sources

<!-- Markdown style -->
![](../Interior_Trim/Images/rear_window.dxf){layers="0,1_Paneling,2_Shelf"}

<!-- typst macro style -->
`#fullpage("../Interior_Trim/Images/rear_window.dxf", layers:"0,1_Paneling,2_Shelf")`{=typst}

# Hello

<!-- typst macro demonstrating extra param (vspace) -->
`#horizontal-center("../Interior_Trim/Images/rear_window.dxf", vspace:1em, layers:"0,1_Paneling,2_Shelf")`{=typst}

# Goodbye
