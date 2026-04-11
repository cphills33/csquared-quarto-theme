# C-Squared Quarto Theme

An installable Quarto theme extension inspired by the C-Squared lab style.

The repository now installs three HTML formats and includes tooling to generate matching PowerPoint template files and Quarto reference decks locally:

- **Paper Wash**: a light, cool-paper document theme with slate text, teal navigation, rose accents, and quiet watercolor wash surfaces.
- **Night Bloom**: a dark navy document theme with cyan and teal highlights, rose accents, and restrained gold emphasis.
- `csquared-html`: the original toggle-enabled HTML format that ships both palettes.
- `csquared-paper-wash-html`: a fixed light-only HTML format with no toggle.
- `csquared-night-bloom-html`: a fixed dark-only HTML format with no toggle.
- A build script for local `.potx` template generation.
- A build script for local Quarto-compatible `.pptx` reference decks.
- A small static preview page in `preview/index.html`.

## Install

Install the extension into a Quarto project with:

```bash
quarto add cphills33/csquared-quarto-theme
```

Then use whichever HTML format you want in a document:

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

For a fixed light page with no theme toggle:

```yaml
---
title: "Your Cool Analyses"
toc: true
title-block-banner: true
format:
  csquared-paper-wash-html:
    embed-resources: true
---
```

For a fixed dark page with no theme toggle:

```yaml
---
title: "Your Cool Analyses"
toc: true
title-block-banner: true
format:
  csquared-night-bloom-html:
    embed-resources: true
---
```

To refresh an already installed copy after this repository changes, run the same command again from the Quarto project:

```bash
quarto add cphills33/csquared-quarto-theme
```

Then re-render the document.

## PowerPoint Templates

Generate the PowerPoint files first:

```bash
python3 tools/build_powerpoint_templates.py
```

Then open one of the `.potx` template files:

```text
_extensions/csquared/powerpoint/csquared-paper-wash.potx
_extensions/csquared/powerpoint/csquared-night-bloom.potx
```

PowerPoint should treat these as templates, so opening one creates a new presentation using the C-Squared theme rather than editing the template directly.

## Quarto PowerPoint

The extension also includes two `.pptx` reference decks under `_extensions/csquared/powerpoint/`. Use them with Quarto's `reference-doc` option:

```yaml
---
title: "Your Cool Analyses"
format:
  pptx:
    reference-doc: _extensions/csquared/powerpoint/csquared-paper-wash.pptx
---
```

For the dark deck:

```yaml
---
title: "Your Cool Analyses"
format:
  pptx:
    reference-doc: _extensions/csquared/powerpoint/csquared-night-bloom.pptx
---
```

Regenerate the `.potx` template files and `.pptx` reference decks after theme changes with:

```bash
python3 tools/build_powerpoint_templates.py
```

## Preview

Open `preview/index.html` in a browser for a quick static look at the light and dark palettes. The real Quarto theme is defined by the SCSS files in `_extensions/csquared/`, and the fixed light/dark formats reuse those same SCSS files.

You can also render the sample Quarto document:

```bash
quarto render template.qmd
```

Or target one of the fixed variants directly:

```bash
quarto render template.qmd --to csquared-paper-wash-html
quarto render template.qmd --to csquared-night-bloom-html
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
    powerpoint/
      # generated locally by tools/build_powerpoint_templates.py
  csquared-paper-wash/
    _extension.yml
  csquared-night-bloom/
    _extension.yml
.gitignore
template.qmd
preview/
  index.html
tools/
  build_powerpoint_templates.py
```

## Notes

The extension declares `quarto-required: ">=1.3.450"` because the toggle-enabled `csquared-html` format uses Quarto's light/dark theme map syntax. The fixed `csquared-paper-wash-html` and `csquared-night-bloom-html` formats render a single palette and therefore do not expose the toggle.

The PowerPoint binaries are generated artifacts and are ignored by Git in this repository.

## License

MIT License. See `LICENSE`.
