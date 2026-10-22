#!/usr/bin/env python3
"""Draw the figures of the time-series deck as themeable, stepwise SVGs.

    python3 day2/07-series/src/draw.py day2/07-series/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), loaded from there so the decks draw alike. The data
figures read the files that `excerpts.py` cuts from open data, next to this script:
the Capital Bikeshare daily rentals (UCI dataset 275, CC BY 4.0), 10 seconds of the
MIT-BIH Arrhythmia Database's record 100 and 4 seconds of the EEG Motor
Movement/Imagery Dataset's run S001R02 (PhysioNet, ODC-By 1.0), one voxel of
OpenNeuro ds000114 (CC0), and `numbers.json`. The Dow Jones extract's licence is
not recorded, so only statistics computed from it are drawn. The random walk of
slide 26 is simulated, and says so.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
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
svg, step, rect, text, line, path = d.svg, d.step, d.rect, d.text, d.line, d.path
INK, MUTED, WHITE, ACCENT, A_LIGHT = d.INK, d.MUTED, d.WHITE, d.ACCENT, d.A_LIGHT
GREY, GREY_INK, EDGE, ALERT = "#e9edf0", "#9aa4a8", "#c9cfd2", "#da232f"
PANEL = "#f4f6f7"
LICENCE = "Oscar Esteban, CC BY 4.0."
BIKE_DATA = "Data: Capital Bikeshare daily rentals, 2011 and 2012, H. Fanaee-T (2013), UCI dataset 275, CC BY 4.0."

N = json.loads((HERE / "numbers.json").read_text())
WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = "J F M A M J J A S O N D".split()


def rows(name: str) -> list[dict]:
    with open(HERE / name, newline="") as f:
        return list(csv.DictReader(f))


BIKE = rows("bike.csv")


def col(rs, key) -> list[float]:
    return [float(r[key]) for r in rs]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def label(x, y, s, size=17, anchor="start", **kw):
    return text(x, y, esc(s), size=size, fill=kw.pop("fill", MUTED), anchor=anchor, **kw)


def fmt(v: float) -> str:
    return f"{v:,.0f}"


# --- chart helpers ------------------------------------------------------------------
class Frame:
    """A plotting box: data ranges mapped onto an x0, y0, w, h rectangle (y grows downwards)."""

    def __init__(self, x0, y0, w, h, xr, yr):
        self.x0, self.y0, self.w, self.h, self.xr, self.yr = x0, y0, w, h, xr, yr

    def x(self, v):
        return self.x0 + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def y(self, v):
        return self.y0 + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h


def poly(fr: Frame, xs, ys, color=ACCENT, w=1.6, cls="accent-stroke", dash="") -> str:
    pts = " ".join(f"{fr.x(a):.1f},{fr.y(b):.1f}" for a, b in zip(xs, ys))
    c = f' class="{cls}"' if cls else ""
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline{c} points="{pts}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linejoin="round"{dd}/>')


def dots(fr: Frame, xs, ys, r=2.2, color=ACCENT, cls="accent-fill", opacity=1.0) -> list[str]:
    c = f' class="{cls}"' if cls else ""
    o = f' fill-opacity="{opacity}"' if opacity < 1 else ""
    return [f'<circle{c} cx="{fr.x(a):.1f}" cy="{fr.y(b):.1f}" r="{r}" fill="{color}"{o}/>' for a, b in zip(xs, ys)]


def axis_x(fr: Frame, ticks, size=15, y=None) -> list[str]:
    """A baseline with labelled ticks: `ticks` is a list of (value, label)."""
    yy = fr.y0 + fr.h if y is None else y
    out = [line(fr.x0, yy, fr.x0 + fr.w, yy, color=GREY_INK, w=1.2, marker="")]
    for v, s in ticks:
        out += [line(fr.x(v), yy, fr.x(v), yy + 6, color=GREY_INK, w=1.2, marker=""),
                label(fr.x(v), yy + 24, s, size=size, anchor="middle")]
    return out


def axis_y(fr: Frame, ticks, size=14) -> list[str]:
    out = [line(fr.x0, fr.y0, fr.x0, fr.y0 + fr.h, color=GREY_INK, w=1.2, marker="")]
    for v, s in ticks:
        out += [line(fr.x0 - 6, fr.y(v), fr.x0, fr.y(v), color=GREY_INK, w=1.2, marker=""),
                label(fr.x0 - 10, fr.y(v) + 5, s, size=size, anchor="end")]
    return out


def acf_bars(fr: Frame, values, bound, first=1, colour=ACCENT, cls="accent-fill", mark=()) -> list[str]:
    """Autocorrelation bars from lag `first`, the white-noise bounds as a dashed band."""
    out = [f'<rect x="{fr.x0}" y="{fr.y(bound):.1f}" width="{fr.w}" height="{fr.y(-bound) - fr.y(bound):.1f}" '
           f'fill="{GREY}"/>',
           line(fr.x0, fr.y(0), fr.x0 + fr.w, fr.y(0), color=GREY_INK, w=1.2, marker=""),
           line(fr.x0, fr.y(bound), fr.x0 + fr.w, fr.y(bound), color=GREY_INK, w=1.2, marker="", dash="5 4"),
           line(fr.x0, fr.y(-bound), fr.x0 + fr.w, fr.y(-bound), color=GREY_INK, w=1.2, marker="", dash="5 4")]
    n = len(values) - first
    bw = fr.w / (n + 1) * 0.55
    for k in range(first, len(values)):
        v = values[k]
        x = fr.x(k) - bw / 2
        top, h = (fr.y(v), fr.y(0) - fr.y(v)) if v >= 0 else (fr.y(0), fr.y(v) - fr.y(0))
        on = k in mark
        c = f' class="{cls}"' if cls and not on else ""
        out.append(f'<rect{c} x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(h, 0.8):.1f}" '
                   f'fill="{ALERT if on else colour}"/>')
    return out


def panel_box(x, y, w, h) -> str:
    return rect(x, y, w, h, fill=PANEL, stroke=EDGE, rx=8, sw=1.2)


# --- Part 1 -------------------------------------------------------------------------
def examples() -> str:
    """Four series, each one quantity at regular steps: a business count and three body signals."""
    W, H = 1000, 470
    pw, ph = 480, 210
    spots = [(10, 10), (510, 10), (10, 250), (510, 250)]

    def panel(i, title, sub, xs, ys, xr, yr, ticks, mark=False):
        x, y = spots[i]
        fr = Frame(x + 22, y + 62, pw - 44, ph - 104, xr, yr)
        out = [panel_box(x, y, pw, ph), text(x + 22, y + 32, esc(title), size=20, weight="bold", anchor="start"),
               label(x + 22, y + 54, sub, size=15), poly(fr, xs, ys, w=1.4)]
        if mark:
            out += dots(fr, xs, ys, r=2.0)
        out += axis_x(fr, ticks, size=14)
        return out

    b = col(BIKE, "rentals")
    p1 = panel(0, "Bike rentals", "one value a day, 731 days", list(range(len(b))), b, (0, len(b) - 1), (0, 9000),
               [(0, "2011"), (365, "2012"), (730, "2013")])
    e = rows("ecg.csv")[: 4 * N["ecg"]["fs"]]
    p2 = panel(1, "Heart: an ECG", f"{N['ecg']['fs']} values a second, 4 seconds", col(e, "time_s"), col(e, "mv"),
               (0, 4), (-0.8, 1.4), [(0, "0 s"), (1, "1"), (2, "2"), (3, "3"), (4, "4 s")])
    g = rows("eeg.csv")[: 2 * N["eeg"]["fs"]]
    gv = col(g, "uv")
    p3 = panel(2, "Brain: an EEG", f"{N['eeg']['fs']} values a second, 2 seconds", col(g, "time_s"), gv,
               (0, 2), (min(gv) * 1.1, max(gv) * 1.1), [(0, "0 s"), (0.5, "0.5"), (1, "1"), (1.5, "1.5"), (2, "2 s")])
    f = rows("fmri.csv")
    fv = col(f, "bold")
    p4 = panel(3, "Brain: an fMRI voxel", "one value every 2.5 seconds, 7.5 minutes", col(f, "time_s"), fv,
               (10, 460), (min(fv) - 10, max(fv) + 10), [(10, "0 min"), (130, "2"), (250, "4"), (370, "6")], mark=True)
    return svg(W, H, [step(1, p1), step(2, p2), step(3, p3), step(4, p4)],
               "Four time series. " + BIKE_DATA + " ECG: MIT-BIH Arrhythmia Database, record 100, lead MLII, its first "
               "4 seconds (G. B. Moody and R. G. Mark 2001; PhysioNet, ODC-By 1.0). EEG: EEG Motor Movement/Imagery "
               "Dataset, run S001R02, eyes closed, channel Oz, seconds 10 to 12 (G. Schalk et al. 2004; PhysioNet, "
               "ODC-By 1.0). fMRI: OpenNeuro ds000114, sub-01, finger-foot-lips task, the unprocessed voxel that best "
               "follows the lips blocks (K. J. Gorgolewski et al. 2013; CC0). Drawn by " + LICENCE)


def shuffle() -> str:
    """The rentals in order, then the same values shuffled: the order is the data."""
    W, H = 1000, 420
    b = col(BIKE, "rentals")
    s = b[:]
    random.Random(7).shuffle(s)
    out = []
    for i, (vals, title) in enumerate(((b, "In order: 1 January 2011 to 31 December 2012"),
                                       (s, "The same 731 values, shuffled"))):
        y = 10 + i * 205
        fr = Frame(40, y + 48, 920, 130, (0, len(b) - 1), (0, 9000))
        out.append([panel_box(10, y, 980, 195), text(40, y + 34, esc(title), size=20, weight="bold", anchor="start"),
                    poly(fr, list(range(len(vals))), vals, w=1.3, color=ACCENT if i == 0 else GREY_INK,
                         cls="accent-stroke" if i == 0 else "")])
    return svg(W, H, [step(1, out[0]), step(2, out[1])],
               "The daily rentals in order, then shuffled with a fixed seed: the same values, the series gone. "
               + BIKE_DATA + " Drawn by " + LICENCE)


# --- Part 2 -------------------------------------------------------------------------
def trend() -> str:
    """Two years of rentals and their trend-cycle: up from one year to the next, rising and falling with the year."""
    W, H = 1000, 420
    b, t = col(BIKE, "rentals"), col(BIKE, "rentals_trend")
    fr = Frame(80, 30, 890, 320, (0, len(b) - 1), (0, 9000))
    base = [poly(fr, list(range(len(b))), b, color=GREY_INK, w=1.1, cls=""),
            *axis_x(fr, [(0, "2011"), (182, "July"), (365, "2012"), (547, "July"), (730, "2013")]),
            *axis_y(fr, [(0, "0"), (3000, "3,000"), (6000, "6,000"), (9000, "9,000")]),
            label(80, 18, "rentals a day", size=15)]
    tr = [poly(fr, list(range(len(t))), t, w=4)]
    ym = N["bike"]["year_mean"]
    means = [line(fr.x(0), fr.y(ym["2011"]), fr.x(364), fr.y(ym["2011"]), color=INK, w=1.6, marker="", dash="7 5"),
             line(fr.x(365), fr.y(ym["2012"]), fr.x(730), fr.y(ym["2012"]), color=INK, w=1.6, marker="", dash="7 5"),
             label(fr.x(30), fr.y(ym["2011"]) - 12, f"2011: {fmt(ym['2011'])} a day", size=17, fill=INK),
             label(fr.x(600), fr.y(ym["2012"]) + 30, f"2012: {fmt(ym['2012'])} a day", size=17, fill=INK, anchor="middle")]
    return svg(W, H, [step(1, base), step(2, tr), step(3, means)],
               "The daily rentals (grey), their trend-cycle (an STL fit with a weekly season, its trend smoothed over 91 "
               "days, robust) and each year's mean. " + BIKE_DATA + " Drawn by " + LICENCE)


def season() -> str:
    """The year in the monthly means of all rentals; the week in two kinds of riders."""
    W, H = 1000, 430
    mm = N["bike"]["month_mean"]
    fr = Frame(70, 70, 400, 280, (0.4, 12.6), (0, 6500))
    left = [text(70, 36, "The year: all rentals, by month", size=20, weight="bold", anchor="start"),
            *axis_y(fr, [(0, "0"), (3000, "3,000"), (6000, "6,000")])]
    for i, v in enumerate(mm, start=1):
        left.append(rect(fr.x(i) - 13, fr.y(v), 26, fr.y(0) - fr.y(v), fill=ACCENT, stroke=None, rx=2,
                         cls="accent-fill"))
    left += axis_x(fr, [(i, m) for i, m in enumerate(MONTHS, start=1)], size=15)
    wm = N["bike"]["weekday_mean"]
    fr2 = Frame(570, 70, 400, 280, (0.6, 7.4), (0, 4500))
    right = [text(570, 36, "The week: two kinds of riders", size=20, weight="bold", anchor="start"),
             *axis_y(fr2, [(0, "0"), (2000, "2,000"), (4000, "4,000")])]
    for key, colour, cls, lab in (("registered", INK, "", "registered"), ("casual", ACCENT, "accent-stroke", "casual")):
        ys = [wm[key][k] for k in WEEK]
        right.append(poly(fr2, list(range(1, 8)), ys, color=colour, w=3, cls=cls))
        right += dots(fr2, list(range(1, 8)), ys, r=4.5, color=colour, cls=cls.replace("stroke", "fill"))
        right.append(text(fr2.x(3), fr2.y(ys[2]) - 16, lab, size=16, weight="bold", fill=colour,
                          cls=cls.replace("stroke", "fill")))
    right += axis_x(fr2, [(i, w[:3]) for i, w in enumerate(WEEK, start=1)], size=15)
    return svg(W, H, [step(1, left), step(2, right)],
               "Monthly means of all rentals over both years; weekday means of casual and registered riders. "
               + BIKE_DATA + " Drawn by " + LICENCE)


def additive() -> str:
    """Swings that keep their size, swings that grow with the level; casual riders' weekends grow."""
    W, H = 1000, 440
    sk = []
    for i, (title, grow) in enumerate((("Additive: the same swing", False), ("Multiplicative: the swing grows", True))):
        x0 = 20 + i * 250
        fr = Frame(x0 + 10, 60, 210, 120, (0, 48), (0, 12))
        xs = [k / 2 for k in range(97)]
        level = [2 + 0.12 * x for x in xs]
        amp = [(0.35 * lv if grow else 1.1) for lv in level]
        ys = [lv + a * math.sin(2 * math.pi * x / 6) for x, lv, a in zip(xs, level, amp)]
        sk += [panel_box(x0, 20, 230, 190), text(x0 + 115, 48, esc(title), size=15, weight="bold"),
               poly(fr, xs, ys, w=2), poly(fr, xs, level, color=GREY_INK, w=1.2, cls="", dash="4 4")]
    sk.append(label(255, 232, "drawn, not data", size=14, anchor="middle"))
    months = N["bike"]["casual_by_month"]
    fr = Frame(560, 60, 400, 290, (0.5, 24.5), (0, 2900))
    xs = list(range(1, 25))
    wd = [m["weekday"] for m in months]
    we = [m["weekend"] for m in months]
    data = [text(560, 36, "Casual riders, by month", size=20, weight="bold", anchor="start"),
            *axis_y(fr, [(0, "0"), (1000, "1,000"), (2000, "2,000")]),
            poly(fr, xs, we, w=3), *dots(fr, xs, we, r=3.5),
            poly(fr, xs, wd, color=INK, w=2.2, cls=""), *dots(fr, xs, wd, r=3, color=INK, cls=""),
            text(fr.x(23.5), fr.y(we[-2]) - 16, "weekends", size=16, weight="bold", fill=ACCENT, anchor="end",
                 cls="accent-fill"),
            text(fr.x(24.4), fr.y(wd[-1]) + 30, "weekdays", size=16, weight="bold", fill=INK, anchor="end"),
            *axis_x(fr, [(1, "2011"), (13, "2012"), (24, "Dec.")], size=15)]
    lo, hi = N["bike"]["casual_weekend_ratio"]
    gap = [text(760, 404, esc(f"The gap: {fmt(we[0] - wd[0])} a day in January 2011, {fmt(we[16] - wd[16])} in May 2012;"),
                size=16, fill=INK),
           text(760, 428, esc(f"the weekend stays {lo} to {hi} times the weekday"), size=16, fill=INK)]
    return svg(W, H, [step(1, sk), step(2, data), step(3, gap)],
               "Two drawn sketches (not data) of additive and multiplicative seasonality, after R. J. Hyndman and G. "
               "Athanasopoulos (2021), section 3.2; casual riders' mean daily rentals on weekdays and at weekends, by "
               "month. " + BIKE_DATA + " Drawn by " + LICENCE)


