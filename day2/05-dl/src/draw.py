#!/usr/bin/env python3
"""Draw the hand-authored figures of the deep-learning deck as themeable, stepwise SVGs.

    python3 day2/05-dl/src/draw.py day2/05-dl/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), loaded from there so the decks draw alike. No
figure shows a photo of the course's photo sets, whose licences are unknown:
the photos drawn on are the openly licensed ones in `images/photos/` (see its
`CREDITS.md`), the tiger first among them, as the deck's running example. The
pixel figures read it and need Pillow. The saliency maps, the tiger's box and
mask and their scores are computed by `vision.py` (PyTorch, in its own
environment) into `images/vision/`, which this script only places. The general
figures (a neuron to the loss) run on deck 4's example wine, line 12 of the
course's `winequality_all.csv` (UCI Wine Quality, CC BY 4.0): its attribute
values are real, the weights illustrative. Every other number is a count from a
wiki page, a value from `compute.csv` (Epoch AI's data, CC BY 4.0) or
`top500.csv` (the TOP500 lists' leading systems), or marked illustrative in the
figure's comment and on its slide.
"""

from __future__ import annotations

import csv
import importlib.util
import math
import re
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


# deck 4's example wine: line 12 of winequality_all.csv, a white of grade 5, so line "low"
WINE = [("alcohol", 12.0), ("volatile acidity", 0.27), ("sulphates", 0.56)]
LINES = ["low", "medium", "high"]
SCORES = [0.4, 1.6, 0.2]               # illustrative output scores for the three lines


def edges_between(xa, ya, xb, yb, color=EDGE, w=1.1):
    return [f'<line x1="{xa}" y1="{y1}" x2="{xb}" y2="{y2}" stroke="{color}" stroke-width="{w}"/>'
            for y1 in ya for y2 in yb]


def _tiger(n=5, x0=104, y0=72):
    """The colours of an n by n patch of the 224 by 224 tiger, read with Pillow, by column then row."""
    from PIL import Image
    im = Image.open(HERE.parent / "images" / "photos" / "tiger-224.jpg").convert("RGB")
    return [[im.getpixel((x0 + i, y0 + j)) for j in range(n)] for i in range(n)]


# --- History and photos --------------------------------------------------------
def pixels(photo: Path) -> str | None:
    """The photo at 224 by 224, one 5 by 5 patch boxed, then zoomed: colours only, no numbers yet."""
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
            zoom.append(f'<rect x="{zx + i * cell}" y="{zy + j * cell}" width="{cell}" height="{cell}" '
                        f'fill="rgb({r},{g},{b})" stroke="{WHITE}" stroke-width="1"/>')
    zoom.append(text(zx + n * cell / 2, zy + n * cell + 26, "25 of its pixels", size=17, fill=MUTED))
    count = [text(zx + n * cell + 26, 150, "224 × 224", size=24, weight="bold", anchor="start"),
             text(zx + n * cell + 26, 190, "= 50,176", size=28, weight="bold", anchor="start", fill=ACCENT,
                  cls="accent-fill"),
             text(zx + n * cell + 26, 220, "pixels", size=20, anchor="start")]
    body = [step(1, left), step(2, box + zoom), step(3, count)]
    return svg(W, H, body, "An openly licensed tiger photo (images/photos/CREDITS.md) resized to 224 by 224, and 25 of "
               "its pixels zoomed, in their colours, read from that resized copy. " + LICENCE)


