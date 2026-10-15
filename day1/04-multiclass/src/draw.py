#!/usr/bin/env python3
"""Draw the hand-authored figures of the multi-class deck as themeable, stepwise SVGs.

    python3 day1/04-multiclass/src/draw.py day1/04-multiclass/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), loaded from there so the decks draw alike. The
numbers of the wine's three lines come from `day1/figures-numbers.json`
(`tools/figures.py --wine`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("intro_draw", HERE.parents[1] / "01-intro" / "src" / "draw.py")
d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d)
svg, step, rect, text, line, path = d.svg, d.step, d.rect, d.text, d.line, d.path
INK, MUTED, WHITE, ACCENT, A_LIGHT, B, B_LIGHT = d.INK, d.MUTED, d.WHITE, d.ACCENT, d.A_LIGHT, d.B, d.B_LIGHT
GREY, GREY_INK = "#e9edf0", "#9aa4a8"
# the four outcomes, in the hues of the credit decks: right decisions in the accent, errors in red
TP_C, TN_C, FP_C, FN_C = ACCENT, A_LIGHT, "#f0a3a8", "#da232f"
NUMBERS = HERE.parents[1] / "figures-numbers.json"
LINE_FILL = {"low": (A_LIGHT, "accent-a-light-fill"), "medium": ("#b9c2c6", ""), "high": (ACCENT, "accent-fill")}


def three() -> dict:
    return json.loads(NUMBERS.read_text())["wine"]["three"]


# ---------------------------------------------------------------------------
def class_probs() -> str:
    """One credit, two probabilities and a threshold; one wine, three probabilities and the largest."""
    ex = three()["example"]
    W, H, base, top = 1040, 360, 268, 40
    hgt = base - top

    def bar(x, p, label, fill, cls, bold=False, w=78):
        h = round(p * hgt, 1)
        return [rect(x, base - h, w, h, fill=fill, stroke=None, rx=3, cls=cls),
                text(x + w / 2, base - h - 10, f"{p:.2f}", size=20, weight="bold" if bold else "normal"),
                text(x + w / 2, base + 26, label, size=18, weight="bold" if bold else "normal")]

    left = [line(0, base, 420, base, color=MUTED, w=1.4, marker=""),
            *bar(90, 0.34, "bad", ACCENT, "accent-fill", bold=True),
            *bar(250, 0.66, "good", A_LIGHT, "accent-a-light-fill"),
            line(76, base - 0.17 * hgt, 182, base - 0.17 * hgt, color=FN_C, w=2.4, marker="", dash="7 5"),
            text(70, base - 0.17 * hgt + 6, "threshold", size=16, anchor="end", fill=FN_C),
            text(225, base + 62, "one credit: P(bad), and a threshold", size=18, fill=MUTED),
            text(225, top - 14, "two classes (deck 2)", size=20, weight="bold")]
    p = ex["proba"]
    win = max(range(3), key=lambda k: p[k])
    right = [line(570, base, 1010, base, color=MUTED, w=1.4, marker="")]
    for k, (name, x) in enumerate(zip(["low", "medium", "high"], [600, 740, 880])):
        fill, cls = LINE_FILL[name]
        right += bar(x, p[k], name, fill, cls, bold=(k == win))
    right += [rect(728, top + 2, 102, base - top + 40, fill="none", stroke=ACCENT, cls="accent-stroke", rx=6, sw=2.4),
              text(790, base + 62, "one wine: three probabilities, the largest wins", size=18, fill=MUTED),
              text(790, top - 14, "three classes", size=20, weight="bold")]
    body = [step(1, ['<g transform="translate(44 0)">', *left, "</g>"]), step(2, right)]
    return svg(W, H, body, f"One credit (deck 1's example, P(bad) = 0.34) against one wine of the course file (line "
               f"{ex['row']}, a {ex['color']} wine of grade {ex['grade']}): its three probabilities from a random forest "
               "under 5-fold cross-validation (tools/figures.py). Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
# illustrative points for one-vs-rest: three groups at the corners of a triangle
PTS = {"low": [(1.0, 1.2), (1.6, 0.7), (2.1, 1.6), (0.8, 2.1), (2.4, 0.9), (1.5, 2.4)],
       "medium": [(5.2, 1.0), (6.0, 1.7), (4.6, 1.6), (5.6, 0.6), (6.4, 1.1), (4.9, 2.2)],
       "high": [(3.0, 4.6), (3.7, 5.2), (3.4, 3.9), (2.6, 5.3), (4.2, 4.4), (3.9, 3.6)]}
# each class against the rest: a straight boundary, given by two points (data units)
OVR = {"low": ((0.2, 3.6), (3.8, 0.0)), "medium": ((3.2, 0.0), (6.8, 3.4)), "high": ((0.0, 3.1), (7.0, 3.1))}


def one_vs_rest() -> str:
    """Three one-vs-rest boundaries, then the regions they make together."""
    W, H, pw, ph, gap, top = 1100, 320, 230, 220, 40, 34
    sx, sy = pw / 7.0, ph / 6.0

    def panel(i):
        x0 = 20 + i * (pw + gap)
        return x0, (lambda u, v: (round(x0 + u * sx, 1), round(top + ph - v * sy, 1)))

    def dots(to, lit=None):
        out = []
        for name, pts in PTS.items():
            fill, cls = LINE_FILL[name] if lit in (None, name) else (GREY, "")
            for u, v in pts:
                x, y = to(u, v)
                out.append(f'<circle{" class=" + chr(34) + cls + chr(34) if cls else ""} cx="{x}" cy="{y}" r="7" '
                           f'fill="{fill}" stroke="{WHITE}" stroke-width="1.2"/>')
        return out

    body = []
    for i, name in enumerate(["low", "medium", "high"]):
        x0, to = panel(i)
        (u0, v0), (u1, v1) = OVR[name]
        (xa, ya), (xb, yb) = to(u0, v0), to(u1, v1)
        body.append(step(i + 1, [rect(x0, top, pw, ph, fill=WHITE, stroke="#c9cfd2", rx=4, sw=1.2), *dots(to, name),
                                 line(xa, ya, xb, yb, color=INK, w=2.4, marker=""),
                                 text(x0 + pw / 2, top + ph + 32, f"{name} against the rest", size=17, weight="bold")]))
    x0, to = panel(3)
    c = to(3.45, 2.55)
    corners = {"low": [to(0, 0), to(3.45, 0), c, to(0, 3.4)], "medium": [to(3.45, 0), to(7, 0), to(7, 3.4), c],
               "high": [to(0, 3.4), c, to(7, 3.4), to(7, 6), to(0, 6)]}
    regions = [rect(x0, top, pw, ph, fill=WHITE, stroke="#c9cfd2", rx=4, sw=1.2)]
    for name, poly in corners.items():
        fill, cls = LINE_FILL[name]
        regions.append(f'<polygon{" class=" + chr(34) + cls + chr(34) if cls else ""} '
                       f'points="{" ".join(f"{x},{y}" for x, y in poly)}" fill="{fill}" opacity="0.28"/>')
    regions += dots(to) + [text(x0 + pw / 2, top + ph + 32, "together: three regions", size=17, weight="bold"),
                           text(x0 + pw / 2, top + ph + 56, "each point goes to the most confident", size=15,
                                fill=MUTED)]
    body.append(step(4, regions))
    return svg(W, H, body, "One-vs-rest on eighteen illustrative points in two attributes: one binary model per "
               "class, each separating it from the others; together they split the inputs into three regions. "
               "Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
def confusion_3() -> str:
    """The 3 x 3 confusion matrix of the three lines; the high line's row and column; deck 2's 2 x 2 for it."""
    t = three()
    cm, labels = t["confusion"], t["labels"]
    W, H, cw, chh, x0, y0 = 1090, 400, 128, 78, 150, 92
    body = [text(x0 + 1.5 * cw, 30, "predicted", size=18, weight="bold"),
            f'<text x="34" y="{y0 + 1.5 * chh}" font-size="18" font-weight="bold" text-anchor="middle" fill="{INK}" '
            f'transform="rotate(-90 34 {y0 + 1.5 * chh})">actual</text>']
    for j, lab in enumerate(labels):
        body.append(text(x0 + j * cw + cw / 2, y0 - 16, lab, size=17))
        body.append(text(x0 - 14, y0 + j * chh + chh / 2 + 6, lab, size=17, anchor="end"))
    for i in range(3):
        for j in range(3):
            diag = i == j
            body += [rect(x0 + j * cw, y0 + i * chh, cw, chh, fill=A_LIGHT if diag else WHITE, stroke="#c9cfd2",
                          rx=0, sw=1.2, cls="accent-a-light-fill" if diag else ""),
                     text(x0 + j * cw + cw / 2, y0 + i * chh + chh / 2 + 8, f"{cm[i][j]:,}", size=22,
                          weight="bold" if diag else "normal")]
    body.append(text(x0 + 1.5 * cw, y0 + 3 * chh + 34, "the diagonal: right; elsewhere: one class taken for another",
                     size=16, fill=MUTED))
    h = labels.index("high")
    tp = cm[h][h]
    fn = sum(cm[h]) - tp
    fp = sum(r[h] for r in cm) - tp
    tn = sum(map(sum, cm)) - tp - fn - fp
    body = [step(1, body)]
    body.append(step(2, [rect(x0, y0 + h * chh, 3 * cw, chh, fill="none", stroke=FN_C, rx=2, sw=3),
                         rect(x0 + h * cw, y0, cw, 3 * chh, fill="none", stroke=FP_C, rx=2, sw=3)]))
    bx, by, bw, bh = 690, 92, 170, 96
    cells = [("TP", tp, TP_C, WHITE, "high, called high", 0, 0),
             ("FN", fn, FN_C, WHITE, "high, called lower", 0, 1),
             ("FP", fp, FP_C, INK, "lower, called high", 1, 0),
             ("TN", tn, TN_C, INK, "lower, called lower", 1, 1)]
    two = [text(bx + bw, 30, "high against the rest", size=18, weight="bold"),
           text(bx + bw / 2, by - 16, "called high", size=15), text(bx + 1.5 * bw, by - 16, "not called high", size=15)]
    for name, n, fill, ink, what, r, c in cells:
        x, y = bx + c * bw, by + r * bh
        two += [rect(x, y, bw, bh, fill=fill, stroke=WHITE, rx=0, sw=2),
                text(x + bw / 2, y + 36, f"{name} {n:,}", size=22, weight="bold", fill=ink),
                text(x + bw / 2, y + 66, what, size=14, fill=ink)]
    two += [text(bx + bw, by + 2 * bh + 40, f"precision {tp / (tp + fp):.2f}, recall {tp / (tp + fn):.2f}",
                 size=19, weight="bold"),
            text(bx + bw, by + 2 * bh + 68, "deck 2's matrix, once per class", size=16, fill=MUTED),
            path(f"M {x0 + 3 * cw + 8} {y0 + 2.6 * chh} C 600 {y0 + 2.6 * chh}, 620 {by + bh}, {bx - 10} {by + bh}",
                 color=MUTED, w=1.6)]
    body.append(step(3, two))
    return svg(W, H, body, "Confusion matrix of the wine's three lines (low: grade 5 or less, medium: 6, high: 7 or "
               "more), 5,320 distinct wines, a random forest under 5-fold cross-validation (tools/figures.py); the "
               "high line folded into the binary matrix of deck 2. Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
def quality_grade() -> str:
    """The new target is a rule applied to the old one: whoever sees quality knows grade."""
    W, H, dx = 700, 420, 34
    grade = {3: "low", 4: "low", 5: "low", 6: "medium", 7: "high", 8: "high", 9: "high"}
    ys = {q: 44 + i * 48 for i, q in enumerate(range(3, 10))}
    gy = {"low": 92, "medium": 188, "high": 284}
    body = [text(90 + dx, 24, "quality (an input)", size=22, weight="bold"),
            text(560 + dx, 24, "grade (the target)", size=22, weight="bold")]
    for q, y in ys.items():
        g = grade[q]
        fill, cls = LINE_FILL[g]
        body += [rect(60 + dx, y - 4, 60, 36, fill=WHITE, stroke="#c9cfd2", rx=4, sw=1.2),
                 text(90 + dx, y + 21, str(q), size=22),
                 line(124 + dx, y + 14, 476 + dx, gy[g] + 11, color=MUTED, w=1.6, marker="ah")]
    for g, y in gy.items():
        fill, cls = LINE_FILL[g]
        body += [rect(482 + dx, y - 12, 156, 46, fill=fill, stroke=None, rx=6, cls=cls),
                 text(560 + dx, y + 19, g, size=23, weight="bold", fill=WHITE if g == "high" else INK)]
    body.append(text(350, 412, "one rule, no exceptions: whoever reads quality never misses", size=20,
                     fill=MUTED))
    return svg(W, H, body, "The Formula of Hands-on 3 turns quality into grade; left in as an input, quality gives "
               "the target away. Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
def twins() -> str:
    """A wine in the training folds and its exact copy in the test fold."""
    W, H, x0, y0, cw, ch = 980, 190, 40, 40, 176, 54
    body = []
    for k in range(5):
        test = k == 4
        body.append(rect(x0 + k * (cw + 6), y0, cw, ch, fill=A_LIGHT if test else GREY, stroke=None, rx=3,
                         cls="accent-a-light-fill" if test else ""))
        body.append(text(x0 + k * (cw + 6) + cw / 2, y0 - 12, "test fold" if test else f"training fold {k + 1}",
                         size=15, weight="bold" if test else "normal", fill=INK if test else MUTED))
    a = (x0 + 1 * (cw + 6) + 60, y0 + ch / 2)
    b = (x0 + 4 * (cw + 6) + 110, y0 + ch / 2)
    body += [f'<circle class="accent-fill" cx="{a[0]}" cy="{a[1]}" r="11" fill="{ACCENT}"/>',
             f'<circle class="accent-fill" cx="{b[0]}" cy="{b[1]}" r="11" fill="{ACCENT}"/>',
             f'<path d="M {a[0]} {a[1] + 14} C {a[0]} {y0 + ch + 60}, {b[0]} {y0 + ch + 60}, {b[0]} {b[1] + 14}" '
             f'fill="none" stroke="{FN_C}" stroke-width="2.2"/>',
             text((a[0] + b[0]) / 2, y0 + ch + 68, "the same wine, twice: the model is tested on a row it has learned",
                  size=17, fill=FN_C)]
    return svg(W, H, body, "Five folds of the wine file with its duplicates left in: a row in training and its exact "
               "copy in the test fold. Illustrative. Oscar Esteban, CC BY 4.0.")


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"class-probs.svg": class_probs, "one-vs-rest.svg": one_vs_rest, "confusion-3.svg": confusion_3,
               "quality-grade.svg": quality_grade, "twins.svg": twins}
    for name, lit in (("du", {"DU"}), ("dp", {"DP"}), ("mo", {"MO"}), ("ev", {"EV"}), ("du-mo", {"DU", "DP", "MO"})):
        figures[f"phase-{name}.svg"] = lambda lit=lit: d.phase_thumb(lit)
    for name, fn in figures.items():
        (out / name).write_text(fn(), encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