def stl() -> str:
    """STL on the casual riders: trend-cycle, weekly season, remainder."""
    W, H = 1000, 470
    n = len(BIKE)
    xs = list(range(n))
    span = lambda key: (min(col(BIKE, key)) * 1.06, max(col(BIKE, key)) * 1.06)
    parts = [("Casual riders", "casual", (0, max(col(BIKE, "casual")) * 1.04)),
             ("Trend-cycle", "casual_trend", (0, max(col(BIKE, "casual_trend")) * 1.08)),
             ("Weekly season", "casual_season", span("casual_season")),
             ("Remainder", "casual_remainder", span("casual_remainder"))]
    out = []
    for i, (title, key, yr) in enumerate(parts):
        y = 8 + i * 114
        fr = Frame(200, y + 10, 770, 90, (0, n - 1), yr)
        g = [rect(10, y, 980, 106, fill=PANEL, stroke=EDGE, rx=6, sw=1),
             text(24, y + 58, esc(title), size=19, weight="bold", anchor="start"),
             poly(fr, xs, col(BIKE, key), w=1.2, color=GREY_INK if i == 0 else ACCENT, cls="" if i == 0 else "accent-stroke")]
        if i in (2, 3):
            g.insert(2, line(fr.x0, fr.y(0), fr.x0 + fr.w, fr.y(0), color=GREY_INK, w=1, marker="", dash="4 4"))
        if i == 3:
            low = next(k for k, r in enumerate(BIKE) if r["date"] == N["bike"]["lowest"]["date"])
            g += [f'<circle cx="{fr.x(low):.1f}" cy="{fr.y(float(BIKE[low][key])):.1f}" r="8" fill="none" '
                  f'stroke="{ALERT}" stroke-width="2.2"/>',
                  label(fr.x(low) - 14, y + 96, "29 October 2012", size=14, anchor="end", fill=ALERT)]
        out.append(g)
    return svg(W, H, [step(1, out[0]), step(2, out[1]), step(3, out[2]), step(4, out[3])],
               "STL (Cleveland et al. 1990) of casual riders' daily rentals, period 7 days, robust fit, statsmodels "
               "defaults otherwise: data, trend-cycle, weekly season, remainder (their sum). The circle marks the "
               "lowest day of the two years. " + BIKE_DATA + " Drawn by " + LICENCE)