def channels() -> str:
    """The same 25 pixels, split into their red, green and blue values: three numbers per pixel."""
    W, H, n, cell = 1000, 400, 5, 46
    px = _tiger(n)
    names = [("red", "#c0392b"), ("green", "#2e8b57"), ("blue", "#2f6db5")]
    left = [text(130, 30, "the 25 pixels", size=17, fill=MUTED)]
    for i in range(n):
        for j in range(n):
            r, g, b = px[i][j]
            left.append(f'<rect x="{15 + i * cell}" y="{44 + j * cell}" width="{cell}" height="{cell}" '
                        f'fill="rgb({r},{g},{b})" stroke="{WHITE}" stroke-width="1"/>')
    left.append(line(256, 159, 292, 159, color=INK, w=2))
    groups = []
    for c, (name, col) in enumerate(names):
        gx = 300 + c * 232
        g = [text(gx + n * 40 / 2, 30, name, size=19, weight="bold", fill=col)]
        for i in range(n):
            for j in range(n):
                v = px[i][j][c]
                g += [f'<rect x="{gx + i * 40}" y="{44 + j * 46}" width="40" height="46" fill="{col}" '
                      f'fill-opacity="{0.08 + 0.55 * v / 255:.2f}" stroke="{WHITE}" stroke-width="1"/>',
                      text(gx + i * 40 + 20, 44 + j * 46 + 29, str(v), size=15, fill=INK)]
        groups.append(g)
    count = [text(500, 330, "224 × 224 × 3 = 150,528 numbers", size=26, weight="bold", fill=ACCENT, cls="accent-fill"),
             text(500, 362, "three channels: every pixel is a red, a green and a blue value", size=17, fill=MUTED)]
    return svg(W, H, [step(1, left), step(2, groups[0]), step(3, groups[1]), step(4, groups[2]), step(5, count)],
               "The 25 pixels of the photo slide's patch, each split into its red, green and blue values, read from "
               "the 224 by 224 copy of the tiger photo (images/photos/CREDITS.md); 224 × 224 × 3 inputs (Prince 2023, "
               "p. 161). " + LICENCE)


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
             ["1958 · The perceptron", "one neuron that learns", "its weights from examples"]),
            (520, 1986, _picture(520, 14, 191, 200, "hinton.jpg"),
             ["1986 · Back-propagation", "a way to train hidden layers", "pictured: G. Hinton, a co-author"]),
            (820, 1998, _picture(820, 14, 300, 200, "mnist.png"),
             ["1998 · LeNet", "a network that read", "the digits on bank cheques"]),
        ]
        body = [step(1, _axis(20, 990, y0, y1, [1958, 1986, 1998], tx))]
        body += [step(i + 2, _event(cx, tx(yr), 14, 200, pic, ls, y0)) for i, (cx, yr, pic, ls) in enumerate(events)]
        comment = ("Three ideas on a time axis, 1950 to 2002: Rosenblatt's perceptron (1958; the Mark I Perceptron, "
                   "U.S. Navy photo, public domain), back-propagation (Rumelhart, Hinton and Williams 1986; G. Hinton "
                   "by Arthur Petron, CC BY-SA 4.0), LeNet (LeCun et al. 1998; MNIST digits by Josef Steppan, CC BY-SA "
                   "4.0); Prince (2023), p. 37. Photos cropped and resized; see images/photos/CREDITS.md. ")
        return svg(W, H, body, comment + LICENCE)

    H, y0, y1 = 400, 358, 390

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
        (2009, mosaic(cols[0]), ["ImageNet", "millions of photos,", "each labelled", "by people"]),
        (2012, [tile(cols[1])] + _picture(cols[1], top + (th - gpu_h) // 2, tw, gpu_h, "gtx580.jpg"),
         ["AlexNet", "wins ImageNet,", "trained on two", "graphics cards"]),
        (2015, stack(cols[2]), ["ResNet", "152 layers that", "can still", "be trained"]),
        (2017, attention(cols[3]), ["The transformer", "a network", "for text"]),
        (2020, weights(cols[4]), ["GPT-3", "175 billion weights:", "a task from", "a few examples"]),
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
    """What, where, which pixels: three questions asked of one tiger photo, the answers computed."""
    import json
    v = json.loads((HERE.parent / "images" / "vision" / "vision.json").read_text())
    W, H, pw, ph = 1000, 330, 296, 197
    s = pw / v["photo2"]["size"][0]
    x0s = [16, 352, 688]

    def photo(x0):
        return [f'<image href="photos/tiger-2.jpg" x="{x0}" y="20" width="{pw}" height="{ph}"/>',
                rect(x0, 20, pw, ph, fill="none", stroke=EDGE, rx=0, sw=1.2)]

    what = photo(x0s[0]) + [
        rect(x0s[0] + pw / 2 - 70, 232, 140, 34, fill=A_LIGHT, stroke=ACCENT, cls="accent-a-light-fill accent-stroke", rx=17),
        text(x0s[0] + pw / 2, 255, "tiger", size=18, weight="bold"),
        text(x0s[0] + pw / 2, 304, "What? One label per photo", size=18, weight="bold")]
    bx = v["detection"]["box_xyxy"]
    where = photo(x0s[1]) + [
        rect(x0s[1] + bx[0] * s, 20 + bx[1] * s, (bx[2] - bx[0]) * s, (bx[3] - bx[1]) * s, fill="none", stroke=WHITE,
             rx=0, sw=6),
        rect(x0s[1] + bx[0] * s, 20 + bx[1] * s, (bx[2] - bx[0]) * s, (bx[3] - bx[1]) * s, fill="none", stroke=ACCENT,
             cls="accent-stroke", rx=0, sw=3),
        text(x0s[1] + pw / 2, 304, "Where? A box per object", size=18, weight="bold")]
    which = photo(x0s[2]) + [
        f'<image href="vision/tiger-mask.png" x="{x0s[2]}" y="20" width="{pw}" height="{ph}"/>',
        text(x0s[2] + pw / 2, 304, "Which pixels? One label per pixel", size=18, weight="bold")]
    return svg(W, H, [step(1, what), step(2, where), step(3, which)],
               "Three questions asked of one tiger photo (Charles J. Sharp, CC BY-SA 4.0): classification, detection "
               "and segmentation (Prince 2023, section 10.5). Computed by src/vision.py: the label by torchvision's "
               f"ResNet-18 (tiger, {v['photo2']['p_top']}), the box and the mask by a Mask R-CNN trained on COCO, "
               f"whose classes hold no tiger (it said {v['detection']['coco_label']}). Adapted, CC BY-SA 4.0.")


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
    """Without a function after the sum, two layers collapse into one line; the logistic and the ReLU."""
    W, H = 1000, 420
    collapse = [rect(150, 8, 700, 66, fill="#f4f6f7", stroke=EDGE, rx=8),
                text(500, 36, "two layers with no function:  0.5 × (2x + 1)  =  x + 0.5", size=20, weight="bold"),
                text(500, 62, "still one weighted sum: a straight line", size=17, fill=MUTED)]

    def panel(x0, title, sub, f, ymin, ymax):
        x1, y_top, y_bot = x0 + 380, 130, 340
        sx = lambda v: x0 + (v + 5) / 10 * (x1 - x0)
        sy = lambda v: y_bot - (v - ymin) / (ymax - ymin) * (y_bot - y_top)
        pts = " ".join(f"{sx(v / 10):.1f},{sy(f(v / 10)):.1f}" for v in range(-50, 51))
        return [line(x0, sy(0), x1, sy(0), color=MUTED, w=1.3, marker=""),
                line(sx(0), y_bot + 6, sx(0), y_top - 10, color=MUTED, w=1.3, marker=""),
                f'<polyline class="accent-stroke" points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="3.4"/>',
                text(x1, sy(0) + 24, "the weighted sum", size=14, fill=MUTED, anchor="end"),
                text((x0 + x1) / 2, 108, title, size=20, weight="bold"),
                text((x0 + x1) / 2, y_bot + 46, sub, size=16, fill=MUTED)]

    logi = panel(60, "logistic", "between 0 and 1: flat at both ends", lambda v: 1 / (1 + math.exp(-v)), -0.1, 1.1)
    relu = panel(560, "ReLU", "0 below zero, the sum itself above", lambda v: max(0.0, v), -0.5, 5.2)
    slope = [text(578, 176, "above zero, slope 1:", size=16, weight="bold", fill=ACCENT, cls="accent-fill", anchor="start"),
             text(578, 198, "training keeps moving", size=16, weight="bold", fill=ACCENT, cls="accent-fill", anchor="start")]
    return svg(W, H, [step(1, collapse), step(2, logi), step(3, relu + slope)],
               "A stack of linear layers is one linear function, so each neuron applies a function after its sum: the "
               "logistic sigmoid, which saturates, and the rectified linear unit, whose derivative is 1 above zero "
               "(Prince 2023, pp. 25, 35, 37 and 38). " + LICENCE)


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
    """The wine's values flow forward, layer by layer, to one score per class."""
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
    groups[2] += [text(760, 335, "one score per class", size=16, fill=MUTED)]
    for y, n in zip(cols["out"][1], LINES):
        groups[2].append(text(805, y + 7, n, size=18, anchor="start"))
    arrow = [line(200, 365, 900, 365, color=ACCENT, w=2.4, marker="ahA", cls="accent-stroke"),
             text(550, 357, "forward", size=15, weight="bold", fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, groups[0]), step(2, groups[1] + arrow), step(3, groups[2])],
               "A forward pass on deck 4's example wine (alcohol 12.0, volatile acidity 0.27, sulphates 0.56): three "
               f"hidden neurons, three class scores {SCORES}, those of the next slide's softmax. Hidden values and "
               "scores illustrative. " + LICENCE)


def _probs():
    e = [math.exp(v) for v in SCORES]
    return [x / sum(e) for x in e]


