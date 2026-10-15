#!/usr/bin/env python3
"""Draw the hand-authored figures of the cross-validation deck as themeable, stepwise SVGs.

    python3 day1/03-cv/src/draw.py day1/03-cv/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), loaded from there so the decks draw alike.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("intro_draw", HERE.parents[1] / "01-intro" / "src" / "draw.py")
d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d)
svg, step, rect, text, line, path = d.svg, d.step, d.rect, d.text, d.line, d.path
INK, MUTED, WHITE, ACCENT, A_LIGHT, B, B_LIGHT = d.INK, d.MUTED, d.WHITE, d.ACCENT, d.A_LIGHT, d.B, d.B_LIGHT
GREY = "#e9edf0"
NUMBERS = HERE.parents[1] / "figures-numbers.json"


def badge(x, y, n):
    return (f'<circle class="accent-fill" cx="{x}" cy="{y}" r="12" fill="{ACCENT}"/>'
            + text(x, y + 5, str(n), size=14, weight="bold", fill=WHITE))


def frame(x, y, w, h):
    return rect(x, y, w, h, fill="none", stroke=ACCENT, cls="accent-stroke", rx=5, sw=2.6)


# ---------------------------------------------------------------------------
def cell(x, y, w, h, test=False, inner=False):
    """One fold. A test fold is two-toned in the data's mix, 70 good (light) to 30 bad (dark),
    so that a stratified fold shows it keeps the mix; an inner validation fold is cyan."""
    if inner:
        return [rect(x, y, w, h, fill=B_LIGHT, stroke=None, rx=2, cls="accent-b-light-fill")]
    if not test:
        return [rect(x, y, w, h, fill=GREY, stroke=None, rx=2)]
    g = round(w * 0.7, 1)
    return [rect(x, y, g, h, fill=A_LIGHT, stroke=None, rx=0, cls="accent-a-light-fill"),
            rect(x + g, y, w - g, h, fill=ACCENT, stroke=None, rx=0, cls="accent-fill")]


def legend(x, y, items, size=14):
    out = []
    for fill, cls, label in items:
        out += [rect(x, y - 12, 16, 16, fill=fill, stroke=None, rx=2, cls=cls),
                text(x + 24, y + 1, label, size=size, anchor="start", fill=MUTED)]
        x += 34 + 8.2 * len(label)
    return out


def k_fold() -> str:
    """Five folds, each tested once; stratified, so each test fold keeps the 70/30 mix."""
    x0, w, k = 140, 700, 5
    fw = w / k
    body = [text(x0 + w / 2, 24, "the 1,000 credits: 700 good, 300 bad", size=16, weight="bold"),
            *cell(x0, 36, w, 34, test=True),
            text(x0 + w * 0.35, 59, "good: 70%", size=15, fill=INK),
            text(x0 + w * 0.85, 59, "bad: 30%", size=15, fill=WHITE, weight="bold")]
    for i in range(k):
        y = 100 + 44 * i
        body.append(text(x0 - 16, y + 21, f"run {i + 1}", size=15, anchor="end"))
        for j in range(k):
            body += cell(x0 + j * fw + 3, y, fw - 6, 30, test=(i == j))
        body.append(text(x0 + w + 16, y + 21, f"score {i + 1}", size=15, anchor="start"))
    body.append(text(x0 + w / 2, 342, "each test fold holds 200 credits, 140 good and 60 bad: the mix of the whole",
                     size=14, fill=MUTED))
    body += legend(x0 + 40, 372, [(GREY, "", "learns from"), (A_LIGHT, "accent-a-light-fill", "tested on: good"),
                                  (ACCENT, "accent-fill", "tested on: bad")])
    return svg(1000, 384, body, "K-fold cross-validation with five stratified folds: each fold is tested once while "
               "the model learns from the four others, and each keeps the data's 70/30 mix. Oscar Esteban, CC BY 4.0.")


def test_kept_apart() -> str:
    """Choose on the training data by cross-validation; score the chosen model once on data kept apart."""
    x0, x1, x2 = 40, 760, 960
    base = [text(500, 26, "the 1,000 credits", size=17, weight="bold"),
            rect(x0, 40, x1 - x0, 44, fill=GREY, stroke=INK, rx=0, sw=1.2),
            text((x0 + x1) / 2, 68, "training data: 800 credits", size=16),
            *cell(x1, 40, x2 - x1, 44, test=True),
            rect(x1, 40, x2 - x1, 44, fill="none", stroke=INK, rx=0, sw=1.2),
            text((x1 + x2) / 2, 68, "test: 200", size=16, weight="bold", fill=WHITE)]
    s1 = [text((x1 + x2) / 2, 106, "kept apart, not opened", size=15, fill=MUTED)]
    fw = (x1 - x0) / 5
    rows = []
    for i in range(5):
        y = 126 + 28 * i
        for j in range(5):
            rows += cell(x0 + j * fw + 3, y, fw - 6, 22, test=(i == j))
    s2 = rows + [text((x0 + x1) / 2, 284, "cross-validation on the training data: compare algorithms, their settings "
                                          "(hyperparameters) and thresholds,", size=15),
                 text((x0 + x1) / 2, 304, "and keep the best", size=15)]
    s3 = [path(f"M{x1 - 2},264 L{x1 - 2},330 L{x1 + 10},330", w=1.6),
          rect(x1 + 14, 304, 186, 52, fill=ACCENT, stroke=None, cls="accent-fill"),
          text(x1 + 107, 326, "scored once on the test:", size=14, fill=WHITE),
          text(x1 + 107, 346, "the number to report", size=15, weight="bold", fill=WHITE),
          path(f"M{(x1 + x2) / 2},112 L{(x1 + x2) / 2},300", w=1.4)]
    return svg(1000, 366, base + [step(1, s1), step(2, s2), step(3, s3)],
               "Model selection with a test set kept apart: choices made by cross-validation on the training data, "
               "one final score on the test data (after Provost and Fawcett 2013, pp. 134 to 135); folds and test "
               "stratified. Oscar Esteban, CC BY 4.0.")


def nested() -> str:
    """Nested cross-validation: an outer loop scores, an inner loop inside each outer run chooses."""
    x0, w, k = 120, 420, 5
    fw = w / k
    outer = [text(x0 + w / 2, 24, "outer loop: five runs, each tests one fold", size=16, weight="bold")]
    for i in range(k):
        y = 40 + 46 * i
        outer.append(text(x0 - 14, y + 21, f"run {i + 1}", size=15, anchor="end"))
        for j in range(k):
            outer += cell(x0 + j * fw + 3, y, fw - 6, 30, test=(i == j))
    # step 2: the inner loop of run 1, zoomed: its four training folds, each validated once
    zx, zy, zw = 640, 40, 320
    iw = zw / 4
    inner = [rect(x0 + fw, 36, w - fw, 38, fill="none", stroke=INK, rx=4, sw=1.4, extra=' stroke-dasharray="5 4"'),
             path(f"M{x0 + w - 40},36 C{x0 + w - 20},14 {zx - 60},14 {zx - 10},{zy + 16}", w=1.4),
             text(zx + zw / 2, zy + 2, "inner loop of run 1: its 800 training credits", size=15, weight="bold")]
    for i in range(4):
        y = zy + 18 + 36 * i
        for j in range(4):
            inner += cell(zx + j * iw + 3, y, iw - 6, 24, inner=(i == j))
    inner += [text(zx + zw / 2, zy + 172, "each algorithm and setting is scored", size=14, fill=MUTED),
              text(zx + zw / 2, zy + 190, "on these four folds; the best is kept", size=14, fill=MUTED),
              rect(zx + 30, zy + 204, zw - 60, 40, fill=ACCENT, stroke=None, cls="accent-fill"),
              text(zx + zw / 2, zy + 229, "then scored once on run 1's test fold", size=14, fill=WHITE, weight="bold")]
    # step 3: every run does the same; five outer scores
    every = []
    for i in range(k):
        y = 40 + 46 * i
        every.append(text(x0 + w + 14, y + 21, f"score {i + 1}", size=15, anchor="start", weight="bold",
                          fill=ACCENT, cls="accent-fill"))
    every += [text(x0 + w / 2, 286, "every run chooses on its own training folds, then tests its choice:",
                   size=15),
              text(x0 + w / 2, 306, "five scores of the whole procedure, the choosing included", size=15,
                   weight="bold")]
    body = outer + [step(2, inner), step(3, every)]
    body += legend(zx, 322, [(A_LIGHT, "accent-a-light-fill", "outer test"),
                             (B_LIGHT, "accent-b-light-fill", "inner validation")], size=13)
    return svg(1000, 334, body, "Nested cross-validation: an inner loop inside each outer run chooses the model; "
               "the outer folds score the choice (after Provost and Fawcett 2013, p. 135; Esteban et al. 2017, "
               "p. 11). Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
def svm_margin() -> str:
    """The widest margin between two groups of points; the points on its edges are the support vectors."""
    W, H, top, left, ph, pw = 560, 440, 16, 30, 340, 500
    m = 1.1
    n = (-1 / math.sqrt(2), 1 / math.sqrt(2))
    a = (1 / math.sqrt(2), 1 / math.sqrt(2))

    def pos(t, s_):
        u, v = 0.9 + t * a[0] + s_ * n[0], 0.5 + t * a[1] + s_ * n[1]
        return left + u * 48, top + ph - v * 48

    bad = ((1.6, 1.1), (4.4, 1.1), (2.6, 2.3), (5.4, 1.9), (3.4, 3.4), (6.0, 3.0), (1.6, 3.1))
    good = ((3.0, -1.1), (2.0, -2.0), (4.6, -2.2), (6.0, -1.5), (3.6, -3.4), (5.4, -3.6), (6.8, -2.9))
    body = ['<defs><clipPath id="svm-plot">'
            f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}"/></clipPath></defs>',
            '<g clip-path="url(#svm-plot)">']
    band = [pos(-2, -m), pos(11, -m), pos(11, m), pos(-2, m)]
    body.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in band)}" fill="{B_LIGHT}" '
                f'class="accent-b-light-fill" opacity="0.55"/>')
    for s_ in (-m, m, 0):
        (xa, ya), (xb, yb) = pos(-2, s_), pos(11, s_)
        body.append(line(round(xa, 1), round(ya, 1), round(xb, 1), round(yb, 1), color=INK if s_ == 0 else MUTED,
                         w=2.4 if s_ == 0 else 1.4, marker="", dash="" if s_ == 0 else "6 5"))
    body.append("</g>")
    for pts, fill, cls in ((bad, ACCENT, "accent-fill"), (good, A_LIGHT, "accent-a-light-fill")):
        for t, s_ in pts:
            x, y = pos(t, s_)
            body.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{fill}"/>')
            if abs(abs(s_) - m) < 1e-9:
                body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="14" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    body += [text(left + 12, top + 26, "bad", size=17, anchor="start", weight="bold", fill=ACCENT, cls="accent-fill"),
             text(left + pw - 12, top + ph - 14, "good", size=17, anchor="end", weight="bold", fill=MUTED),
             text(W / 2, top + ph + 34, "the boundary: the middle of the widest band free of points", size=17),
             text(W / 2, top + ph + 60, "ringed: the support vectors, the points that fix the band", size=17,
                  fill=MUTED)]
    return svg(W, H, body, "A support vector machine's margin on fourteen illustrative points: the boundary sits in "
               "the middle of the widest band free of points; the ringed points fix it. Oscar Esteban, CC BY 4.0.")


QUESTION = {"status_200 DM or more or salary for at least 1 year": "checking account: 200 DM or more,",
            "duration": "duration",
            "amount": "amount"}


def tree() -> str:
    """A depth-2 classification tree of the credit data (tools/figures.py), then the forest it belongs to."""
    nodes = json.loads(NUMBERS.read_text())["credit"]["tree"]
    assert [n["feature"] for n in nodes] == ["status_200 DM or more or salary for at least 1 year", "duration", None,
                                             None, "amount", None, None], "the tree changed: redraw by hand"

    def box(x, y, lines, accent=False, w=250, h=58):
        out = [rect(x - w / 2, y, w, h, fill=ACCENT if accent else WHITE, stroke=ACCENT, cls="accent-stroke", rx=8)]
        for k, (s_, size, weight) in enumerate(lines):
            out.append(text(x, y + 24 + 20 * k, s_, size=size, weight=weight, fill=WHITE if accent else INK))
        return out

    def leaf(x, y, n):
        share = n["bad"] / n["n"]
        return box(x, y, [(f"{n['n']} credits", 15, "bold"), (f"{share:.0%} bad", 15, "normal")], w=140, h=58)

    root, dur, amt = nodes[0], nodes[1], nodes[4]
    body = box(340, 10, [("Checking account at 200 DM", 15, "bold"), ("or more, or a salary for a year?", 15, "bold")])
    body += [line(280, 68, 160, 110, marker="ah"), text(205, 86, "no", size=14, anchor="end", fill=MUTED),
             line(400, 68, 520, 110, marker="ah"), text(475, 86, "yes", size=14, anchor="start", fill=MUTED)]
    body += box(160, 112, [(f"duration over {dur['threshold']:g} months?", 15, "bold"),
                           (f"{dur['n']} credits, {dur['bad'] / dur['n']:.0%} bad", 14, "normal")])
    body += box(520, 112, [(f"amount over {amt['threshold']:,.0f} DM?", 15, "bold"),
                           (f"{amt['n']} credits, {amt['bad'] / amt['n']:.0%} bad", 14, "normal")])
    for x_parent, kids in ((160, (nodes[2], nodes[3])), (520, (nodes[5], nodes[6]))):
        for k, (n, lab) in enumerate(zip(kids, ("no", "yes"))):
            xc = x_parent - 92 + 184 * k
            body += [line(x_parent - 40 + 80 * k, 170, xc, 214, marker="ah"),
                     text(xc + (-12 if k == 0 else 12), 196, lab, size=13, anchor="end" if k == 0 else "start",
                          fill=MUTED)]
            body += leaf(xc, 216, n)
    forest = [line(700, 150, 734, 150, marker="ah"),
              rect(740, 60, 252, 190, fill=WHITE, stroke=ACCENT, cls="accent-stroke", rx=10)]
    for k in range(3):
        cx = 786 + 80 * k
        forest += [f'<circle class="accent-fill" cx="{cx}" cy="96" r="9" fill="{ACCENT}"/>',
                   line(cx, 105, cx - 20, 128, marker=""), line(cx, 105, cx + 20, 128, marker=""),
                   f'<circle cx="{cx - 20}" cy="134" r="7" fill="{A_LIGHT}" class="accent-a-light-fill"/>',
                   f'<circle cx="{cx + 20}" cy="134" r="7" fill="{A_LIGHT}" class="accent-a-light-fill"/>']
    forest += [text(866, 82, "…", size=16, fill=MUTED),
               text(866, 172, "500 trees, each grown on", size=14),
               text(866, 190, "a resample of the credits,", size=14),
               text(866, 208, "each question from a few", size=14),
               text(866, 226, "columns drawn at random", size=14),
               text(866, 280, "the forest's P(bad): the average", size=14, weight="bold"),
               text(866, 298, "of the 500 trees' answers", size=14, weight="bold")]
    return svg(1000, 310, body + [step(2, forest)],
               "A classification tree of depth 2 fitted to the 1,000 credits of South German Credit (scikit-learn), "
               "then a random forest as many such trees on resampled credits. Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
def decision_chart() -> str:
    """Dataiku's decision chart, with three numbered frames: the curves, the gain and its cut-off, the bands."""
    w, h = 1552, 356
    body = [f'<image href="dataiku/decision-chart.png" x="0" y="0" width="{w}" height="{h}"/>',
            step(1, [frame(1132, 59, 212, 22), badge(1132, 59, 1)]),
            step(2, [frame(1349, 59, 110, 22), frame(316, 76, 36, 242), badge(316, 76, 2)]),
            step(3, [frame(852, 80, 452, 218), badge(852, 80, 3)])]
    return svg(w, h, body, "Screen capture of Dataiku DSS (Performance, Decision chart; a support vector machine "
               "with cross-validation and the cost matrix gain), course server, 14 October 2026; frames by Oscar Esteban.")