# --- Part 3 -------------------------------------------------------------------------
def lag() -> str:
    """Each day's rentals against the day before's: autocorrelation at lag 1."""
    W, H = 1000, 440
    b = col(BIKE, "rentals")
    tab = [text(50, 40, "Each row: a day and the day before", size=18, weight="bold", anchor="start")]
    hdr = [("date", 60), ("rentals", 190), ("the day before", 300)]
    for s, x in hdr:
        tab.append(text(x, 86, s, size=16, weight="bold", fill=MUTED, anchor="start"))
    for i in range(1, 7):
        y = 86 + i * 44
        r = BIKE[i]
        tab += [line(50, y - 30, 420, y - 30, color=EDGE, w=1, marker=""),
                text(60, y, r["date"], size=17, anchor="start"), text(250, y, fmt(b[i]), size=17, anchor="end"),
                text(390, y, fmt(b[i - 1]), size=17, anchor="end", fill=ACCENT, cls="accent-fill")]
    fr = Frame(560, 30, 400, 330, (0, 9000), (0, 9000))
    sc = [*dots(fr, b[:-1], b[1:], r=2.2, opacity=0.45),
          *axis_x(fr, [(0, "0"), (4000, "4,000"), (8000, "8,000")]),
          *axis_y(fr, [(0, "0"), (4000, "4,000"), (8000, "8,000")]),
          label(760, 412, "the day before", size=15, anchor="middle"), label(560, 18, "rentals", size=15)]
    r1 = [text(700, 70, esc(f"correlation {N['bike']['lag1_corr']:.2f}"), size=22, weight="bold", fill=ACCENT,
               cls="accent-fill")]
    return svg(W, H, [step(1, tab), step(2, sc), step(3, r1)],
               "Daily rentals against the previous day's, 730 pairs, and their correlation. " + BIKE_DATA
               + " Drawn by " + LICENCE)