def softmax() -> str:
    """Three scores become three probabilities that sum to one: the formula, worked once."""
    W, H = 1000, 400
    p = _probs()
    e = [math.exp(v) for v in SCORES]
    top_i = max(range(3), key=lambda i: p[i])
    left = [text(130, 30, "the last layer's scores", size=19, weight="bold")]
    for i, (n, v) in enumerate(zip(LINES, SCORES)):
        y = 56 + i * 76
        left += [rect(30, y, 200, 56, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
                 text(130, y + 36, f"{n}: {v:+.1f}".replace("-", "−"), size=22)]
    formula = [rect(262, 70, 210, 150, fill="#f4f6f7", stroke=EDGE, rx=8),
               text(367, 104, "softmax", size=20, weight="bold"),
               text(367, 146, "p = e<tspan baseline-shift='super' font-size='14'>score</tspan>", size=22),
               line(300, 162, 434, 162, color=INK, w=1.6, marker=""),
               text(367, 192, "sum of e<tspan baseline-shift='super' font-size='14'>score</tspan>", size=19),
               line(474, 145, 510, 145, color=ACCENT, w=2.6, marker="ahA", cls="accent-stroke")]
    base, top, x0 = 270, 50, 540
    bars = [text(745, 30, "probabilities, summing to 1", size=19, weight="bold"),
            line(x0 - 10, base, 960, base, color=MUTED, w=1.4, marker="")]
    for i, (n, q) in enumerate(zip(LINES, p)):
        h = q * (base - top)
        x = x0 + i * 145
        lit = i == top_i
        fill, cls = (ACCENT, "accent-fill") if lit else (A_LIGHT, "accent-a-light-fill")
        bars += [rect(x, base - h, 96, h, fill=fill, stroke=None, rx=3, cls=cls),
                 text(x + 48, base - h - 10, f"{q:.2f}", size=21, weight="bold" if lit else "normal"),
                 text(x + 48, base + 28, n, size=19, weight="bold" if lit else "normal")]
    worked = [text(500, 346, f"e<tspan baseline-shift='super' font-size='13'>0.4</tspan> = {e[0]:.2f},   "
                   f"e<tspan baseline-shift='super' font-size='13'>1.6</tspan> = {e[1]:.2f},   "
                   f"e<tspan baseline-shift='super' font-size='13'>0.2</tspan> = {e[2]:.2f}:   sum {sum(e):.2f}", size=19),
              text(500, 380, f"medium: {e[1]:.2f} / {sum(e):.2f} = {p[1]:.2f}", size=19, weight="bold", fill=ACCENT,
                   cls="accent-fill")]
    body = [step(1, left), step(2, formula + bars), step(3, worked)]
    return svg(W, H, body, f"Softmax of three illustrative class scores {SCORES}: e raised to each score, divided by "
               f"their sum, gives {', '.join(f'{q:.2f}' for q in p)} (Prince 2023, section 5.5). Illustrative. " + LICENCE)


def learn() -> str:
    """A training wine has a true class: the output is compared with it, and the network must change."""
    W, H = 1000, 380
    p = _probs()
    wine = [rect(20, 40, 250, 200, fill="#f4f6f7", stroke=EDGE, rx=8),
            text(145, 72, "one training wine", size=18, weight="bold")]
    wine += [text(145, 104 + 26 * i, f"{n}: {v}", size=16, fill=MUTED) for i, (n, v) in enumerate(WINE)]
    wine += [rect(70, 186, 150, 36, fill="#fdecee", stroke=ALERT, rx=18),
             text(145, 210, "its class: low", size=17, weight="bold", fill=ALERT)]
    net = [line(274, 140, 318, 140, color=INK, w=2),
           rect(322, 90, 170, 100, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
           text(407, 130, "the network", size=18, weight="bold"),
           text(407, 156, "weights still random", size=15, fill=MUTED),
           line(496, 140, 540, 140, color=INK, w=2)]
    base, top, x0 = 230, 40, 560
    bars = []
    for i, (n, q) in enumerate(zip(LINES, p)):
        h = q * (base - top)
        x = x0 + i * 140
        bars += [rect(x, base - h, 92, h, fill=A_LIGHT, stroke=None, rx=3, cls="accent-a-light-fill"),
                 text(x + 46, base - h - 10, f"{q:.2f}", size=20),
                 text(x + 46, base + 26, n, size=18)]
    truth = [rect(x0 - 8, base - p[0] * (base - top) - 40, 108, p[0] * (base - top) + 78, fill="none", stroke=ALERT,
                  rx=8, sw=3),
             text(x0 + 46, base + 62, "the true class gets 0.19", size=17, weight="bold", fill=ALERT)]
    need = [text(500, 350, "to learn, the network needs one number for how wrong this is", size=20, weight="bold",
                 fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, wine), step(2, net + bars), step(3, truth), step(4, need)],
               "Deck 4's example wine, whose grade of 5 puts it in the low class, against the illustrative output of "
               f"the softmax slide ({', '.join(f'{q:.2f}' for q in p)}): the loss is that mismatch as one number "
               "(Prince 2023, pp. 56 and 77). Illustrative. " + LICENCE)


def loss() -> str:
    """Minus the log of the probability given to the true class: high when wrong, low when right."""
    W, H = 1000, 400
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
        l_ = -math.log(round(q, 2))               # from the probability as printed, so the slide's arithmetic checks
        hi = l_ > 1
        out += [text(x0 + 220, 330, f"−log {q:.2f} = {l_:.2f}: {'high' if hi else 'low'}", size=22, weight="bold",
                     fill=ALERT if hi else ACCENT, cls="" if hi else "accent-fill")]
        return out, l_

    a, la = panel(20, "low", "this wine's class is low")
    b_, lb = panel(540, "medium", "a medium wine, the same output")
    cap = [text(500, 384, "loss = −log (the probability given to the true class)", size=19, weight="bold")]
    return svg(W, H, [step(1, a), step(2, b_), step(3, cap)],
               f"Cross-entropy loss on the same illustrative output, natural logarithm: {la:.2f} for the example wine, "
               f"whose class is low, {lb:.2f} for a medium wine (Prince 2023, section 5.5). Illustrative. " + LICENCE)


def gradient() -> str:
    """The loss as a function of one weight; the gradient is its slope where the weight is now."""
    W, H = 1000, 380
    x0, x1, y0, y1 = 80, 920, 40, 300

    def L(w):
        return 0.6 * (w - 3) ** 2 + 0.5

    def px(w):
        return x0 + w / 6 * (x1 - x0)

    def py(v):
        return y1 - (v / 6.0) * (y1 - y0)

    curve = " ".join(f"{px(w / 20):.1f},{py(L(w / 20)):.1f}" for w in range(0, 121))
    w0 = 1.0
    axes = [line(x0, y1, x1 + 20, y1, color=MUTED, w=1.4), line(x0, y1, x0, y0 - 10, color=MUTED, w=1.4),
            text(x1, y1 + 30, "one weight", size=16, fill=MUTED, anchor="end"),
            text(x0 + 8, y0 - 14, "loss", size=16, fill=MUTED, anchor="start"),
            f'<polyline points="{curve}" fill="none" stroke="{INK}" stroke-width="2.4"/>',
            f'<circle class="accent-fill" cx="{px(w0):.1f}" cy="{py(L(w0)):.1f}" r="10" fill="{ACCENT}"/>',
            text(px(w0) - 20, py(L(w0)) + 44, "the weight now", size=16, anchor="end")]
    s = 1.2 * (w0 - 3)                              # dL/dw at w0
    a, b = w0 - 0.7, w0 + 0.7
    tang = [line(px(a), py(L(w0) + s * (a - w0)), px(b), py(L(w0) + s * (b - w0)), color=ALERT, w=3, marker=""),
            text(px(1.9), py(4.7), "the slope here: the gradient", size=18, weight="bold", fill=ALERT, anchor="start"),
            text(px(1.9), py(4.7) + 24, "how much the loss changes when the weight changes a little",
                 size=15, fill=ALERT, anchor="start")]
    down = [line(px(w0) + 14, py(L(w0)) - 18, px(w0 + 0.75) - 4, py(L(w0 + 0.75)) - 22, color=ACCENT, w=2.6, marker="ahA",
                 cls="accent-stroke"),
            text(500, 352, "the loss falls the other way: there lies the next step", size=18, weight="bold",
                 fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, axes), step(2, tang), step(3, down)],
               "An illustrative loss curve over one weight, the weight's current value and the tangent there: the "
               "derivative of the loss with respect to the weight (Prince 2023, pp. 77, 78 and 97). Illustrative. "
               + LICENCE)


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
    lw = -math.log(round(_probs()[0], 2))
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


