#!/usr/bin/env python3
"""Draw the figures of the forecasting deck as themeable, stepwise SVGs.

    python3 day2/08-forecast/src/draw.py day2/08-forecast/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), and the chart helpers the time-series deck's
(`day2/07-series/src/draw.py`), loaded from there so the decks draw alike. The data
figures read what `excerpts.py` writes next to this script: the Capital Bikeshare daily
rentals (UCI dataset 275, CC BY 4.0) and `numbers.json`. The Dow Jones extract's licence is
not recorded, so only statistics computed from it are drawn. Sketches and the simulated walks
say so; the random walk is the time-series deck's own figure.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


d = _load("intro_draw", HERE.parents[2] / "day1" / "01-intro" / "src" / "draw.py")
s7 = _load("series_draw", HERE.parents[1] / "07-series" / "src" / "draw.py")
svg, step, rect, text, line, path = d.svg, d.step, d.rect, d.text, d.line, d.path
INK, MUTED, WHITE, ACCENT, A_LIGHT = d.INK, d.MUTED, d.WHITE, d.ACCENT, d.A_LIGHT
GREY, GREY_INK, EDGE, ALERT, PANEL = s7.GREY, s7.GREY_INK, s7.EDGE, s7.ALERT, s7.PANEL
Frame, poly, dots, axis_x, axis_y, panel_box = s7.Frame, s7.poly, s7.dots, s7.axis_x, s7.axis_y, s7.panel_box
esc, label, fmt, sub = s7.esc, s7.label, s7.fmt, s7.sub
LICENCE = s7.LICENCE
BIKE_DATA = s7.BIKE_DATA
SKETCH = "A drawn sketch, not data."

N = json.loads((HERE / "numbers.json").read_text())
with open(HERE / "bike.csv", newline="") as f:
    BIKE = list(csv.DictReader(f))
DATES = [r["date"] for r in BIKE]
RENTALS = [float(r["rentals"]) for r in BIKE]


def history(origin: str, days: int) -> list[float]:
    i = DATES.index(origin)
    return RENTALS[i - days + 1:i + 1]


def thin_dashed(fr: Frame, x: float, h: float | None = None) -> str:
    return line(fr.x(x), fr.y0, fr.x(x), fr.y0 + fr.h, color=GREY_INK, w=1.2, marker="", dash="5 4")


def forecast_panel(x, y, w, h, title, subtitle, hist, fc, yr, ticks, eq=""):
    """A small panel: the last weeks of rentals in grey, a forecast in the accent colour, its formula top right."""
    n = len(hist)
    fr = Frame(x + 60, y + 66, w - 84, h - 104, (0, n + len(fc) - 1), yr)
    return [panel_box(x, y, w, h), text(x + 20, y + 32, esc(title), size=19, weight="bold", anchor="start"),
            label(x + 20, y + 54, subtitle, size=15),
            text(x + w - 18, y + 34, eq, size=18, weight="bold", anchor="end", fill=ACCENT, cls="accent-fill") if eq else "",
            *axis_y(fr, ticks, size=13), thin_dashed(fr, n - 0.5),
            poly(fr, list(range(n)), hist, color=GREY_INK, w=1.4, cls=""),
            poly(fr, list(range(n, n + len(fc))), list(fc), w=3.4)]


# --- Part 1 -------------------------------------------------------------------------
def simple() -> str:
    """The four simple forecasts, two weeks ahead from the same last day."""
    W, H = 1000, 470
    b = N["bike"]
    hist = history(b["origin"], 42)
    ticks = [(0, "0"), (3000, "3,000"), (6000, "6,000")]
    spots = [(10, 8), (510, 8), (10, 240), (510, 240)]
    yh = "ŷ" + sub("T+h")
    names = (("The mean", "of every day so far", "mean", f"{yh} = ȳ"),
             ("The last value", "the naive forecast", "naive", f"{yh} = y{sub('T')}"),
             ("The same day a week before", "the seasonal naive forecast", "snaive", f"{yh} = y{sub('T+h−7')}"),
             ("The drift line", "first day to last, extended", "drift",
              f"{yh} = y{sub('T')} + h (y{sub('T')} − y{sub('1')}) / (T − 1)"))
    panels = [forecast_panel(x, y, 480, 222, t, st, hist, b["simple"][k], (0, 7200), ticks, eq=e)
              for (x, y), (t, st, k, e) in zip(spots, names)]
    return svg(W, H, [step(i + 1, p) for i, p in enumerate(panels)],
               f"The last six weeks of daily rentals to {b['origin']} (grey) and four simple forecasts of the next two "
               "weeks, after R. J. Hyndman and G. Athanasopoulos (2021), section 5.2. " + BIKE_DATA + " Drawn by "
               + LICENCE)


# --- Part 2 -------------------------------------------------------------------------
def weights() -> str:
    """Exponential smoothing's weights: falling with age, faster when alpha is large; then its formula."""
    W, H = 1000, 460
    out = []
    for i, a in enumerate((0.8, 0.2)):
        y0 = 30 + i * 175
        fr = Frame(250, y0 + 20, 700, 120, (-0.5, 11.5), (0, 0.85))
        g = [text(30, y0 + 70, f"α = {a}", size=24, weight="bold", anchor="start"),
             label(30, y0 + 98, "the weight of each past day", size=15),
             line(fr.x0, fr.y(0), fr.x0 + fr.w, fr.y(0), color=GREY_INK, w=1.2, marker="")]
        for k in range(12):
            wgt = a * (1 - a) ** k
            x = fr.x(11 - k)
            g.append(rect(x - 20, fr.y(wgt), 40, max(fr.y(0) - fr.y(wgt), 1), fill=ACCENT, stroke=None, rx=2,
                          cls="accent-fill"))
            if k < 4:
                g.append(text(x, fr.y(wgt) - 8, f"{wgt:.2f}", size=14, fill=INK))
        g += [label(fr.x(11), fr.y(0) + 24, "the last day", size=14, anchor="middle"),
              label(fr.x(0), fr.y(0) + 24, "11 days before", size=14, anchor="middle")]
        out.append(g)
    ends = [text(500, 400, f"ŷ{sub('T+1')} = α y{sub('T')} + α(1 − α) y{sub('T−1')} + α(1 − α)² y{sub('T−2')} + …",
                 size=24, weight="bold", fill=ACCENT, cls="accent-fill"),
            text(500, 442, "α = 1: all the weight on the last day, the naive forecast;   α near 0: almost equal "
                 "weights, close to the mean", size=17, fill=INK)]
    return svg(W, H, [step(1, out[0]), step(2, out[1]), step(3, ends)],
               "The weights simple exponential smoothing gives the last twelve days, α(1 - α)^k, for α = 0.8 and 0.2 "
               "(R. J. Hyndman and G. Athanasopoulos 2021, section 8.1). Drawn by " + LICENCE)


