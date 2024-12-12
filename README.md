# Tiny Home Manual - Post Tilt Up

### Background

This is the manual for the Sound Foundations Tiny Home post tilt-up process. 

The manual has been created in Markdown so text and images can be edited independently. 

### Authors
* David Means (text) 
* Daphne Chong (images)

### Editing Images
Images and diagrams in this manual are created using LayOut, based on this [Tiny Home Model](https://web.connect.trimble.com/projects/H3xXgzdyUMc/viewer/3d/?modelId=GoTtRh_ju8U&=&origin=app.connect.trimble.com&stoken=GOGUIZCqsLxEMBMi8d1WT_BkEB3nBpZNHqCMOSf_CtXKWa8dqnla6RG2KN0q6lWB) built in SketchUp. 

You will need:
 * [SketchUp](https://www.sketchup.com) to edit the model. There are [free web-based editions of SketchUp](https://www.sketchup.com/en/plans-and-pricing/sketchup-free), although the model was built on a desktop using SketchUp Pro.
 * [LayOut](https://www.sketchup.com/en/products/layout), part of the SketchUp Pro package, for taking scenes built in the model and laying them out on to pages with various insets and annotations.
 * Permissions to edit the model. At the moment, only a limited number of people have access. 

### Editing Text

You will need:
* An editor capable of rendering markdown to preview your changes. [VS Code](https://code.visualstudio.com/) is a free option.
* The [Quarto extension](https://marketplace.visualstudio.com/items?itemName=quarto.quarto) for VS Code, or separate [Quarto](https://quarto.org/) installation. We use this specifically for 
  * Adding custom **page breaks** 
  * Render the manual in **docx** format
  * Ability to use a docx template file to specify page numbers, a date that is inserted on printing, and to have full control over text styles formatting 
  * It is much faster to render docx over PDF. You can use a PDF printer on the docx file if a PDF file is required.


### Rendering the Manual

#### Custom template file
The `post-tilt-up-template.docx` file is used by Quarto as a template for rendering the finished docx file. 

The template has instances of:
* Heading 1
* Heading 2
* Normal text
* Footer page number
* Automatic date insertion into footer when the document is printed

#### Rendering the docx file

Contents are taken from `post-tilt-up.qmd` and rendered into a new document based on the custom template file. 

To render the document:
* open the markdown file in VS Code
* click on `"..." in the top right > Preview Format > Preview MS Word`.
* This generates a new file `post-tilt-up.docx` in the same folder as the `post-tilt-up.qmd` file, with all of the correct formatting (based on styles in the template file), and the text and images referenced in the markdown. 

Additional instructions with diagrams are available on the [Quarto Extension](https://marketplace.visualstudio.com/items?itemName=quarto.quarto) page. 