def batches() -> str:
    """Three ways to take a step: all the examples, one example, a batch; their paths down an illustrative loss."""
    import random
    W, H = 1000, 390
    rnd = random.Random(7)

    def panel(x0, title, lines_, steps, lr, noise, dots=False):
        cx, cy, a, b = x0 + 150, 150, 130, 70            # the bowl's centre and half-axes, in pixels
        out = [text(cx, 26, title, size=19, weight="bold")]
        out += [f'<ellipse cx="{cx}" cy="{cy}" rx="{a * k / 4:.1f}" ry="{b * k / 4:.1f}" fill="none" '
                f'stroke="{EDGE}" stroke-width="1.4"/>' for k in range(1, 5)]
        x, y = -0.92, 0.85                              # the start, in the bowl's own units
        pts = [(x, y)]
        for _ in range(steps):
            gx, gy = 2 * x * 0.35, 2 * y * 1.6             # the gradient of an elongated bowl
            x -= lr * (gx + noise * rnd.gauss(0, 1))
            y -= lr * (gy + noise * rnd.gauss(0, 1))
            pts.append((x, y))
        path_ = " ".join(f"{cx + a * px:.1f},{cy - b * py:.1f}" for px, py in pts)
        out += [f'<polyline class="accent-stroke" points="{path_}" fill="none" stroke="{ACCENT}" stroke-width="2.4"/>',
                f'<circle cx="{cx + a * pts[0][0]:.1f}" cy="{cy - b * pts[0][1]:.1f}" r="6" fill="{INK}"/>',
                f'<circle cx="{cx}" cy="{cy}" r="5" fill="{ALERT}"/>']
        if dots:
            out += [f'<circle class="accent-fill" cx="{cx + a * px:.1f}" cy="{cy - b * py:.1f}" r="3.2" fill="{ACCENT}"/>'
                    for px, py in pts[1:]]
        out += [text(cx, 262 + 24 * i, s_, size=16 if i == 0 else 15, weight="bold" if i == 0 else "normal",
                     fill=INK if i == 0 else MUTED) for i, s_ in enumerate(lines_)]
        return out

    full = panel(20, "all the examples", ["each step: the whole set", "exact, but slow, and still many steps:",
                                           "no formula gives a network's weights"], 26, 0.15, 0.0, dots=True)
    one = panel(680, "one example", ["each step: one example", "cheap, but very noisy, and the card",
                                     "computes one small sum at a time"], 45, 0.1, 1.5)
    batch = panel(350, "a batch", ["each step: a few dozen", "computed together on the card;",
                                   "less noise, but some left"], 24, 0.22, 0.45)
    return svg(W, H, [step(1, full), step(2, one), step(3, batch)],
               "Paths down an illustrative, elongated loss from the same start (black) to the lowest point (red): "
               "full-batch gradient descent, one example per step and a batch per step (Prince 2023, pp. 85 to 86; "
               "Zhang et al. 2023, section 12.5.2). Illustrative, simulated noise. " + LICENCE)


def blame() -> str:
    """A weight in the first layer reaches the loss only through every layer after it."""
    W, H = 1000, 340
    xs = [40, 230, 420, 610]
    names = ["layer 1", "layer 2", "layer 3", "last layer"]
    boxes = []
    for x, n in zip(xs, names):
        boxes += [rect(x, 90, 150, 100, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
                  text(x + 75, 120, n, size=18, weight="bold")]
    boxes += [line(x + 154, 140, x + 186, 140, color=INK, w=1.8) for x in xs[:3]]
    boxes += [line(764, 140, 800, 140, color=INK, w=1.8),
              rect(804, 95, 150, 90, fill="#fdecee", stroke=ALERT, rx=8),
              text(879, 135, "the loss", size=18, weight="bold", fill=ALERT),
              text(879, 160, "measured here", size=15, fill=ALERT)]
    w1 = [f'<circle cx="115" cy="160" r="11" fill="{ALERT}"/>',
          text(115, 230, "one weight here", size=17, weight="bold", fill=ALERT)]
    ripple = [rect(x - 4, 86, 158, 108, fill="none", stroke=ALERT, rx=10, sw=2.4, extra=' stroke-dasharray="7 5"')
              for x in xs[1:]]
    ripple += [line(x + 154, 140, x + 186, 140, color=ALERT, w=3) for x in xs[:3]]
    ripple += [line(764, 140, 800, 140, color=ALERT, w=3),
               text(500, 50, "a small change ripples through every layer after it", size=18, weight="bold",
                    fill=ALERT)]
    cap = [text(500, 300, "to lower the loss, every weight must move: but which way, and how much?",
                size=19, weight="bold", fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, boxes), step(2, w1), step(3, ripple), step(4, cap)],
               "A weight of the first layer changes the loss only through the layers after it, the ripple effect of "
               "Prince (2023), p. 97. Schematic. " + LICENCE)


def loop() -> str:
    """A batch drawn from the training examples, then the loop: forward, loss, backward, update."""
    W, H = 1000, 400
    tiles = []
    pick = {2, 7, 11, 16, 20, 25}
    for i in range(28):
        x = 150 + i * 25
        lit = i in pick
        tiles.append(rect(x, 14, 20, 20, fill=A_LIGHT if lit else WHITE, stroke=ACCENT if lit else GREY_INK,
                          cls="accent-a-light-fill accent-stroke" if lit else "", rx=3, sw=1.6 if lit else 1.2))
    tiles += [text(140, 30, "training examples", size=15, fill=MUTED, anchor="end"),
              text(500, 58, "a batch: a few examples drawn at random from the training set", size=17, weight="bold",
                   fill=ACCENT, cls="accent-fill")]
    names = [("1 · forward", "the batch", "to its scores"), ("2 · loss", "how wrong", "the batch is"),
             ("3 · backward", "each weight's", "gradient"), ("4 · update", "every weight moves", "a small step")]
    groups = []
    for i, (t, a, b_) in enumerate(names):
        x = 30 + i * 245
        g = [rect(x, 110, 200, 120, fill=A_LIGHT if i == 3 else WHITE, stroke=ACCENT,
                  cls="accent-a-light-fill accent-stroke" if i == 3 else "accent-stroke"),
             text(x + 100, 148, t, size=20, weight="bold"), text(x + 100, 182, a, size=16, fill=MUTED),
             text(x + 100, 204, b_, size=16, fill=MUTED)]
        if i:
            g.insert(0, line(x - 43, 170, x - 4, 170, color=INK, w=2))
        groups.append(g)
    back = [path("M 865 234 L 865 290 L 130 290 L 130 236", color=ACCENT, w=2.6, marker="ahA", cls="accent-stroke"),
            text(497, 322, "then the next batch, until every example has been used", size=17, weight="bold",
                 fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, tiles), step(2, groups[0]), step(3, groups[1]), step(4, groups[2]), step(5, groups[3]),
                      step(6, back)],
               "A batch drawn at random from the training examples, then the training loop of stochastic gradient "
               "descent: forward pass on the batch, loss, backward pass, update, repeated batch after batch (Prince "
               "2023, pp. 85 to 86, sections 6.2 and 7.2; Zhang et al. 2023, section 3.4). " + LICENCE)


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
    """One 3 by 3 filter, its 9 weights, two positions on the pixels, then its whole map."""
    W, H, c, n = 1000, 400, 46, 6
    gx, gy = 30, 70
    dark, light = 0.2, 0.9
    val = [[dark if i < 3 else light for j in range(n)] for i in range(n)]   # by column, then row
    grid = [text(gx + n * c / 2, 40, "the pixels: dark on the left, light on the right", size=16, fill=MUTED)]
    for i in range(n):
        for j in range(n):
            g = int(40 + 200 * val[i][j])
            grid += [rect(gx + i * c, gy + j * c, c, c, fill=f"rgb({g},{g},{g})", stroke=WHITE, rx=0, sw=1.5),
                     text(gx + i * c + c / 2, gy + j * c + c / 2 + 6, f"{val[i][j]:.1f}", size=14,
                          fill=WHITE if val[i][j] < 0.5 else INK)]
    wts = [-1, 0, 1]
    fx, fy, fc = 372, 130, 40
    filt = [text(fx + 1.5 * fc, 108, "the filter: 9 weights", size=17, weight="bold", fill=ACCENT, cls="accent-fill")]
    for i in range(3):
        for j in range(3):
            filt += [rect(fx + i * fc, fy + j * fc, fc, fc, fill=A_LIGHT, stroke=ACCENT, cls="accent-a-light-fill accent-stroke",
                          rx=0, sw=1.6),
                     text(fx + i * fc + fc / 2, fy + j * fc + fc / 2 + 6, f"{wts[i]:+d}".replace("+0", "0").replace("-", "−"),
                          size=16, weight="bold")]
    filt.append(text(fx + 1.5 * fc, fy + 3 * fc + 26, "it looks for dark, then light", size=15, fill=MUTED))
    m, mx, my, mc = n - 2, 640, 110, 56

    def window(i, j):
        return rect(gx + i * c, gy + j * c, 3 * c, 3 * c, fill="none", stroke=ACCENT, cls="accent-stroke", rx=2, sw=4)

    def resp(i, j):
        return sum(wts[a] * val[i + a][j + b] for a in range(3) for b in range(3))

    def cell(i, j, show=True):
        v = resp(i, j)
        lit = v > 0.5
        out = [rect(mx + i * mc, my + j * mc, mc, mc, fill=ACCENT if lit else GREY, stroke=EDGE, rx=0, sw=1.2,
                    cls="accent-fill" if lit else "")]
        if show:
            out.append(text(mx + i * mc + mc / 2, my + j * mc + mc / 2 + 7, f"{v:.1f}", size=17, weight="bold",
                            fill=WHITE if lit else INK))
        return out

    frame = [rect(mx + i * mc, my + j * mc, mc, mc, fill=WHITE, stroke=EDGE, rx=0, sw=1.2) for i in range(m) for j in range(m)]
    frame.append(text(mx + m * mc / 2, 88, "the filter's map", size=16, fill=MUTED))
    s3 = cell(0, 1)
    s4 = cell(1, 1)
    s5 = sum((cell(i, j) for i in range(m) for j in range(m)), []) + [
        text(mx + m * mc / 2, my + m * mc + 34, "lit where the pattern is: the edge", size=17, weight="bold",
             fill=ACCENT, cls="accent-fill"),
        text(gx + n * c / 2, gy + n * c + 34, "the same 9 weights at every position", size=17, weight="bold")]
    return svg(W, H, [step(1, grid), step(2, filt + frame), step(3, [window(0, 1)], hide="4-end"), step(3, s3),
                      step(4, [window(1, 1)], hide="5-end"), step(4, s4), step(5, s5)],
               "A 3 by 3 filter with weights −1, 0 and +1 by column, slid over a 6 by 6 grid with a vertical edge: "
               "a weighted sum of each pixel and its eight neighbours, 0 on a flat patch, 2.1 across the edge "
               "(Prince 2023, section 10.3). Illustrative values. " + LICENCE)


