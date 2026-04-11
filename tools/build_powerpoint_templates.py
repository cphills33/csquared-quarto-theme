#!/usr/bin/env python3
"""Build C-Squared PowerPoint templates without third-party packages."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "_extensions" / "csquared" / "powerpoint"

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"

PRESENTATION_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
TEMPLATE_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"

ET.register_namespace("p", P)
ET.register_namespace("a", A)
ET.register_namespace("r", R)
ET.register_namespace("", CT)


BASE_QMD = """---
title: "C-Squared PowerPoint Template"
subtitle: "Reference deck for Quarto and PowerPoint"
author: "Curtis Phills"
format: pptx
---

# Section Break

Use section slides to reset attention between analysis stages.

# Analysis Question

- What are the main patterns?
- Which estimates are most stable?
- Where should interpretation slow down?

# Two-Column Evidence

::: columns
::: {.column width="50%"}
## Model

- Predictor set
- Covariates
- Diagnostics
:::

::: {.column width="50%"}
## Interpretation

- Direction
- Uncertainty
- Substantive meaning
:::
:::

# Table

| Construct | Document role |
|---|---|
| Implicit bias | Core topic |
| Intersectionality | Organizing frame |
| Prejudice reduction | Applied payoff |

# Code

```r
scores <- c(0.12, 0.18, 0.31, 0.27)
mean(scores)
```
"""


PALETTES = {
    "paper-wash": {
        "output": "csquared-paper-wash.pptx",
        "template_output": "csquared-paper-wash.potx",
        "theme_name": "C-Squared Paper Wash",
        "bg": "F7FBFA",
        "surface": "EAF4F3",
        "surface_alt": "EEF7F6",
        "text": "263540",
        "heading": "21313B",
        "muted": "557A94",
        "cyan": "1F7185",
        "teal": "2C8D83",
        "rose": "B93E63",
        "coral": "D96D58",
        "gold": "A86B1E",
    },
    "night-bloom": {
        "output": "csquared-night-bloom.pptx",
        "template_output": "csquared-night-bloom.potx",
        "theme_name": "C-Squared Night Bloom",
        "bg": "0A111D",
        "surface": "101B2A",
        "surface_alt": "111C2B",
        "text": "EAF4F3",
        "heading": "F6FBFA",
        "muted": "94AFC2",
        "cyan": "58D7E8",
        "teal": "42C7B7",
        "rose": "F06A92",
        "coral": "FF5C7A",
        "gold": "E2B84B",
    },
}


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def elem(ns: str, tag: str, **attrs: str) -> ET.Element:
    return ET.Element(qn(ns, tag), attrs)


def remove_fill(parent: ET.Element) -> None:
    fill_tags = {
        qn(A, "solidFill"),
        qn(A, "gradFill"),
        qn(A, "noFill"),
        qn(A, "blipFill"),
        qn(A, "pattFill"),
        qn(A, "grpFill"),
    }
    for child in list(parent):
        if child.tag in fill_tags:
            parent.remove(child)


def add_solid_fill(parent: ET.Element, color: str, alpha: int | None = None) -> None:
    remove_fill(parent)
    solid = elem(A, "solidFill")
    srgb = elem(A, "srgbClr", val=color)
    if alpha is not None:
        srgb.append(elem(A, "alpha", val=str(alpha)))
    solid.append(srgb)
    insert_at = 0
    for index, child in enumerate(list(parent)):
        if child.tag in {qn(A, "xfrm"), qn(A, "custGeom"), qn(A, "prstGeom")}:
            insert_at = index + 1
    parent.insert(insert_at, solid)


def set_color_node(parent: ET.Element, color: str) -> None:
    for child in list(parent):
        parent.remove(child)
    parent.append(elem(A, "srgbClr", val=color))


def ensure_latin_font(parent: ET.Element, typeface: str = "Avenir Next") -> None:
    latin = parent.find(qn(A, "latin"))
    if latin is None:
        latin = elem(A, "latin")
        parent.append(latin)
    latin.set("typeface", typeface)


def style_theme(root: ET.Element, palette: dict[str, str]) -> None:
    root.set("name", palette["theme_name"])
    clr_scheme = root.find(f".//{qn(A, 'clrScheme')}")
    if clr_scheme is not None:
        clr_scheme.set("name", palette["theme_name"])
        colors = {
            "dk1": palette["text"],
            "lt1": palette["bg"],
            "dk2": palette["heading"],
            "lt2": palette["surface"],
            "accent1": palette["cyan"],
            "accent2": palette["rose"],
            "accent3": palette["teal"],
            "accent4": palette["gold"],
            "accent5": palette["coral"],
            "accent6": palette["muted"],
            "hlink": palette["cyan"],
            "folHlink": palette["rose"],
        }
        for key, value in colors.items():
            node = clr_scheme.find(qn(A, key))
            if node is not None:
                set_color_node(node, value)

    for latin in root.findall(f".//{qn(A, 'latin')}"):
        latin.set("typeface", "Avenir Next")


def placeholder_type(shape: ET.Element) -> str:
    ph = shape.find(f".//{qn(P, 'ph')}")
    if ph is None:
        return ""
    return ph.attrib.get("type", "")


def set_text_fill(container: ET.Element, color: str) -> None:
    targets = []
    for tag in ("rPr", "defRPr", "endParaRPr"):
        targets.extend(container.findall(f".//{qn(A, tag)}"))
    for target in targets:
        add_solid_fill(target, color)
        ensure_latin_font(target)


def style_text(container: ET.Element, palette: dict[str, str]) -> None:
    for shape in container.findall(f".//{qn(P, 'sp')}"):
        ph_type = placeholder_type(shape)
        if ph_type in {"title", "ctrTitle"}:
            color = palette["heading"]
        elif ph_type in {"subTitle", "dt", "ftr", "sldNum"}:
            color = palette["muted"]
        else:
            color = palette["text"]
        set_text_fill(shape, color)


def set_background(csld: ET.Element, palette: dict[str, str]) -> None:
    for bg in csld.findall(qn(P, "bg")):
        csld.remove(bg)
    bg = elem(P, "bg")
    bg_pr = elem(P, "bgPr")
    add_solid_fill(bg_pr, palette["bg"])
    bg_pr.append(elem(A, "effectLst"))
    bg.append(bg_pr)
    csld.insert(0, bg)


def max_shape_id(sp_tree: ET.Element) -> int:
    max_id = 1
    for node in sp_tree.findall(f".//{qn(P, 'cNvPr')}"):
        raw = node.attrib.get("id")
        if raw and raw.isdigit():
            max_id = max(max_id, int(raw))
    return max_id


def wash_shape(shape_id: int, name: str, color: str, alpha: int, x: int, y: int, cx: int, cy: int) -> ET.Element:
    sp = elem(P, "sp")
    nv = elem(P, "nvSpPr")
    nv.append(elem(P, "cNvPr", id=str(shape_id), name=name))
    nv.append(elem(P, "cNvSpPr"))
    nv.append(elem(P, "nvPr"))
    sp.append(nv)

    sp_pr = elem(P, "spPr")
    xfrm = elem(A, "xfrm")
    xfrm.append(elem(A, "off", x=str(x), y=str(y)))
    xfrm.append(elem(A, "ext", cx=str(cx), cy=str(cy)))
    sp_pr.append(xfrm)
    geom = elem(A, "prstGeom", prst="ellipse")
    geom.append(elem(A, "avLst"))
    sp_pr.append(geom)
    add_solid_fill(sp_pr, color, alpha=alpha)
    ln = elem(A, "ln")
    ln.append(elem(A, "noFill"))
    sp_pr.append(ln)
    effects = elem(A, "effectLst")
    effects.append(elem(A, "softEdge", rad="520000"))
    sp_pr.append(effects)
    sp.append(sp_pr)
    return sp


def add_washes(csld: ET.Element, palette: dict[str, str]) -> None:
    sp_tree = csld.find(qn(P, "spTree"))
    if sp_tree is None:
        return
    first_id = max_shape_id(sp_tree) + 1
    washes = [
        wash_shape(first_id, "C-Squared cyan wash", palette["cyan"], 15000, -1100000, -680000, 4900000, 1750000),
        wash_shape(first_id + 1, "C-Squared rose wash", palette["rose"], 11000, 6250000, -460000, 3800000, 1550000),
        wash_shape(first_id + 2, "C-Squared teal wash", palette["teal"], 13500, 900000, 3780000, 7600000, 1180000),
    ]
    for offset, shape in enumerate(washes):
        sp_tree.insert(2 + offset, shape)


def style_slide_like(root: ET.Element, palette: dict[str, str], add_background_washes: bool) -> None:
    for csld in root.findall(f".//{qn(P, 'cSld')}"):
        set_background(csld, palette)
        if add_background_washes:
            add_washes(csld, palette)
    style_text(root, palette)


def restyle_pptx(base_pptx: Path, output_pptx: Path, palette: dict[str, str]) -> None:
    with ZipFile(base_pptx, "r") as src, ZipFile(output_pptx, "w", compression=ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename.startswith("ppt/theme/") and item.filename.endswith(".xml"):
                root = ET.fromstring(data)
                style_theme(root, palette)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            elif item.filename.startswith("ppt/slideMasters/") and item.filename.endswith(".xml"):
                root = ET.fromstring(data)
                style_slide_like(root, palette, add_background_washes=True)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            elif item.filename.startswith("ppt/slideLayouts/") and item.filename.endswith(".xml"):
                root = ET.fromstring(data)
                style_slide_like(root, palette, add_background_washes=True)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            elif item.filename.startswith("ppt/slides/") and item.filename.endswith(".xml"):
                root = ET.fromstring(data)
                style_slide_like(root, palette, add_background_washes=True)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            dst.writestr(item, data)


def convert_to_potx(input_pptx: Path, output_potx: Path) -> None:
    with ZipFile(input_pptx, "r") as src, ZipFile(output_potx, "w", compression=ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "[Content_Types].xml":
                root = ET.fromstring(data)
                for override in root.findall(qn(CT, "Override")):
                    if (
                        override.attrib.get("PartName") == "/ppt/presentation.xml"
                        and override.attrib.get("ContentType") == PRESENTATION_CONTENT_TYPE
                    ):
                        override.set("ContentType", TEMPLATE_CONTENT_TYPE)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            dst.writestr(item, data)


def build_base_deck(work_dir: Path) -> Path:
    source = work_dir / "base.qmd"
    source.write_text(BASE_QMD, encoding="utf-8")
    subprocess.run(
        ["quarto", "render", source.name, "--to", "pptx", "--output", "base.pptx"],
        cwd=work_dir,
        check=True,
    )
    return work_dir / "base.pptx"


def main() -> None:
    if shutil.which("quarto") is None:
        raise SystemExit("quarto is required to build the PowerPoint templates")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="csquared-pptx-") as tmp:
        work_dir = Path(tmp)
        base = build_base_deck(work_dir)
        for palette in PALETTES.values():
            output = OUT_DIR / palette["output"]
            template_output = OUT_DIR / palette["template_output"]
            restyle_pptx(base, output, palette)
            convert_to_potx(output, template_output)
            print(f"wrote {output.relative_to(ROOT)}")
            print(f"wrote {template_output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