def ets() -> str:
    """Three ETS forms on the same rentals: no trend, a trend, a trend and a weekly season; the AIC chooses."""
    W, H = 1000, 410
    b = N["bike"]
    hist = history(b["origin"], 42)
    ticks = [(0, "0"), (3000, "3,000"), (6000, "6,000")]
    names = (("ETS(A,N,N)", "no trend, no season", "ANN"), ("ETS(A,A,N)", "a trend", "AAN"),
             ("ETS(A,A,A)", "a trend and a weekly season", "AAA"))
    panels = [forecast_panel(10 + i * 330, 50, 320, 300, t, s, hist, b["ets"][k], (0, 7200), ticks)
              for i, (t, s, k) in enumerate(names)]
    key = [label(500, 26, "the letters: error A or M; trend N, A or damped; season N, A or M (N none, A additive, M multiplicative)", size=16,
                 anchor="middle", fill=INK)]
    aic = [text(500, 392, "The form is chosen by the AIC: a score that rewards the fit and charges each parameter",
                size=18, weight="bold", fill=INK)]
    return svg(W, H, [step(1, key + panels[0]), step(2, panels[1]), step(3, panels[2]), step(4, aic)],
               f"Daily rentals to {b['origin']} (grey) and the two-week point forecasts of three exponential smoothing "
               "forms fitted to them with statsmodels (R. J. Hyndman and G. Athanasopoulos 2021, sections 8.4 and 8.5). "
               + BIKE_DATA + " Drawn by " + LICENCE)