def sharing() -> str:
    """One filter, its 9 weights, used at every position of the photo; against a plain layer's billions."""
    W, H, k = 1000, 400, 1.4
    ox, oy = 30, 20
    pos = [(60, 40), (130, 96), (40, 150)]           # filter windows on stripes, in the 224 image
    im = [f'<image href="photos/tiger-224.jpg" x="{ox}" y="{oy}" width="{224 * k}" height="{224 * k}"/>']
    fx, fy, fc = 420, 110, 36
    filt = [text(fx + 1.5 * fc, 92, "one filter: 9 weights", size=17, weight="bold", fill=ACCENT, cls="accent-fill")]
    filt += [rect(fx + i * fc, fy + j * fc, fc, fc, fill=A_LIGHT, stroke=ACCENT, cls="accent-a-light-fill accent-stroke",
                  rx=0, sw=1.6) for i in range(3) for j in range(3)]
    wins = []
    for x, y in pos:
        wx, wy, ws = ox + x * k, oy + y * k, 22 * k
        wins += [rect(wx, wy, ws, ws, fill="none", stroke=WHITE, rx=0, sw=5),
                 rect(wx, wy, ws, ws, fill="none", stroke=ACCENT, cls="accent-stroke", rx=0, sw=3),
                 line(wx + ws + 4, wy + ws / 2, fx - 6, fy + 1.5 * fc, color=ACCENT, w=1.6, marker="", dash="5 4",
                      cls="accent-stroke")]
    wins.append(text(fx + 1.5 * fc, fy + 3 * fc + 30, "the same weights here, here and here:", size=15, fill=MUTED))
    wins.append(text(fx + 1.5 * fc, fy + 3 * fc + 50, "a stripe is found wherever it is", size=15, fill=MUTED))
    count = [rect(640, 70, 340, 110, fill="#fdecee", stroke=ALERT, rx=8),
             text(810, 110, "a plain layer: 22 billion", size=20, weight="bold", fill=ALERT),
             text(810, 140, "weights, each pixel its own,", size=15, fill=ALERT),
             text(810, 160, "for every neuron", size=15, fill=ALERT),
             rect(640, 200, 340, 110, fill=A_LIGHT, stroke=ACCENT, cls="accent-a-light-fill accent-stroke", rx=8),
             text(810, 240, "a filter: 9 weights", size=20, weight="bold"),
             text(810, 270, "27 over the three colours,", size=15, fill=MUTED),
             text(810, 290, "the same at every position", size=15, fill=MUTED)]
    return svg(W, H, [step(1, im), step(2, filt + wins), step(3, count)],
               "One 3 by 3 filter applied at three places of the 224 by 224 tiger photo (S. Taheri, edited by "
               "Fir0002, CC BY-SA 2.5): the same weights at every position; a plain layer from a 224 × 224 colour "
               "photo to as many neurons needs over 22 billion weights (Prince 2023, pp. 161, 163 and 170). Window "
               "places drawn by hand. Adapted, CC BY-SA 2.5.")


def visualise() -> str:
    """How a feature picture is made: a starting picture, changed step by step until one filter responds most."""
    import random
    W, H, S = 1000, 360, 220
    rnd = random.Random(3)
    cells = 20
    start = [text(150, 26, "1 · a starting picture", size=18, weight="bold")]
    for i in range(cells):
        for j in range(cells):
            r, g, b = (rnd.randint(90, 200) for _ in range(3))
            start.append(f'<rect x="{40 + i * S / cells:.1f}" y="{40 + j * S / cells:.1f}" width="{S / cells + 0.5:.1f}" '
                         f'height="{S / cells + 0.5:.1f}" fill="rgb({r},{g},{b})"/>')
    start.append(rect(40, 40, S, S, fill="none", stroke=EDGE, rx=0, sw=1.2))
    change = [line(285, 150, 715, 150, color=ACCENT, w=3, marker="ahA", cls="accent-stroke"),
              text(500, 26, "2 · change its pixels, step by step", size=18, weight="bold"),
              text(500, 108, "so that one filter of the first layer", size=16),
              text(500, 130, "responds more and more", size=16),
              text(500, 186, "the gradient of part 2, taken for the pixels:", size=15, fill=MUTED),
              text(500, 206, "the network's weights stay as they are", size=15, fill=MUTED)]
    result = [text(850, 26, "3 · after 2,560 steps", size=18, weight="bold"),
              f'<image href="features/features-edges.png" x="740" y="40" width="{S}" height="{S}"/>',
              rect(740, 40, S, S, fill="none", stroke=EDGE, rx=0, sw=1.2),
              text(850, 292, "what this filter looks for: edges", size=17, weight="bold", fill=ACCENT,
                   cls="accent-fill")]
    note = [text(500, 340, "not the filter's weights, nor a photo: a picture made for one filter", size=17,
                 weight="bold", fill=ALERT)]
    return svg(W, H, [step(1, start), step(2, change), step(3, result), step(4, note)],
               "Feature visualisation by optimisation (Olah et al. 2017): a picture changed by gradient steps, 2,560 "
               "of them for the article's images, until one channel of GoogLeNet's first layer (conv2d0) responds "
               "most. The starting picture is drawn, illustrative; the result is the article's tile, CC BY 4.0 "
               "(images/features/CREDITS.md). " + LICENCE)