def ecg_acf() -> str:
    """Ten seconds of ECG and its autocorrelation: a peak at the interval between beats."""
    W, H = 1000, 450
    e = rows("ecg.csv")
    fs = N["ecg"]["fs"]
    fr = Frame(60, 50, 910, 140, (0, 10), (-0.8, 1.4))
    top = [panel_box(10, 10, 980, 210), text(30, 38, "Ten seconds of an ECG", size=19, weight="bold", anchor="start"),
           poly(fr, col(e, "time_s"), col(e, "mv"), w=1.2),
           *axis_x(fr, [(k, f"{k} s" if k in (0, 10) else str(k)) for k in range(0, 11)], size=13)]
    r = N["ecg"]["acf"]
    lags = [k / fs for k in range(len(r))]
    fr2 = Frame(60, 270, 910, 130, (0, 2), (-0.4, 1))
    bot = [text(30, 252, "Its autocorrelation, at lags up to 2 seconds", size=19, weight="bold", anchor="start"),
           line(fr2.x0, fr2.y(0), fr2.x0 + fr2.w, fr2.y(0), color=GREY_INK, w=1, marker=""),
           poly(fr2, lags, r, w=1.8),
           *axis_x(fr2, [(0, "0 s"), (0.5, "0.5"), (1, "1"), (1.5, "1.5"), (2, "2 s")], size=14)]
    pk = N["ecg"]["peak_lag_s"]
    mark = [line(fr2.x(pk), fr2.y(N["ecg"]["peak_acf"]) - 8, fr2.x(pk), fr2.y(N["ecg"]["peak_acf"]) - 46,
                 color=ALERT, w=2.2, marker=""),
            text(fr2.x(pk) + 10, fr2.y(N["ecg"]["peak_acf"]) - 30,
                 esc(f"{pk:.2f} s between beats: {N['ecg']['peak_bpm']} a minute"), size=18, weight="bold",
                 fill=ALERT, anchor="start")]
    return svg(W, H, [step(1, top), step(2, bot), step(3, mark)],
               "MIT-BIH Arrhythmia Database, record 100, lead MLII, its first 10 seconds at 360 values a second, and "
               "their autocorrelation (G. B. Moody and R. G. Mark 2001; PhysioNet, ODC-By 1.0). The highest peak past "
               "0.4 s is marked; the record's beat annotations give a mean interval of "
               f"{N['ecg']['rr_mean_s']:.3f} s over the same 10 seconds. Drawn by " + LICENCE)


