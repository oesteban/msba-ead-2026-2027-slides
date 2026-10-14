#!/usr/bin/env python3
"""Draw the hand-authored figures of the intro deck as themeable, stepwise SVGs.

    python3 day1/intro/src/draw.py day1/intro/images

Shapes that follow the theme carry the remark engine's `accent-*` classes
(`ext/svg-theme.js`) and a literal fill, shown when no script runs. Groups
carry `data-step` for `ext/stepwise-svg.js`. The last step of every figure
shows everything, because a printed deck shows only the final step; the frames
over the week-1 canvas are the exception, cleared at their last step.

Palette (remark/themes/hesso-master.css): accent #00609c, accent-a-light
#8cb3cf, accent-b #25bcca, accent-b-light #a8e4ea; slate #1c2e36 and #556268.
"""

from __future__ import annotations

import sys
from pathlib import Path

INK, MUTED, WHITE = "#1c2e36", "#556268", "#ffffff"
ACCENT, A_LIGHT, B, B_LIGHT = "#00609c", "#8cb3cf", "#25bcca", "#a8e4ea"
FONT = "Inter, Arimo, Helvetica, sans-serif"

# The week-1 canvas (Data science 1, p. 7): Dorard's v1.1 with four regions drawn on it. The crop is
# images/ml-canvas-week1.png, 1840 x 1458 px; boxes in its pixels, and the CRISP-DM phase that fills each
# (a reading, not Dorard's).
WEEK1 = ("ml-canvas-week1.png", 1840, 1458)
CANVAS = [  # key, x0, y0, x1, y1, step
    ("pt", 11, 90, 384, 614, 1), ("dec", 384, 90, 745, 614, 1), ("vp", 745, 90, 1106, 1145, 1),
    ("col", 1106, 90, 1464, 614, 2), ("src", 1464, 90, 1827, 614, 2), ("fea", 1464, 614, 1827, 1369, 3),
    ("bld", 1106, 614, 1464, 1145, 4), ("imp", 11, 614, 384, 1369, 5), ("mak", 384, 614, 745, 1145, 6),
    ("mon", 384, 1145, 1464, 1369, 6),
]


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
def canvas_course() -> str:
    """The week-1 canvas, untouched, with a frame on the boxes of the phase lit on the flowchart."""
    src, w, h = WEEK1
    body = [f'<image href="{src}" x="0" y="0" width="{w}" height="{h}"/>']
    for k in range(1, 7):
        frames = [rect(x0 + 9, y0 + 9, x1 - x0 - 18, y1 - y0 - 18, fill="none", stroke=ACCENT, cls="accent-stroke",
                       rx=4, sw=18) for _, x0, y0, x1, y1, step_ in CANVAS if step_ == k]
        body.append(step(k, frames, hide=f"{k + 1}-end"))
    body.append('<g data-step="7"></g>')  # the last step clears the frames
    return svg(w, h, body, "L. Dorard, The Machine Learning Canvas v1.1 (ownml.co), CC BY-SA 4.0, with the regions "
               "drawn on it in week 1 of the EAD module; cropped. Frames: Oscar Esteban, CC BY-SA 4.0.")