# --- Augmentation, a plain network on pixels, data sizes, test hygiene ------------
def augment() -> str:
    """Varied copies with the same label: the tiger photo flipped, a sentence with a synonym, a sound filtered."""
    W, H = 1000, 360

    def card(x, y, inner, w=280, h=120):
        return [rect(x - w / 2, y, w, h, fill=WHITE, stroke=EDGE, rx=6, sw=1.6)] + inner

    def wave(x, y, amp, k=1.0):
        pts = " ".join(f"{x - 120 + t * 4:.1f},{y + amp * (math.sin(t / 3.2) + 0.5 * k * math.sin(t / 1.1)):.1f}"
                       for t in range(61))
        return f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" class="accent-stroke" stroke-width="2.4"/>'

    def tiger(cx, y, flip=False):
        im = f'<image href="photos/tiger-224.jpg" x="{cx - 52}" y="{y + 8}" width="104" height="104"/>'
        if flip:
            im = f'<g transform="translate({2 * cx},0) scale(-1,1)">{im}</g>'
        return im

    cols = [170, 500, 830]
    heads = ["a photo", "a sentence", "a sound"]
    orig = [card(cols[0], 40, [tiger(cols[0] - 30, 40), text(cols[0] + 34, 96, "label:", size=14, fill=MUTED,
                                                              anchor="start"),
                               text(cols[0] + 34, 116, "tiger", size=14, fill=MUTED, anchor="start")]),
            card(cols[1], 40, [text(cols[1], 92, "“The wine was excellent.”", size=17),
                               text(cols[1], 120, "label: positive", size=14, fill=MUTED)]),
            card(cols[2], 40, [wave(cols[2], 100, 14)])]
    copy = [card(cols[0], 210, [tiger(cols[0] - 30, 210, flip=True), text(cols[0] + 34, 266, "label:", size=14,
                                                                           fill=MUTED, anchor="start"),
                                text(cols[0] + 34, 286, "tiger", size=14, fill=MUTED, anchor="start")]),
            card(cols[1], 210, [text(cols[1], 262, "“The wine was superb.”", size=17),
                                text(cols[1], 290, "label: positive", size=14, fill=MUTED)]),
            card(cols[2], 210, [wave(cols[2], 270, 14, k=0.25)])]
    how = ["flipped", "a synonym", "filtered"]
    groups = []
    for i in range(3):
        g = [text(cols[i], 26, heads[i], size=18, weight="bold")] + orig[i] + [
            line(cols[i], 164, cols[i], 204, color=ACCENT, w=2.2, marker="ahA", cls="accent-stroke"),
            text(cols[i] + 12, 190, how[i], size=15, fill=ACCENT, cls="accent-fill", anchor="start")] + copy[i]
        groups.append(g)
    same = [text(500, 352, "a new training example, with the same label", size=17, weight="bold")]
    return svg(W, H, [step(1, groups[0]), step(2, groups[1]), step(3, groups[2]), step(4, same)],
               "Data augmentation on three kinds of input: the tiger photo of the photo slides flipped (S. Taheri, "
               "edited by Fir0002, CC BY-SA 2.5), a sentence with a synonym, a sound with a frequency band attenuated; "
               "the label does not change (Prince 2023, sections 9.3.6 and 9.3.8). The sentence and the wave are "
               "drawn. Adapted, CC BY-SA 2.5.")


def flatten() -> str:
    """A 4 by 4 patch is three planes of numbers; a plain network reads them as one list of 48."""
    W, H, n, c = 1000, 360, 4, 40
    px = _tiger(n)                                   # the first 4 by 4 of the photo slide's patch
    a_, b_ = (1, 1), (1, 2)                          # a pixel and the one below it
    names = [("red", "#c0392b"), ("green", "#2e8b57"), ("blue", "#2f6db5")]
    gx, gy = 60, 124
    grid = [text(gx + 60, 28, "4 by 4 of the tiger's pixels:", size=15, fill=MUTED),
            text(gx + 60, 48, "three planes of numbers", size=15, fill=MUTED)]
    for k in (2, 1, 0):                                # the planes behind the colours: red, then green, blue at the back
        ox, oy = 16 * (k + 1), -16 * (k + 1)
        _, col = names[k]
        for j in range(n):
            for i in range(n):
                v = px[i][j][k]
                grid.append(f'<rect x="{gx + ox + i * c}" y="{gy + oy + j * c}" width="{c}" height="{c}" fill="{col}" '
                            f'fill-opacity="{0.15 + 0.6 * v / 255:.2f}" stroke="{WHITE}" stroke-width="1.2"/>')
    for j in range(n):                                 # the colours in front
        for i in range(n):
            r, g, b = px[i][j]
            grid.append(rect(gx + i * c, gy + j * c, c, c, fill=f"rgb({r},{g},{b})", stroke=WHITE, rx=0, sw=1.5))
    mark = [rect(gx + a_[0] * c, gy + a_[1] * c, c, c, fill="none", stroke=ALERT, rx=0, sw=3.5),
            rect(gx + b_[0] * c, gy + b_[1] * c, c, c, fill="none", stroke=ALERT, rx=0, sw=3.5),
            text(gx + n * c / 2 + 10, gy + n * c + 30, "neighbours: one above the other", size=15, fill=ALERT)]
    lx, ly, lc, rh = 372, 112, 38, 40
    row = [text(lx + 8 * lc, 58, "the same pixels as one list of 48 numbers, row after row,", size=15, fill=MUTED),
           text(lx + 8 * lc, 76, "plane after plane: 16 reds, then 16 greens, then 16 blues", size=15, fill=MUTED),
           line(gx + n * c + 58, ly + 1.5 * rh, lx - 58, ly + 1.5 * rh, color=INK, w=1.8)]
    ka, kb = a_[1] * n + a_[0], b_[1] * n + b_[0]
    for k, (name, col) in enumerate(names):
        y = ly + k * rh
        row.append(text(lx - 8, y + rh / 2 + 5, name, size=14, fill=col, anchor="end"))
        for m in range(16):
            j, i = divmod(m, n)
            v = px[i][j][k]
            row.append(f'<rect x="{lx + m * lc}" y="{y}" width="{lc}" height="{rh}" fill="{col}" '
                       f'fill-opacity="{0.15 + 0.6 * v / 255:.2f}" stroke="{WHITE}" stroke-width="1.2"/>')
        row += [rect(lx + ka * lc, y, lc, rh, fill="none", stroke=ALERT, rx=0, sw=3),
                rect(lx + kb * lc, y, lc, rh, fill="none", stroke=ALERT, rx=0, sw=3)]
    yb = ly + 3 * rh
    apart = [path(f"M {lx + ka * lc + lc / 2} {yb + 6} L {lx + ka * lc + lc / 2} {yb + 20} "
                  f"L {lx + kb * lc + lc / 2} {yb + 20} L {lx + kb * lc + lc / 2} {yb + 6}", color=ALERT, w=2, marker=""),
             text(lx + (ka + kb + 1) * lc / 2, yb + 44, "4 places apart here; 224 in a photo 224 pixels wide", size=16,
                  fill=ALERT, weight="bold")]
    note = [text(lx + 8 * lc - 20, 340, "every input is wired to every neuron alike: nothing says which pixels touch",
                 size=16, weight="bold")]
    return svg(W, H, [step(1, grid), step(2, mark + row + apart), step(3, note)],
               "Four by four of the tiger photo's pixels, read from its 224 by 224 copy, as three planes (red, green, "
               "blue), unrolled row by row and plane by plane into the 48 inputs of a plain, fully connected layer: "
               "two vertical neighbours land 4 places apart (Prince 2023, p. 161). Adapted from S. Taheri's photo, "
               "edited by Fir0002, CC BY-SA 2.5.")


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
           text(170, 258, "useful for other tasks too", size=16, fill=MUTED)]
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


