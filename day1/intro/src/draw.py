#!/usr/bin/env python3
"""Draw the hand-authored figures of the intro deck as themeable, stepwise SVGs.

    python3 day1/intro/src/draw.py day1/intro/images

Shapes that follow the theme carry the remark engine's `accent-*` classes
(`ext/svg-theme.js`) and a literal fill, shown when no script runs. Groups
carry `data-step` for `ext/stepwise-svg.js`. The last step of every figure
shows everything, because a printed deck shows only the final step.

Palette (remark/themes/hesso-master.css): accent #00609c, accent-a-light
#8cb3cf, accent-b #25bcca, accent-b-light #a8e4ea; slate #1c2e36 and #556268.
"""

from __future__ import annotations

import sys
from pathlib import Path

INK, MUTED, WHITE = "#1c2e36", "#556268", "#ffffff"
ACCENT, A_LIGHT, B, B_LIGHT = "#00609c", "#8cb3cf", "#25bcca", "#a8e4ea"
FONT = "Inter, Arimo, Helvetica, sans-serif"

# Machine Learning Canvas regions, as the week-1 annotation names them.
REGION = {
    "goal": ("accent-fill", ACCENT),
    "predict": ("accent-a-light-fill", A_LIGHT),
    "learn": ("accent-b-fill", B),
    "evaluate": ("accent-b-light-fill", B_LIGHT),
}


def svg(w: int, h: int, body: list[str], comment: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}">\n'
        f"<!-- {comment} -->\n"
        "<defs>\n"
        f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>\n'
        f'<marker id="ahA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="accent-fill" d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>\n'
        "</defs>\n" + "\n".join(body) + "\n</svg>\n"
    )


def step(n: int, items: list[str], hide: str | None = None) -> str:
    extra = f' data-hide="{hide}"' if hide else ""
    return f'<g data-step="{n}"{extra}>\n' + "\n".join(items) + "\n</g>"


def rect(x, y, w, h, fill=WHITE, stroke=ACCENT, cls="", rx=8, sw=1.6, extra=""):
    c = f' class="{cls}"' if cls else ""
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect{c} x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}{extra}/>'


def text(x, y, s, size=15, fill=INK, weight="normal", anchor="middle", cls="", style=""):
    c = f' class="{cls}"' if cls else ""
    st = f' font-style="{style}"' if style else ""
    return (f'<text{c} x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill}"{st}>{s}</text>')


def line(x1, y1, x2, y2, color=INK, w=1.6, marker="ah", dash="", cls=""):
    c = f' class="{cls}"' if cls else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line{c} x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d}{m}/>'


def path(d, color=INK, w=1.6, marker="ah", cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} d="{d}" fill="none" stroke="{color}" stroke-width="{w}" marker-end="url(#{marker})"/>'


