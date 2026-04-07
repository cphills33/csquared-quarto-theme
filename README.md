# C-Squared Quarto Theme

An installable Quarto HTML theme extension inspired by the C-Squared lab style.

The extension contributes one HTML format, `csquared-html`, with:

- **Paper Wash**: a light, cool-paper document theme with slate text, teal navigation, rose accents, and quiet watercolor wash surfaces.
- **Night Bloom**: a dark navy document theme with cyan and teal highlights, rose accents, and restrained gold emphasis.
- Light/dark mode support through Quarto's color-scheme toggle.
- A small static preview page in `preview/index.html`.

## Install

Install the extension into a Quarto project with:

```bash
quarto add cphills33/csquared-quarto-theme
```

Then use the format in a document:

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

To refresh an already installed copy after this repository changes, run the same command again from the Quarto project:

```bash
quarto add cphills33/csquared-quarto-theme
```

Then re-render the document.

## Preview

Open `preview/index.html` in a browser for a quick static look at the light and dark palettes. The real Quarto theme is defined by the SCSS files in `_extensions/csquared/`.

You can also render the sample Quarto document:

```bash
quarto render template.qmd
```

## Files

```text
LICENSE
README.md
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

The extension declares `quarto-required: ">=1.3.450"` because it uses Quarto's light/dark theme map syntax. Update Quarto if an older renderer does not produce the theme toggle.

## License

MIT License. See `LICENSE`.