def arima() -> str:
    """ARIMA's three parts; ARIMA(0,1,0) is the random walk; AutoARIMA searches the orders."""
    W, H = 1000, 420
    parts = (("AR", "p", "past values"), ("I", "d", "differences"), ("MA", "q", "past forecast errors"))
    top = []
    for i, (k, o, s) in enumerate(parts):
        x = 40 + i * 320
        top += [rect(x, 20, 280, 120, fill=PANEL, stroke=EDGE, rx=8, sw=1.4),
                text(x + 140, 66, f"{k}  ·  {o}", size=28, weight="bold", fill=ACCENT, cls="accent-fill"),
                text(x + 140, 106, s, size=19)]
    rw = [rect(40, 180, 920, 90, fill=A_LIGHT, stroke=ACCENT, rx=8, sw=2, cls="accent-a-light-fill accent-stroke"),
          text(70, 216, "ARIMA(0,1,0): one difference, no other term", size=21, weight="bold", anchor="start"),
          text(70, 250, "the random walk: its forecast is the last value", size=19, anchor="start")]
    cands = ["(0,1,0)", "(1,1,0)", "(0,1,1)", "(1,1,1)", "(2,1,2)", "..."]
    auto = [text(40, 320, "AutoARIMA: it chooses the differences, tries the other orders, keeps the lowest AICc",
                 size=18, weight="bold", anchor="start")]
    for i, c in enumerate(cands):
        x = 40 + i * 155
        on = i == 0
        auto += [rect(x, 340, 135, 46, fill=A_LIGHT if on else WHITE, stroke=ACCENT if on else GREY_INK, rx=6,
                      sw=2 if on else 1.2, cls="accent-a-light-fill accent-stroke" if on else ""),
                 text(x + 67, 370, c, size=18, weight="bold" if on else "normal")]
    return svg(W, H, [step(1, top), step(2, rw), step(3, auto)],
               "The parts of an ARIMA(p,d,q) model, the random walk as ARIMA(0,1,0), and the automatic search of "
               "R. J. Hyndman and Y. Khandakar (2008); after R. J. Hyndman and G. Athanasopoulos (2021), sections 9.5 "
               "to 9.7 and Table 9.1. Drawn by " + LICENCE)


def global_() -> str:
    """A global model learns across many related series; one series gives it nothing to share."""
    W, H = 1000, 400
    rng = random.Random(5)

    def spark(x, y, w, h, level, cls=True):
        ys = [level + 0.25 * (1 if k % 7 in (5, 6) else 0) + rng.gauss(0, 0.06) for k in range(28)]
        fr = Frame(x, y, w, h, (0, 27), (0, 1.6))
        return poly(fr, list(range(28)), ys, w=1.6, color=ACCENT if cls else GREY_INK, cls="accent-stroke" if cls else "")

    def net(x, y, sub):
        return [rect(x, y, 170, 90, fill=PANEL, stroke=INK, rx=10, sw=1.6),
                text(x + 85, y + 40, "one network", size=19, weight="bold"), text(x + 85, y + 68, sub, size=15,
                                                                                  fill=MUTED)]
    left = [text(30, 34, "Many related series", size=21, weight="bold", anchor="start")]
    for i in range(6):
        y = 56 + i * 52
        left += [spark(30, y, 190, 40, 0.5 + 0.15 * i), line(232, y + 22, 300, 200, color=GREY_INK, w=1.2)]
    left += net(306, 155, "learnt across all")
    right = [text(560, 34, "One series", size=21, weight="bold", anchor="start"),
             spark(560, 180, 190, 40, 0.9), line(762, 202, 800, 202, color=GREY_INK, w=1.2),
             *net(806, 157, "nothing to share")]
    return svg(W, H, [step(1, left), step(2, right)],
               SKETCH + " The deep models in Dataiku DSS train a single model on all the series at once (DSS 13 "
               "documentation; D. Salinas et al. 2020). Drawn by " + LICENCE)