# ---------------------------------------------------------------------------
def results_capture() -> str:
    """Dataiku's Results list, cropped to the metric and two models, with three numbered frames."""
    w, h = 650, 214
    body = [f'<image href="dataiku/results-session5.png" x="0" y="0" width="{w}" height="{h}"/>',
            step(1, [frame(378, 54, 250, 30), badge(378, 54, 1)]),
            step(2, [frame(331, 179, 38, 26), badge(331, 179, 2)]),
            step(3, [frame(370, 179, 50, 26), badge(420, 179, 3)])]
    return svg(w, h, body, "Screen capture of Dataiku DSS (Results, sessions view), course server, 14 October 2026, "
               "cropped and joined; frames by Oscar Esteban.")


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"results-capture.svg": results_capture, "test-kept-apart.svg": test_kept_apart,
               "decision-chart.svg": decision_chart, "k-fold.svg": k_fold, "nested.svg": nested,
               "svm-margin.svg": svm_margin, "tree.svg": tree}
    for name, lit in (("mo", {"MO"}), ("dp", {"DP"}), ("ev", {"EV"}), ("mo-ev", {"MO", "EV"})):
        figures[f"phase-{name}.svg"] = lambda lit=lit: d.phase_thumb(lit)
    for name, fn in figures.items():
        (out / name).write_text(fn(), encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