def acf() -> str:
    """Two autocorrelation functions: a slow decay with the trend, spikes at a weekly season."""
    W, H = 1000, 440
    b = N["bike"]
    out = []
    for i, (title, key) in enumerate((("All rentals: a slow decay", "acf_rentals"),
                                      ("Casual riders: spikes every 7 days", "acf_casual"))):
        x0 = 10 + i * 500
        fr = Frame(x0 + 50, 70, 410, 290, (0, 29), (-0.2, 1))
        g = [text(x0 + 30, 38, esc(title), size=19, weight="bold", anchor="start"),
             *acf_bars(fr, b[key], b["bound"], mark=(7, 14, 21, 28) if i == 1 else ()),
             *axis_y(fr, [(0, "0"), (0.5, "0.5"), (1, "1")]),
             *axis_x(fr, [(1, "1"), (7, "7"), (14, "14"), (21, "21"), (28, "28 days")], size=14, y=fr.y(-0.2))]
        out.append(g)
    note = [label(500, 432, f"grey band: ±{b['bound']:.3f}, where 95% of the bars of pure noise would fall", size=15,
                  anchor="middle")]
    return svg(W, H, [step(1, out[0] + note), step(2, out[1])],
               "Autocorrelation of the daily rentals and of casual riders' rentals, lags 1 to 28 days; the band is "
               "±1.96/√T for T = 731 (R. J. Hyndman and G. Athanasopoulos 2021, section 2.9). " + BIKE_DATA
               + " Drawn by " + LICENCE)


def rolling(vals, k=30):
    """Centred rolling mean over k values, None near the ends."""
    out = []
    for i in range(len(vals)):
        lo, hi = i - k // 2, i + k // 2
        out.append(None if lo < 0 or hi >= len(vals) else sum(vals[lo:hi]) / k)
    return out


