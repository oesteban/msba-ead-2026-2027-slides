#!/usr/bin/env python3
"""Draw the hand-authored figures of the deep-learning deck as themeable, stepwise SVGs.

    python3 day2/05-dl/src/draw.py day2/05-dl/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), loaded from there so the decks draw alike. No
figure shows a photo of the course's photo sets, whose licences are unknown:
the photos drawn on are the openly licensed ones in `images/photos/` (see its
`CREDITS.md`). The pixel patch reads one of them and needs Pillow; without it,
that figure is skipped. The general figures (a neuron to the loss) run on deck
4's example wine, line 12 of the course's `winequality_all.csv` (UCI Wine
Quality, CC BY 4.0): its attribute values are real, the weights illustrative.
Every other number is a count from a wiki page, a value from `compute.csv`
(Epoch AI's data, CC BY 4.0), or marked illustrative in the figure's comment
and on its slide.
"""

from __future__ import annotations

import csv
import importlib.util
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("intro_draw", HERE.parents[2] / "day1" / "01-intro" / "src" / "draw.py")
d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d)
svg, step, rect, text, line, path = d.svg, d.step, d.rect, d.text, d.line, d.path
INK, MUTED, WHITE, ACCENT, A_LIGHT, B, B_LIGHT = d.INK, d.MUTED, d.WHITE, d.ACCENT, d.A_LIGHT, d.B, d.B_LIGHT
GREY, GREY_INK, EDGE, ALERT = "#e9edf0", "#9aa4a8", "#c9cfd2", "#da232f"
LICENCE = "Oscar Esteban, CC BY 4.0."


def node(x, y, r=13, fill=WHITE, stroke=ACCENT, cls="accent-stroke"):
    return f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def glyph(x, y, s=1.0, flip=False, fill=A_LIGHT, cls="accent-a-light-fill"):
    """The deck's stand-in for an animal in a photo: a triangle and a dark eye."""
    sx = -s if flip else s
    return (f'<g transform="translate({x},{y}) scale({sx},{s})">'
            f'<polygon class="{cls}" points="-50,40 -10,-40 50,40" fill="{fill}"/>'
            f'<circle cx="18" cy="-18" r="14" fill="{INK}"/></g>')


# deck 4's example wine: line 12 of winequality_all.csv, a white of grade 5, so line "low"
WINE = [("alcohol", 12.0), ("volatile acidity", 0.27), ("sulphates", 0.56)]
LINES = ["low", "medium", "high"]
SCORES = [0.4, 1.6, 0.2]               # illustrative output scores for the three lines


def edges_between(xa, ya, xb, yb, color=EDGE, w=1.1):
    return [f'<line x1="{xa}" y1="{y1}" x2="{xb}" y2="{y2}" stroke="{color}" stroke-width="{w}"/>'
            for y1 in ya for y2 in yb]


# --- History and photos --------------------------------------------------------
def pixels(photo: Path) -> str | None:
    """The photo at 224 by 224, one 5 by 5 patch boxed, then zoomed to its values."""
    try:
        from PIL import Image
    except ImportError:
        print("pixels.svg skipped: no Pillow", file=sys.stderr)
        return None
    im = Image.open(photo).convert("RGB")
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((224, 224), Image.LANCZOS)
    small = photo.parent / "tiger-224.jpg"
    im.save(small, quality=90)
    px0, py0, n = 104, 72, 5                       # the patch, in the 224 image
    k = 1.5                                         # the photo is drawn at 336 px
    W, H = 1000, 400
    ox, oy = 30, 22
    left = [f'<image href="photos/{small.name}" x="{ox}" y="{oy}" width="{224 * k}" height="{224 * k}"/>',
            text(ox + 112 * k, oy + 224 * k + 26, "224 by 224 pixels", size=17, fill=MUTED)]
    box = [rect(ox + px0 * k - 3, oy + py0 * k - 3, n * k + 6, n * k + 6, fill="none", stroke=WHITE, rx=0, sw=5),
           rect(ox + px0 * k - 3, oy + py0 * k - 3, n * k + 6, n * k + 6, fill="none", stroke=ALERT, rx=0, sw=2.5)]
    cell, zx, zy = 64, 450, 22
    zoom = [line(ox + (px0 + n) * k + 2, oy + py0 * k, zx - 6, zy + 4, color=ALERT, w=1.4, marker="", dash="4 3"),
            line(ox + (px0 + n) * k + 2, oy + (py0 + n) * k, zx - 6, zy + n * cell - 4, color=ALERT, w=1.4, marker="",
                 dash="4 3")]
    for i in range(n):
        for j in range(n):
            r, g, b = im.getpixel((px0 + i, py0 + j))
            ink = INK if (0.299 * r + 0.587 * g + 0.114 * b) > 140 else WHITE
            x, y = zx + i * cell, zy + j * cell
            zoom += [f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="rgb({r},{g},{b})" '
                     f'stroke="{WHITE}" stroke-width="1"/>']
            zoom += [text(x + cell / 2, y + 19 + 17 * t, v, size=14, fill=ink) for t, v in enumerate((r, g, b))]
    zoom.append(text(zx + n * cell / 2, zy + n * cell + 26, "25 of its pixels: red, green, blue", size=17, fill=MUTED))
    count = [text(zx + n * cell + 22, 120, "224 × 224 × 3", size=22, weight="bold", anchor="start"),
             text(zx + n * cell + 22, 160, "= 150,528", size=26, weight="bold", anchor="start", fill=ACCENT,
                  cls="accent-fill"),
             text(zx + n * cell + 22, 190, "numbers", size=20, anchor="start"),
             text(zx + n * cell + 22, 250, "not one of them", size=17, anchor="start", fill=MUTED),
             text(zx + n * cell + 22, 272, "says tiger", size=17, anchor="start", fill=MUTED)]
    body = [step(1, left), step(2, box + zoom), step(3, count)]
    return svg(W, H, body, "An openly licensed tiger photo (images/photos/CREDITS.md) resized to 224 by 224, and 25 of "
               "its pixels with their red, green and blue values, read from that resized copy. " + LICENCE)


def _picture(cx, y, w, h, name):
    """An openly licensed photo from images/photos/ (CREDITS.md), centred on cx, with a thin frame."""
    x = cx - w / 2
    return [f'<image href="photos/{name}" x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" '
            f'preserveAspectRatio="xMidYMid slice"/>',
            rect(x, y, w, h, fill="none", stroke=EDGE, rx=0, sw=1.2)]


def _axis(x0, x1, y0, y1, years, tx, muted=False):
    col, cls = (GREY_INK, "") if muted else (ACCENT, "accent-fill")
    out = [f'<polygon{" class=" + chr(34) + cls + chr(34) if cls else ""} points="{x0},{y0} {x1 - 28},{y0} '
           f'{x1 - 28},{y0 - 12} {x1},{(y0 + y1) / 2} {x1 - 28},{y1 + 12} {x1 - 28},{y1} {x0},{y1}" fill="{col}"/>']
    out += [text(tx(yr), (y0 + y1) / 2 + 6, str(yr), size=15, weight="bold", fill=WHITE) for yr in years]
    return out


def _event(cx, yr_x, top, h, pic, lines_, y_axis):
    """A picture, its caption under it, and a dashed leader down to its year on the axis."""
    cap_y = top + h + 28
    out = list(pic)
    out += [text(cx, cap_y + 22 * i, s_, size=18 if i == 0 else 15, weight="bold" if i == 0 else "normal",
                 fill=INK if i < 2 else MUTED) for i, s_ in enumerate(lines_)]
    y_lead = cap_y + 22 * (len(lines_) - 1) + 10
    out.append(path(f"M {cx} {y_lead} L {yr_x:.1f} {y_axis - 3}", color=MUTED, w=1.3, marker="")
               .replace('fill="none"', 'fill="none" stroke-dasharray="3 3"'))
    return out