# ---------------------------------------------------------------------------
def kdd_to_crisp() -> str:
    """KDD's drawn steps (after Fayyad et al. 1996, Fig. 1) above the CRISP-DM phases."""
    kdd = [("Selection", 180), ("Preprocessing", 338), ("Transformation", 496),
           ("Data mining", 654), ("Interpretation /", 812)]
    top = [text(20, 24, "Knowledge Discovery in Databases (KDD), the figure (Fayyad et al. 1996)", size=15, fill=MUTED, anchor="start", weight="bold"),
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


# ---------------------------------------------------------------------------
def sensimed_timeline() -> str:
    """SENSIMED: the record above the arrow, D. Genoud's 2025 stages below it."""
    x = {"2003": 60, "2010": 200, "2011": 310, "2012": 420, "2013": 530, "2014": 640, "2016": 760, "2018": 1000}
    y0, y1 = 233, 267                                       # the arrow's body

    def block(cx, y, lines, anchor="middle", conn=None):
        """A heading and its lines; `conn` draws a line from (cx, conn[0]) to the arrow."""
        out = [text(cx, y, lines[0], size=17, weight="bold", anchor=anchor, cls="accent-fill", fill=ACCENT)]
        out += [text(cx, y + 21 * (i + 1), s_, size=16, anchor=anchor) for i, s_ in enumerate(lines[1:])]
        if conn:
            out.insert(0, line(conn[1], conn[0], conn[1], y0 - 2, color=MUTED, w=1.4, marker="", dash="3 3"))
        return out

    def genoud(cx, lines):
        out = [line(cx, y1 + 2, cx, y1 + 16, color=MUTED, w=1.4, marker="")]
        out += [text(cx, y1 + 38 + 20 * i, s_, size=16, fill=MUTED, style="italic") for i, s_ in enumerate(lines)]
        return out

    arrow = [f'<polygon class="accent-fill" points="30,{y0} 1088,{y0} 1088,{y0 - 15} 1116,250 1088,{y1 + 15} '
             f'1088,{y1} 30,{y1}" fill="{ACCENT}"/>',
             f'<path d="M122,{y1 + 4} L134,{y0 - 4} M134,{y1 + 4} L146,{y0 - 4}" stroke="{WHITE}" stroke-width="5"/>']
    arrow += [text(v, 256, k, size=15, weight="bold", fill=WHITE) for k, v in x.items()]
    arrow += [text(1062, 256, "now", size=15, weight="bold", fill=WHITE),
              text(22, 40, "The record", size=16, weight="bold", fill=MUTED, anchor="start"),
              text(22, y1 + 38, "As D. Genoud's", size=15, fill=MUTED, anchor="start", weight="bold"),
              text(22, y1 + 58, "team told it", size=15, fill=MUTED, anchor="start", weight="bold")]
    s1 = arrow + block(22, 140, ["A device", "EPFL spin-off: a contact", "lens records the eye's",
                                 "volume over 24 hours"], anchor="start", conn=(212, x["2003"]))
    s2 = genoud(x["2010"], ["Device"]) + genoud(x["2011"], ["Signal", "processing"]) + \
        genoud(x["2012"], ["Information", "system"])
    s3 = ([rect(x["2014"] - 22, y0, x["2016"] - x["2014"] + 44, y1 - y0, fill=B, stroke=None, cls="accent-b-fill", rx=0,
                extra=' fill-opacity="0.85"'),
           text(x["2014"], 256, "2014", size=15, weight="bold", fill=WHITE),
           text(x["2016"], 256, "2016", size=15, weight="bold", fill=WHITE)]
          + block(700, 40, ["A platform", "HES-SO Valais-Wallis:", "machine learning on", "the 24-hour profiles"],
                  conn=(108, 700))
          + block(772, 140, ["A narrower use", "US marketing to time", "eye-pressure checks;",
                             "not a diagnostic tool"], anchor="start", conn=(124, x["2016"]))
          + genoud(585, ["Machine learning,", "data mining,", "new features"])
          + genoud(x["2016"], ["Speed of disease", "prediction"]))
    s4 = (block(1000, 40, ["An evaluation", "glaucoma or healthy, AUC:", "lens 0.61, pressure 0.68,", "both 0.76"],
                conn=(108, x["2018"]))
          + genoud(1050, ["Improvement,", "deep learning"]))
    return svg(1120, 380, [step(1, s1), step(2, s2), step(3, s3), step(4, s4)],
               "SENSIMED, above the arrow from its record (CTI 17325.1; FDA 2016; Martin et al. 2018), below it "
               "after D. Genoud's 2025 slide. Oscar Esteban, CC BY 4.0.")


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("systemic-model.svg", systemic_model), ("ml-canvas-course.svg", canvas_course),
                     ("kdd-to-crisp.svg", kdd_to_crisp), ("mining-vs-using.svg", mining_vs_using),
                     ("sensimed-timeline.svg", sensimed_timeline)):
        (out / name).write_text(fn(), encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