def stationary() -> str:
    """The level's mean drifts; the change's mean stays at zero."""
    W, H = 1000, 420
    b = col(BIKE, "rentals")
    ch = [b[i] - b[i - 1] for i in range(1, len(b))]
    out = []
    for i, (title, vals, yr, ticks) in enumerate((
            ("The level: its mean drifts", b, (0, 9000), [(0, "0"), (4000, "4,000"), (8000, "8,000")]),
            ("The change from the day before: its mean stays at 0", ch, (-6500, 6500),
             [(-5000, "-5,000"), (0, "0"), (5000, "5,000")]))):
        x0 = 10 + i * 500
        fr = Frame(x0 + 70, 60, 400, 290, (0, len(vals) - 1), yr)
        m = rolling(vals)
        xs = [k for k, v in enumerate(m) if v is not None]
        g = [text(x0 + 245, 34, esc(title), size=17, weight="bold"),
             poly(fr, list(range(len(vals))), vals, color=GREY_INK, w=0.9, cls=""),
             poly(fr, xs, [m[k] for k in xs], w=3.5),
             *axis_y(fr, ticks), *axis_x(fr, [(0, "2011"), (365, "2012"), (len(vals) - 1, "2013")], size=14)]
        out.append(g)
    note = [label(500, 412, "blue: the mean over the 30 days around each day", size=15, anchor="middle")]
    return svg(W, H, [step(1, out[0] + note), step(2, out[1])],
               "Daily rentals and their change from the day before, each with its centred 30-day mean. " + BIKE_DATA
               + " Drawn by " + LICENCE)


def diff() -> str:
    """After differencing: the trend's slow decay and the weekly spikes are gone."""
    W, H = 1000, 440
    b = N["bike"]
    out = []
    for i, (title, key) in enumerate((("All rentals, change from the day before", "acf_rentals_change"),
                                      ("Casual riders, change from a week before", "acf_casual_week_change"))):
        x0 = 10 + i * 500
        fr = Frame(x0 + 50, 70, 410, 290, (0, 29), (-0.6, 1))
        g = [text(x0 + 30, 38, esc(title), size=18, weight="bold", anchor="start"),
             *acf_bars(fr, b[key], b["bound"]),
             *axis_y(fr, [(-0.5, "-0.5"), (0, "0"), (0.5, "0.5"), (1, "1")]),
             *axis_x(fr, [(1, "1"), (7, "7"), (14, "14"), (21, "21"), (28, "28 days")], size=14, y=fr.y(-0.6))]
        out.append(g)
    return svg(W, H, [step(1, out[0]), step(2, out[1])],
               "Autocorrelation, lags 1 to 28 days, of the daily rentals' change from the day before and of casual "
               "riders' change from the same day a week before; band ±1.96/√T. " + BIKE_DATA + " Drawn by " + LICENCE)


# --- Part 4 -------------------------------------------------------------------------
def dss_window() -> str:
    """A drawing of Dataiku's Window recipe: ordered by Date, lags 1 and 2 on Close."""
    W, H = 1000, 380
    nav = [rect(20, 20, 220, 340, fill=PANEL, stroke=EDGE, rx=4)]
    for i, n in enumerate(["Windows definitions", "Aggregations", "Output"]):
        yy = 60 + i * 46
        on = n == "Aggregations"
        if on:
            nav += [rect(20, yy - 24, 220, 38, fill=A_LIGHT, stroke=None, rx=0, cls="accent-a-light-fill"),
                    rect(20, yy - 24, 6, 38, fill=ACCENT, stroke=None, rx=0, cls="accent-fill")]
        nav.append(text(42, yy, n, size=17, anchor="start", weight="bold" if on else "normal"))
    win = [rect(256, 20, 724, 100, fill=WHITE, stroke=EDGE, rx=4),
           text(276, 56, "Windows definitions", size=18, weight="bold", anchor="start"),
           text(276, 96, "Order columns", size=17, anchor="start"),
           rect(430, 72, 210, 36, fill=WHITE, stroke=ACCENT, rx=4, sw=2.4, cls="accent-stroke"),
           text(444, 96, "Date, ascending", size=17, anchor="start", weight="bold")]
    agg = [rect(256, 140, 724, 220, fill=WHITE, stroke=EDGE, rx=4),
           text(276, 176, "Aggregations", size=18, weight="bold", anchor="start")]
    for i, (n, on) in enumerate((("Open", False), ("Close", True), ("Volume", False))):
        yy = 222 + i * 44
        agg.append(text(296, yy, n, size=17, anchor="start", weight="bold" if on else "normal",
                        fill=INK if on else GREY_INK))
    lagbox = [rect(420, 242, 110, 36, fill=A_LIGHT, stroke=ACCENT, rx=4, sw=2.4, cls="accent-a-light-fill accent-stroke"),
              text(475, 266, "Lag", size=17, weight="bold"),
              text(560, 266, "offsets", size=17, anchor="start"),
              rect(640, 242, 100, 36, fill=WHITE, stroke=GREY_INK, rx=4), text(690, 266, "1, 2", size=17, weight="bold")]
    outc = [text(276, 344, "new columns: Close one and two trading days before (names as the server shows them)",
                 size=15, fill=MUTED, anchor="start", style="italic")]
    return svg(W, H, [step(1, nav + win), step(2, agg + lagbox), step(3, outc)],
               "A drawing, not a capture, of Dataiku DSS's Window recipe: rows ordered by Date, a lag of 1 and 2 on "
               "Close; labels as in the DSS reference documentation, to be checked on DSS 15.0. " + LICENCE)


