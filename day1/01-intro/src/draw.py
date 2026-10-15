#!/usr/bin/env python3
"""Draw the hand-authored figures of the intro deck as themeable, stepwise SVGs.

    python3 day1/01-intro/src/draw.py day1/01-intro/images

Shapes that follow the theme carry the remark engine's `accent-*` classes
(`ext/svg-theme.js`) and a literal fill, shown when no script runs. Groups
carry `data-step` for `ext/stepwise-svg.js`. The last step of every figure
shows everything, because a printed deck shows only the final step; the frames
over the week-1 canvas are the exception, cleared at their last step.

Palette (remark/themes/hesso-master.css): accent #00609c, accent-a-light
#8cb3cf, accent-b #25bcca, accent-b-light #a8e4ea; slate #1c2e36 and #556268.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

INK, MUTED, WHITE = "#1c2e36", "#556268", "#ffffff"
ACCENT, A_LIGHT, B, B_LIGHT = "#00609c", "#8cb3cf", "#25bcca", "#a8e4ea"
FONT = "Inter, Arimo, Helvetica, sans-serif"

# The week-1 canvas (Data science 1, p. 7): Dorard's v1.1 with four regions drawn on it. The crop is
# images/ml-canvas-week1.png, 1840 x 1458 px; boxes in its pixels, and the steps (CRISP-DM phases, 1 to 6)
# at which each is framed (a reading, not Dorard's): value proposition at business understanding and again at
# deployment; the PREDICT boxes with building models at modeling; monitoring at evaluation.
WEEK1 = ("ml-canvas-week1.png", 1840, 1458)
CANVAS = [  # key, x0, y0, x1, y1, steps
    ("vp", 745, 90, 1106, 1145, (1, 6)),
    ("col", 1106, 90, 1464, 614, (2,)), ("src", 1464, 90, 1827, 614, (2,)), ("fea", 1464, 614, 1827, 1369, (3,)),
    ("pt", 11, 90, 384, 614, (4,)), ("dec", 384, 90, 745, 614, (4,)), ("bld", 1106, 614, 1464, 1145, (4,)),
    ("imp", 11, 614, 384, 1369, (4,)), ("mak", 384, 614, 745, 1145, (4,)),
    ("mon", 384, 1145, 1464, 1369, (5,)),
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
        step(9, [
            text(712, 274, "learned from past cases:", size=14),
            text(712, 293, "supervised learning,", size=15, cls="accent-fill", fill=ACCENT, weight="bold"),
            text(712, 311, "16.10 and 23.10", size=14, cls="accent-fill", fill=ACCENT),
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
                       rx=4, sw=18) for _, x0, y0, x1, y1, steps in CANVAS if k in steps]
        body.append(step(k, frames, hide=f"{k + 1}-end"))
    body.append('<g data-step="7"></g>')  # the last step clears the frames
    return svg(w, h, body, "L. Dorard, The Machine Learning Canvas v1.1 (ownml.co), CC BY-SA 4.0, with the regions "
               "drawn on it in week 1 of the EAD module; cropped. Frames: Oscar Esteban, CC BY-SA 4.0.")


# ---------------------------------------------------------------------------
def kdd_to_crisp() -> str:
    """KDD's drawn steps (after Fayyad et al. 1996, Fig. 1) above the CRISP-DM phases, wrapped by the business."""
    kdd = [("Selection", 180), ("Preprocessing", 338), ("Transformation", 496),
           ("Data mining", 654), ("Interpretation /", 812)]
    top = [text(30, 40, "Knowledge Discovery in Databases (KDD), after Fayyad et al. 1996", size=15, fill=MUTED, anchor="start", weight="bold"),
           rect(80, 64, 72, 44, fill="#f3f3f3", stroke=MUTED, rx=22), text(116, 92, "Data", size=14),
           rect(970, 64, 96, 44, fill="#f3f3f3", stroke=MUTED, rx=22), text(1018, 92, "Knowledge", size=14)]
    for name, x in kdd:
        top.append(rect(x, 58, 128, 56, stroke=MUTED, sw=1.3))
        if name.endswith("/"):
            top += [text(x + 64, 82, "Interpretation /", size=14), text(x + 64, 100, "evaluation", size=14)]
        else:
            top.append(text(x + 64, 92, name, size=14))
    for x1, x2 in [(152, 180), (308, 338), (466, 496), (624, 654), (782, 812), (940, 970)]:
        top.append(line(x1, 86, x2 - 2, 86, color=MUTED, w=1.3))

    def phase(x, w, l1, l2=None, fill=WHITE, ink=INK, cls="accent-stroke"):
        out = [rect(x, 172, w, 50, fill=fill, cls=cls)]
        if l2:
            out += [text(x + w / 2, 193, l1, size=14, fill=ink, weight="bold"), text(x + w / 2, 211, l2, size=14, fill=ink, weight="bold")]
        else:
            out.append(text(x + w / 2, 202, l1, size=14, fill=ink, weight="bold"))
        return out

    middle = [text(560, 254, "CRISP-DM (Chapman et al. 2000)", size=15, fill=MUTED, weight="bold")]
    middle += phase(180, 128, "Data", "understanding") + phase(417, 128, "Data", "preparation")
    middle += phase(654, 128, "Modeling") + phase(812, 128, "Evaluation")
    for x1, x2 in [(244, 244), (402, 481), (560, 481), (718, 718), (876, 876)]:
        middle.append(line(x1, 116, x2, 169, color=MUTED, w=1.2, dash="4 4", marker=""))
    for x1, x2 in [(308, 417), (545, 654), (782, 812)]:
        middle.append(line(x1, 197, x2 - 2, 197))

    ends = [f'<rect class="accent-stroke" x="6" y="12" width="1068" height="262" rx="18" fill="none" '
            f'stroke="{ACCENT}" stroke-width="2.4" stroke-dasharray="8 5"/>',
            rect(460, 1, 160, 24, fill=WHITE, stroke=None, rx=4),
            text(540, 19, "the business", size=16, cls="accent-fill", fill=ACCENT, weight="bold")]
    ends += phase(30, 136, "Business", "understanding", fill=ACCENT, ink=WHITE, cls="accent-fill")
    ends += phase(950, 116, "Deployment", fill=ACCENT, ink=WHITE, cls="accent-fill")
    ends += [line(166, 197, 178, 197), line(940, 197, 948, 197),
             text(98, 244, "the question,", size=14, cls="accent-fill", fill=ACCENT, weight="bold"),
             text(98, 262, "before the data", size=14, cls="accent-fill", fill=ACCENT),
             text(1008, 244, "the use of", size=14, cls="accent-fill", fill=ACCENT, weight="bold"),
             text(1008, 262, "the model", size=14, cls="accent-fill", fill=ACCENT)]
    return svg(1080, 280, [step(1, top), step(2, middle), step(3, ends)],
               "KDD steps after Fayyad, Piatetsky-Shapiro and Smyth (1996), Fig. 1; CRISP-DM phases after "
               "Chapman et al. (2000). Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
# Slide 3's illustration: heights of women and men as two normal curves (illustrative, not measured).
HEIGHT = {"female": (164.0, 7.0), "male": (178.0, 7.0)}
H_RANGE = (140.0, 202.0)


def _pdf(x: float, mu: float, sd: float) -> float:
    return math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))