# --- Hands-on 4 --------------------------------------------------------------------
def interval() -> str:
    """50 right of 56 is 89%, and could be anything from 78% to 96%."""
    W, H = 1000, 330
    x0, x1 = 50, 950

    def px(v):
        return x0 + (v - 70) / 30 * (x1 - x0)

    axis = [line(x0, 140, x1, 140, color=MUTED, w=1.8, marker="")]
    axis += [line(px(v), 132, px(v), 148, color=MUTED, w=1.6, marker="") for v in range(70, 101, 5)]
    axis += [text(px(v), 178, f"{v}%", size=20, fill=MUTED) for v in range(70, 101, 5)]
    pt = [f'<circle class="accent-fill" cx="{px(89.3):.1f}" cy="140" r="14" fill="{ACCENT}"/>',
          text(px(89.3), 104, "50 of 56 right: 89%", size=24, weight="bold")]
    ci = [rect(px(78.1), 129, px(96.0) - px(78.1), 22, fill=ACCENT, stroke=None, rx=11, cls="accent-fill",
               extra=' fill-opacity="0.3"'),
          text(px(78.1), 216, "78%", size=23, weight="bold", fill=ACCENT, cls="accent-fill"),
          text(px(96.0), 216, "96%", size=23, weight="bold", fill=ACCENT, cls="accent-fill"),
          text(px(87.2), 254, "a 95% interval: the score could be anywhere here", size=22, fill=ACCENT,
               cls="accent-fill")]
    big = [rect(px(89.0), 290, px(90.0) - px(89.0), 16, fill=INK, stroke=None, rx=5),
           text(px(89.0) - 16, 304, "with 10,000 test photos: about 1 point either way", size=20, anchor="end")]
    return svg(W, H, [step(1, axis + pt), step(2, ci), step(3, big)],
               "An observed 50 of 56 (89%) with its 95% Clopper-Pearson interval, 78% to 96%, against the at most 1 "
               "point of 10,000 test images (Recht et al. 2019). " + LICENCE)


# --- Saliency maps ------------------------------------------------------------------
def saliency_map() -> str:
    """The tiger photo and its gradient map: the pixels the tiger score is most sensitive to, computed."""
    import json
    v = json.loads((HERE.parent / "images" / "vision" / "vision.json").read_text())
    W, H, S = 1000, 310, 230

    def frame(x0):
        return rect(x0, 20, S, S, fill="none", stroke=EDGE, rx=0, sw=1.6)

    img = [f'<image href="photos/tiger-224.jpg" x="160" y="20" width="{S}" height="{S}"/>', frame(160),
           text(160 + S / 2, 280, f"the network says tiger, {v['photo1']['p_tiger']:.2f}", size=17, weight="bold")]
    grad = [line(400, 135, 600, 135, color=ACCENT, w=2.4, marker="ahA", cls="accent-stroke"),
            rect(610, 20, S, S, fill=WHITE, stroke=None, rx=0),
            f'<image href="vision/saliency.png" x="610" y="20" width="{S}" height="{S}"/>', frame(610),
            text(610 + S / 2, 280, "its map: where the tiger score", size=17, weight="bold"),
            text(610 + S / 2, 302, "reacts most to a change", size=17, weight="bold")]
    return svg(W, H, [step(1, img), step(2, grad)],
               "A gradient saliency map (Simonyan et al. 2014) of torchvision's ResNet-18 tiger score on the tiger "
               "photo (S. Taheri, edited by Fir0002, CC BY-SA 2.5), computed by src/vision.py: the largest absolute "
               "gradient over the colour channels, averaged over 4 by 4 pixel blocks. Adapted, CC BY-SA 2.5.")


def saliency_scrambled() -> str:
    """Two methods' maps, before and after the network's top layers are re-initialised: one changes, one does not."""
    import json
    v = json.loads((HERE.parent / "images" / "vision" / "vision.json").read_text())["randomised"]
    W, H, S = 1000, 420, 170
    cx = [250, 470]
    head = [text(cx[0] + S / 2, 26, "the trained network", size=17, weight="bold"),
            text(cx[1] + S / 2, 26, "top layers scrambled", size=17, weight="bold", fill=ALERT)]

    def tile(x, y, name):
        return [rect(x, y, S, S, fill=WHITE, stroke=None, rx=0),
                f'<image href="vision/{name}.png" x="{x}" y="{y}" width="{S}" height="{S}"/>',
                rect(x, y, S, S, fill="none", stroke=EDGE, rx=0, sw=1.4)]

    photo = [f'<image href="photos/tiger-224.jpg" x="30" y="130" width="{S}" height="{S}"/>',
             text(30 + S / 2, 330, "the photo", size=16, fill=MUTED)]
    rows = [(44, "saliency", "saliency-random", "plain gradient", "changes"),
            (230, "guided", "guided-random", "Guided Backprop: a gradient", "barely changes")]
    trained = photo + head[:1] + sum((tile(cx[0], y, a) for y, a, _, _, _ in rows), [])
    scr = head[1:] + sum((tile(cx[1], y, b) for y, _, b, _, _ in rows), [])
    verdict = []
    for y, _, _, name, says in rows:
        lit = says == "changes"
        if not lit:
            verdict.append(text(670, y + S / 2 - 30, "that passes back only positive signals", size=14, fill=MUTED,
                                anchor="start"))
        verdict += [text(670, y + S / 2 - 8 - (52 if not lit else 0), name, size=18, weight="bold", anchor="start"),
                    text(670, y + S / 2 + 18, f"{says}: the map " + ("follows the model" if lit else "ignores the model"),
                         size=16, anchor="start", fill=ACCENT if lit else ALERT, cls="accent-fill" if lit else "")]
    return svg(W, H, [step(1, trained), step(2, scr), step(3, verdict)],
               "Maps of torchvision's ResNet-18 tiger score on the tiger photo, computed by src/vision.py, before and "
               "after its last block and output layer are re-initialised at random (after Adebayo et al. 2018): rank "
               f"correlation {v['rank_corr_gradient_blocks']} for the plain gradient, {v['rank_corr_guided_blocks']} "
               "for Guided Backprop, over 4 by 4 pixel blocks. Adapted from S. Taheri's photo, edited by Fir0002, "
               "CC BY-SA 2.5.")


# --- The compute chart: Epoch AI's training compute, against the TOP500 leaders ----------
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