def timeline(part: int) -> str:
    """Part 1: three ideas, 1958 to 1998. Part 2: data, graphics cards and size, 2009 to 2022."""
    W, H = 1000, 430
    if part == 1:
        H, y0, y1 = 372, 330, 362

        def tx(yr):
            return 60 + (yr - 1950) * 880 / 52

        events = [
            (200, 1958, _picture(200, 14, 211, 200, "perceptron.jpg"),
             ["1958 · The perceptron", "one artificial neuron", "learns from examples"]),
            (520, 1986, _picture(520, 14, 191, 200, "hinton.jpg"),
             ["1986 · Back-propagation", "errors sent back through layers", "pictured: G. Hinton, a co-author"]),
            (820, 1998, _picture(820, 14, 300, 200, "mnist.png"),
             ["1998 · LeNet", "reads handwritten digits", "on bank cheques"]),
        ]
        body = [step(1, _axis(20, 990, y0, y1, [1958, 1986, 1998], tx))]
        body += [step(i + 2, _event(cx, tx(yr), 14, 200, pic, ls, y0)) for i, (cx, yr, pic, ls) in enumerate(events)]
        comment = ("Three ideas on a time axis, 1950 to 2002: Rosenblatt's perceptron (1958; the Mark I Perceptron, "
                   "U.S. Navy photo, public domain), back-propagation (Rumelhart, Hinton and Williams 1986; G. Hinton "
                   "by Arthur Petron, CC BY-SA 4.0), LeNet (LeCun et al. 1998; MNIST digits by Josef Steppan, CC BY-SA "
                   "4.0). Photos cropped and resized; see images/photos/CREDITS.md. ")
        return svg(W, H, body, comment + LICENCE)

    H, y0, y1 = 372, 330, 362

    def tx(yr):
        return 60 + (yr - 2008) * 880 / 15

    cols = [95 + i * 162 for i in range(6)]
    top, th, tw = 16, 150, 150
    gt = top + (th - 120) / 2              # the drawn glyphs are 120 high

    def tile(cx):
        return rect(cx - tw / 2, top, tw, th, fill="#f4f6f7", stroke=EDGE, rx=4, sw=1.2)

    def mosaic(cx):
        out = [tile(cx)]
        shades = [ACCENT, A_LIGHT, GREY_INK, B, B_LIGHT, "#f0c46a"]
        for i in range(6):
            for j in range(4):
                k = (i * 5 + j * 3 + i * j) % len(shades)
                out.append(rect(cx - 63 + i * 21, gt + 14 + j * 24, 19, 21, fill=shades[k], stroke=None, rx=2))
        return out

    def stack(cx):
        out = [tile(cx)]
        out += [rect(cx - 30, gt + 8 + i * 3.5, 60, 2.2, fill=ACCENT, stroke=None, rx=0, cls="accent-fill")
                for i in range(30)]
        return out

    def attention(cx):
        out = [tile(cx)]
        for i in range(6):
            for j in range(6):
                v = 0.85 if i == j else (0.45 if abs(i - j) == 1 else (0.25 if (i + 2 * j) % 5 == 0 else 0.08))
                out.append(f'<rect class="accent-fill" x="{cx - 51 + i * 17}" y="{gt + 9 + j * 17}" width="15" '
                           f'height="15" fill="{ACCENT}" fill-opacity="{v}"/>')
        return out

    def weights(cx):
        out = [tile(cx)]
        out += [f'<circle cx="{cx - 62 + i * 8.6:.1f}" cy="{gt + 10 + j * 8.4:.1f}" r="2.3" fill="{ACCENT}" '
                f'class="accent-fill" fill-opacity="{0.35 + 0.6 * ((i * 7 + j * 11) % 5) / 4:.2f}"/>'
                for i in range(15) for j in range(13)]
        return out

    def chat(cx):
        out = [tile(cx)]
        out += [f'<path d="M {cx - 58} {gt + 14} h 80 a 8 8 0 0 1 8 8 v 26 a 8 8 0 0 1 -8 8 h -62 l -14 12 v -12 '
                f'a 8 8 0 0 1 -4 -8 v -26 a 8 8 0 0 1 8 -8 z" fill="{WHITE}" stroke="{GREY_INK}" stroke-width="1.6"/>',
                f'<path class="accent-fill" d="M {cx - 22} {gt + 66} h 72 a 8 8 0 0 1 8 8 v 26 a 8 8 0 0 1 -4 8 v 12 '
                f'l -14 -12 h -62 a 8 8 0 0 1 -8 -8 v -26 a 8 8 0 0 1 8 -8 z" fill="{ACCENT}"/>']
        out += [rect(cx - 50, gt + 25 + 12 * k, 64 - 18 * k, 4, fill=GREY_INK, stroke=None, rx=2) for k in range(2)]
        out += [rect(cx - 12, gt + 78 + 12 * k, 56 - 16 * k, 4, fill=WHITE, stroke=None, rx=2) for k in range(2)]
        return out

    gpu_h = round(258 * tw / 460)
    events = [
        (2009, mosaic(cols[0]), ["ImageNet", "3.2 million", "labelled photos"]),
        (2012, [tile(cols[1])] + _picture(cols[1], top + (th - gpu_h) // 2, tw, gpu_h, "gtx580.jpg"),
         ["AlexNet", "two graphics cards:", "GTX 580"]),
        (2015, stack(cols[2]), ["ResNet", "152 layers"]),
        (2017, attention(cols[3]), ["The transformer", "built for", "translation"]),
        (2020, weights(cols[4]), ["GPT-3", "175 billion", "weights"]),
        (2022, chat(cols[5]), ["ChatGPT", "a chatbot open", "to the public"]),
    ]
    parts = [_event(cx, tx(yr), top, th, pic, ls, y0) for cx, (yr, pic, ls) in zip(cols, events)]
    body = [step(1, _axis(20, 990, y0, y1, [e[0] for e in events], tx)),
            step(2, parts[0] + parts[1]), step(3, parts[2] + parts[3]), step(4, parts[4] + parts[5])]
    comment = ("Six milestones, 2009 to 2022: ImageNet (Deng et al. 2009), AlexNet on two GTX 580 cards (Krizhevsky "
               "et al. 2012; a GTX 580 board by Fritzchens Fritz, CC0), ResNet (He et al. 2016), the transformer "
               "(Vaswani et al. 2017), GPT-3 (Brown et al. 2020), ChatGPT (OpenAI 2022). The mosaic, stack, grid, "
               "dots and bubbles are drawn. ")
    return svg(W, H, body, comment + LICENCE)


def tasks() -> str:
    """What, where, which pixels: three questions to ask of a photo."""
    W, H = 1000, 330

    def frame(x0):
        return rect(x0, 20, 290, 200, fill=WHITE, stroke=EDGE, rx=6, sw=1.6)

    def tree(x, y, fill=GREY_INK):
        return (f'<rect x="{x - 6}" y="{y}" width="12" height="44" fill="{fill}"/>'
                f'<circle cx="{x}" cy="{y - 18}" r="30" fill="{fill}" fill-opacity="0.55"/>')

    def scene(x0, mask=False):
        g = [tree(x0 + 225, 130), glyph(x0 + 110, 140, s=0.95)]
        if mask:
            g = [tree(x0 + 225, 130, fill=B), glyph(x0 + 110, 140, s=0.95, fill=ACCENT, cls="accent-fill")]
        return g

    what = [frame(20)] + scene(20) + [
        rect(95, 232, 140, 34, fill=A_LIGHT, stroke=ACCENT, cls="accent-a-light-fill accent-stroke", rx=17),
        text(165, 255, "animal", size=18, weight="bold"),
        text(165, 300, "What? One label per photo", size=18, weight="bold")]
    where = [frame(355)] + scene(355) + [
        rect(405, 82, 128, 104, fill="none", stroke=ACCENT, cls="accent-stroke", rx=2, sw=3),
        text(410, 76, "animal", size=15, weight="bold", anchor="start", fill=ACCENT, cls="accent-fill"),
        rect(545, 72, 72, 108, fill="none", stroke=GREY_INK, rx=2, sw=3),
        text(550, 66, "tree", size=15, weight="bold", anchor="start", fill=GREY_INK),
        text(500, 300, "Where? A box per object", size=18, weight="bold")]
    which = [frame(690)] + scene(690, mask=True) + [
        text(835, 300, "Which pixels? A label for each pixel", size=18, weight="bold")]
    return svg(W, H, [step(1, what), step(2, where), step(3, which)],
               "Three questions asked of a photo: classification (a label), detection (boxes) and segmentation "
               "(a label for each pixel); after Prince (2023), section 10.5. Illustrative shapes. " + LICENCE)


# --- How a network learns, on the example wine -----------------------------------
def unit() -> str:
    """One neuron: the wine's three values times weights, summed with a bias, then the logistic function."""
    W, H = 1000, 360
    ws, b = [0.5, -2.0, 1.5], -7.0                 # illustrative
    z = sum(v * w for (_, v), w in zip(WINE, ws)) + b
    p = 1 / (1 + math.exp(-z))
    ins = []
    for i, ((name, v), w) in enumerate(zip(WINE, ws)):
        y = 70 + i * 100
        ins += [text(184, y + 6, name, size=16, fill=MUTED, anchor="end"),
                node(230, y, r=30), text(230, y + 7, f"{v}", size=19, weight="bold"),
                line(262, y, 416, 170, color=EDGE, w=2, marker=""),
                text(296, y + 0.22 * (170 - y) + (-12 if i < 2 else 24), f"× {w:+.1f}".replace("-", "−"), size=17,
                     fill=ACCENT, cls="accent-fill", weight="bold", anchor="start")]
    ins.append(text(160, 30, "one wine, three of its values", size=16, fill=MUTED))
    s_ = [rect(420, 120, 190, 100, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
          text(515, 155, "weighted sum", size=18, weight="bold"),
          text(515, 180, f"plus a bias ({b:+.1f})".replace("-", "−"), size=15, fill=MUTED),
          text(515, 207, f"= {z:.2f}".replace("-", "−"), size=19, weight="bold")]
    cx, cy = 690, 120
    curve = " ".join(f"{cx + 10 + t * 13:.1f},{cy + 90 - 80 / (1 + math.exp(-(t - 6))):.1f}" for t in range(13))
    sq = [line(612, 170, 676, 170, color=INK, w=1.8),
          rect(cx, cy, 176, 100, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
          f'<polyline points="{curve}" fill="none" stroke="{ACCENT}" class="accent-stroke" stroke-width="3"/>',
          text(cx + 88, cy + 126, "a function: here 0 to 1", size=15, fill=MUTED),
          line(868, 170, 900, 170, color=INK, w=1.8),
          text(950, 162, f"{p:.2f}", size=26, weight="bold", fill=ACCENT, cls="accent-fill"),
          text(950, 188, "P(high)", size=15, fill=MUTED)]
    cap = [text(520, 330, "the logistic regression of the first day", size=19, weight="bold", fill=ACCENT,
                cls="accent-fill")]
    return svg(W, H, [step(1, ins), step(2, s_), step(3, sq), step(4, cap)],
               f"One neuron on deck 4's example wine (line 12 of winequality_all.csv: alcohol 12.0, volatile acidity "
               f"0.27, sulphates 0.56), illustrative weights {ws} and bias {b}: weighted sum {z:.2f}, logistic "
               f"{p:.2f} (Provost and Fawcett 2013, pp. 106 to 108). Weights illustrative. " + LICENCE)


def activation() -> str:
    """Two functions applied after the weighted sum: the logistic, and the ReLU."""
    W, H = 1000, 340

    def panel(x0, title, sub, f, ymin, ymax):
        x1, y_top, y_bot = x0 + 380, 50, 270
        sx = lambda v: x0 + (v + 5) / 10 * (x1 - x0)
        sy = lambda v: y_bot - (v - ymin) / (ymax - ymin) * (y_bot - y_top)
        pts = " ".join(f"{sx(v / 10):.1f},{sy(f(v / 10)):.1f}" for v in range(-50, 51))
        return [line(x0, sy(0), x1, sy(0), color=MUTED, w=1.3, marker=""),
                line(sx(0), y_bot + 6, sx(0), y_top - 10, color=MUTED, w=1.3, marker=""),
                f'<polyline class="accent-stroke" points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="3.4"/>',
                text(x1, sy(0) + 24, "the weighted sum", size=14, fill=MUTED, anchor="end"),
                text((x0 + x1) / 2, 22, title, size=20, weight="bold"),
                text((x0 + x1) / 2, y_bot + 46, sub, size=16, fill=MUTED)]

    logi = panel(60, "logistic", "between 0 and 1: the first day's", lambda v: 1 / (1 + math.exp(-v)), -0.1, 1.1)
    relu = panel(560, "ReLU", "0 below zero, the sum itself above", lambda v: max(0.0, v), -0.5, 5.2)
    return svg(W, H, [step(1, logi), step(2, relu)],
               "Two activation functions of the weighted sum: the logistic sigmoid and the rectified linear unit, the "
               "most common choice (Prince 2023, pp. 25 and 66). " + LICENCE)


NET = {"in": (220, [70, 125, 180, 260, 315]), "h1": (430, [80, 150, 220, 290]),
       "h2": (610, [80, 150, 220, 290]), "out": (800, [110, 185, 260])}


def layers() -> str:
    """Input, hidden and output layers; deep means many hidden ones."""
    W, H = 1000, 400
    xi, yi = NET["in"]
    xo, yo = NET["out"]
    io = [node(xi, y) for y in yi] + [text(xi, 226, "⋮", size=26, fill=MUTED),
                                      text(xi, 30, "input layer", size=17, weight="bold"),
                                      text(xi, 360, "a wine's values", size=16, fill=MUTED),
                                      text(xo, 30, "output layer", size=17, weight="bold"),
                                      text(xo, 330, "one neuron per class", size=16, fill=MUTED)]
    io += [text(xi - 24, y + 5, n, size=15, fill=MUTED, anchor="end")
           for y, n in zip(yi, ["alcohol", "volatile acidity", "sulphates", "pH", "colour"])]
    for y, n in zip(yo, LINES):
        io += [node(xo, y, r=16, fill=A_LIGHT, cls="accent-a-light-fill"),
               text(xo + 30, y + 6, n, size=18, anchor="start")]
    hid = []
    for a, b_ in (("in", "h1"), ("h1", "h2"), ("h2", "out")):
        hid += edges_between(NET[a][0], NET[a][1], NET[b_][0], NET[b_][1])
    hid += [node(x, y) for k in ("h1", "h2") for x in [NET[k][0]] for y in NET[k][1]]
    hid += [text(520, 30, "hidden layers", size=17, weight="bold")]
    deep = [path("M 410 330 L 410 340 L 630 340 L 630 330", color=ACCENT, w=2.2, marker="", cls="accent-stroke"),
            text(520, 368, "deep: more than one hidden layer", size=17, weight="bold", fill=ACCENT, cls="accent-fill")]
    # the hidden layers go under the input and output units, so they are drawn first
    return svg(W, H, [step(2, hid), step(1, io), step(3, deep)],
               "A network's layers on deck 4's wines: input neurons for a wine's values, two hidden layers, one output "
               "neuron per line (low, medium, high); deep means more than one hidden layer (Prince 2023, p. 41). "
               "Schematic. " + LICENCE)


def forward() -> str:
    """The wine's values flow forward, layer by layer, to one score per line."""
    W, H = 1000, 380
    cols = {"in": (200, [80, 180, 280]), "h": (480, [80, 180, 280]), "out": (760, [80, 180, 280])}
    vals = {"in": [f"{v}" for _, v in WINE], "h": ["0.9", "0", "1.4"],
            "out": [f"{v:.1f}" for v in SCORES]}
    groups = []
    prev = None
    for k in ("in", "h", "out"):
        x, ys = cols[k]
        g = []
        if prev:
            g += edges_between(cols[prev][0] + 32, cols[prev][1], x - 32, ys, color=EDGE, w=1.6)
        for y, v in zip(ys, vals[k]):
            g += [node(x, y, r=30, fill=A_LIGHT if k == "out" else WHITE,
                       cls="accent-a-light-fill accent-stroke" if k == "out" else "accent-stroke"),
                  text(x, y + 7, v, size=19, weight="bold")]
        groups.append(g)
        prev = k
    groups[0] += [text(200, 335, "the wine's values", size=16, fill=MUTED)]
    groups[0] += [text(156, y + 5, n, size=15, fill=MUTED, anchor="end") for y, (n, _) in zip(cols["in"][1], WINE)]
    groups[1] += [text(480, 335, "each neuron: a weighted sum, then ReLU", size=16, fill=MUTED)]
    groups[2] += [text(760, 335, "one score per line", size=16, fill=MUTED)]
    for y, n in zip(cols["out"][1], LINES):
        groups[2].append(text(805, y + 7, n, size=18, anchor="start"))
    arrow = [line(200, 365, 900, 365, color=ACCENT, w=2.4, marker="ahA", cls="accent-stroke"),
             text(550, 357, "forward", size=15, weight="bold", fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, groups[0]), step(2, groups[1] + arrow), step(3, groups[2])],
               "A forward pass on deck 4's example wine (alcohol 12.0, volatile acidity 0.27, sulphates 0.56): three "
               f"hidden neurons, three line scores {SCORES}, those of the next slide's softmax. Hidden values and "
               "scores illustrative. " + LICENCE)


def _probs():
    e = [math.exp(v) for v in SCORES]
    return [x / sum(e) for x in e]


def softmax() -> str:
    """Three scores become three probabilities that sum to one."""
    W, H = 1000, 390
    p = _probs()
    top_i = max(range(3), key=lambda i: p[i])
    left = [text(150, 40, "the last layer's scores", size=19, weight="bold")]
    for i, (n, v) in enumerate(zip(LINES, SCORES)):
        y = 80 + i * 86
        left += [rect(40, y, 220, 60, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
                 text(150, y + 38, f"{n}: {v:+.1f}".replace("-", "−"), size=22)]
    mid = [line(300, 190, 450, 190, color=ACCENT, w=2.6, marker="ahA", cls="accent-stroke"),
           text(375, 170, "softmax", size=20, weight="bold"),
           text(375, 222, "e to each score,", size=15, fill=MUTED), text(375, 242, "divided by their sum", size=15, fill=MUTED)]
    base, top, x0 = 300, 60, 520
    bars = [text(740, 40, "probabilities, summing to 1", size=19, weight="bold"),
            line(x0 - 10, base, 960, base, color=MUTED, w=1.4, marker="")]
    for i, (n, q) in enumerate(zip(LINES, p)):
        h = q * (base - top)
        x = x0 + i * 150
        lit = i == top_i
        fill, cls = (ACCENT, "accent-fill") if lit else (A_LIGHT, "accent-a-light-fill")
        bars += [rect(x, base - h, 100, h, fill=fill, stroke=None, rx=3, cls=cls),
                 text(x + 50, base - h - 10, f"{q:.2f}", size=21, weight="bold" if lit else "normal"),
                 text(x + 50, base + 28, n, size=19, weight="bold" if lit else "normal")]
    win = [text(740, 378, "the most probable line wins, unless the costs say otherwise", size=17, fill=ACCENT,
                cls="accent-fill", weight="bold")]
    body = [step(1, left), step(2, mid + bars), step(3, win)]
    return svg(W, H, body, f"Softmax of three illustrative line scores {SCORES} into "
               f"{', '.join(f'{q:.2f}' for q in p)}. Illustrative. " + LICENCE)


def loss() -> str:
    """Minus the log of the probability given to the true line: high when wrong, low when right."""
    W, H = 1000, 380
    probs = list(zip(LINES, _probs()))

    def panel(x0, truth, head_):
        q = dict(probs)[truth]
        out = [rect(x0, 20, 440, 270, fill=WHITE, stroke=EDGE, rx=8),
               text(x0 + 220, 52, head_, size=19, weight="bold")]
        base = 230
        for i, (c, v) in enumerate(probs):
            x = x0 + 60 + i * 120
            h = v * 140
            right = c == truth
            out += [rect(x, base - h, 80, h, fill=ACCENT if right else A_LIGHT, stroke=None, rx=3,
                         cls="accent-fill" if right else "accent-a-light-fill"),
                    text(x + 40, base - h - 8, f"{v:.2f}", size=18, weight="bold" if right else "normal"),
                    text(x + 40, base + 24, c, size=17, weight="bold" if right else "normal")]
        l_ = -math.log(q)
        hi = l_ > 1
        out += [text(x0 + 220, 330, f"loss = {l_:.2f}: {'high' if hi else 'low'}", size=22, weight="bold",
                     fill=ALERT if hi else ACCENT, cls="" if hi else "accent-fill")]
        return out, l_

    a, la = panel(20, "low", "this wine's line is low")
    b_, lb = panel(540, "medium", "a medium wine, the same output")
    cap = [text(500, 372, "the loss: minus the log of the probability given to the true line", size=16, fill=MUTED)]
    return svg(W, H, [step(1, a), step(2, b_), step(3, cap)],
               f"Cross-entropy loss on the same illustrative output: {la:.2f} for the example wine, whose line is low, "
               f"{lb:.2f} for a medium wine (Prince 2023, section 5.5). Illustrative. " + LICENCE)


def descent() -> str:
    """Gradient descent on one weight: each step goes a little downhill."""
    W, H = 1000, 380
    x0, x1, y0, y1 = 80, 920, 40, 310

    def L(w):
        return 0.6 * (w - 3) ** 2 + 0.5

    def px(w):
        return x0 + w / 6 * (x1 - x0)

    def py(v):
        return y1 - (v / 6.0) * (y1 - y0)

    curve = " ".join(f"{px(w / 20):.1f},{py(L(w / 20)):.1f}" for w in range(0, 121))
    axes = [line(x0, y1, x1 + 20, y1, color=MUTED, w=1.4), line(x0, y1, x0, y0 - 10, color=MUTED, w=1.4),
            text(x1, y1 + 30, "one weight", size=16, fill=MUTED, anchor="end"),
            text(x0 + 8, y0 - 14, "loss", size=16, fill=MUTED, anchor="start"),
            f'<polyline points="{curve}" fill="none" stroke="{INK}" stroke-width="2.4"/>']
    ws, w = [0.4], 0.4
    for _ in range(5):
        w = w - 0.35 * 1.2 * (w - 3)
        ws.append(w)
    start = [f'<circle class="accent-fill" cx="{px(ws[0]):.1f}" cy="{py(L(ws[0])):.1f}" r="10" fill="{ACCENT}"/>',
             text(px(ws[0]) + 16, py(L(ws[0])) + 4, "start: a random weight", size=16, anchor="start")]
    steps_ = []
    for a, b_ in zip(ws, ws[1:]):
        steps_ += [line(px(a), py(L(a)) + 2, px(b_) - 4, py(L(b_)) - 6, color=ACCENT, w=2.2, marker="ahA",
                        cls="accent-stroke"),
                   f'<circle class="accent-fill" cx="{px(b_):.1f}" cy="{py(L(b_)):.1f}" r="7" fill="{ACCENT}"/>']
    steps_ += [text(px(2.0), py(L(1.2)) + 30, "each step: a little downhill", size=17, weight="bold", fill=ACCENT,
                    cls="accent-fill", anchor="start")]
    cap = [text(500, 360, "training moves every weight at once: GPT-3 has 175 billion", size=17, weight="bold")]
    return svg(W, H, [step(1, axes + start), step(2, steps_), step(3, cap)],
               "Gradient descent on an illustrative loss curve of one weight, five steps with a fixed step size; "
               "GPT-3's 175 billion parameters from Brown et al. (2020), p. 5. Illustrative. " + LICENCE)


def backprop() -> str:
    """Forward to a score, the loss, then each weight's share of the error sent back."""
    W, H = 1000, 340
    xs = [60, 260, 460, 660]
    names = ["layer 1", "layer 2", "layer 3", "last layer"]
    boxes = []
    for x, n in zip(xs, names):
        boxes += [rect(x, 120, 150, 90, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
                  text(x + 75, 172, n, size=18, weight="bold")]
    fwd = boxes + [line(60, 80, 800, 80, color=GREY_INK, w=2.4), text(430, 66, "forward: the inputs to the scores",
                                                                         size=17, fill=GREY_INK)]
    lw = -math.log(_probs()[0])
    l_ = [line(812, 165, 846, 165, color=INK, w=1.8),
          rect(850, 120, 120, 90, fill="#fdecee", stroke=ALERT, rx=8),
          text(910, 160, "the loss", size=18, weight="bold", fill=ALERT), text(910, 186, f"{lw:.2f}", size=18, fill=ALERT)]
    back = [line(850, 250, 70, 250, color=ACCENT, w=2.8, marker="ahA", cls="accent-stroke", dash="9 6"),
            text(460, 284, "back: each weight gets its share of the error", size=18, weight="bold", fill=ACCENT,
                 cls="accent-fill")]
    back += [line(x + 75, 246, x + 75, 214, color=ACCENT, w=2, marker="ahA", cls="accent-stroke") for x in xs]
    return svg(W, H, [step(1, fwd), step(2, l_), step(3, back)],
               f"Back-propagation: a forward pass to the loss ({lw:.2f}, the example wine of the loss slide), then the "
               "error sent back layer by layer (Rumelhart et al. 1986; Prince 2023, chapter 7). Schematic. " + LICENCE)


def loop() -> str:
    """The training loop: forward, loss, backward, update, one batch at a time."""
    W, H = 1000, 330
    names = [("1 · forward", "a batch of examples", "to the scores"), ("2 · loss", "how wrong", "the batch is"),
             ("3 · backward", "each weight's", "gradient"), ("4 · update", "every weight moves", "a small step")]
    groups = []
    for i, (t, a, b_) in enumerate(names):
        x = 30 + i * 245
        g = [rect(x, 60, 200, 120, fill=A_LIGHT if i == 3 else WHITE, stroke=ACCENT,
                  cls="accent-a-light-fill accent-stroke" if i == 3 else "accent-stroke"),
             text(x + 100, 98, t, size=20, weight="bold"), text(x + 100, 132, a, size=16, fill=MUTED),
             text(x + 100, 154, b_, size=16, fill=MUTED)]
        if i:
            g.insert(0, line(x - 43, 120, x - 4, 120, color=INK, w=2))
        groups.append(g)
    back = [path("M 865 184 L 865 240 L 130 240 L 130 186", color=ACCENT, w=2.6, marker="ahA", cls="accent-stroke"),
            text(497, 272, "then the next batch, until every example has been used", size=17, weight="bold",
                 fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, groups[0]), step(2, groups[1]), step(3, groups[2]), step(4, groups[3]),
                      step(5, back)],
               "The training loop of stochastic gradient descent: forward pass on a batch, loss, backward pass, "
               "update, repeated batch after batch (Prince 2023, sections 6.2 and 7.2; Zhang et al. 2023, section "
               "3.4). " + LICENCE)


def _curve(f, n, px, py):
    return " ".join(f"{px(e):.1f},{py(f(e)):.1f}" for e in [i / 4 for i in range(4 * n + 1)])


def epochs() -> str:
    """One epoch is every training example once; training runs many."""
    W, H = 1000, 390
    tiles = []
    for i in range(29):
        x = 60 + i * 30 + (i // 8) * 14
        tiles.append(rect(x, 30, 24, 24, fill=A_LIGHT if i % 2 else WHITE, stroke=ACCENT,
                          cls="accent-a-light-fill accent-stroke" if i % 2 else "accent-stroke", rx=3, sw=1.2))
    tiles += [path("M 60 66 L 60 76 L 966 76 L 966 66", color=ACCENT, w=2, marker="", cls="accent-stroke"),
              text(513, 100, "one epoch: every training example seen once, a batch at a time", size=17, weight="bold",
                   fill=ACCENT, cls="accent-fill")]
    x0, x1, y0, y1, n = 80, 940, 140, 330, 20

    def px(e):
        return x0 + e / n * (x1 - x0)

    def py(v):
        return y1 - v / 1.2 * (y1 - y0)

    axes = [line(x0, y1, x1 + 10, y1, color=MUTED, w=1.4), line(x0, y1, x0, y0 - 6, color=MUTED, w=1.4),
            text(x1, y1 + 46, "epochs", size=16, fill=MUTED, anchor="end"),
            text(x0 + 8, y0 - 4, "training loss", size=16, fill=MUTED, anchor="start")]
    axes += [text(px(e), y1 + 22, str(e), size=14, fill=MUTED) for e in range(0, n + 1, 5)]
    axes += [line(px(e), y1, px(e), y1 + 6, color=MUTED, w=1.2, marker="") for e in range(1, n + 1)]
    tr = [f'<polyline class="accent-stroke" points="{_curve(lambda e: 0.15 + 0.95 * math.exp(-e / 4), n, px, py)}" '
          f'fill="none" stroke="{ACCENT}" stroke-width="3"/>']
    return svg(W, H, [step(1, tiles), step(2, axes + tr)],
               "One epoch over 29 tiles standing for the training examples, in batches of 8; an illustrative training loss "
               "over 20 epochs (Prince 2023, chapter 6). Illustrative. " + LICENCE)


def early_stop() -> str:
    """Training loss keeps falling; validation loss turns up: stop at its lowest point."""
    W, H = 1000, 380
    x0, x1, y0, y1, n = 80, 940, 40, 300, 20

    def px(e):
        return x0 + e / n * (x1 - x0)

    def py(v):
        return y1 - v / 1.2 * (y1 - y0)

    def val(e):
        return 0.3 + 0.85 * math.exp(-e / 3) + 0.018 * e

    best = min(range(4 * n + 1), key=lambda i: val(i / 4)) / 4
    axes = [line(x0, y1, x1 + 10, y1, color=MUTED, w=1.4), line(x0, y1, x0, y0 - 6, color=MUTED, w=1.4),
            text(x1, y1 + 46, "epochs", size=16, fill=MUTED, anchor="end"),
            text(x0 + 8, y0 - 4, "loss", size=16, fill=MUTED, anchor="start")]
    axes += [text(px(e), y1 + 22, str(e), size=14, fill=MUTED) for e in range(0, n + 1, 5)]
    tr = axes + [f'<polyline class="accent-stroke" points="{_curve(lambda e: 0.12 + 0.95 * math.exp(-e / 4), n, px, py)}" '
                 f'fill="none" stroke="{ACCENT}" stroke-width="3"/>',
                 text(px(19), py(0.12) - 12, "training", size=17, weight="bold", fill=ACCENT, cls="accent-fill",
                      anchor="end")]
    va = [f'<polyline points="{_curve(val, n, px, py)}" fill="none" stroke="{ALERT}" stroke-width="3" '
          f'stroke-dasharray="8 5"/>',
          text(px(19), py(val(19)) - 12, "validation", size=17, weight="bold", fill=ALERT, anchor="end")]
    stop = [line(px(best), y0 + 10, px(best), y1, color=INK, w=2, marker="", dash="5 4"),
            text(px(best) + 10, y0 + 30, "stop here", size=18, weight="bold", anchor="start"),
            f'<rect x="{px(best) + 4:.1f}" y="{y0 + 44}" width="{x1 - px(best) - 4:.1f}" height="{y1 - y0 - 44}" '
            f'fill="{ALERT}" fill-opacity="0.06"/>',
            text((px(best) + x1) / 2, y0 + 70, "overfitting: training improves,", size=16, fill=ALERT),
            text((px(best) + x1) / 2, y0 + 92, "validation gets worse", size=16, fill=ALERT)]
    return svg(W, H, [step(1, tr), step(2, va), step(3, stop)],
               f"Illustrative training and validation loss over 20 epochs; the validation loss is lowest at epoch "
               f"{best:g}, where early stopping ends training (Prince 2023, chapter 8). Illustrative. " + LICENCE)


def convolution() -> str:
    """The same 3 by 3 filter slides over the pixels; where it meets its pattern, its map lights up."""
    W, H = 1000, 380
    c, gx, gy, n = 36, 40, 40, 8
    grid = []
    for i in range(n):
        for j in range(n):
            dark = i < 4
            grid.append(rect(gx + i * c, gy + j * c, c, c, fill="#6c7a80" if dark else GREY, stroke=WHITE, rx=0, sw=1.5))
    pos = [(0, 0), (2, 3), (5, 5)]
    fm_x, fm_y, fc = 520, 76, 36
    m = n - 2

    def window(i, j, dash=False):
        extra = ' stroke-dasharray="6 4"' if dash else ""
        return rect(gx + i * c, gy + j * c, 3 * c, 3 * c, fill="none", stroke=ACCENT, cls="accent-stroke", rx=2, sw=4,
                    extra=extra)

    def hit(i):                                    # the filter finds the vertical edge between columns 3 and 4
        return 1.0 if i in (2, 3) else 0.0

    fmap = [rect(fm_x + i * fc, fm_y + j * fc, fc, fc, fill=WHITE, stroke=EDGE, rx=0, sw=1.2) for i in range(m) for j in range(m)]
    labels = [text(gx + n * c / 2, 26, "the pixels: dark left, light right", size=16, fill=MUTED),
              text(fm_x + m * fc / 2, 62, "the filter's map", size=16, fill=MUTED)]

    def cell(i, j):
        v = hit(i)
        return rect(fm_x + i * fc, fm_y + j * fc, fc, fc, fill=ACCENT if v else GREY, stroke=EDGE, rx=0, sw=1.2,
                    cls="accent-fill" if v else "")

    s1 = grid + fmap + labels + [window(*pos[0]), cell(*pos[0]),
                                 line(gx + 3 * c + 6, gy + 50, fm_x - 8, fm_y + 18, color=ACCENT, w=2, marker="ahA",
                                      cls="accent-stroke")]
    s2 = [window(*pos[1], dash=True), cell(*pos[1])]
    s3 = [cell(i, j) for i in range(m) for j in range(m)] + [
        text(fm_x + m * fc / 2, fm_y + m * fc + 34, "lit where the pattern is: an edge", size=17, weight="bold",
             fill=ACCENT, cls="accent-fill"),
        text(gx + n * c / 2, gy + n * c + 34, "the same 9 weights at every position", size=17, weight="bold")]
    return svg(W, H, [step(1, s1), step(2, s2), step(3, s3)],
               "A 3 by 3 filter slid over an 8 by 8 grid with a vertical edge gives a 6 by 6 feature map, lit where "
               "the edge is (Prince 2023, chapter 10). Illustrative. " + LICENCE)


# --- Augmentation, a plain network on pixels, data sizes, test hygiene ------------
def augment() -> str:
    """Varied copies with the same label: a photo flipped, a sentence with a synonym, a sound filtered."""
    W, H = 1000, 330

    def card(x, y, inner, w=280, h=96):
        return [rect(x - w / 2, y, w, h, fill=WHITE, stroke=EDGE, rx=6, sw=1.6)] + inner

    def wave(x, y, amp, k=1.0):
        pts = " ".join(f"{x - 120 + t * 4:.1f},{y + amp * (math.sin(t / 3.2) + 0.5 * k * math.sin(t / 1.1)):.1f}"
                       for t in range(61))
        return f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" class="accent-stroke" stroke-width="2.4"/>'

    cols = [170, 500, 830]
    heads = ["a photo", "a sentence", "a sound"]
    orig = [card(cols[0], 40, [glyph(cols[0], 88, s=0.55)]),
            card(cols[1], 40, [text(cols[1], 82, "“The wine was excellent.”", size=17),
                               text(cols[1], 108, "label: positive", size=14, fill=MUTED)]),
            card(cols[2], 40, [wave(cols[2], 88, 14)])]
    copy = [card(cols[0], 190, [glyph(cols[0], 238, s=0.55, flip=True)]),
            card(cols[1], 190, [text(cols[1], 232, "“The wine was superb.”", size=17),
                                text(cols[1], 258, "label: positive", size=14, fill=MUTED)]),
            card(cols[2], 190, [wave(cols[2], 238, 14, k=0.25)])]
    how = ["flipped", "a synonym", "filtered"]
    groups = []
    for i in range(3):
        g = [text(cols[i], 26, heads[i], size=18, weight="bold")] + orig[i] + [
            line(cols[i], 140, cols[i], 184, color=ACCENT, w=2.2, marker="ahA", cls="accent-stroke"),
            text(cols[i] + 12, 168, how[i], size=15, fill=ACCENT, cls="accent-fill", anchor="start")] + copy[i]
        groups.append(g)
    same = [text(500, 318, "a new training example, with the same label", size=17, weight="bold")]
    return svg(W, H, [step(1, groups[0]), step(2, groups[1]), step(3, groups[2]), step(4, same)],
               "Data augmentation on three kinds of input: an image flipped, a sentence with a synonym, a sound with "
               "a frequency band attenuated; the label does not change (Prince 2023, sections 9.3.6 and 9.3.8). "
               "Drawn; illustrative. " + LICENCE)


def flatten() -> str:
    """A plain network reads a photo as one long list: neighbours in the grid end up far apart."""
    W, H = 1000, 330
    n, c, gx, gy = 4, 46, 40, 40
    shade = [[0.15, 0.3, 0.55, 0.8], [0.2, 0.35, 0.6, 0.85], [0.25, 0.45, 0.7, 0.9], [0.3, 0.5, 0.75, 0.95]]
    a_, b_ = (1, 1), (1, 2)                          # a pixel and the one below it

    def grey(v):
        g = int(60 + 180 * v)
        return f"rgb({g},{g},{g})"

    grid = [text(gx + n * c / 2, 26, "4 by 4 pixels", size=16, fill=MUTED)]
    for j in range(n):
        for i in range(n):
            grid.append(rect(gx + i * c, gy + j * c, c, c, fill=grey(shade[j][i]), stroke=WHITE, rx=0, sw=1.5))
    mark = [rect(gx + a_[0] * c, gy + a_[1] * c, c, c, fill="none", stroke=ALERT, rx=0, sw=3.5),
            rect(gx + b_[0] * c, gy + b_[1] * c, c, c, fill="none", stroke=ALERT, rx=0, sw=3.5),
            text(gx + n * c / 2, gy + n * c + 30, "neighbours: one above the other", size=16, fill=ALERT)]
    lx, ly, lc = 290, 120, 42
    row = [text(lx + 8 * lc, ly - 40, "the same pixels as one list, row after row", size=16, fill=MUTED),
           line(gx + n * c + 12, gy + n * c / 2, lx - 12, ly + lc / 2, color=INK, w=1.8)]
    for k in range(16):
        j, i = divmod(k, n)
        row.append(rect(lx + k * lc, ly, lc, lc, fill=grey(shade[j][i]), stroke=WHITE, rx=0, sw=1.5))
    ka, kb = a_[1] * n + a_[0], b_[1] * n + b_[0]
    apart = [rect(lx + ka * lc, ly, lc, lc, fill="none", stroke=ALERT, rx=0, sw=3.5),
             rect(lx + kb * lc, ly, lc, lc, fill="none", stroke=ALERT, rx=0, sw=3.5),
             path(f"M {lx + ka * lc + lc / 2} {ly + lc + 6} L {lx + ka * lc + lc / 2} {ly + lc + 22} "
                  f"L {lx + kb * lc + lc / 2} {ly + lc + 22} L {lx + kb * lc + lc / 2} {ly + lc + 6}",
                  color=ALERT, w=2, marker=""),
             text(lx + (ka + kb + 1) * lc / 2, ly + lc + 46, "4 places apart here; 224 in a photo 224 pixels wide", size=16,
                  fill=ALERT, weight="bold")]
    note = [text(lx + 8 * lc, 290, "every input is wired to every neuron alike: nothing says which pixels touch",
                 size=16, weight="bold")]
    return svg(W, H, [step(1, grid), step(2, mark + row + apart), step(3, note)],
               "A 4 by 4 patch unrolled row by row into the 16 inputs of a plain, fully connected layer: two vertical "
               "neighbours land 4 places apart; fully connected networks have no notion of nearby pixels (Prince "
               "2023, p. 161). Illustrative grey levels. " + LICENCE)


def data_sizes() -> str:
    """Training sets, from thousands of examples to hundreds of billions, on a log scale."""
    W, H = 1000, 360
    rows = [(1998, "MNIST", 6e4, "handwritten digits", "LeCun et al. 1998, p. 10"),
            (2012, "ImageNet", 1.28e6, "labelled photos", "He et al. 2016, p. 4"),
            (2018, "BERT", 3.3e9, "words of books and Wikipedia", "Devlin et al. 2019, p. 13"),
            (2020, "GPT-3", 3e11, "tokens of text", "Brown et al. 2020, p. 8"),
            (2021, "CLIP", 4e8, "photos with their captions", "Radford et al. 2021, p. 1")]
    x0, x1, lo, hi = 210, 740, 4, 12

    def px(v):
        return x0 + (math.log10(v) - lo) / (hi - lo) * (x1 - x0)

    axis = [line(x0, 318, x1, 318, color=MUTED, w=1.3, marker="")]
    for e in range(lo, hi + 1, 2):
        axis += [line(px(10 ** e), 312, px(10 ** e), 324, color=MUTED, w=1.2, marker=""),
                 text(px(10 ** e), 344, f"10<tspan baseline-shift='super' font-size='11'>{e}</tspan>", size=15,
                      fill=MUTED)]
    axis.append(text(x1, 300, "training examples, log scale", size=14, fill=MUTED, anchor="end"))

    def bar(i, r):
        yr, name, v, unit, _ = r
        y = 24 + i * 56
        word = f"{v:,.0f}" if v < 1e6 else (f"{v / 1e6:g} million" if v < 1e9 else f"{v / 1e9:g} billion")
        return [text(x0 - 14, y + 20, f"{yr} · {name}", size=16, weight="bold", anchor="end"),
                rect(x0, y + 2, px(v) - x0, 28, fill=ACCENT if i < 2 else A_LIGHT, stroke=None, rx=3,
                     cls="accent-fill" if i < 2 else "accent-a-light-fill"),
                text(px(v) + 10, y + 22, f"{word} {unit}", size=15, anchor="start")]

    imgs = sum((bar(i, r) for i, r in enumerate(rows[:2])), [])
    txts = sum((bar(i + 2, r) for i, r in enumerate(rows[2:])), [])
    return svg(W, H, [step(1, axis + imgs), step(2, txts)],
               "Training-set sizes, log scale: " + "; ".join(f"{r[1]} {r[2]:g} {r[3]} ({r[4]})" for r in rows)
               + ". Units differ: digits, photos, words, tokens, image and caption pairs. " + LICENCE)


def hygiene() -> str:
    """The inherited test set: a photo in both sets, and two photos under the wrong animal."""
    W, H = 1000, 330

    def tile(x, y, name, fill=WHITE, stroke=EDGE, ink=INK):
        return [rect(x, y, 120, 54, fill=fill, stroke=stroke, rx=6, sw=1.6), text(x + 60, y + 33, name, size=16, fill=ink)]

    left = [text(200, 32, "training photos", size=19, weight="bold"), text(760, 32, "test photos", size=19, weight="bold")]
    for i, n in enumerate(["lion_007", "tiger_012", "lion_017", "tiger_020"]):
        left += tile(70 + (i % 2) * 140, 56 + (i // 2) * 74, n)
    for i, n in enumerate(["tiger_003", "lion_031", "lion_017", "tiger_009"]):
        left += tile(630 + (i % 2) * 140, 56 + (i // 2) * 74, n)
    twin = [rect(210, 130, 120, 54, fill="none", stroke=ALERT, rx=6, sw=3),
            rect(630, 130, 120, 54, fill="none", stroke=ALERT, rx=6, sw=3),
            f'<path d="M 330 157 C 450 230, 520 230, 630 157" fill="none" stroke="{ALERT}" stroke-width="2.2"/>',
            text(480, 232, "the same photo in both sets: 8 of the 65", size=17, fill=ALERT, weight="bold"),
            text(480, 254, "test photos were copies of training photos", size=16, fill=ALERT)]
    wrong = tile(140, 236, "labelled lion", fill="#fdecee", stroke=ALERT, ink=ALERT) + [
        text(200, 312, "shows a tiger: 2 such labels", size=16, fill=ALERT, weight="bold")]
    body = [step(1, left), step(2, twin), step(3, wrong)]
    return svg(W, H, body, "The inherited photo sets before cleaning: a test photo byte-identical to a training photo "
               "(8 of 65) and a mislabelled photo (2), as counted on the course copy. File names illustrative. " + LICENCE)


# --- Pretrained networks ---------------------------------------------------------
def lock(x, y, open_=False, color=GREY_INK):
    """A small padlock: closed for a frozen block, open for one that trains."""
    arc = (f"M {x - 7} {y} L {x - 7} {y - 8} A 7 7 0 0 1 {x + 7} {y - 8} L {x + 7} {y - 4}" if open_ else
           f"M {x - 7} {y} L {x - 7} {y - 8} A 7 7 0 0 1 {x + 7} {y - 8} L {x + 7} {y}")
    return (f'<path d="{arc}" fill="none" stroke="{color}" stroke-width="2.4"/>'
            f'<rect x="{x - 10}" y="{y}" width="20" height="15" rx="2" fill="{color}"/>')


def backbone(unlocked: int = 0) -> list[str]:
    """Seven blocks of a pretrained network, the last `unlocked` of them lit and open."""
    out = []
    for i in range(7):
        x = 40 + i * 92
        lit = i >= 7 - unlocked
        out += [rect(x, 110, 76, 110, fill=A_LIGHT if lit else GREY, stroke=ACCENT if lit else GREY_INK, rx=6,
                     sw=2.2 if lit else 1.6, cls="accent-a-light-fill accent-stroke" if lit else ""),
                text(x + 38, 150, f"{i + 1}", size=18, fill=INK if lit else GREY_INK),
                lock(x + 38, 182, open_=lit, color=ACCENT if lit else GREY_INK)]
        if i < 6:
            out.append(line(x + 78, 165, x + 90, 165, color=GREY_INK, w=1.4, marker=""))
    out += [text(360, 90, "a pretrained network: its layers, trained on a large dataset", size=19, weight="bold"),
            line(682, 165, 722, 165, color=INK, w=1.6)]
    return out


def head(lit=True):
    if not lit:
        return [rect(728, 110, 230, 110, fill=WHITE, stroke=GREY_INK, rx=8, sw=1.6),
                text(843, 152, "the old head", size=19), text(843, 180, "the original task's", size=16, fill=MUTED),
                text(843, 200, "classes", size=16, fill=MUTED)]
    return [rect(728, 110, 230, 110, fill=A_LIGHT, stroke=ACCENT, rx=8, sw=2.4, cls="accent-a-light-fill accent-stroke"),
            text(843, 152, "a new head", size=20, weight="bold"), text(843, 180, "your classes", size=18),
            text(843, 204, "learns from your examples", size=15, fill=MUTED)]


def transfer() -> str:
    """Keep the pretrained blocks frozen; replace the last layer by a new head."""
    W, H = 1000, 300
    cap = [text(360, 258, "locked: the pretrained weights stay as they are", size=17, fill=MUTED),
           text(843, 258, "the only weights that learn", size=17, weight="bold", fill=ACCENT, cls="accent-fill")]
    body = [step(1, backbone(0)), step(1, head(lit=False), hide="2-end"), step(2, head()), step(3, cap)]
    return svg(W, H, body, "Transfer learning: a pretrained network's layers, locked, its original output layer "
               "replaced by a new head for the new task's classes, the only part trained (Prince 2023, section 9.3.6; "
               "Zhang et al. 2023, section 14.2). Schematic. " + LICENCE)


def finetune() -> str:
    """The same network with its last two blocks unlocked: fine-tuning."""
    W, H = 1000, 300
    br = [path("M 500 240 L 500 250 L 674 250 L 674 240", color=ACCENT, w=2.2, marker="", cls="accent-stroke"),
          text(587, 278, "fine-tuned: the last 2 learn too", size=17, fill=ACCENT, cls="accent-fill", weight="bold"),
          text(240, 278, "still locked", size=17, fill=MUTED)]
    body = [step(1, backbone(0) + head()), step(2, backbone(2) + br)]
    return svg(W, H, body, "Fine-tuning: the same pretrained network with its last two blocks unlocked and trained "
               "with the new head. Schematic. " + LICENCE)


def general() -> str:
    """A pretrained network: general features in its first layers, specific ones in its last."""
    W, H = 1000, 320
    blocks = []
    for i in range(7):
        x = 40 + i * 92
        v = i / 6
        blocks += [f'<rect class="accent-fill" x="{x}" y="70" width="76" height="110" rx="6" fill="{ACCENT}" '
                   f'fill-opacity="{0.12 + 0.7 * v:.2f}"/>',
                   rect(x, 70, 76, 110, fill="none", stroke=ACCENT, rx=6, sw=1.6, cls="accent-stroke"),
                   text(x + 38, 132, f"{i + 1}", size=18, weight="bold", fill=INK if i < 4 else WHITE)]
        if i < 6:
            blocks.append(line(x + 78, 125, x + 90, 125, color=GREY_INK, w=1.4, marker=""))
    blocks += [text(360, 50, "a pretrained network", size=19, weight="bold"),
               line(682, 125, 722, 125, color=INK, w=1.6),
               rect(728, 70, 230, 110, fill=WHITE, stroke=GREY_INK, rx=8, sw=1.6),
               text(843, 120, "its head", size=19), text(843, 148, "the original classes", size=16, fill=MUTED)]
    gen = [path("M 40 196 L 40 206 L 300 206 L 300 196", color=ACCENT, w=2.2, marker="", cls="accent-stroke"),
           text(170, 234, "first layers: general", size=18, weight="bold", fill=ACCENT, cls="accent-fill"),
           text(170, 258, "useful for other tasks too", size=16, fill=MUTED),
           text(170, 280, "(for photos: edges, colours)", size=15, fill=MUTED)]
    spec = [path("M 408 196 L 408 206 L 958 206 L 958 196", color=INK, w=2.2, marker=""),
            text(683, 234, "last layers and head: specific", size=18, weight="bold"),
            text(683, 258, "fitted to the task it was trained on", size=16, fill=MUTED)]
    return svg(W, H, [step(1, blocks), step(2, gen), step(3, spec)],
               "General first layers and specific last layers in a pretrained network (Yosinski et al. 2014, p. 1); "
               "the shading only orders the blocks. Schematic. " + LICENCE)


def dss_training() -> str:
    """A drawing of Dataiku's Design, Training panel, for Hands-on 4: B0 and zero fine-tuned layers."""
    W, H = 1000, 330
    nav = [rect(20, 20, 230, 290, fill="#f4f6f7", stroke=EDGE, rx=4)]
    for i, n in enumerate(["Target", "Train / Test set", "Training", "Metrics", "Data augmentation"]):
        y = 60 + i * 46
        lit = n == "Training"
        if lit:
            nav.append(rect(20, y - 24, 230, 38, fill=A_LIGHT, stroke=None, rx=0, cls="accent-a-light-fill"))
            nav.append(rect(20, y - 24, 6, 38, fill=ACCENT, stroke=None, rx=0, cls="accent-fill"))
        nav.append(text(44, y, n, size=17, anchor="start", weight="bold" if lit else "normal"))
    pane = [rect(270, 20, 710, 290, fill=WHITE, stroke=EDGE, rx=4), text(296, 58, "Model", size=19, weight="bold",
                                                                         anchor="start")]
    f1 = [text(296, 112, "Pretrained model", size=17, anchor="start"),
          rect(560, 88, 330, 38, fill=WHITE, stroke=GREY_INK, rx=4),
          text(576, 113, "EfficientNet B0", size=17, anchor="start", weight="bold"),
          text(872, 113, "▾", size=17, fill=MUTED)]
    f2 = [text(296, 178, "Number of fine-tuned layers", size=17, anchor="start"),
          rect(560, 154, 90, 38, fill=WHITE, stroke=ACCENT, rx=4, sw=2.4, cls="accent-stroke"),
          text(605, 180, "0", size=19, weight="bold")]
    f3 = [text(296, 246, "The last layer is trained from scratch: with 0, it is the only one that learns.", size=16,
               anchor="start", fill=MUTED, style="italic")]
    return svg(W, H, [step(1, nav + pane + f1), step(2, f2), step(3, f3)],
               "A drawing, not a capture, of Dataiku DSS's Design, Training panel for image classification, labels "
               "as in the previous teacher's 2025 captures of the course server; to be checked on DSS 15.0. " + LICENCE)


def zeroshot() -> str:
    """Zero-shot: the task described in words to a pretrained model, with no example and no training."""
    W, H = 1000, 320
    prompt = [rect(30, 40, 430, 190, fill="#f4f6f7", stroke=EDGE, rx=10),
              text(50, 76, "Is this review positive or negative?", size=17, weight="bold", anchor="start"),
              text(50, 120, "“The bottle arrived broken, and", size=17, anchor="start"),
              text(50, 146, "what was left tasted of cork.”", size=17, anchor="start"),
              text(50, 200, "the task, in words; no labelled example", size=15, fill=MUTED, anchor="start")]
    model = [line(466, 135, 540, 135, color=INK, w=2),
             rect(546, 85, 190, 100, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
             text(641, 128, "a pretrained", size=18, weight="bold"), text(641, 152, "language model", size=18,
                                                                          weight="bold"),
             text(641, 212, "no weight changes", size=15, fill=MUTED)]
    answer = [line(742, 135, 800, 135, color=INK, w=2),
              rect(806, 105, 160, 60, fill=A_LIGHT, stroke=ACCENT, rx=30, cls="accent-a-light-fill accent-stroke"),
              text(886, 142, "negative", size=20, weight="bold")]
    cap = [text(500, 292, "for photos, CLIP compares a photo with the class names written as text", size=16,
                fill=MUTED)]
    return svg(W, H, [step(1, prompt), step(2, model), step(3, answer), step(4, cap)],
               "Zero-shot: a pretrained model given only a natural-language description of the task (Brown et al. "
               "2020, p. 7); CLIP does the same for images from the class names (Radford et al. 2021, p. 6). The "
               "review is invented. " + LICENCE)


# --- Hands-on 4 --------------------------------------------------------------------
def flow() -> str:
    """The Flow of Hands-on 4: two folders, listings, labels, the model, the score, the check."""
    W, H = 1000, 380

    def folder(x, y, name):
        return [f'<path class="accent-stroke" d="M {x} {y + 8} L {x + 22} {y + 8} L {x + 30} {y} L {x + 64} {y} '
                f'L {x + 64} {y + 50} L {x} {y + 50} Z" fill="{WHITE}" stroke="{ACCENT}" stroke-width="2"/>',
                text(x + 32, y + 74, name, size=15)]

    def dataset(x, y, name, sub=""):
        out = [rect(x, y, 56, 50, fill=A_LIGHT, stroke=ACCENT, rx=6, cls="accent-a-light-fill accent-stroke"),
               text(x + 28, y + 74, name, size=15)]
        if sub:
            out.append(text(x + 28, y + 92, sub, size=13, fill=MUTED))
        return out

    def recipe(x, y, name, fill="#f0c46a", below=False):
        return [f'<circle cx="{x}" cy="{y}" r="20" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>',
                text(x, y + 42 if below else y - 30, name, size=14, fill=MUTED)]

    def model(x, y):
        return [f'<polygon class="accent-fill" points="{x},{y - 30} {x + 30},{y} {x},{y + 30} {x - 30},{y}" '
                f'fill="{ACCENT}"/>', text(x + 40, y + 6, "the model", size=15, weight="bold", anchor="start")]

    def arr(x1, y1, x2, y2):
        return line(x1, y1, x2, y2, color=INK, w=1.6)

    y1, y2 = 60, 250
    row1 = (folder(20, y1, "train") + [arr(88, y1 + 25, 128, y1 + 25)] + recipe(150, y1 + 25, "List")
            + [arr(172, y1 + 25, 212, y1 + 25)] + dataset(216, y1, "listing")
            + [arr(276, y1 + 25, 316, y1 + 25)] + recipe(338, y1 + 25, "Prepare")
            + [arr(360, y1 + 25, 400, y1 + 25)] + dataset(404, y1, "labelled", "label from the name")
            + [text(20, 30, "steps 1 and 2", size=15, weight="bold", fill=ACCENT, cls="accent-fill", anchor="start")])
    lab = ([arr(464, y1 + 25, 520, y1 + 25)] + recipe(542, y1 + 25, "Lab", fill="#8fd19e")
           + [arr(564, y1 + 25, 610, y1 + 25)] + model(642, y1 + 25))
    row2 = (folder(20, y2, "test") + [arr(88, y2 + 25, 128, y2 + 25)] + recipe(150, y2 + 25, "List")
            + [arr(172, y2 + 25, 212, y2 + 25)] + dataset(216, y2, "listing")
            + [arr(276, y2 + 25, 316, y2 + 25)] + recipe(338, y2 + 25, "Prepare")
            + [arr(360, y2 + 25, 400, y2 + 25)] + dataset(404, y2, "labelled")
            + [arr(464, y2 + 25, 620, y2 + 25)] + recipe(642, y2 + 25, "Score", fill="#8fd19e", below=True)
            + [arr(642, y1 + 57, 642, y2 + 3)]
            + [arr(664, y2 + 25, 700, y2 + 25)] + dataset(704, y2, "scored", "a prediction per photo")
            + [text(20, y2 - 30, "step 3", size=15, weight="bold", fill=ACCENT, cls="accent-fill", anchor="start")])
    check = ([arr(764, y2 + 25, 800, y2 + 25)] + recipe(822, y2 + 25, "Prepare")
             + [arr(844, y2 + 25, 880, y2 + 25)] + dataset(884, y2, "checked", "right or wrong"))
    return svg(W, H, [step(1, row1), step(2, lab), step(3, row2), step(4, check)],
               "The Flow of Hands-on 4, drawn after Dataiku DSS's Flow (folders, recipes, datasets, a model), with "
               "the sheet's steps; recipe colours schematic. " + LICENCE)


def interval() -> str:
    """51 right of 57 is 89%, and could be anything from 78% to 96%."""
    W, H = 1000, 260
    x0, x1 = 60, 940

    def px(v):
        return x0 + (v - 70) / 30 * (x1 - x0)

    axis = [line(x0, 120, x1, 120, color=MUTED, w=1.4, marker="")]
    axis += [line(px(v), 114, px(v), 126, color=MUTED, w=1.2, marker="") for v in range(70, 101, 5)]
    axis += [text(px(v), 150, f"{v}%", size=15, fill=MUTED) for v in range(70, 101, 5)]
    pt = [f'<circle class="accent-fill" cx="{px(89.5):.1f}" cy="120" r="10" fill="{ACCENT}"/>',
          text(px(89.5), 92, "51 of 57 right: 89%", size=18, weight="bold")]
    ci = [rect(px(78.5), 112, px(96.0) - px(78.5), 16, fill=ACCENT, stroke=None, rx=8, cls="accent-fill",
               extra=' fill-opacity="0.3"'),
          text(px(78.5), 182, "78%", size=17, weight="bold", fill=ACCENT, cls="accent-fill"),
          text(px(96.0), 182, "96%", size=17, weight="bold", fill=ACCENT, cls="accent-fill"),
          text(px(87.2), 214, "a 95% interval: the score could be anywhere here", size=17, fill=ACCENT,
               cls="accent-fill")]
    big = [rect(px(89.0), 230, px(90.0) - px(89.0), 12, fill=INK, stroke=None, rx=4),
           text(px(90.0) + 14, 241, "with 10,000 test photos: about 1 point either way", size=15, anchor="start")]
    return svg(W, H, [step(1, axis + pt), step(2, ci), step(3, big)],
               "An observed 51 of 57 (89%) with its 95% Clopper-Pearson interval, 78% to 96%, against the at most 1 "
               "point of 10,000 test images (Recht et al. 2019). " + LICENCE)


# --- Reading the result ------------------------------------------------------------
def _heat(x0, S, n, scramble=False):
    cell = S / n

    def seg_dist(px, py, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - ax - t * dx, py - ay - t * dy)

    out = []
    for i in range(n):
        for j in range(n):
            px, py = -S / 2 + (i + 0.5) * cell, -S / 2 + (j + 0.5) * cell
            eye = math.exp(-((px - 18) ** 2 + (py + 18) ** 2) / 500)
            edge = max(math.exp(-seg_dist(px, py, *s) ** 2 / 90) for s in
                       ((-50, 40, -10, -40), (-10, -40, 50, 40), (-50, 40, 50, 40)))
            v = min(1.0, eye + 0.55 * edge)
            if scramble:
                v = min(1.0, 0.94 * v + (0.05 if (i * 7 + j * 3) % 4 == 0 else 0.0))
            if v > 0.08:
                out.append(f'<rect x="{x0 + i * cell:.1f}" y="{20 + j * cell:.1f}" '
                           f'width="{cell:.1f}" height="{cell:.1f}" fill="{ACCENT}" fill-opacity="{v:.2f}"/>')
    return out


def saliency_map() -> str:
    """An image and its gradient map: the pixels the class score is most sensitive to."""
    W, H, S, n = 1000, 300, 210, 10

    def frame(x0):
        return rect(x0, 20, S, S, fill=WHITE, stroke=EDGE, rx=4, sw=1.6)

    img = [frame(160), glyph(160 + S / 2, 20 + S / 2), text(160 + S / 2, 262, "an image the model calls tiger", size=17,
                                                          weight="bold")]
    grad = [line(382, 125, 618, 125, color=ACCENT, w=2.4, marker="ahA", cls="accent-stroke"),
            frame(630)] + _heat(630, S, n) + [text(630 + S / 2, 262, "its map: the pixels the score", size=17,
                                                   weight="bold"),
                                              text(630 + S / 2, 284, "is most sensitive to", size=17, weight="bold")]
    return svg(W, H, [step(1, img), step(2, grad)],
               "A saliency map as the gradient of the class score with respect to the pixels (Simonyan et al. "
               "2014). Illustrative: shapes stand for a photo, the map is drawn. " + LICENCE)


def saliency_scrambled() -> str:
    """The map, and a near-identical one after the model's top layers are scrambled."""
    W, H, S, n = 1000, 300, 210, 10

    def frame(x0):
        return rect(x0, 20, S, S, fill=WHITE, stroke=EDGE, rx=4, sw=1.6)

    a = [frame(160)] + _heat(160, S, n) + [text(160 + S / 2, 262, "the trained model's map", size=17, weight="bold")]
    b_ = [frame(630)] + _heat(630, S, n, scramble=True) + [
        text(630 + S / 2, 262, "after scrambling its top layers:", size=17, fill=ALERT, weight="bold"),
        text(630 + S / 2, 284, "for some methods, the same map", size=17, fill=ALERT, weight="bold")]
    return svg(W, H, [step(1, a), step(2, b_)],
               "A saliency map and a near-identical map after the model's top layers are randomised, as Adebayo "
               "et al. (2018) found for some methods. Illustrative. " + LICENCE)


# --- The compute chart: Epoch AI's training compute, with Lonestar 5 -----------------
LONESTAR5_PEAK = 1.25e15          # FLOP per second at peak (TACC 2015); in production January 2016 to July 2021
DOUBLING_EARLY, DOUBLING_DL = 20, 6   # months, Sevilla et al. (2022), rounded


def _models():
    rows = []
    with open(HERE / "compute.csv", newline="") as f:
        for r in csv.DictReader(f):
            y, m, dd = (int(v) for v in r["date"].split("-"))
            rows.append((y + (m - 1) / 12 + (dd - 1) / 365, math.log10(float(r["training_compute_flop"])), r["label"]))
    return rows


def _cx(year):
    """Broken axis: 1955 to 2005 compressed on the left, 2008 to 2026 stretched on the right."""
    return 90 + (year - 1955) * 330 / 50 if year <= 2006 else 470 + (year - 2008) * 490 / 18


def _cy(lg):
    return 340 - (lg - 4) * 310 / 23


LABEL_AT = {"Perceptron": (10, 5, "start"), "back-propagation": (10, 5, "start"), "LeNet-5": (10, 5, "start"),
            "AlexNet": (0, 26, "middle"), "ResNet-152": (0, -13, "middle"), "Transformer": (0, 24, "middle"),
            "BERT": (11, 5, "start"), "GPT-3": (-11, 5, "end"), "CLIP": (11, 5, "start"),
            "PaLM": (10, 11, "start"), "GPT-4": (-10, -9, "end"), "Llama 3.1": (0, -13, "middle")}


def _axes():
    out = [line(90, 340, 975, 340, color=MUTED, w=1.4), line(90, 340, 90, 20, color=MUTED, w=1.4),
           f'<path d="M438,346 L446,334 M446,346 L454,334" stroke="{MUTED}" stroke-width="2"/>']
    for lg in range(5, 27, 5):
        out += [line(84, _cy(lg), 975, _cy(lg), color="#eef1f2", w=1, marker=""),
                text(80, _cy(lg) + 5, f"10<tspan baseline-shift='super' font-size='11'>{lg}</tspan>", size=15,
                     fill=MUTED, anchor="end")]
    for yr in (1960, 1980, 2000, 2010, 2015, 2020, 2025):
        out += [line(_cx(yr), 340, _cx(yr), 346, color=MUTED, w=1.2, marker=""),
                text(_cx(yr), 366, str(yr), size=15, fill=MUTED)]
    out.append(text(96, 16, "training compute, FLOP", size=15, fill=MUTED, anchor="start"))
    return out


def _dots(muted=False, early=True, late=True, only=None):
    out = []
    for yr, lg, lab in _models():
        if (yr < 2010 and not early) or (yr >= 2010 and not late):
            continue
        if only is not None and lab not in only:
            out.append(f'<circle cx="{_cx(yr):.1f}" cy="{_cy(lg):.1f}" r="6" fill="{GREY_INK}"/>')
            continue
        x, y = _cx(yr), _cy(lg)
        dx, dy, anc = LABEL_AT[lab]
        out += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{GREY_INK if muted else ACCENT}"'
                f'{"" if muted else " class=" + chr(34) + "accent-fill" + chr(34)}/>',
                text(x + dx, y + dy, lab, size=15, fill=GREY_INK if muted else INK, anchor=anc)]
    return out


def compute(part: int) -> str:
    W, H = 1000, 380
    if part == 1:
        body = [step(1, _axes() + _dots(late=False)), step(2, _dots(early=False))]
        what = "the milestone models' training compute"
    elif part == 2:
        rows = _models()
        late = [(yr, lg) for yr, lg, _ in rows if yr >= 2010]
        my = sum(yr for yr, _ in late) / len(late)
        ml = sum(lg for _, lg in late) / len(late)
        s_dl = math.log10(2) / (DOUBLING_DL / 12)
        a = [f'<line x1="{_cx(2011.5):.1f}" y1="{_cy(ml + (2011.5 - my) * s_dl):.1f}" x2="{_cx(2025.5):.1f}" '
             f'y2="{_cy(ml + (2025.5 - my) * s_dl):.1f}" stroke="{ACCENT}" class="accent-stroke" stroke-width="3" '
             f'stroke-dasharray="9 5"/>',
             text(_cx(2013.3), _cy(ml + (2013.3 - my) * s_dl) - 64, f"since 2012: doubling", size=17, weight="bold",
                  fill=ACCENT, cls="accent-fill", anchor="end"),
             text(_cx(2013.3), _cy(ml + (2013.3 - my) * s_dl) - 42, f"about every {DOUBLING_DL} months", size=17,
                  weight="bold", fill=ACCENT, cls="accent-fill", anchor="end")]
        s_e = math.log10(2) / (DOUBLING_EARLY / 12)
        p0 = rows[0]
        b_ = [f'<line x1="{_cx(1955):.1f}" y1="{_cy(p0[1] + (1955 - p0[0]) * s_e):.1f}" x2="{_cx(2004):.1f}" '
              f'y2="{_cy(p0[1] + (2004 - p0[0]) * s_e):.1f}" stroke="{GREY_INK}" stroke-width="3" stroke-dasharray="9 5"/>',
              text(_cx(1975), _cy(p0[1] + (1975 - p0[0]) * s_e) - 66, f"before: doubling about", size=16, fill=MUTED),
              text(_cx(1975), _cy(p0[1] + (1975 - p0[0]) * s_e) - 46, f"every {DOUBLING_EARLY} months", size=16,
                   fill=MUTED)]
        body = [step(1, _axes() + _dots(muted=True, only={"Perceptron", "LeNet-5", "AlexNet", "GPT-3", "Llama 3.1"})),
                step(2, b_), step(3, a)]
        what = (f"trend lines for doubling times of {DOUBLING_EARLY} months before 2010 and {DOUBLING_DL} months "
                f"after, drawn through the points (Sevilla et al. 2022)")
    else:
        day = LONESTAR5_PEAK * 86400
        ly = _cy(math.log10(day))
        rows = {lab: (yr, lg) for yr, lg, lab in _models()}
        ax_, al = rows["AlexNet"]
        gx, gl = rows["GPT-3"]
        mins = 10 ** al / LONESTAR5_PEAK / 60
        yrs = 10 ** gl / day / 365.25
        ls = [f'<line x1="{_cx(2016.05):.1f}" y1="{ly:.1f}" x2="{_cx(2021.5):.1f}" y2="{ly:.1f}" stroke="{ALERT}" '
              f'stroke-width="3"/>',
              line(_cx(2008.2), ly, _cx(2016), ly, color=ALERT, w=1.6, marker="", dash="4 4"),
              text(_cx(2008.4), ly - 30, "one day of Lonestar 5", size=17, weight="bold", fill=ALERT, anchor="start"),
              text(_cx(2008.4), ly - 10, "at peak, in service 2016 to 2021", size=16, fill=ALERT, anchor="start"),
              line(_cx(2021.5), ly, _cx(2025.5), ly, color=ALERT, w=1.6, marker="", dash="4 4")]
        pic = _picture(225, 26, 230, 154, "hazel-hen.jpg") + [
            text(225, 200, "a Cray XC40, the model of Lonestar 5", size=14, fill=MUTED)]
        notes = [text(_cx(ax_) + 14, _cy(al) + 46, f"{mins:.0f} minutes of it", size=16, weight="bold", anchor="start"),
                 text(_cx(gx) - 12, _cy(gl) - 22, f"{yrs:.0f} years of it", size=17, weight="bold", anchor="end",
                      fill=ACCENT, cls="accent-fill")]
        body = [step(1, _axes() + _dots(muted=True, only={"AlexNet", "GPT-3", "Llama 3.1"})), step(2, ls + pic),
                step(3, notes)]
        what = (f"one day of Lonestar 5 at its peak of {LONESTAR5_PEAK:.3g} FLOP/s ({day:.3g} FLOP): AlexNet in "
                f"{mins:.1f} minutes, GPT-3 in {yrs:.1f} years; peak and training arithmetic differ, so an order of "
                f"magnitude only; inset, HLRS Stuttgart's Cray XC40 Hazel Hen by Julian Herzog, CC BY 4.0")
    return svg(W, H, body, f"Training compute of milestone models, log scale, broken time axis; {what}. Data: Epoch AI, "
               "Data on Notable AI Models, CC BY 4.0 (src/compute.csv). " + LICENCE)


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"timeline-1.svg": lambda: timeline(1), "timeline-2.svg": lambda: timeline(2),
               "data-sizes.svg": data_sizes, "tasks.svg": tasks, "unit.svg": unit, "activation.svg": activation,
               "layers.svg": layers, "forward.svg": forward, "softmax.svg": softmax, "loss.svg": loss,
               "descent.svg": descent, "backprop.svg": backprop, "loop.svg": loop, "epochs.svg": epochs,
               "early-stop.svg": early_stop, "flatten.svg": flatten, "general.svg": general,
               "convolution.svg": convolution, "augment.svg": augment, "hygiene.svg": hygiene,
               "transfer.svg": transfer, "finetune.svg": finetune, "dss-training.svg": dss_training, "zeroshot.svg": zeroshot,
               "flow.svg": flow, "interval.svg": interval, "saliency-map.svg": saliency_map,
               "saliency-scrambled.svg": saliency_scrambled, "compute-1.svg": lambda: compute(1),
               "compute-2.svg": lambda: compute(2), "compute-3.svg": lambda: compute(3)}
    photo = out / "photos" / "tiger-1.jpg"
    if photo.is_file():
        figures["pixels.svg"] = lambda: pixels(photo)
    for name, lit in (("mo", {"MO"}), ("du", {"DU"}), ("dp", {"DP"}), ("ev", {"EV"}), ("de", {"DE"}),
                      ("du-mo", {"DU", "DP", "MO"})):
        figures[f"phase-{name}.svg"] = lambda lit=lit: d.phase_thumb(lit)
    for name, fn in figures.items():
        s = fn()
        if s is None:
            continue
        (out / name).write_text(s, encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