def _p_male(h: float) -> float:
    m, f = _pdf(h, *HEIGHT["male"]), _pdf(h, *HEIGHT["female"])
    return m / (m + f)


def _threshold() -> float:
    lo, hi = HEIGHT["female"][0], HEIGHT["male"][0]
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _p_male(mid) < 0.5 else (lo, mid)
    return (lo + hi) / 2


def gauss_model(x, y, w=250, h=104, mark: float | None = None) -> list[str]:
    """A model box holding the two curves, the threshold between them and, if `mark`, a new case."""
    x0, x1, base, top = x + 12, x + w - 12, y + h - 22, y + 16
    peak = _pdf(HEIGHT["female"][0], *HEIGHT["female"])
    px = lambda v: x0 + (v - H_RANGE[0]) / (H_RANGE[1] - H_RANGE[0]) * (x1 - x0)
    py = lambda d: base - d / peak * (base - top)
    out = [rect(x, y, w, h, fill=WHITE, stroke=ACCENT, cls="accent-stroke", sw=2)]
    for name, (mu, sd), (fill, cls) in [("female", HEIGHT["female"], (B_LIGHT, "accent-b-light")),
                                        ("male", HEIGHT["male"], (A_LIGHT, "accent-a-light"))]:
        pts = [(px(v / 4), py(_pdf(v / 4, mu, sd))) for v in range(int(H_RANGE[0] * 4), int(H_RANGE[1] * 4) + 1)]
        d = f"M{pts[0][0]:.1f},{base} " + " ".join(f"L{a:.1f},{b:.1f}" for a, b in pts) + f" L{pts[-1][0]:.1f},{base} z"
        out.append(f'<path class="{cls}-fill" d="{d}" fill="{fill}" fill-opacity="0.75" stroke="{INK}" stroke-width="1"/>')
        out.append(text(px(mu), py(peak) - 3, name, size=12, weight="bold"))
    t = _threshold()
    out += [line(x0, base, x1, base, w=1.2, marker=""),
            line(px(t), top - 6, px(t), base, color=INK, w=1.6, dash="5 3", marker=""),
            text(px(t), base + 15, f"threshold {t:.0f} cm", size=11, fill=MUTED)]
    if mark is not None:
        out += [line(px(mark), top + 4, px(mark), base, color=ACCENT, w=3, marker="", cls="accent-stroke"),
                text(px(mark), y - 7, f"new case: {mark:.0f} cm", size=13, weight="bold",
                     cls="accent-fill", fill=ACCENT)]
    return out


