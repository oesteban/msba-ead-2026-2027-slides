#!/usr/bin/env python3
"""Draw the hand-authored figures of the cross-validation deck as themeable, stepwise SVGs.

    python3 day1/03-cv/src/draw.py day1/03-cv/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), loaded from there so the decks draw alike.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("intro_draw", HERE.parents[1] / "01-intro" / "src" / "draw.py")
d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d)
svg, step, rect, text, line, path = d.svg, d.step, d.rect, d.text, d.line, d.path
INK, MUTED, WHITE, ACCENT, A_LIGHT = d.INK, d.MUTED, d.WHITE, d.ACCENT, d.A_LIGHT


def badge(x, y, n):
    return (f'<circle class="accent-fill" cx="{x}" cy="{y}" r="12" fill="{ACCENT}"/>'
            + text(x, y + 5, str(n), size=14, weight="bold", fill=WHITE))


def frame(x, y, w, h):
    return rect(x, y, w, h, fill="none", stroke=ACCENT, cls="accent-stroke", rx=5, sw=2.6)


# ---------------------------------------------------------------------------
def test_kept_apart() -> str:
    """Choose on the training data by cross-validation; score the chosen model once on data kept apart."""
    x0, x1, x2 = 40, 760, 960
    base = [text(500, 26, "the 1,000 credits", size=15, weight="bold"),
            rect(x0, 40, x1 - x0, 40, fill="#e9edf0", stroke=INK, rx=0, sw=1.2),
            text((x0 + x1) / 2, 66, "training data: 800 credits", size=14),
            rect(x1, 40, x2 - x1, 40, fill="#c9cfd2", stroke=INK, rx=0, sw=1.2),
            text((x1 + x2) / 2, 66, "test data: 200", size=14, weight="bold")]
    s1 = [text((x1 + x2) / 2, 100, "kept apart, not opened", size=13, fill=MUTED)]
    fw = (x1 - x0) / 5
    rows = []
    for i in range(5):
        y = 118 + 20 * i
        for j in range(5):
            on = i == j
            rows.append(rect(x0 + j * fw + 2, y, fw - 4, 15, fill=ACCENT if on else "#e9edf0",
                             stroke=None, rx=2, cls="accent-fill" if on else ""))
    s2 = rows + [text((x0 + x1) / 2, 236, "cross-validation on the training data: compare algorithms, their settings "
                                          "(hyperparameters) and thresholds", size=13),
                 text((x0 + x1) / 2, 254, "and keep the best", size=13)]
    s3 = [path(f"M{x1 - 2},216 L{x1 - 2},270 L{x1 + 10},270", w=1.6),
          rect(x1 + 14, 248, 186, 44, fill=ACCENT, stroke=None, cls="accent-fill"),
          text(x1 + 107, 268, "scored once on the test:", size=12, fill=WHITE),
          text(x1 + 107, 285, "the number to report", size=13, weight="bold", fill=WHITE),
          path(f"M{(x1 + x2) / 2},106 L{(x1 + x2) / 2},244", w=1.4)]
    return svg(1000, 310, base + [step(1, s1), step(2, s2), step(3, s3)],
               "Model selection with a test set kept apart: choices made by cross-validation on the training data, "
               "one final score on the test data (after Provost and Fawcett 2013, pp. 134 to 135). "
               "Oscar Esteban, CC BY 4.0.")


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


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"test-kept-apart.svg": test_kept_apart, "decision-chart.svg": decision_chart}
    for name, lit in (("mo", {"MO"}), ("dp", {"DP"}), ("mo-ev", {"MO", "EV"})):
        figures[f"phase-{name}.svg"] = lambda lit=lit: d.phase_thumb(lit)
    for name, fn in figures.items():
        (out / name).write_text(fn(), encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