# --- Part 3 -------------------------------------------------------------------------
def rolling() -> str:
    """Test on the future: each fold trains on the past and tests on the next horizon."""
    W, H = 1000, 420
    n, h, k = 40, 2, 4
    fr = Frame(150, 60, 820, 280, (0, n), (0, 1))
    tests = [n - h - 2 * h * j for j in range(k)][::-1]

    def row(i, o):
        y = 70 + i * 66
        return [rect(fr.x(0), y, fr.x(o) - fr.x(0), 44, fill=A_LIGHT, stroke=ACCENT, rx=3, sw=1.2,
                     cls="accent-a-light-fill accent-stroke"),
                rect(fr.x(o), y, fr.x(o + h) - fr.x(o), 44, fill=ACCENT, stroke=None, rx=3, cls="accent-fill"),
                rect(fr.x(o + h), y, fr.x(n) - fr.x(o + h), 44, fill=GREY, stroke=None, rx=3) if o + h < n else ""]
    head = [label(fr.x(0), 44, "the first day", size=16), label(fr.x(n), 44, "the last day", size=16, anchor="end"),
            text(30, 70 + (k - 1) * 66 + 29, "a split", size=17, weight="bold", anchor="start")]
    last = row(k - 1, tests[-1])
    first = [text(fr.x(tests[-1] - 4), 70 + (k - 1) * 66 + 29, "train", size=17, weight="bold"),
             label(fr.x(tests[-1]) - 8, 70 + (k - 1) * 66 - 8, "test: one horizon", size=15, anchor="end")]
    others = sum((row(i, o) for i, o in enumerate(tests[:-1])), [])
    others.append(text(30, 70 + 29, "more folds", size=17, weight="bold", anchor="start"))
    note = [label(560, 400, "DSS: the last horizon tests first, each next fold one horizon earlier; fold offset: "
                  "one more horizon between tests", size=15, anchor="middle")]
    return svg(W, H, [step(1, head + last + first), step(2, others + note)],
               "Time-ordered evaluation: each fold trains on all the days before its test set (light) and tests on the "
               "next horizon (dark); grey days are not used by that fold. After R. J. Hyndman and G. Athanasopoulos "
               "(2021), section 5.10, and the K-fold cross-test of the Dataiku DSS 13 documentation. " + SKETCH
               + " Drawn by " + LICENCE)


def leak() -> str:
    """Smoothing the whole series before the split carries the test days into training."""
    W, H = 1000, 400
    rng = random.Random(3)
    ys = [3 + 0.04 * k + rng.gauss(0, 0.5) for k in range(40)]
    fr = Frame(60, 60, 900, 230, (0, 39), (0, 7))
    cut = 27.5
    base = [rect(fr.x(cut), fr.y0, fr.x(39) - fr.x(cut), fr.h, fill=GREY, stroke=None, rx=0),
            line(fr.x(cut), fr.y0 - 10, fr.x(cut), fr.y0 + fr.h, color=INK, w=2, marker=""),
            label(fr.x(cut) - 12, fr.y0 - 18, "training", size=17, anchor="end", fill=INK),
            label(fr.x(cut) + 12, fr.y0 - 18, "test", size=17, anchor="start", fill=INK),
            poly(fr, list(range(28)), ys[:28], w=2), poly(fr, list(range(27, 40)), ys[27:], color=GREY_INK, w=2, cls="")]
    win = [rect(fr.x(24), fr.y0 + 6, fr.x(31) - fr.x(24), fr.h - 12, fill="none", stroke=ALERT, rx=4, sw=2.4),
           label(fr.x(27.5), fr.y0 + fr.h + 30, "a seven-day average for day 27 reads days 28 to 30, in the test",
                 size=16, anchor="middle", fill=ALERT)]
    fix = [text(500, 380, "Every step is fitted on each fold's training days only, then applied to its test days",
                size=18, weight="bold", fill=INK)]
    return svg(W, H, [step(1, base), step(2, win), step(3, fix)],
               SKETCH + " Smoothing, decomposition or normalisation over the whole series before it is split leaks "
               "the test period into training (H. Hewamalage et al. 2023, section 3.4). Drawn by " + LICENCE)