def mining_vs_using(case: str) -> str:
    """Mining a model from labelled history, then using it on a new case (after Provost & Fawcett 2013, Fig. 2-1)."""
    if case == "height":
        def table(x, y, rows, caption):
            out = [text(x, y - 8, "height (cm)", size=13, fill=MUTED, anchor="start"),
                   text(x + 138, y - 8, "sex", size=13, fill=MUTED, weight="bold")]
            for r, (hgt, sex) in enumerate(rows):
                yy = y + r * 24
                out.append(rect(x, yy, 96, 18, fill="#e9edf0", stroke=None, rx=3))
                out.append(text(x + 48, yy + 14, hgt, size=13))
                fill, cls = {"female": (B_LIGHT, "accent-b-light-fill"), "male": (A_LIGHT, "accent-a-light-fill")}.get(
                    sex, ("#f3f3f3", ""))
                out.append(rect(x + 102, yy, 72, 18, fill=fill, stroke=None, rx=3, cls=cls))
                out.append(text(x + 138, yy + 14, sex, size=13, weight="bold"))
            out.append(text(x, y + len(rows) * 24 + 12, caption, size=13, fill=MUTED, anchor="start", style="italic"))
            return out

        p = _p_male(174)
        top = [text(0, 22, "Mining: learn from past cases whose class is known", size=15, weight="bold", anchor="start"),
               *table(0, 52, [("182", "male"), ("158", "female"), ("169", "female"), ("176", "male"), ("...", "...")],
                      "every value known"),
               line(184, 106, 230, 106),
               rect(234, 80, 150, 52, stroke=INK, sw=1.3),
               text(309, 111, "data mining", size=15, weight="bold"),
               line(384, 106, 446, 106), *gauss_model(450, 54)]
        bottom = [text(0, 222, "Use: predict the class of a new case", size=15, weight="bold", anchor="start"),
                  *table(0, 256, [("174", "?")], "class unknown"),
                  line(184, 265, 446, 265), *gauss_model(450, 214, mark=174),
                  line(470, 159, 470, 212, color=MUTED, w=1.2, dash="4 4", marker=""),
                  text(462, 190, "the same model", size=13, fill=MUTED, anchor="end"),
                  line(700, 265, 738, 265),
                  rect(742, 236, 180, 58, fill=A_LIGHT, stroke=None, cls="accent-a-light-fill"),
                  text(832, 260, "class: male", size=15, weight="bold"),
                  text(832, 282, f"probability {p:.2f}", size=15, weight="bold")]
        return svg(925, 330, [step(1, top), step(2, bottom)],
                   "After Provost and Fawcett (2013), Data Science for Business, Fig. 2-1, p. 26, redrawn with "
                   "height and sex; the two normal curves are illustrative (means 164 and 178 cm, standard "
                   "deviation 7 cm). Oscar Esteban, CC BY 4.0.")

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
              rect(752, 222, 168, 46, fill=A_LIGHT, stroke=None, cls="accent-a-light-fill"),
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

    # Genoud's pictures (images/sensimed/, not openly licensed), in a row under his labels, each with a leader to
    # its label: file, pixel size, the label's x, how many lines the label has, the step.
    pics = [("lens.jpg", 269, 166, x["2010"], 1, 2), ("signal.jpg", 330, 251, x["2011"], 2, 2),
            ("information-system.jpg", 415, 250, x["2012"], 2, 2), ("features.jpg", 371, 232, 585, 3, 3),
            ("workflow.jpg", 524, 336, 585, 3, 3), ("diagnostic-helper.jpg", 215, 332, x["2016"], 2, 3)]
    ph, gap, ytop = 96, 10, 374
    widths = [w * ph / h for _, w, h, *_ in pics]
    offsets = [sum(widths[:i]) + gap * i for i in range(len(pics))]
    want = [x["2010"], x["2011"], x["2012"], 530, 650, x["2016"]]          # where each picture would sit alone
    left = max(22, sum(c - w / 2 - o for c, w, o in zip(want, widths, offsets)) / len(pics))
    for (src, _, _, lx, n, k), w, o in zip(pics, widths, offsets):
        px = left + o
        item = [line(lx, y1 + 38 + 20 * (n - 1) + 8, px + w / 2, ytop - 4, color=MUTED, w=1, dash="2 3", marker=""),
                f'<image href="sensimed/{src}" x="{px:.1f}" y="{ytop}" width="{w:.1f}" height="{ph}"/>',
                rect(px, ytop, w, ph, fill="none", stroke="#c9cfd2", rx=0, sw=1)]
        (s2 if k == 2 else s3).extend(item)
    return svg(1120, ytop + ph + 6, [step(1, s1), step(2, s2), step(3, s3), step(4, s4)],
               "SENSIMED, above the arrow from its record (CTI 17325.1; FDA 2016; Martin et al. 2018), below it "
               "after D. Genoud's 2025 slide, with his team's pictures (not openly licensed; see "
               "sensimed/LICENSE.txt). Oscar Esteban, CC BY 4.0 for the drawing.")