def _leaders():
    """The TOP500 leader of each list: (decimal year of the list, Rpeak in FLOP/s, system's short name)."""
    unit = {"G": 1e9, "T": 1e12, "P": 1e15}
    fix = {"2018-11": "T"}            # the November 2018 page labels GFlop/s; its values are TFlop/s (refs page)
    out = []
    with open(HERE / "top500.csv", newline="") as f:
        for r in csv.DictReader(f):
            y, m = (int(v) for v in r["list"].split("-"))
            u = unit[fix.get(r["list"], r["unit_on_page"])]
            out.append((y + (m - 1) / 12, float(r["rpeak"]) * u, re.split(r" - |, ", r["system"])[0]))
    return out


def compute(part: int) -> str:
    W, H = 1000, 380
    if part == 1:
        flop = [text(110, 84, "FLOP: floating-point operations,", size=16, weight="bold", anchor="start"),
                text(110, 106, "a computer's additions and multiplications", size=16, anchor="start"),
                text(110, 152, "log scale: each gridline is", size=16, fill=MUTED, anchor="start"),
                text(110, 174, "100,000 times the one below", size=16, fill=MUTED, anchor="start")]
        body = [step(1, _axes() + _dots(late=False) + flop), step(2, _dots(early=False))]
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
        lead = _leaders()
        segs = []
        for (y, r, _), nxt in zip(lead, lead[1:] + [(2026.9, None, None)]):
            lg = math.log10(r * 86400)
            for a, b in ((y, min(nxt[0], 2005.95)), (max(y, 2008.0), nxt[0])):
                if b > a and not (2005.95 < a < 2008.0):
                    segs.append(f'<line x1="{_cx(a):.1f}" y1="{_cy(lg):.1f}" x2="{_cx(b):.1f}" y2="{_cy(lg):.1f}" '
                                f'stroke="{ALERT}" stroke-width="3"/>')
            if nxt[1] is not None:
                ny = math.log10(nxt[1] * 86400)
                xb = nxt[0]
                if not (2005.95 < xb < 2008.0):
                    segs.append(f'<line x1="{_cx(xb):.1f}" y1="{_cy(lg):.1f}" x2="{_cx(xb):.1f}" y2="{_cy(ny):.1f}" '
                                f'stroke="{ALERT}" stroke-width="3"/>')
        segs += [text(_cx(1991), _cy(18.6), "one day of the year's", size=16, weight="bold", fill=ALERT, anchor="end"),
                 text(_cx(1991), _cy(18.6) + 20, "fastest supercomputer", size=16, weight="bold", fill=ALERT,
                      anchor="end"),
                 text(_cx(1991), _cy(18.6) + 40, "(the TOP500 leader, at peak)", size=14, fill=ALERT, anchor="end")]
        rows = {lab: (yr, lg) for yr, lg, lab in _models()}

        def days(lab):
            yr, lg = rows[lab]
            r, name = [(rr, nn) for y, rr, nn in lead if y <= yr][-1]
            d = 10 ** lg / (r * 86400)
            return d, name

        def say(lab):
            d, name = days(lab)
            if d < 1 / 1440:
                return f"{d * 86400:.0f} seconds of {name}"
            if d < 1 / 24:
                return f"{d * 1440:.0f} minutes of {name}"
            return f"{d:.0f} days of {name}"

        ax_, al = rows["AlexNet"]
        bx_, bl = rows["BERT"]
        gx, gl = rows["GPT-3"]
        lx, ll = rows["Llama 3.1"]
        def lit(lab):
            yr, lg = rows[lab]
            return f'<circle class="accent-fill" cx="{_cx(yr):.1f}" cy="{_cy(lg):.1f}" r="7" fill="{ACCENT}"/>'

        mins = [lit("AlexNet"), lit("BERT"),
                text(_cx(ax_) + 12, _cy(al) + 26, "AlexNet: " + say("AlexNet"), size=16, anchor="start"),
                text(_cx(bx_) + 14, _cy(bl) + 6, "BERT: " + say("BERT"), size=16, anchor="start")]
        mons = [lit("GPT-3"), lit("Llama 3.1"),
                text(_cx(gx) - 14, _cy(gl) + 6, "GPT-3: " + say("GPT-3"), size=16, weight="bold", anchor="end",
                     fill=ACCENT, cls="accent-fill"),
                text(_cx(lx) + 40, _cy(ll) - 16, "Llama 3.1: " + say("Llama 3.1"), size=16, weight="bold",
                     anchor="end", fill=ACCENT, cls="accent-fill")]
        body = [step(1, _axes() + _dots(muted=True, only=set())), step(2, segs),
                step(3, mins), step(4, mons)]
        what = ("one day of each TOP500 list's leading system at its theoretical peak (Rpeak × 86,400 s; TOP500 lists, "
                "June 1993 to June 2026, src/top500.csv), against which: AlexNet " + say("AlexNet") + ", BERT "
                + say("BERT") + ", GPT-3 " + say("GPT-3") + ", Llama 3.1 " + say("Llama 3.1") + "; peak and training "
                "arithmetic differ, so an order of magnitude only")
    return svg(W, H, body, f"Training compute of milestone models, log scale, broken time axis; {what}. Data: Epoch AI, "
               "Data on Notable AI Models, CC BY 4.0 (src/compute.csv). " + LICENCE)


CROP = {"layers.svg": (85, 915), "forward.svg": (45, 915), "data-sizes.svg": (60, 890), "convolution.svg": (0, 1000),
        "hygiene.svg": (55, 905), "saliency-map.svg": (130, 870)}


def crop(s: str, x0: int, x1: int) -> str:
    """Narrow the viewBox of a figure drawn on a 0-based canvas to x0..x1, its full height kept."""
    return re.sub(r'viewBox="0 0 (\d+) (\d+)"', lambda m: f'viewBox="{x0} 0 {x1 - x0} {m.group(2)}"', s, count=1)


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"timeline-1.svg": lambda: timeline(1), "timeline-2.svg": lambda: timeline(2),
               "data-sizes.svg": data_sizes, "tasks.svg": tasks, "unit.svg": unit, "activation.svg": activation,
               "layers.svg": layers, "forward.svg": forward, "softmax.svg": softmax, "learn.svg": learn,
               "loss.svg": loss, "gradient.svg": gradient, "descent.svg": descent, "blame.svg": blame,
               "backprop.svg": backprop, "batches.svg": batches, "loop.svg": loop, "epochs.svg": epochs,
               "early-stop.svg": early_stop, "flatten.svg": flatten, "general.svg": general,
               "convolution.svg": convolution, "sharing.svg": sharing, "augment.svg": augment, "hygiene.svg": hygiene,
               "transfer.svg": transfer, "finetune.svg": finetune, "dss-training.svg": dss_training,
               "interval.svg": interval, "saliency-map.svg": saliency_map,
               "saliency-scrambled.svg": saliency_scrambled, "visualise.svg": visualise, "compute-1.svg": lambda: compute(1),
               "compute-2.svg": lambda: compute(2), "compute-3.svg": lambda: compute(3)}
    photo = out / "photos" / "tiger-1.jpg"
    if photo.is_file():
        figures["pixels.svg"] = lambda: pixels(photo)
        figures["channels.svg"] = channels
    for name, lit in (("mo", {"MO"}), ("du", {"DU"}), ("dp", {"DP"}), ("ev", {"EV"}), ("de", {"DE"}),
                      ("du-mo", {"DU", "DP", "MO"})):
        figures[f"phase-{name}.svg"] = lambda lit=lit: d.phase_thumb(lit)
    for name, fn in figures.items():
        s = fn()
        if s is None:
            continue
        if name in CROP:
            s = crop(s, *CROP[name])
        (out / name).write_text(s, encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
