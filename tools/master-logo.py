#!/usr/bin/env python3
"""Compose the HES-SO Master logo: the HES-SO wordmark with "Master" set below it.

    conda run -n base python tools/master-logo.py assets/hes-so-wordmark.svg \
        /path/to/Arimo-Bold.ttf assets/hes-so-logo.svg

Needs fontTools, lxml, Pillow and rsvg-convert (which measures the wordmark).

No vector file of the HES-SO Master mark is public. This one follows the mark
on the HES-SO Master slide template, as measured on a 304 x 112 px copy of it:
"Master" sits right-aligned under the wordmark, in the wordmark's blue, its cap
height 0.407 of the wordmark's height and its ink width 0.389 of the wordmark's
width, 8 px (0.148 of the wordmark's height) below it. Arimo Bold (SIL OFL,
Arial's metrics) sets the word at that cap height with its letters drawn
closer, to meet that width. The wordmark itself is copied untouched from the
official HES-SO artwork (HES-SO_logo_CMJN.eps, converted to SVG). Replace the
output with the official file when HES-SO supplies one.
"""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from lxml import etree
from PIL import Image

SVG = "http://www.w3.org/2000/svg"
BLUE = "#1a619a"                       # the wordmark's own "Hes"
# Measured on the template's mark, relative to the wordmark's ink box.
CAP, WIDTH, GAP = 22 / 54, 95 / 244, 8 / 54
WORD = "Master"


def ink_box(svg_path: Path, px: int = 4000) -> tuple[float, float, float, float]:
    """The wordmark's ink box in its user units, measured on a render `px` pixels wide."""
    root = etree.parse(str(svg_path)).getroot()
    x, y, w, h = map(float, root.get("viewBox").split())
    png = subprocess.run(["rsvg-convert", "-w", str(px), "-b", "white", str(svg_path)],
                         check=True, capture_output=True).stdout
    im = Image.open(io.BytesIO(png)).convert("L").point(lambda v: 255 if v < 230 else 0)  # the grey too
    l, t, r, b = im.getbbox()
    k = w / im.width
    return x + l * k, y + t * k, x + r * k, y + b * k


def master_paths(font_path: str, cap: float, width: float) -> tuple[list[str], float]:
    """SVG path data for WORD at cap height `cap`, tracked to ink width `width`; origin at the baseline's left ink edge."""
    font = TTFont(font_path)
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    scale = cap / font["OS/2"].sCapHeight
    names = [cmap[ord(c)] for c in WORD]
    bounds = []
    for n in names:
        bp = BoundsPen(glyphs)
        glyphs[n].draw(bp)
        bounds.append(bp.bounds)
    advances = [glyphs[n].width for n in names]
    natural = sum(advances[:-1]) + bounds[-1][2] - bounds[0][0]
    track = (width / scale - natural) / (len(WORD) - 1)      # font units per gap, negative: closer
    paths, x = [], -bounds[0][0]
    for n, adv in zip(names, advances):
        pen = SVGPathPen(glyphs)
        glyphs[n].draw(pen)
        paths.append(f'<path d="{pen.getCommands()}" transform="scale({scale:.6f},{-scale:.6f}) '
                     f'translate({x:.1f},0)"/>')
        x += adv + track
    return paths, track


def main(wordmark: Path, font_path: str, out: Path) -> int:
    x0, y0, x1, y1 = ink_box(wordmark)
    ww, wh = x1 - x0, y1 - y0
    cap, width = CAP * wh, WIDTH * ww
    paths, track = master_paths(font_path, cap, width)
    baseline = y1 + GAP * wh + cap
    left = x1 - width

    src = etree.parse(str(wordmark)).getroot()
    keep = [el for el in src if etree.QName(el).localname in ("defs", "g", "path")]  # the dot is a bare path
    vb = (x0 - 2, y0 - 2, ww + 4, baseline - y0 + 4)
    root = etree.Element(f"{{{SVG}}}svg", nsmap={None: SVG}, attrib={
        "viewBox": " ".join(f"{v:.3f}" for v in vb),
        "width": f"{vb[2]:.3f}pt", "height": f"{vb[3]:.3f}pt"})
    root.append(etree.Comment(" HES-SO Master: the HES-SO wordmark (official artwork, untouched) with "
                              "'Master' in Arimo Bold below it, after the HES-SO Master slide template; "
                              "composed by tools/master-logo.py. "))
    for el in keep:
        for attr in list(el.attrib):
            if "}" in attr and not attr.startswith(f"{{{SVG}}}"):
                del el.attrib[attr]                # inkscape and sodipodi attributes
        root.append(el)
    word = etree.fromstring(f'<g xmlns="{SVG}" fill="{BLUE}" transform="translate({left:.3f},{baseline:.3f})">'
                            + "".join(paths) + "</g>")
    root.append(word)
    etree.cleanup_namespaces(root)
    out.write_bytes(etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True))
    print(f"{out}: viewBox {root.get('viewBox')}; 'Master' cap {cap:.2f}, width {width:.2f}, "
          f"tracking {track:.0f} font units per gap")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])))