def flow() -> str:
    """The Flow of Hands-on 6: the Dow Jones read step by step; the bike rentals in the tail."""
    W, H = 1000, 360

    def dataset(x, y, name, sub=""):
        out = [rect(x, y, 56, 50, fill=A_LIGHT, stroke=ACCENT, rx=6, cls="accent-a-light-fill accent-stroke"),
               text(x + 28, y + 72, name, size=15)]
        if sub:
            out.append(text(x + 28, y + 90, sub, size=13, fill=MUTED))
        return out

    def recipe(x, y, name, fill="#f0c46a"):
        return [f'<circle cx="{x}" cy="{y}" r="20" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>',
                text(x, y - 30, name, size=14, fill=MUTED)]

    def arr(x1, y1, x2, y2):
        return line(x1, y1, x2, y2, color=INK, w=1.6)

    y1, y2 = 60, 220
    row1 = (dataset(10, y1, "dowjones") + [arr(70, y1 + 25, 112, y1 + 25)] + recipe(134, y1 + 25, "Prepare")
            + [arr(156, y1 + 25, 196, y1 + 25)] + dataset(200, y1, "dated", "Date parsed")
            + [arr(260, y1 + 25, 302, y1 + 25)] + recipe(324, y1 + 25, "Window", fill="#8fc9e8")
            + [arr(346, y1 + 25, 386, y1 + 25)] + dataset(390, y1, "lagged", "lags 1 and 2")
            + [arr(450, y1 + 25, 492, y1 + 25)] + recipe(514, y1 + 25, "Prepare")
            + [arr(536, y1 + 25, 576, y1 + 25)] + dataset(580, y1, "changes", "change, weekday")
            + [arr(640, y1 + 25, 682, y1 + 25)] + recipe(704, y1 + 25, "Group", fill="#8fd19e")
            + [arr(726, y1 + 25, 766, y1 + 25)] + dataset(770, y1, "by weekday", "mean, spread")
            + [text(10, 30, "steps 1 to 3", size=15, weight="bold", fill=ACCENT, cls="accent-fill", anchor="start")])
    row2 = (dataset(10, y2, "bike-rentals") + [arr(70, y2 + 25, 112, y2 + 25)] + recipe(134, y2 + 25, "Prepare")
            + [arr(156, y2 + 25, 196, y2 + 25)] + dataset(200, y2, "dated", "weekday, month")
            + [path(f"M 260 {y2 + 25} L 300 {y2 + 25} L 300 {y2 - 2} L 492 {y2 - 2}", color=INK, w=1.6)]
            + recipe(514, y2 - 2, "Group", fill="#8fd19e") + [arr(536, y2 - 2, 576, y2 - 2)]
            + dataset(580, y2 - 27, "by weekday")
            + [path(f"M 300 {y2 + 25} L 300 {y2 + 62} L 492 {y2 + 62}", color=INK, w=1.6)]
            + [f'<circle cx="514" cy="{y2 + 62}" r="20" fill="#8fd19e" stroke="{INK}" stroke-width="1.2"/>',
               text(514, y2 + 104, "Group", size=14, fill=MUTED),
               arr(536, y2 + 62, 706, y2 + 62)] + dataset(710, y2 + 37, "by month")
            + [text(10, y2 - 30, "panel 4", size=15, weight="bold", fill=ACCENT, cls="accent-fill", anchor="start")])
    shift = lambda items: ['<g transform="translate(60,0)">' + "\n".join(items) + "</g>"]
    return svg(W, H, [step(1, shift(row1)), step(2, shift(row2))],
               "The Flow of Hands-on 6, drawn after Dataiku DSS's Flow (datasets and visual recipes), with the "
               "sheet's steps; recipe colours schematic. " + LICENCE)


def dj_acf() -> str:
    """The Dow Jones: the close's autocorrelation stays high; the change's sits in the noise band."""
    W, H = 1000, 430
    dj = N["dowjones"]
    out = []
    for i, (title, key, bound) in enumerate((("The close", "acf_close", dj["bound_close"]),
                                             ("The change from the day before", "acf_change", dj["bound_change"]))):
        x0 = 10 + i * 500
        fr = Frame(x0 + 50, 70, 410, 290, (0, 11), (-0.3, 1))
        mark = tuple(k for k in range(1, 11) if abs(dj[key][k]) > bound) if i == 1 else ()
        g = [text(x0 + 30, 38, esc(title), size=19, weight="bold", anchor="start"),
             *acf_bars(fr, dj[key], bound, mark=mark),
             *axis_y(fr, [(0, "0"), (0.5, "0.5"), (1, "1")]),
             *axis_x(fr, [(k, str(k)) for k in range(1, 11)], size=14, y=fr.y(-0.3)),
             label(x0 + 255, 412, "lag, in trading days", size=14, anchor="middle")]
        if i == 0:
            g.append(text(fr.x(1) + 14, fr.y(dj[key][1]) - 10, f"{dj[key][1]:.2f}", size=17, weight="bold",
                          fill=ACCENT, anchor="start", cls="accent-fill"))
        else:
            g.append(text(fr.x(1), fr.y(0.25), f"{dj[key][1]:.2f}", size=17, weight="bold", fill=ACCENT,
                          cls="accent-fill"))
        out.append(g)
    return svg(W, H, [step(1, out[0]), step(2, out[1])],
               "Autocorrelation of the Dow Jones daily close and of its change from the previous trading day, lags 1 "
               f"to 10, on the module's extract ({dj['rows']} trading days, {dj['first']} to {dj['last']}); band "
               "±1.96/√T; a bar outside it in red. Statistics only: the extract's licence is not recorded. Drawn by "
               + LICENCE)