# ---------------------------------------------------------------------------
def _ellipse_arc(cx, cy, rx, ry, a0, a1, boxes, pad=6):
    """Points along the ellipse from angle a0 to a1 (degrees, clockwise on screen), outside every box."""
    out = []
    for i in range(121):
        t = math.radians(a0 + (a1 - a0) * i / 120)
        px, py = cx + rx * math.cos(t), cy + ry * math.sin(t)
        if not any(bx - pad <= px <= bx + bw + pad and by - pad <= py <= by + bh + pad for bx, by, bw, bh in boxes):
            out.append((px, py))
    return out


def nested_cycles() -> str:
    """CRISP-DM recasts KDD's line as a cycle, with cycles inside it (after Provost & Fawcett 2013, pp. 27, 28, 34)."""
    cx, cy, rx, ry, bw, bh = 320, 282, 225, 125, 130, 40
    phases = [("BU", "Business", "understanding", -120), ("DU", "Data", "understanding", -60),
              ("DP", "Data", "preparation", 0), ("MO", "Modeling", None, 60), ("EV", "Evaluation", None, 120),
              ("DE", "Deployment", None, 180)]
    pos = {k: (cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for k, *_, a in phases}
    boxes = [(pos[k][0] - bw / 2, pos[k][1] - bh / 2, bw, bh) for k, *_ in phases]

    names = ["selection", "preprocessing", "transformation", "data mining", "interpretation"]
    s1 = [text(20, 22, "KDD: a line, from data to knowledge", size=15, weight="bold", fill=MUTED, anchor="start"),
          text(26, 46, "data", size=13, fill=MUTED, anchor="start"),
          text(614, 46, "knowledge", size=13, fill=MUTED, anchor="end"),
          line(26, 56, 612, 56, color=MUTED, w=1.6)]
    for i, n in enumerate(names):
        xx = 110 + 105 * i
        s1 += [f'<circle cx="{xx}" cy="56" r="5" fill="{MUTED}"/>', text(xx, 78, n, size=12, fill=MUTED)]

    s2 = [text(320, 118, "CRISP-DM closes the line into a cycle", size=15, weight="bold", anchor="middle",
               cls="accent-fill", fill=ACCENT)]
    angles = [a for *_, a in phases] + [240]
    for a0, a1 in zip(angles[:-1], angles[1:]):
        pts = _ellipse_arc(cx, cy, rx, ry, a0, a1, boxes)
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        s2.append(path(d, color=ACCENT, w=2.4, marker="ahA", cls="accent-stroke"))
    s2 += [text(112, 206, "the next turn", size=13, anchor="end", cls="accent-fill", fill=ACCENT, weight="bold"),
           text(112, 222, "starts again", size=13, anchor="end", cls="accent-fill", fill=ACCENT)]
    for (k, l1, l2, _), (bx, by, _, _) in zip(phases, boxes):
        s2.append(rect(bx, by, bw, bh, cls="accent-stroke"))
        if l2:
            s2 += [text(bx + bw / 2, by + 17, l1, size=13, weight="bold"), text(bx + bw / 2, by + 32, l2, size=13, weight="bold")]
        else:
            s2.append(text(bx + bw / 2, by + 25, l1, size=13, weight="bold"))

    (bux, buy), (dux, duy), (dpx, dpy), (mox, moy), (evx, evy) = (pos[k] for k in ("BU", "DU", "DP", "MO", "EV"))
    s3 = [path(f"M{dux - 40:.1f},{duy + bh / 2 + 2:.1f} Q{cx:.1f},{duy + 72:.1f} {bux + 40:.1f},{buy + bh / 2 + 4:.1f}"),
          path(f"M{mox - 20:.1f},{moy - bh / 2 - 2:.1f} Q{mox - 60:.1f},{dpy + 46:.1f} {dpx - 46:.1f},{dpy + bh / 2 + 4:.1f}"),
          f'<path d="M{evx + 16:.1f},{evy - bh / 2 - 2:.1f} L{bux + 16:.1f},{buy + bh / 2 + 6:.1f}" fill="none" '
          f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#ah)"/>',
          text(evx + 24, 318, "shortcut", size=12, fill=MUTED, anchor="start"),
          text(evx + 24, 332, "back", size=12, fill=MUTED, anchor="start"),
          text(352, 288, "cycles within", size=15, weight="bold"),
          text(352, 306, "a cycle", size=15, weight="bold")]
    return svg(640, 420, [step(1, s1), step(2, s2), step(3, s3)],
               "KDD's line (after Fayyad et al. 1996, Fig. 1) and the CRISP-DM cycle with its inner loops (after "
               "Chapman et al. 2000, Fig. 2), as Provost and Fawcett (2013) read them, pp. 27, 28 and 34. "
               "Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
def expected_value() -> str:
    """The expected cost of a credit model: rates from the data, costs from the business (after P&F Fig. 7-2).

    Only the two errors carry a cost, so no sum of money is counted twice (Provost & Fawcett 2013, p. 203)."""
    def grid(x, y, cw, ch, cells, cls="", fill=WHITE, header=True):
        out = []
        if header:
            out += [text(x + cw / 2, y - 8, "refuse", size=13, fill=MUTED, weight="bold"),
                    text(x + cw * 1.5, y - 8, "grant", size=13, fill=MUTED, weight="bold"),
                    text(x - 8, y + ch / 2 + 5, "bad", size=13, fill=MUTED, weight="bold", anchor="end"),
                    text(x - 8, y + ch * 1.5 + 5, "good", size=13, fill=MUTED, weight="bold", anchor="end")]
        for r in range(2):
            for c in range(2):
                out.append(rect(x + c * cw, y + r * ch, cw, ch, fill=fill, stroke=INK, cls=cls, rx=0, sw=1.2))
                for i, t in enumerate(cells[r][c]):
                    out.append(text(x + c * cw + cw / 2, y + r * ch + ch / 2 + 5 + 16 * (i - (len(cells[r][c]) - 1) / 2),
                                    t, size=13))
        return out

    data = [rect(20, 40, 110, 210, fill="#f3f3f3", stroke=MUTED, rx=4)]
    data += [line(30, 58 + 14 * i, 120, 58 + 14 * i, color="#c9cfd2", w=1, marker="") for i in range(13)]
    data += [line(14, 170, 136, 170, color=INK, w=2, dash="6 4", marker=""),
             text(75, 30, "past credits", size=14, weight="bold"),
             text(75, 120, "learn", size=13, weight="bold", fill=INK),
             text(75, 216, "test", size=13, weight="bold", fill=INK)]
    s1 = data + [
        line(130, 105, 176, 105), rect(180, 80, 110, 50, stroke=INK, sw=1.3), text(235, 110, "learning", size=14),
        line(290, 105, 326, 105), rect(330, 80, 100, 50, fill=ACCENT, stroke=None, cls="accent-fill"),
        text(380, 111, "model", size=16, weight="bold", fill=WHITE),
        path("M380,130 L380,160 L330,160 L330,180", w=1.6), path("M130,215 L186,215", w=1.6),
        *grid(250, 200, 80, 44, [[["refused,", "was bad"], ["granted,", "went bad"]],
                                 [["refused,", "was good"], ["granted,", "was good"]]]),
        text(330, 310, "the model's decisions on the test credits", size=13, fill=MUTED),
        line(414, 244, 466, 244), text(440, 236, "÷ all", size=12, fill=MUTED),
        *grid(470, 200, 76, 44, [[["rate"], ["rate"]], [["rate"], ["rate"]]], fill="#e9edf0", header=False),
        text(546, 310, "rates", size=13, fill=MUTED),
        text(390, 352, "from the data", size=15, weight="bold", fill=MUTED)]
    s2 = [*grid(760, 60, 104, 50, [[["no cost"], ["capital", "lost"]],
                                   [["interest", "forgone"], ["no cost"]]],
                fill=B_LIGHT, cls="accent-b-light-fill"),
          text(864, 186, "cost per credit", size=13, fill=MUTED),
          text(864, 26, "from the business", size=15, weight="bold", cls="accent-fill", fill=ACCENT)]
    s3 = [line(622, 244, 664, 244),
          f'<circle cx="690" cy="244" r="22" fill="{WHITE}" stroke="{INK}" stroke-width="1.6"/>',
          text(690, 251, "×", size=20, weight="bold"),
          path("M812,196 L812,204 L690,204 L690,218", w=1.6),
          line(712, 244, 736, 244),
          f'<circle cx="762" cy="244" r="22" fill="{WHITE}" stroke="{INK}" stroke-width="1.6"/>',
          text(762, 252, "Σ", size=20, weight="bold"),
          line(784, 244, 806, 244),
          rect(810, 218, 180, 54, fill=ACCENT, stroke=None, cls="accent-fill"),
          text(900, 241, "expected cost", size=14, weight="bold", fill=WHITE),
          text(900, 259, "per application", size=13, fill=WHITE),
          text(800, 300, "multiply each rate by its cost, then add", size=13, fill=MUTED, anchor="middle")]
    return svg(1000, 362, [step(1, s1), step(2, s2), step(3, s3)],
               "After Provost and Fawcett (2013), Data Science for Business, Fig. 7-2, p. 197, redrawn for a credit "
               "decision; rows are the outcome and columns the decision, the transpose of the book's layout. "
               "Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
# The week-1 canvas hues of each phase (strong hue, tint), as on the coloured flowchart.
PHASE_HUE = {"BU": ("#292929", "#ffffff"), "DU": ("#bad80a", "#fbffe5"), "DP": ("#bad80a", "#fbffe5"),
             "MO": ("#00187a", "#e5e5f4"), "EV": ("#ff8c00", "#f2e4da"), "DE": ("#292929", "#ffffff")}


def phase_thumb(lit: set[str]) -> str:
    """A small copy of the coloured linear flowchart, the phases in `lit` in their canvas hue, the rest greyed."""
    seq = [("BU", "Business", "understanding"), ("DU", "Data", "understanding"), ("G",), ("DP", "Data", "preparation"),
           ("MO", "Modeling", None), ("G",), ("EV", "Evaluation", None), ("G",), ("DE", "Deployment", None)]
    grey, grey_ink = "#c9cfd2", "#9aa4a8"
    body, y = [], 4
    for i, item in enumerate(seq):
        if item[0] == "G":
            body.append(f'<polygon points="60,{y} 70,{y + 8} 60,{y + 16} 50,{y + 8}" fill="{WHITE}" stroke="{grey}" stroke-width="1.4"/>')
            y += 16
        else:
            k, l1, l2 = item
            on = k in lit
            hue, tint = PHASE_HUE[k]
            body.append(rect(8, y, 104, 38, fill=tint if on else WHITE, stroke=hue if on else grey, rx=6, sw=3 if on else 1.4))
            ink, wt = (INK, "bold") if on else (grey_ink, "normal")
            if l2:
                body += [text(60, y + 16, l1, size=12, fill=ink, weight=wt), text(60, y + 30, l2, size=12, fill=ink, weight=wt)]
            else:
                body.append(text(60, y + 23, l1, size=12, fill=ink, weight=wt))
            y += 38
        if i < len(seq) - 1:
            body.append(f'<line x1="60" y1="{y}" x2="60" y2="{y + 12}" stroke="{grey}" stroke-width="1.4"/>')
            y += 12
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 {y + 4}" font-family="{FONT}">\n'
            f"<!-- The CRISP-DM phases as on the coloured flowchart, {', '.join(sorted(lit))} lit in the hues of the "
            "week-1 canvas. Oscar Esteban, CC BY 4.0. -->\n" + "\n".join(body) + "\n</svg>\n")


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"systemic-model.svg": systemic_model, "ml-canvas-course.svg": canvas_course,
               "kdd-to-crisp.svg": kdd_to_crisp, "mining-vs-using.svg": lambda: mining_vs_using("height"),
               "mining-vs-using-credit.svg": lambda: mining_vs_using("credit"),
               "nested-cycles.svg": nested_cycles, "sensimed-timeline.svg": sensimed_timeline,
               "expected-value.svg": expected_value}
    for name, lit in (("bu", {"BU"}), ("du", {"DU"}), ("mo", {"MO"}), ("du-mo", {"DU", "DP", "MO"})):
        figures[f"phase-{name}.svg"] = lambda lit=lit: phase_thumb(lit)
    for name, fn in figures.items():
        (out / name).write_text(fn(), encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