def mape() -> str:
    """The hurricane week: the last value's errors in rentals, then in percent."""
    W, H = 1000, 460
    s = N["bike"]["sandy"]
    days = [d[8:10] + "." + d[5:7] for d in s["days"]]
    fr = Frame(150, 40, 640, 200, (0.4, 7.6), (0, 9000))
    base = [*axis_y(fr, [(0, "0"), (4000, "4,000"), (8000, "8,000")]), label(150, 26, "rentals a day", size=15)]
    for i, v in enumerate(s["actual"], start=1):
        base.append(rect(fr.x(i) - 32, fr.y(v), 64, max(fr.y(0) - fr.y(v), 1.5), fill=ACCENT, stroke=None, rx=2,
                         cls="accent-fill"))
        base.append(label(fr.x(i), 264, days[i - 1], size=16, anchor="middle"))
    base += [line(fr.x(0.5), fr.y(s["last"]), fr.x(7.5), fr.y(s["last"]), color=INK, w=2.4, marker="", dash="8 5"),
             text(fr.x(7.5) + 12, fr.y(s["last"]) + 6, "the forecast:", size=16, anchor="start", weight="bold"),
             text(fr.x(7.5) + 12, fr.y(s["last"]) + 28, esc(f"the last value, {fmt(s['last'])}"), size=16,
                  anchor="start", weight="bold")]
    err = [text(30, 312, "error", size=17, weight="bold", anchor="start"),
           label(30, 332, "rentals", size=14)]
    pct = [text(30, 372, "error", size=17, weight="bold", anchor="start"), label(30, 392, "percent", size=14)]
    for i, (a, p) in enumerate(zip(s["abs_error"], s["pct_error"]), start=1):
        err.append(text(fr.x(i), 320, fmt(a), size=17))
        big = p > 1000
        pct.append(text(fr.x(i), 380, f"{p:,.0f}%", size=17, weight="bold" if big else "normal",
                        fill=ALERT if big else INK))
    err += [text(985, 312, esc(f"MAE {fmt(s['mae'])}"), size=19, weight="bold", anchor="end", fill=ACCENT,
                 cls="accent-fill"),
            text(985, 336, esc(f"RMSE {fmt(s['rmse'])}"), size=19, weight="bold", anchor="end", fill=ACCENT,
                 cls="accent-fill")]
    pct += [text(985, 380, esc(f"MAPE {fmt(s['mape'])}%"), size=19, weight="bold", anchor="end", fill=ALERT),
            label(985, 412, "MAPE: the mean of |y − ŷ| / y, in percent", size=15, anchor="end")]
    return svg(W, H, [step(1, base), step(2, err), step(3, pct)],
               f"Daily rentals from {s['days'][0]} to {s['days'][-1]}, the week of hurricane Sandy, and the naive "
               f"forecast from {s['origin']}; the errors in rentals and in percent of each day's rentals (R. J. Hyndman "
               "and G. Athanasopoulos 2021, section 5.8). " + BIKE_DATA + " Drawn by " + LICENCE)


def mase() -> str:
    """MASE: the forecast's mean error over the last value's mean one-step error in training."""
    W, H = 1000, 420
    s = N["bike"]["sandy"]
    st = s["steps_recent"]
    fr = Frame(80, 60, 460, 260, (-0.5, len(st) - 0.5), (0, 4600))
    left = [text(80, 34, "The scale: the change from one day to the next", size=18, weight="bold", anchor="start"),
            *axis_y(fr, [(0, "0"), (2000, "2,000"), (4000, "4,000")], size=13)]
    for i, v in enumerate(st):
        left.append(rect(fr.x(i) - 3.2, fr.y(v), 6.4, max(fr.y(0) - fr.y(v), 1), fill=GREY_INK, stroke=None, rx=1))
    left += [line(fr.x0, fr.y(s["scale"]), fr.x0 + fr.w, fr.y(s["scale"]), color=ACCENT, w=3, marker="",
                  cls="accent-stroke"),
             text(80, 350, esc(f"line: the mean over all {s['train_days'] - 1} changes in training, {fmt(s['scale'])}"),
                  size=16, weight="bold", fill=ACCENT, anchor="start", cls="accent-fill"),
             label(80, 372, "bars: the last 8 weeks of them", size=14)]
    right = [rect(600, 90, 370, 220, fill=PANEL, stroke=EDGE, rx=8, sw=1.2),
             text(785, 140, "the hurricane week", size=18, weight="bold"),
             text(785, 190, esc(f"MAE {fmt(s['mae'])}  /  {fmt(s['scale'])}"), size=22),
             text(785, 250, esc(f"MASE {s['mase']:.2f}"), size=34, weight="bold", fill=ACCENT, cls="accent-fill"),
             text(785, 292, "MASE = MAE / mean |y" + sub("t") + " − y" + sub("t−1") + "| in training", size=15,
                  fill=MUTED)]
    rule = [text(500, 410, "Below 1: smaller errors than the last value's average one-step error in training",
                 size=18, weight="bold", fill=INK)]
    return svg(W, H, [step(1, left), step(2, right), step(3, rule)],
               "The scale of the mean absolute scaled error (R. J. Hyndman and A. B. Koehler 2006, section 3): the mean "
               f"absolute change between consecutive days over the training days to {s['origin']}, and the hurricane "
               "week's naive forecast scaled by it. " + BIKE_DATA + " Drawn by " + LICENCE)


