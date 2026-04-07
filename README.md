# C-Squared Quarto Theme

An installable Quarto HTML theme extension inspired by the C-Squared style docs and the existing RStudio themes:

- **Paper Wash**: a light, cool-paper document theme with slate text, teal navigation, rose accents, and quiet watercolor wash surfaces.
- **Night Bloom**: a dark navy document theme with cyan and teal highlights, rose accents, and restrained gold emphasis.

The extension contributes one HTML format, `csquared-html`, that provides both light and dark modes.

Major document sections get subtle watercolor wash bursts behind the heading area, so the banner color treatment reappears as readers scroll.

## Install from GitHub

After this folder is published as a GitHub repository, install it into a Quarto project with:

```bash
quarto add cphills33/csquared-quarto-theme
```

Then use it in a document like this:

```yaml
---
title: "Your Cool Analyses"
toc: true
title-block-banner: true
format:
  csquared-html:
    embed-resources: true
---
```

## Files

```text
_extensions/
  csquared/
    _extension.yml
    csquared-light.scss
    csquared-dark.scss
.gitignore
template.qmd
preview/
  index.html
```

## Notes

The local Quarto install checked while creating this scaffold was `1.3.450`. The extension uses Quarto's light/dark theme map syntax, so update Quarto if an older renderer does not produce the theme toggle.
