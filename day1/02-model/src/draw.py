#!/usr/bin/env python3
"""Draw the hand-authored figures of the evaluation deck as themeable, stepwise SVGs.

    python3 day1/02-model/src/draw.py day1/02-model/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), loaded from there so both decks draw alike.
Numbers come from `day1/figures-numbers.json`, written by `tools/figures.py`.
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
INK, MUTED, WHITE, ACCENT, A_LIGHT, B_LIGHT = d.INK, d.MUTED, d.WHITE, d.ACCENT, d.A_LIGHT, d.B_LIGHT
WARN, WARN_LIGHT = "#da232f", "#f0a3a8"

NUMBERS = json.loads((HERE.parents[1] / "figures-numbers.json").read_text())["credit"]


# ---------------------------------------------------------------------------
def decision_rule() -> str:
    """One application through a binary classifier: attributes, two probabilities, one threshold, one class."""
    rows = [("status", "no checking account"), ("duration", "18 months"), ("purpose", "car (used)"),
            ("amount", "1,049 DM"), ("savings", "unknown or none"), ("age", "21"), ("…", "…")]
    card = [rect(20, 40, 300, 236, fill="#f4f6f7", stroke=MUTED, rx=6, sw=1.2),
            text(170, 28, "a new application", size=15, weight="bold")]
    for i, (k, v) in enumerate(rows):
        card += [text(36, 72 + 26 * i, k, size=13, fill=MUTED, anchor="start"),
                 text(150, 72 + 26 * i, v, size=13, anchor="start")]
    card += [line(30, 252, 310, 252, color="#c9cfd2", w=1, marker=""),
             text(36, 268, "credit_risk", size=13, fill=MUTED, anchor="start", weight="bold"),
             text(150, 268, "?  not known yet", size=13, anchor="start", weight="bold",
                  cls="accent-fill", fill=ACCENT)]
    model = [line(320, 158, 356, 158), rect(360, 128, 110, 60, fill=ACCENT, stroke=None, cls="accent-fill"),
             text(415, 164, "model", size=17, weight="bold", fill=WHITE)]
    s1 = [line(470, 158, 506, 158),
          rect(510, 100, 170, 50, fill=WARN_LIGHT, stroke=None, rx=6), text(595, 131, "P(bad) = 0.34", size=16, weight="bold"),
          rect(510, 166, 170, 50, fill=A_LIGHT, stroke=None, rx=6, cls="accent-a-light-fill"),
          text(595, 197, "P(good) = 0.66", size=16, weight="bold"),
          text(595, 240, "the two add up to 1", size=13, fill=MUTED)]
    s2 = [path("M680,125 L716,125", w=1.6),
          rect(720, 92, 260, 66, fill=WHITE, stroke=INK, rx=6, sw=1.4),
          text(850, 118, "the decision rule", size=13, fill=MUTED),
          text(850, 144, "bad if P(bad) &gt; t", size=17, weight="bold"),
          text(850, 186, "with t = 0.5: 0.34 is not above 0.5", size=13),
          line(850, 194, 850, 214),
          rect(745, 218, 210, 48, fill=A_LIGHT, stroke=None, rx=6, cls="accent-a-light-fill"),
          text(850, 248, "class: good → grant", size=16, weight="bold")]
    s3 = [text(500, 312, "Two classes: one threshold, on the probability of the positive class. "
                         "More classes: the most probable class wins.", size=14, fill=INK)]
    return svg(1000, 330, [step(1, card + model), step(2, s1), step(3, s2), step(4, s3)],
               "A binary classifier ends in a decision rule: a threshold on the probability of the positive class. "
               "Attributes from row 1 of the course file (South German Credit, UCI 573, CC BY 4.0); the probability "
               "is an example. Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
def classification_duration() -> str:
    """The intro deck's mining-versus-using figure (after P&F Fig. 2-1), on credit, with one attribute.

    The model holds the number of good and bad credits per duration (curves from tools/figures.py);
    where they cross, a credit is as likely bad as good: the threshold. A new application is placed
    on the same curves."""
    m = NUMBERS["duration_model"]
    months, good, bad = m["months"], m["good"], m["bad"]
    tint = {"good": (A_LIGHT, "accent-a-light-fill"), "bad": (WARN_LIGHT, "")}

    def table(x, y, rows, caption):
        out = [text(x, y - 8, "duration (months)", size=13, fill=MUTED, anchor="start"),
               text(x + 150, y - 8, "credit_risk", size=13, fill=MUTED, weight="bold")]
        for r, (dur, risk) in enumerate(rows):
            yy = y + r * 24
            out.append(rect(x, yy, 96, 18, fill="#e9edf0", stroke=None, rx=3))
            out.append(text(x + 48, yy + 14, dur, size=13))
            fill, cls = tint.get(risk, ("#f3f3f3", ""))
            out.append(rect(x + 112, yy, 76, 18, fill=fill, stroke=None, rx=3, cls=cls))
            out.append(text(x + 150, yy + 14, risk, size=13, weight="bold"))
        out.append(text(x, y + len(rows) * 24 + 12, caption, size=13, fill=MUTED, anchor="start", style="italic"))
        return out

    def model(x, y, w=270, h=110, mark=None):
        x0, x1, base, top = x + 12, x + w - 12, y + h - 22, y + 18
        peak = max(max(good), max(bad))
        px = lambda v: x0 + (v - months[0]) / (months[-1] - months[0]) * (x1 - x0)
        py = lambda c: base - c / peak * (base - top)
        out = [rect(x, y, w, h, fill=WHITE, stroke=ACCENT, cls="accent-stroke", sw=2)]
        for name, ys, (fill, cls), lab_at in (("good", good, tint["good"], 14), ("bad", bad, tint["bad"], 48)):
            pts = [(px(a), py(b)) for a, b in zip(months, ys)]
            d = f"M{pts[0][0]:.1f},{base} " + " ".join(f"L{a:.1f},{b:.1f}" for a, b in pts) + f" L{pts[-1][0]:.1f},{base} z"
            out.append(f'<path class="{cls}" d="{d}" fill="{fill}" fill-opacity="0.75" stroke="{INK}" stroke-width="1"/>')
            k = min(range(len(months)), key=lambda i: abs(months[i] - lab_at))
            out.append(text(px(lab_at), py(ys[k]) - 4, name, size=12, weight="bold"))
        t = m["threshold"]
        out += [line(x0, base, x1, base, w=1.2, marker=""),
                line(px(t), top - 8, px(t), base, color=INK, w=1.6, dash="5 3", marker=""),
                text(px(t), base + 15, f"threshold {t:.0f} months", size=11, fill=MUTED)]
        if mark is not None:
            out += [line(px(mark), top + 4, px(mark), base, color=ACCENT, w=3, marker="", cls="accent-stroke"),
                    text(px(mark), y - 7, f"new application: {mark} months", size=13, weight="bold",
                         cls="accent-fill", fill=ACCENT)]
        return out

    new, pbad = m["new_case"], m["p_bad_new"]
    top = [text(0, 22, "Mining: learn from past credits whose outcome is known", size=15, weight="bold", anchor="start"),
           *table(0, 52, [("18", "good"), ("36", "bad"), ("12", "good"), ("18", "bad"), ("...", "...")],
                  "every outcome known"),
           line(196, 106, 232, 106),
           rect(236, 80, 150, 52, stroke=INK, sw=1.3),
           text(311, 111, "data mining", size=15, weight="bold"),
           line(386, 106, 426, 106), *model(430, 50)]
    bottom = [text(0, 228, "Use: predict the outcome of a new application", size=15, weight="bold", anchor="start"),
              *table(0, 262, [(str(new), "?")], "outcome unknown"),
              line(196, 271, 426, 271), *model(430, 220, mark=new),
              line(452, 161, 452, 218, color=MUTED, w=1.2, dash="4 4", marker=""),
              text(444, 196, "the same model", size=13, fill=MUTED, anchor="end"),
              line(700, 271, 728, 271),
              rect(732, 242, 188, 58, fill=A_LIGHT, stroke=None, cls="accent-a-light-fill"),
              text(826, 266, "class: good", size=15, weight="bold"),
              text(826, 288, f"P(bad) = {pbad:.2f}", size=15, weight="bold")]
    return svg(925, 340, [step(1, top), step(2, bottom)],
               "After Provost and Fawcett (2013), Data Science for Business, Fig. 2-1, p. 26, redrawn on South German "
               "Credit (UCI 573, CC BY 4.0) with one attribute: the number of good and bad credits per duration, "
               "smoothed. Oscar Esteban, CC BY 4.0.")


# ---------------------------------------------------------------------------
def expected_value_numbers() -> str:
    """Deck 1's expected-cost figure (after P&F Fig. 7-2), now with the credit model's numbers at threshold 0.5."""
    m, n = NUMBERS["cm_05"], NUMBERS["n"]
    cells = [[m["tp"], m["fn"]], [m["fp"], m["tn"]]]          # rows: was bad, was good; columns: refuse, grant
    costs = [[0, 5], [1, 0]]

    def grid(x, y, cw, ch, vals, fill=WHITE, cls="", header=True, bold=None):
        out = []
        if header:
            out += [text(x + cw / 2, y - 8, "refuse", size=13, fill=MUTED, weight="bold"),
                    text(x + cw * 1.5, y - 8, "grant", size=13, fill=MUTED, weight="bold"),
                    text(x - 8, y + ch / 2 + 5, "bad", size=13, fill=MUTED, weight="bold", anchor="end"),
                    text(x - 8, y + ch * 1.5 + 5, "good", size=13, fill=MUTED, weight="bold", anchor="end")]
        for r in range(2):
            for c in range(2):
                f = fill(r, c) if callable(fill) else fill
                out.append(rect(x + c * cw, y + r * ch, cw, ch, fill=f, stroke=INK, cls=cls, rx=0, sw=1.2))
                wt = "bold" if bold and bold(r, c) else "normal"
                out.append(text(x + c * cw + cw / 2, y + r * ch + ch / 2 + 6, vals[r][c], size=16, weight=wt))
        return out

    tint = {(0, 0): A_LIGHT, (0, 1): WARN, (1, 0): WARN_LIGHT, (1, 1): "#dbe7f0"}
    s1 = [text(150, 30, f"the {n:,} credits, cut at 0.5", size=15, weight="bold"),
          *grid(70, 60, 80, 48, [[str(v) for v in r] for r in cells],
                fill=lambda r, c: WHITE if (r, c) != (0, 1) else "#f7d3d6"),
          line(240, 108, 290, 108), text(265, 98, f"÷ {n:,}", size=13, fill=MUTED),
          *grid(300, 60, 80, 48, [[f"{v / n:.3f}" for v in r] for r in cells], fill="#e9edf0", header=False),
          text(380, 30, "rates", size=15, weight="bold"),
          text(230, 200, "from the data", size=15, weight="bold", fill=MUTED)]
    s2 = [text(620, 30, "cost per credit", size=15, weight="bold"),
          *grid(540, 60, 80, 48, [[str(v) for v in r] for r in costs], fill=B_LIGHT, cls="accent-b-light-fill"),
          text(620, 200, "from the business", size=15, weight="bold", cls="accent-fill", fill=ACCENT),
          text(620, 222, "a bad credit granted costs 5, a good customer refused costs 1", size=12, fill=MUTED)]
    fn_r, fp_r = m["fn"] / n, m["fp"] / n
    s3 = [line(470, 108, 500, 108, marker=""), text(485, 100, "×", size=18, weight="bold"),
          line(710, 108, 760, 108),
          rect(770, 70, 210, 76, fill=ACCENT, stroke=None, cls="accent-fill"),
          text(875, 102, f"{NUMBERS['exp_cost_05']:.3f}", size=24, weight="bold", fill=WHITE),
          text(875, 128, "expected cost per application", size=12, fill=WHITE),
          text(500, 280, f"{fn_r:.3f} × 5  +  {fp_r:.3f} × 1  =  {NUMBERS['exp_cost_05']:.3f}", size=18, weight="bold"),
          text(500, 306, "multiply each rate by its cost, then add; the right decisions cost nothing", size=13,
               fill=MUTED)]
    return svg(1000, 320, [step(1, s1), step(2, s2), step(3, s3)],
               "After Provost and Fawcett (2013), Data Science for Business, Fig. 7-2, p. 197, with the credit "
               "model's decisions at threshold 0.5 (South German Credit, scores of credits the model did not learn "
               "from) and the Statlog cost matrix; rows are the outcome and columns the decision. "
               "Oscar Esteban, CC BY 4.0.")


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"classification-duration.svg": classification_duration, "decision-rule.svg": decision_rule,
               "expected-value-numbers.svg": expected_value_numbers}
    for name, lit in (("mo", {"MO"}), ("ev", {"EV"})):
        figures[f"phase-{name}.svg"] = lambda lit=lit: d.phase_thumb(lit)
    for name, fn in figures.items():
        (out / name).write_text(fn(), encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