def spread() -> str:
    """Two forecasts' fold scores: overlapping ± bars, yet one lower on most folds."""
    W, H = 1000, 420
    a = [1.0, 2.4, 1.6, 1.4, 3.4, 1.5, 1.3, 0.8, 0.6, 0.9]
    b = [0.8, 2.0, 1.7, 1.1, 2.7, 1.2, 1.0, 0.9, 0.5, 0.7]
    mean = lambda v: sum(v) / len(v)
    sd = lambda v: (sum((x - mean(v)) ** 2 for x in v) / (len(v) - 1)) ** 0.5
    fr = Frame(470, 40, 480, 300, (0.5, 10.5), (0, 4))
    lft = Frame(80, 40, 300, 300, (0, 3), (0, 4))
    bars = [text(80, 26, "mean ± twice the spread", size=17, weight="bold", anchor="start"),
            *axis_y(lft, [(0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4")], size=13)]
    for i, (v, nm, col, cls) in enumerate(((a, "A", INK, ""), (b, "B", ACCENT, "accent"))):
        x = lft.x(1 + i)
        lo, hi = max(mean(v) - 2 * sd(v), 0), mean(v) + 2 * sd(v)
        bars += [line(x, lft.y(lo), x, lft.y(min(hi, 4)), color=col, w=3, marker="", cls=f"{cls}-stroke" if cls else ""),
                 f'<circle cx="{x}" cy="{lft.y(mean(v)):.1f}" r="9" fill="{col}"' + (f' class="{cls}-fill"' if cls else "")
                 + "/>",
                 text(x, lft.y(0) + 28, nm, size=20, weight="bold", fill=col, cls=f"{cls}-fill" if cls else "")]
    folds = [text(470, 26, "fold by fold", size=17, weight="bold", anchor="start"),
             *axis_x(fr, [(i, str(i)) for i in range(1, 11)], size=13)]
    for i in range(10):
        lower = b[i] < a[i]
        folds += [line(fr.x(i + 1), fr.y(a[i]), fr.x(i + 1), fr.y(b[i]), color=ACCENT if lower else ALERT, w=2,
                       marker="", cls="accent-stroke" if lower else ""),
                  f'<circle cx="{fr.x(i + 1):.1f}" cy="{fr.y(a[i]):.1f}" r="6" fill="{INK}"/>',
                  f'<circle class="accent-fill" cx="{fr.x(i + 1):.1f}" cy="{fr.y(b[i]):.1f}" r="6" fill="{ACCENT}"/>']
    wins = sum(x < y for x, y in zip(b, a))
    folds.append(text(710, 400, f"B is lower on {wins} folds of 10", size=19, weight="bold", fill=ACCENT,
                      cls="accent-fill"))
    return svg(W, H, [step(1, bars), step(2, folds)],
               SKETCH + " The error margin Dataiku DSS shows after a K-fold cross-test is twice the standard deviation "
               "of the fold scores (DSS 13 documentation); the folds share most of their training days, so their scores "
               "are correlated (S. J. Taylor and B. Letham 2018, section 4.3). Drawn by " + LICENCE)


# --- Part 4 -------------------------------------------------------------------------
def fill() -> str:
    """A weekend gap: the previous value repeats Friday's close; a line would borrow Monday's."""
    W, H = 1000, 400
    days = ["Thu", "Fri", "Sat", "Sun", "Mon"]
    v = {0: 3.2, 1: 2.4, 4: 4.4}
    fr = Frame(120, 40, 800, 260, (-0.5, 4.5), (0, 6))
    base = [*axis_x(fr, [(i, s) for i, s in enumerate(days)], size=17),
            *[f'<circle cx="{fr.x(i):.1f}" cy="{fr.y(y):.1f}" r="9" fill="{INK}"/>' for i, y in v.items()],
            *[f'<circle cx="{fr.x(i):.1f}" cy="{fr.y(v[1]):.1f}" r="9" fill="none" stroke="{GREY_INK}" '
              f'stroke-width="2" stroke-dasharray="4 3"/>' for i in (2, 3)],
            label(fr.x(2.5), fr.y(0.6), "no close: the market is shut", size=16, anchor="middle")]
    prev = [poly(fr, [1, 2, 3], [v[1]] * 3, w=3),
            *dots(fr, [2, 3], [v[1]] * 2, r=9),
            text(fr.x(2.5), fr.y(v[1]) + 36, "previous: Friday's close repeated", size=18, weight="bold",
                 fill=ACCENT, cls="accent-fill")]
    lin = [line(fr.x(1), fr.y(v[1]), fr.x(4), fr.y(v[4]), color=ALERT, w=2.4, marker="", dash="7 5"),
           *[f'<circle cx="{fr.x(i):.1f}" cy="{fr.y(v[1] + (v[4] - v[1]) * (i - 1) / 3):.1f}" r="8" fill="{ALERT}"/>'
             for i in (2, 3)],
           text(fr.x(2.5), fr.y(5.4), "linear: a line to Monday's close, not known on Saturday", size=18,
                weight="bold", fill=ALERT)]
    return svg(W, H, [step(1, base), step(2, prev), step(3, lin)],
               SKETCH + " With a one-day time step, Dataiku DSS fills the days without a close by the chosen "
               "interpolation method (DSS 13 documentation). Drawn by " + LICENCE)


def dss_forecast() -> str:
    """A drawing of a Dataiku forecasting session's settings, as Hands-on 7 sets them, and its algorithms' order."""
    W, H = 1000, 500
    nav = [rect(20, 20, 220, 468, fill=PANEL, stroke=EDGE, rx=4)]
    for i, n in enumerate(["General settings", "Train / Test Set", "Metrics", "Algorithms"]):
        yy = 60 + i * 46
        nav.append(text(42, yy, n, size=17, anchor="start"))

    def field(x, y, name, value, w=150):
        return [text(x, y, esc(name), size=16, anchor="start"),
                rect(x + 330, y - 24, w, 34, fill=WHITE, stroke=ACCENT, rx=4, sw=2, cls="accent-stroke"),
                text(x + 330 + w / 2, y, esc(value), size=16, weight="bold")]
    gen = [rect(256, 20, 724, 120, fill=WHITE, stroke=EDGE, rx=4),
           text(276, 50, "General settings", size=18, weight="bold", anchor="start"),
           *field(296, 84, "Time step", "1 Day"), *field(296, 124, "Forecast horizon (in time steps)", "7")]
    tt = [rect(256, 152, 724, 140, fill=WHITE, stroke=EDGE, rx=4),
          text(276, 182, "Train / Test Set", size=18, weight="bold", anchor="start"),
          *field(296, 216, "Numerical interpolation", "previous value", w=180),
          *field(296, 256, "K-fold cross-test, number of folds", "10"),
          text(296, 284, "Fold offset: ticked", size=16, anchor="start", fill=MUTED)]
    met = [rect(256, 304, 724, 76, fill=WHITE, stroke=EDGE, rx=4),
           text(276, 334, "Metrics", size=18, weight="bold", anchor="start"),
           text(296, 364, "Mean Absolute Scaled Error", size=17, anchor="start", weight="bold", fill=ACCENT,
                cls="accent-fill")]
    alg = [rect(256, 392, 724, 96, fill=WHITE, stroke=EDGE, rx=4),
           text(276, 422, "Algorithms", size=18, weight="bold", anchor="start"),
           text(296, 456, "first:", size=16, anchor="start", fill=MUTED),
           text(350, 456, "Trivial identity, Seasonal naive (season 7)", size=17, weight="bold", anchor="start",
                fill=ACCENT, cls="accent-fill"),
           text(296, 480, "then:", size=16, anchor="start", fill=MUTED),
           text(350, 480, "AutoARIMA, ETS, each read beside Trivial identity", size=17, weight="bold", anchor="start")]
    return svg(W, H, [step(1, nav + gen), step(2, tt), step(3, met), step(4, alg)],
               "A drawing, not a capture, of the settings of a Time Series Forecasting analysis in Dataiku DSS and the "
               "order in which Hands-on 7 trains its algorithms; labels after the DSS 13 documentation and the 2025 "
               "course server, to be checked on DSS 15.0. " + LICENCE)


def trail() -> str:
    """A forecast that trails by a day hugs the series on a chart: it is yesterday's value."""
    W, H = 1000, 400
    rng = random.Random(23)
    y, ys = 100.0, []
    for _ in range(60):
        y += rng.gauss(0, 1.6)
        ys.append(y)
    fr = Frame(60, 30, 560, 300, (0, 59), (min(ys) - 3, max(ys) + 3))
    walk = [poly(fr, list(range(60)), ys, color=INK, w=2, cls=""),
            label(60, 380, "a simulated random walk", size=15)]
    fc = [poly(fr, list(range(1, 60)), ys[:-1], w=2.4, dash="6 4"),
          text(340, 22, "the forecast for each day: the day before's value", size=16, weight="bold", fill=ACCENT,
               cls="accent-fill")]
    z0 = 40
    fz = Frame(690, 60, 270, 260, (z0 - 0.5, z0 + 7.5), (min(ys[z0 - 1:z0 + 8]) - 1, max(ys[z0 - 1:z0 + 8]) + 1))
    zoom = [panel_box(670, 20, 310, 330), text(825, 48, "eight days, close up", size=16, weight="bold"),
            poly(fz, list(range(z0, z0 + 8)), ys[z0:z0 + 8], color=INK, w=2, cls=""),
            *dots(fz, list(range(z0, z0 + 8)), ys[z0:z0 + 8], r=4, color=INK, cls=""),
            poly(fz, list(range(z0, z0 + 8)), ys[z0 - 1:z0 + 7], w=2.4, dash="6 4"),
            *dots(fz, list(range(z0, z0 + 8)), ys[z0 - 1:z0 + 7], r=4),
            text(825, 380, "one day late, every day", size=17, weight="bold", fill=ALERT)]
    return svg(W, H, [step(1, walk), step(2, fc), step(3, zoom)],
               "A simulated random walk (seed 23, Gaussian steps) and its one-step naive forecast, the previous day's "
               "value; plots hide the lag that the errors measure (H. Hewamalage et al. 2023, section 3.3). Drawn by "
               + LICENCE)


# Side margins cut from a figure's canvas, x from and x to, so that it draws larger at the slide's width.
CROP: dict[str, tuple[int, int]] = {}


def crop(s: str, x0: int, x1: int) -> str:
    """Narrow the viewBox of a figure drawn on a 0-based canvas to x0..x1, its full height kept."""
    return re.sub(r'viewBox="0 0 (\d+) (\d+)"', lambda m: f'viewBox="{x0} 0 {x1 - x0} {m.group(2)}"', s, count=1)


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"simple.svg": simple, "weights.svg": weights, "ets.svg": ets, "arima.svg": arima,
               "global.svg": global_, "rolling.svg": rolling, "leak.svg": leak, "mape.svg": mape, "mase.svg": mase,
               "spread.svg": spread, "fill.svg": fill, "dss-forecast.svg": dss_forecast, "trail.svg": trail,
               "naive.svg": s7.naive}
    for name, lit_ in (("dp", {"DP"}), ("mo-ev", {"MO", "EV"})):
        figures[f"phase-{name}.svg"] = lambda lit_=lit_: d.phase_thumb(lit_)
    for name, fn in figures.items():
        s = fn()
        if name in CROP:
            s = crop(s, *CROP[name])
        (out / name).write_text(s, encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
