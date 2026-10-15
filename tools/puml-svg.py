#!/usr/bin/env python3
"""Render a PlantUML diagram to an SVG that the remark engine can theme and step.

    python3 tools/puml-svg.py day1/intro/src/crisp-linear.puml \
        day1/intro/src/crisp-linear.steps.json day1/intro/images/crisp-linear.svg

The engine's two SVG extensions read markup that PlantUML does not write:
`ext/svg-theme.js` recolours shapes that carry an `accent-*` class, and
`ext/stepwise-svg.js` reveals elements in the order of their `data-step`
(hiding them again over a `data-hide` range). This script renders the diagram
with PlantUML, then writes that markup from a sidecar JSON:

    {
      "comment": "credit and licence line, kept in the SVG",
      "nodes": {
        "BU": {"step": 1, "class": "accent-fill", "fill": "#00609c",
               "text_fill": "#ffffff", "sub": {"step": 7, "fill": "#d9e6f0"}}
      },
      "edges": {"BU-to-DU": {"step": 2, "hide": "5-end"}}
    }

- A node is the `<g class="entity">` whose `data-qualified-name` is the alias in
  the .puml; an edge is the `<g class="link">` holding the path whose id is
  `<from>-to-<to>` (stable across edits, unlike PlantUML's `entNNNN` ids).
- `step` and `hide` go on the group. `class` and `fill` go on the shape itself
  (its own `fill` attribute beats one inherited from the group); `fill` is the
  colour shown when no script runs, `class` the one the theme applies. A node
  with `fill` and no `class` keeps its colour whatever the theme. `stroke` (and
  `stroke_width`, default 3) outline the shape.
- `text_fill` recolours every text line of a node; `sub` addresses its second
  line (a `\\n` in the label), which can then step on its own.

Every key must match: a key that matches nothing exits non-zero, because a
PlantUML upgrade that renames its output would otherwise drop steps silently.

The jar is not in this repository (30 MB); the script looks for it in
$PLANTUML_JAR, then ~/.local/share/plantuml/plantuml.jar.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from lxml import etree

SVG = "http://www.w3.org/2000/svg"
NS = {"s": SVG}


def jar() -> str:
    path = os.environ.get("PLANTUML_JAR") or str(Path.home() / ".local/share/plantuml/plantuml.jar")
    if not Path(path).exists():
        sys.exit(f"puml-svg: PlantUML jar not found at {path} (set PLANTUML_JAR)")
    return path


def render(puml: Path) -> bytes:
    out = subprocess.run(["java", "-jar", jar(), "-tsvg", "-pipe"],
                         input=puml.read_bytes(), capture_output=True, check=False)
    if out.returncode != 0 or not out.stdout.startswith(b"<svg"):
        sys.exit(f"puml-svg: PlantUML failed on {puml}:\n{out.stderr.decode()}")
    return out.stdout


def set_steps(el, spec: dict) -> None:
    if "step" in spec:
        el.set("data-step", str(spec["step"]))
    if "hide" in spec:
        el.set("data-hide", str(spec["hide"]))


def add_class(el, cls: str) -> None:
    el.set("class", " ".join(filter(None, [el.get("class"), cls])))


def process(svg: bytes, side: dict) -> bytes:
    root = etree.fromstring(svg)
    for pi in root.xpath("//processing-instruction()"):
        pi.getparent().remove(pi)
    for attr in ("preserveAspectRatio", "zoomAndPan", "contentStyleType", "width", "height", "style"):
        root.attrib.pop(attr, None)

    missing = []
    for name, spec in side.get("nodes", {}).items():
        g = root.xpath(f"//s:g[@class='entity'][@data-qualified-name='{name}']", namespaces=NS)
        if not g:
            missing.append(f"node {name}")
            continue
        g = g[0]
        set_steps(g, spec)
        shape = g.xpath("s:rect|s:polygon|s:path|s:ellipse", namespaces=NS)
        if (spec.get("class") or spec.get("fill") or spec.get("stroke")) and not shape:
            missing.append(f"shape of node {name}")
            continue
        if spec.get("class"):
            add_class(shape[0], spec["class"])
        if spec.get("fill"):
            shape[0].set("fill", spec["fill"])
        if spec.get("stroke"):
            # PlantUML writes the stroke into `style`, which beats an attribute
            style = [d for d in (shape[0].get("style") or "").split(";")
                     if d.strip() and d.split(":")[0].strip() not in ("stroke", "stroke-width")]
            shape[0].set("style", ";".join(style))
            shape[0].set("stroke", spec["stroke"])
            shape[0].set("stroke-width", str(spec.get("stroke_width", 3)))
        texts = g.xpath("s:text", namespaces=NS)
        if spec.get("text_fill"):
            for t in texts:
                t.set("fill", spec["text_fill"])
        if "sub" in spec:
            if len(texts) < 2:
                missing.append(f"second text line of node {name}")
                continue
            set_steps(texts[1], spec["sub"])
            if spec["sub"].get("fill"):
                texts[1].set("fill", spec["sub"]["fill"])

    for pid, spec in side.get("edges", {}).items():
        path = root.xpath(f"//s:g[@class='link']/s:path[@id='{pid}']", namespaces=NS)
        if not path:
            missing.append(f"edge {pid}")
            continue
        set_steps(path[0].getparent(), spec)

    if missing:
        sys.exit("puml-svg: no match in the rendered SVG for " + ", ".join(missing))

    if side.get("comment"):
        root.insert(0, etree.Comment(f" {side['comment']} "))
    return etree.tostring(root, xml_declaration=False, encoding="utf-8") + b"\n"


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        sys.exit(__doc__)
    puml, sidecar, out = map(Path, argv[1:])
    side = json.loads(sidecar.read_text(encoding="utf-8"))
    out.write_bytes(process(render(puml), side))
    print(f"{out}: {len(side.get('nodes', {}))} nodes, {len(side.get('edges', {}))} edges marked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