def weekday() -> str:
    """Mean change by weekday, beside its spread."""
    W, H = 1000, 420
    wk = N["dowjones"]["weekday"]
    fr = Frame(140, 40, 800, 320, (0.4, 5.6), (-700, 700))
    base = [*axis_y(fr, [(-600, "-600"), (-300, "-300"), (0, "0"), (300, "300"), (600, "600")]),
            line(fr.x0, fr.y(0), fr.x0 + fr.w, fr.y(0), color=GREY_INK, w=1.2, marker=""),
            label(140, 26, "change from the day before, index points", size=15)]
    means, spreads = [], []
    for i, k in enumerate(WEEK[:5], start=1):
        m, s = wk[k]["mean"], wk[k]["sd"]
        top, h = (fr.y(m), fr.y(0) - fr.y(m)) if m >= 0 else (fr.y(0), fr.y(m) - fr.y(0))
        means += [rect(fr.x(i) - 30, top, 60, max(h, 1), fill=ACCENT, stroke=None, rx=2, cls="accent-fill"),
                  text(fr.x(i) + 40, fr.y(m) + (-8 if m >= 0 else 22), f"{m:+.0f}", size=17, weight="bold",
                       anchor="start", fill=ACCENT, cls="accent-fill")]
        spreads += [line(fr.x(i), fr.y(m - s), fr.x(i), fr.y(m + s), color=INK, w=2, marker=""),
                    line(fr.x(i) - 16, fr.y(m - s), fr.x(i) + 16, fr.y(m - s), color=INK, w=2, marker=""),
                    line(fr.x(i) - 16, fr.y(m + s), fr.x(i) + 16, fr.y(m + s), color=INK, w=2, marker="")]
        base.append(label(fr.x(i), 392, k, size=16, anchor="middle"))
    spreads.append(label(940, 26, "whiskers: one standard deviation each way", size=15, anchor="end"))
    return svg(W, H, [step(1, base + means), step(2, spreads)],
               "Mean change of the Dow Jones close from the previous trading day, by weekday, with one standard "
               "deviation each way, on the module's extract; statistics only. Drawn by " + LICENCE)


def naive() -> str:
    """A simulated random walk and its naive forecast: the last value, carried forward."""
    W, H = 1000, 400
    rng = random.Random(11)
    y, ys = 100.0, []
    for _ in range(80):
        y += rng.gauss(0, 1.6)
        ys.append(y)
    fr = Frame(60, 40, 900, 300, (0, 100), (min(ys) - 6, max(ys) + 6))
    walk = [poly(fr, list(range(80)), ys, color=INK, w=2, cls=""),
            line(fr.x(79.5), fr.y0, fr.x(79.5), fr.y0 + fr.h, color=GREY_INK, w=1.2, marker="", dash="5 4"),
            label(fr.x(79.5) - 10, fr.y0 + 16, "today", size=16, anchor="end"),
            label(60, 380, "a simulated random walk: each step adds a random change to the last value", size=15)]
    fc = [poly(fr, [79, 100], [ys[-1], ys[-1]], w=4, dash="10 6"),
          *[text(fr.x(81), fr.y(ys[-1]) + 36 + 24 * k, s, size=17, weight="bold", fill=ACCENT, anchor="start",
                 cls="accent-fill") for k, s in enumerate(("the forecast for", "every day ahead:", "today's value"))]]
    return svg(W, H, [step(1, walk), step(2, fc)],
               "A simulated random walk (seed 11, Gaussian steps) and its naive forecast, the last value carried "
               "forward (R. J. Hyndman and G. Athanasopoulos 2021, section 5.2). Drawn by " + LICENCE)


# Side margins cut from a figure's canvas, x from and x to, so that it draws larger at the slide's width.
CROP: dict[str, tuple[int, int]] = {}


def crop(s: str, x0: int, x1: int) -> str:
    """Narrow the viewBox of a figure drawn on a 0-based canvas to x0..x1, its full height kept."""
    return re.sub(r'viewBox="0 0 (\d+) (\d+)"', lambda m: f'viewBox="{x0} 0 {x1 - x0} {m.group(2)}"', s, count=1)


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"examples.svg": examples, "shuffle.svg": shuffle, "trend.svg": trend, "season.svg": season,
               "additive.svg": additive, "stl.svg": stl, "lag.svg": lag, "ecg-acf.svg": ecg_acf, "acf.svg": acf,
               "stationary.svg": stationary, "diff.svg": diff, "dss-window.svg": dss_window, "flow.svg": flow,
               "dj-acf.svg": dj_acf, "weekday.svg": weekday, "naive.svg": naive}
    for name, lit_ in (("bu", {"BU"}), ("du", {"DU"})):
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