# ---------------------------------------------------------------------------
def systemic_model() -> str:
    """The firm as three systems (Le Moigne 1977; drawing after Bucki & Pesqueux 1994, Fig. 2)."""
    def system(y, name, french, tx=400):
        return [rect(200, y, 400, 76, cls="accent-stroke"),
                text(tx, y + 34, name, size=22, weight="bold"),
                text(tx, y + 59, french, size=15, fill=MUTED, style="italic")]

    body = [
        step(1, system(20, "Steering system", "système de pilotage")
             + system(206, "Information system", "système d'information", tx=370)
             + system(392, "Operations system", "système opérant")),
        step(2, [
            f'<polygon class="accent-a-light-fill" points="40,418 168,418 168,406 198,430 168,454 168,442 40,442" fill="{A_LIGHT}"/>',
            f'<polygon class="accent-a-light-fill" points="602,418 732,418 732,406 762,430 732,454 732,442 602,442" fill="{A_LIGHT}"/>',
            text(104, 400, "inputs", size=15, weight="bold"),
            text(682, 400, "outputs", size=15, weight="bold"),
        ]),
        step(3, [
            line(300, 98, 300, 204), text(290, 156, "decisions", anchor="end"),
            line(300, 284, 300, 390), text(290, 342, "instructions", anchor="end"),
        ]),
        step(4, [
            line(500, 390, 500, 286), text(510, 342, "activity recorded", anchor="start"),
            line(500, 204, 500, 98), text(510, 156, "indicators", anchor="start"),
        ]),
        step(5, [
            line(40, 244, 198, 244), text(118, 234, "from outside", size=14),
            text(118, 262, "the firm", size=14),
        ]),
        step(6, [
            f'<ellipse class="accent-b-light-fill" cx="545" cy="226" rx="34" ry="9" fill="{B_LIGHT}" stroke="{INK}" stroke-width="1.2"/>',
            f'<path class="accent-b-light-fill" d="M511,226 L511,262 A34,9 0 0 0 579,262 L579,226 A34,9 0 0 1 511,226 z" fill="{B_LIGHT}" stroke="{INK}" stroke-width="1.2"/>',
            text(545, 252, "data", size=15, weight="bold"),
        ]),
        step(7, [
            rect(640, 120, 130, 52, fill=ACCENT, stroke=None, cls="accent-fill"),
            text(705, 152, "model", size=17, weight="bold", fill=WHITE),
            path("M581,250 L705,250 L705,174", color=ACCENT, marker="ahA", cls="accent-stroke"),
            path("M705,118 L705,58 L603,58", color=ACCENT, marker="ahA", cls="accent-stroke"),
            text(714, 96, "a score", anchor="start", cls="accent-fill", fill=ACCENT, weight="bold"),
        ]),
        step(8, [
            text(104, 478, "credit applications:", size=14, cls="accent-fill", fill=ACCENT, weight="bold"),
            text(104, 496, "the flow is information", size=14, cls="accent-fill", fill=ACCENT),
            text(682, 478, "credits granted", size=14, cls="accent-fill", fill=ACCENT, weight="bold"),
            text(682, 496, "or refused", size=14, cls="accent-fill", fill=ACCENT),
        ]),
    ]
    return svg(800, 505, body, "The firm as three systems: Le Moigne (1977), drawing after Bucki and "
               "Pesqueux (1994), Fig. 2. Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
CANVAS = [  # key, x, y, w, h, label lines, region, step (the CRISP-DM phase that fills it)
    ("pt", 0, 30, 120, 130, ["PREDICTION", "TASK"], "predict", 1),
    ("dec", 120, 30, 120, 130, ["DECISIONS"], "predict", 1),
    ("vp", 240, 30, 120, 260, ["VALUE", "PROPOSITION"], "goal", 1),
    ("col", 360, 30, 120, 130, ["DATA", "COLLECTION"], "learn", 2),
    ("src", 480, 30, 120, 130, ["DATA", "SOURCES"], "learn", 2),
    ("imp", 0, 160, 120, 130, ["IMPACT", "SIMULATION"], "predict", 5),
    ("mak", 120, 160, 120, 130, ["MAKING", "PREDICTIONS"], "predict", 6),
    ("bld", 360, 160, 120, 130, ["BUILDING", "MODELS"], "learn", 4),
    ("fea", 480, 160, 120, 130, ["FEATURES"], "learn", 3),
    ("mon", 120, 290, 360, 60, ["MONITORING"], "evaluate", 6),
]


def canvas_schematic() -> str:
    """Dorard's Machine Learning Canvas v1.1 as ten boxes, lit by CRISP-DM phase."""
    body = [text(0, 16, "Machine Learning Canvas v1.1 (Dorard), schematic", size=13, fill=MUTED, anchor="start")]
    for key, x, y, w, h, lines, region, k in CANVAS:
        cls, hexa = REGION[region]
        body.append(rect(x + 1, y, w, h, stroke=INK, rx=0, sw=1.2))
        body.append(step(k, [rect(x + 1, y, w, h, fill=hexa, stroke=None, cls=cls, rx=0, extra=' fill-opacity="0.35"'),
                             rect(x + 1, y, w, 8, fill=hexa, stroke=None, cls=cls, rx=0)]))
        for i, s in enumerate(lines):
            body.append(text(x + 9, y + 28 + 16 * i, s, size=12.5, weight="bold", anchor="start"))
    x = 0
    for region in ("goal", "predict", "learn", "evaluate"):
        cls, hexa = REGION[region]
        body.append(rect(x + 1, 368, 16, 16, fill=hexa, stroke=None, cls=cls, rx=2))
        body.append(text(x + 24, 381, region.upper(), size=12.5, weight="bold", anchor="start"))
        x += 130
    return svg(602, 392, body, "After L. Dorard, The Machine Learning Canvas v1.1 (ownml.co), CC BY-SA 4.0. "
               "Schematic and phase colours: Oscar Esteban, CC BY-SA 4.0.")


# ---------------------------------------------------------------------------
def kdd_to_crisp() -> str:
    """KDD's drawn steps (after Fayyad et al. 1996, Fig. 1) above the CRISP-DM phases."""
    kdd = [("Selection", 180), ("Preprocessing", 338), ("Transformation", 496),
           ("Data mining", 654), ("Interpretation /", 812)]
    top = [text(20, 24, "KDD, the figure (Fayyad et al. 1996)", size=15, fill=MUTED, anchor="start", weight="bold"),
           rect(80, 50, 72, 44, fill="#f3f3f3", stroke=MUTED, rx=22), text(116, 78, "Data", size=14),
           rect(970, 50, 96, 44, fill="#f3f3f3", stroke=MUTED, rx=22), text(1018, 78, "Knowledge", size=14)]
    for name, x in kdd:
        top.append(rect(x, 44, 128, 56, stroke=MUTED, sw=1.3))
        if name.endswith("/"):
            top += [text(x + 64, 68, "Interpretation /", size=14), text(x + 64, 86, "evaluation", size=14)]
        else:
            top.append(text(x + 64, 78, name, size=14))
    for x1, x2 in [(152, 180), (308, 338), (466, 496), (624, 654), (782, 812), (940, 970)]:
        top.append(line(x1, 72, x2 - 2, 72, color=MUTED, w=1.3))

    def phase(x, w, l1, l2=None, fill=WHITE, ink=INK, cls="accent-stroke"):
        out = [rect(x, 200, w, 56, fill=fill, cls=cls)]
        if l2:
            out += [text(x + w / 2, 224, l1, size=14, fill=ink, weight="bold"), text(x + w / 2, 242, l2, size=14, fill=ink, weight="bold")]
        else:
            out.append(text(x + w / 2, 233, l1, size=14, fill=ink, weight="bold"))
        return out

    middle = [text(20, 186, "CRISP-DM (Chapman et al. 2000)", size=15, fill=MUTED, anchor="start", weight="bold")]
    middle += phase(180, 128, "Data", "understanding") + phase(417, 128, "Data", "preparation")
    middle += phase(654, 128, "Modeling") + phase(812, 128, "Evaluation")
    for x1, x2 in [(244, 244), (402, 481), (560, 481), (718, 718), (876, 876)]:
        middle.append(line(x1, 102, x2, 197, color=MUTED, w=1.2, dash="4 4", marker=""))
    for x1, x2 in [(308, 417), (545, 654), (782, 812)]:
        middle.append(line(x1, 228, x2 - 2, 228))

    ends = phase(30, 136, "Business", "understanding", fill=ACCENT, ink=WHITE, cls="accent-fill")
    ends += phase(950, 116, "Deployment", fill=ACCENT, ink=WHITE, cls="accent-fill")
    ends += [line(166, 228, 178, 228), line(940, 228, 948, 228),
             text(98, 280, "added: the business", size=14, cls="accent-fill", fill=ACCENT, weight="bold"),
             text(98, 298, "question, before the data", size=14, cls="accent-fill", fill=ACCENT),
             text(1008, 280, "added: acting on", size=14, cls="accent-fill", fill=ACCENT, weight="bold"),
             text(1008, 298, "what was learned", size=14, cls="accent-fill", fill=ACCENT)]
    return svg(1080, 310, [step(1, top), step(2, middle), step(3, ends)],
               "KDD steps after Fayyad, Piatetsky-Shapiro and Smyth (1996), Fig. 1; CRISP-DM phases after "
               "Chapman et al. (2000). Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
def mining_vs_using() -> str:
    """Mining a model from labelled history, then using it on a new case (after Provost & Fawcett 2013, Fig. 2-1)."""
    def table(x, y, rows, target):
        out = [text(x, y - 8, "attributes", size=13, fill=MUTED, anchor="start"),
               text(x + 236, y - 8, "credit_risk", size=13, fill=MUTED, weight="bold")]
        for r in range(rows):
            yy = y + r * 24
            for c in range(4):
                out.append(rect(x + c * 46, yy, 40, 18, fill="#e9edf0", stroke=None, rx=3))
            v = target[r]
            fill, cls = {"good": (B_LIGHT, "accent-b-light-fill"), "bad": (A_LIGHT, "accent-a-light-fill")}.get(v, ("#f3f3f3", ""))
            out.append(rect(x + 200, yy, 72, 18, fill=fill, stroke=None, rx=3, cls=cls))
            out.append(text(x + 236, yy + 14, v, size=13, weight="bold"))
        return out

    def model(x, y):
        return [rect(x, y, 120, 54, fill=ACCENT, stroke=None, cls="accent-fill"),
                text(x + 60, y + 33, "model", size=17, fill=WHITE, weight="bold")]

    top = [text(0, 22, "Mining: learn from past credits whose outcome is known", size=15, weight="bold", anchor="start"),
           *table(0, 58, 4, ["good", "bad", "good", "good"]),
           line(286, 94, 344, 94),
           rect(348, 66, 170, 56, stroke=INK, sw=1.3),
           text(433, 90, "data mining", size=15, weight="bold"), text(433, 110, "Lab → Visual ML", size=13, fill=MUTED),
           line(518, 94, 576, 94), *model(580, 67)]
    bottom = [text(0, 200, "Use: score a new application, outcome unknown", size=15, weight="bold", anchor="start"),
              *table(0, 236, 1, ["?"]),
              line(286, 245, 576, 245), *model(580, 218),
              line(640, 123, 640, 214, color=MUTED, w=1.2, dash="4 4"),
              text(650, 172, "the same model", size=13, fill=MUTED, anchor="start"),
              line(700, 245, 748, 245),
              rect(752, 222, 168, 46, fill=B_LIGHT, stroke=None, cls="accent-b-light-fill"),
              text(836, 251, "P(bad) = 0.34", size=15, weight="bold")]
    return svg(925, 285, [step(1, top), step(2, bottom)],
               "After Provost and Fawcett (2013), Data Science for Business, Fig. 2-1, p. 26, redrawn on "
               "credit data; the probability is illustrative. Oscar Esteban, CC BY 4.0.")


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("systemic-model.svg", systemic_model), ("ml-canvas-schematic.svg", canvas_schematic),
                     ("kdd-to-crisp.svg", kdd_to_crisp), ("mining-vs-using.svg", mining_vs_using)):
        (out / name).write_text(fn(), encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
