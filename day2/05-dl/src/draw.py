#!/usr/bin/env python3
"""Draw the hand-authored figures of the deep-learning deck as themeable, stepwise SVGs.

    python3 day2/05-dl/src/draw.py day2/05-dl/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), loaded from there so the decks draw alike. No
figure shows a photo of the course's photo sets, whose licences are unknown:
the photos drawn on are the openly licensed ones in `images/photos/` (see its
`CREDITS.md`). The pixel patch reads one of them and needs Pillow; without it,
that figure is skipped. Every number is a count from a wiki page, a value from
`compute.csv` (Epoch AI's data, CC BY 4.0), or marked illustrative in the
figure's comment and on its slide.
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


def edges_between(xa, ya, xb, yb, color=EDGE, w=1.1):
    return [f'<line x1="{xa}" y1="{y1}" x2="{xb}" y2="{y2}" stroke="{color}" stroke-width="{w}"/>'
            for y1 in ya for y2 in yb]


# --- Part 1: why networks, why now ----------------------------------------------
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


def deep_features() -> str:
    """A table brings its features; a network learns them from the pixels."""
    W, H = 1000, 330

    def box(x, y, w, t1, t2="", lit=False):
        out = [rect(x, y, w, 76, fill=A_LIGHT if lit else WHITE, stroke=ACCENT,
                    cls="accent-a-light-fill accent-stroke" if lit else "accent-stroke"),
               text(x + w / 2, y + (32 if t2 else 45), t1, size=19, weight="bold")]
        if t2:
            out.append(text(x + w / 2, y + 58, t2, size=15, fill=MUTED))
        return out

    def arrow(x1, x2, y):
        return line(x1, y, x2, y, color=INK, w=1.8)

    y1, y2 = 40, 200
    row1 = (box(30, y1, 250, "the columns", "duration, amount, age")
            + [arrow(284, 344, y1 + 38)] + box(350, y1, 280, "a model", "trees, a regression")
            + [arrow(634, 694, y1 + 38)] + box(700, y1, 260, "good or bad")
            + [text(30, y1 - 12, "a table: the features come with it", size=17, fill=MUTED, anchor="start")])
    row2 = (box(30, y2, 250, "the pixels", "150,528 numbers")
            + [arrow(284, 344, y2 + 38)] + box(350, y2, 280, "layers learn the features", "edges, parts, objects",
                                                lit=True)
            + [arrow(634, 694, y2 + 38)] + box(700, y2, 260, "lion or tiger")
            + [text(30, y2 - 12, "a photo: the network learns its features", size=17, fill=MUTED, anchor="start")])
    return svg(W, H, [step(1, row1), step(2, row2)],
               "A table's columns are features before any model; a deep network learns its features from raw pixels "
               "(LeCun et al. 2015). Schematic. " + LICENCE)


def _tx(year: float) -> float:
    """The timeline's broken axis: 1955 to 2000 on the left, 2005 to 2024 stretched on the right."""
    return 40 + (year - 1955) * 360 / 45 if year <= 2002 else 450 + (year - 2005) * 510 / 19


EVENTS = [  # year, lines, above the axis?
    (1958, ["One artificial neuron", "learns from examples"], True),
    (1986, ["Errors sent back", "through the layers"], False),
    (1998, ["A network reads", "digits on cheques"], True),
    (2009, ["ImageNet: millions", "of labelled photos"], False),
    (2012, ["AlexNet wins,", "on two gaming GPUs"], True),
    (2015, ["ResNet:", "152 layers"], False),
    (2017, ["The transformer,", "for text"], True),
    (2020, ["GPT-3: 175 billion", "weights"], False),
    (2022, ["ChatGPT opens", "to the public"], True),
]


def timeline(part: int) -> str:
    """Part 1 lights 1958 to 1998; part 2 keeps them muted and lights 2009 to 2022."""
    W, H, y0, y1 = 1000, 330, 150, 184
    axis = [f'<polygon class="accent-fill" points="20,{y0} 962,{y0} 962,{y0 - 14} 990,{(y0 + y1) / 2} 962,{y1 + 14} '
            f'962,{y1} 20,{y1}" fill="{ACCENT}"/>',
            f'<path d="M418,{y1 + 4} L430,{y0 - 4} M430,{y1 + 4} L442,{y0 - 4}" stroke="{WHITE}" stroke-width="5"/>']
    groups = {1: [], 2: []}
    first = [e for e in EVENTS if e[0] < 2005]
    for k, (yr, lines_, above) in enumerate(EVENTS):
        x = _tx(yr)
        era = 1 if yr < 2005 else 2
        lit = era == part
        col, ink = (ACCENT, INK) if lit else (GREY_INK, GREY_INK)
        out = [text(x, (y0 + y1) / 2 + 6, str(yr), size=15, weight="bold", fill=WHITE)]
        if above:
            ys = [y0 - 66 + 21 * i for i in range(len(lines_))]
            out.insert(0, line(x, ys[-1] + 8, x, y0 - 2, color=MUTED, w=1.3, marker="", dash="3 3"))
        else:
            ys = [y1 + 40 + 21 * i for i in range(len(lines_))]
            out.insert(0, line(x, y1 + 2, x, ys[0] - 16, color=MUTED, w=1.3, marker="", dash="3 3"))
        anchor = "start" if x < 90 else "middle"
        tx = x - 20 if anchor == "start" else x
        out += [text(tx, y, s_, size=16, fill=ink, weight="bold" if i == 0 else "normal", anchor=anchor)
                for i, (y, s_) in enumerate(zip(ys, lines_))]
        groups[era].append((k, out))
    body = [step(1, axis)]
    if part == 1:
        body += [step(i + 1, out) for i, (_, out) in enumerate(groups[1])]
        body.append(step(len(first) + 1, [
            text(700, 70, "still missing:", size=17, fill=MUTED, anchor="middle"),
            text(700, 96, "labelled data, and compute", size=19, weight="bold", fill=ALERT, anchor="middle")]))
    else:
        body.append(step(1, [o for _, out in groups[1] for o in out]))
        body += [step(i + 1, out) for i, (_, out) in enumerate(groups[2])]
    comment = ("Milestones of neural networks on a broken time axis: Rosenblatt 1958, Rumelhart et al. 1986, "
               "LeCun et al. 1998, Deng et al. 2009, Krizhevsky et al. 2012, He et al. 2016 (ILSVRC 2015), "
               "Vaswani et al. 2017, Brown et al. 2020, OpenAI 2022. ")
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
        text(165, 255, "tiger", size=18, weight="bold"),
        text(165, 300, "What? One label per photo", size=18, weight="bold")]
    where = [frame(355)] + scene(355) + [
        rect(405, 82, 128, 104, fill="none", stroke=ACCENT, cls="accent-stroke", rx=2, sw=3),
        text(410, 76, "tiger", size=15, weight="bold", anchor="start", fill=ACCENT, cls="accent-fill"),
        rect(545, 72, 72, 108, fill="none", stroke=GREY_INK, rx=2, sw=3),
        text(550, 66, "tree", size=15, weight="bold", anchor="start", fill=GREY_INK),
        text(500, 300, "Where? A box per object", size=18, weight="bold")]
    which = [frame(690)] + scene(690, mask=True) + [
        text(835, 300, "Which pixels? A mask per object", size=18, weight="bold")]
    return svg(W, H, [step(1, what), step(2, where), step(3, which)],
               "Three questions asked of a photo: classification (a label), detection (boxes) and segmentation "
               "(a mask per object); after Prince (2023), chapter 10. Illustrative shapes. " + LICENCE)


# --- Part 2: how a network learns -------------------------------------------------
def unit() -> str:
    """One unit: inputs times weights, summed with a bias, then squashed between 0 and 1."""
    W, H = 1000, 360
    xs, ws, b = [0.2, 0.9, 0.5], [1.5, -0.8, 2.0], -0.3
    z = sum(x * w for x, w in zip(xs, ws)) + b
    p = 1 / (1 + math.exp(-z))
    ins = []
    for i, (x, w) in enumerate(zip(xs, ws)):
        y = 70 + i * 100
        ins += [node(110, y, r=30), text(110, y + 7, f"{x:.1f}", size=19, weight="bold"),
                line(142, y, 416, 170, color=EDGE, w=2, marker=""),
                text(214, y + 0.26 * (170 - y) - 9, f"× {w:+.1f}".replace("-", "−"), size=17, fill=ACCENT,
                     cls="accent-fill", weight="bold")]
    ins.append(text(110, 30, "three pixel values", size=16, fill=MUTED))
    s = [rect(420, 120, 190, 100, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
         text(515, 155, "weighted sum", size=18, weight="bold"), text(515, 180, f"plus a bias ({b:+.1f})".replace("-", "−"),
                                                                       size=15, fill=MUTED),
         text(515, 207, f"= {z:.2f}", size=19, weight="bold")]
    cx, cy = 690, 120
    curve = " ".join(f"{cx + 10 + t * 13:.1f},{cy + 90 - 80 / (1 + math.exp(-(t - 6))):.1f}" for t in range(13))
    sq = [line(612, 170, 676, 170, color=INK, w=1.8),
          rect(cx, cy, 176, 100, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
          f'<polyline points="{curve}" fill="none" stroke="{ACCENT}" class="accent-stroke" stroke-width="3"/>',
          text(cx + 88, cy + 126, "a squash: 0 to 1", size=15, fill=MUTED),
          line(868, 170, 912, 170, color=INK, w=1.8),
          text(950, 178, f"{p:.2f}", size=26, weight="bold", fill=ACCENT, cls="accent-fill")]
    cap = [text(520, 330, "the logistic regression of the first day", size=19, weight="bold", fill=ACCENT,
                cls="accent-fill")]
    return svg(W, H, [step(1, ins), step(2, s), step(3, sq), step(4, cap)],
               f"One unit with illustrative inputs {xs}, weights {ws} and bias {b}: weighted sum {z:.2f}, logistic "
               f"squash {p:.2f} (Provost and Fawcett 2013, pp. 106 to 108). Illustrative. " + LICENCE)


NET = {"in": (110, [70, 125, 180, 260, 315]), "h1": (360, [80, 150, 220, 290]),
       "h2": (560, [80, 150, 220, 290]), "out": (790, [110, 185, 260])}


def layers() -> str:
    """Input, hidden and output layers; deep means many hidden ones."""
    W, H = 1000, 400
    xi, yi = NET["in"]
    xo, yo = NET["out"]
    io = [node(xi, y) for y in yi] + [text(xi, 226, "⋮", size=26, fill=MUTED),
                                      text(xi, 30, "input layer", size=17, weight="bold"),
                                      text(xi, 360, "the pixels", size=16, fill=MUTED),
                                      text(xo, 30, "output layer", size=17, weight="bold"),
                                      text(xo, 330, "one unit per class", size=16, fill=MUTED)]
    for y, n in zip(yo, ["lion", "tiger", "cat"]):
        io += [node(xo, y, r=16, fill=A_LIGHT, cls="accent-a-light-fill"),
               text(xo + 30, y + 6, n, size=18, anchor="start")]
    hid = []
    for a, b_ in (("in", "h1"), ("h1", "h2"), ("h2", "out")):
        hid += edges_between(NET[a][0], NET[a][1], NET[b_][0], NET[b_][1])
    hid += [node(x, y) for k in ("h1", "h2") for x in [NET[k][0]] for y in NET[k][1]]
    hid += [text(460, 30, "hidden layers", size=17, weight="bold")]
    deep = [path("M 340 330 L 340 340 L 580 340 L 580 330", color=ACCENT, w=2.2, marker="", cls="accent-stroke"),
            text(460, 368, "deep: many hidden layers, not two", size=17, weight="bold", fill=ACCENT, cls="accent-fill")]
    # the hidden layers go under the input and output units, so they are drawn first
    return svg(W, H, [step(2, hid), step(1, io), step(3, deep)],
               "A network's layers: input units for the pixels, two hidden layers, one output unit per class. "
               "Schematic. " + LICENCE)


def forward() -> str:
    """A photo's values flow forward, layer by layer, to one score per class."""
    W, H = 1000, 380
    cols = {"in": (110, [80, 180, 280]), "h": (420, [80, 180, 280]), "out": (730, [80, 180, 280])}
    vals = {"in": ["0.2", "0.9", "0.5"], "h": ["0.6", "0.1", "0.8"], "out": ["2.1", "0.4", "−1.0"]}
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
    groups[0] += [text(110, 335, "pixel values", size=16, fill=MUTED)]
    groups[1] += [text(420, 335, "each unit: a weighted sum, squashed", size=16, fill=MUTED)]
    groups[2] += [text(730, 335, "one score per class", size=16, fill=MUTED)]
    for y, n in zip(cols["out"][1], ["lion", "tiger", "cat"]):
        groups[2].append(text(775, y + 7, n, size=18, anchor="start"))
    arrow = [line(110, 365, 880, 365, color=ACCENT, w=2.4, marker="ahA", cls="accent-stroke"),
             text(495, 357, "forward", size=15, weight="bold", fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, groups[0]), step(2, groups[1] + arrow), step(3, groups[2])],
               "A forward pass with illustrative values: three inputs, three hidden units, three class scores "
               "(2.1, 0.4, -1.0, the scores of the next slide's softmax). Illustrative. " + LICENCE)


def softmax() -> str:
    """Three scores become three probabilities that sum to one."""
    W, H = 1000, 390
    z = [("lion", 2.1), ("tiger", 0.4), ("cat", -1.0)]
    e = [math.exp(v) for _, v in z]
    p = [x / sum(e) for x in e]
    left = [text(150, 40, "the last layer's scores", size=19, weight="bold")]
    for i, (n, v) in enumerate(z):
        y = 80 + i * 86
        left += [rect(40, y, 220, 60, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
                 text(150, y + 38, f"{n}: {v:+.1f}".replace("-", "−"), size=22)]
    mid = [line(300, 190, 450, 190, color=ACCENT, w=2.6, marker="ahA", cls="accent-stroke"),
           text(375, 170, "softmax", size=20, weight="bold"),
           text(375, 222, "e to each score,", size=15, fill=MUTED), text(375, 242, "divided by their sum", size=15, fill=MUTED)]
    base, top, x0 = 300, 60, 520
    bars = [text(740, 40, "probabilities, summing to 1", size=19, weight="bold"),
            line(x0 - 10, base, 960, base, color=MUTED, w=1.4, marker="")]
    for i, ((n, _), q) in enumerate(zip(z, p)):
        h = q * (base - top)
        x = x0 + i * 150
        fill, cls = (ACCENT, "accent-fill") if i == 0 else (A_LIGHT, "accent-a-light-fill")
        bars += [rect(x, base - h, 100, h, fill=fill, stroke=None, rx=3, cls=cls),
                 text(x + 50, base - h - 10, f"{q:.2f}", size=21, weight="bold" if i == 0 else "normal"),
                 text(x + 50, base + 28, n, size=19, weight="bold" if i == 0 else "normal")]
    win = [text(740, 378, "the most probable class wins, unless the costs say otherwise", size=17, fill=ACCENT,
                cls="accent-fill", weight="bold")]
    body = [step(1, left), step(2, mid + bars), step(3, win)]
    return svg(W, H, body, "Softmax of three illustrative scores (2.1, 0.4, -1.0) into 0.81, 0.15 and 0.04. "
               "Illustrative. " + LICENCE)


def loss() -> str:
    """Minus the log of the probability given to the true class: high when wrong, low when right."""
    W, H = 1000, 380
    probs = [("lion", 0.81), ("tiger", 0.15), ("cat", 0.04)]

    def panel(x0, truth, n):
        q = dict(probs)[truth]
        out = [rect(x0, 20, 440, 270, fill=WHITE, stroke=EDGE, rx=8),
               text(x0 + 220, 52, f"photo {n}: its label is {truth}", size=19, weight="bold")]
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

    a, la = panel(20, "tiger", 1)
    b_, lb = panel(540, "lion", 2)
    cap = [text(500, 372, "the loss: minus the log of the probability given to the true class", size=16, fill=MUTED)]
    return svg(W, H, [step(1, a), step(2, b_), step(3, cap)],
               f"Cross-entropy loss on the same illustrative output (0.81, 0.15, 0.04): {la:.2f} for a tiger photo, "
               f"{lb:.2f} for a lion photo (Prince 2023, section 5.5). Illustrative. " + LICENCE)


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
    cap = [text(500, 360, "training does this for every weight at once: 5.3 million in EfficientNet B0", size=17,
                weight="bold")]
    return svg(W, H, [step(1, axes + start), step(2, steps_), step(3, cap)],
               "Gradient descent on an illustrative loss curve of one weight, five steps with a fixed step size; "
               "EfficientNet B0's 5.3 million parameters from Tan and Le (2019), Table 2. Illustrative. " + LICENCE)


def backprop() -> str:
    """Forward to a score, the loss, then each weight's share of the error sent back."""
    W, H = 1000, 340
    xs = [60, 260, 460, 660]
    names = ["layer 1", "layer 2", "layer 3", "last layer"]
    boxes = []
    for x, n in zip(xs, names):
        boxes += [rect(x, 120, 150, 90, fill=WHITE, stroke=ACCENT, cls="accent-stroke"),
                  text(x + 75, 172, n, size=18, weight="bold")]
    fwd = boxes + [line(60, 80, 800, 80, color=GREY_INK, w=2.4), text(430, 66, "forward: the photo to a score", size=17,
                                                                         fill=GREY_INK)]
    l_ = [line(812, 165, 846, 165, color=INK, w=1.8),
          rect(850, 120, 120, 90, fill="#fdecee", stroke=ALERT, rx=8),
          text(910, 160, "the loss", size=18, weight="bold", fill=ALERT), text(910, 186, "1.90", size=18, fill=ALERT)]
    back = [line(850, 250, 70, 250, color=ACCENT, w=2.8, marker="ahA", cls="accent-stroke", dash="9 6"),
            text(460, 284, "back: each weight gets its share of the error", size=18, weight="bold", fill=ACCENT,
                 cls="accent-fill")]
    back += [line(x + 75, 246, x + 75, 214, color=ACCENT, w=2, marker="ahA", cls="accent-stroke") for x in xs]
    return svg(W, H, [step(1, fwd), step(2, l_), step(3, back)],
               "Back-propagation: a forward pass to the loss (1.90, the tiger photo of the loss slide), then the "
               "error sent back layer by layer (Rumelhart et al. 1986; Prince 2023, chapter 7). Schematic. " + LICENCE)


def _curve(f, n, px, py):
    return " ".join(f"{px(e):.1f},{py(f(e)):.1f}" for e in [i / 4 for i in range(4 * n + 1)])


def epochs() -> str:
    """One epoch is every training photo once; training runs many."""
    W, H = 1000, 390
    tiles = []
    for i in range(29):
        x = 60 + i * 30 + (i // 8) * 14
        tiles.append(rect(x, 30, 24, 24, fill=A_LIGHT if i % 2 else WHITE, stroke=ACCENT,
                          cls="accent-a-light-fill accent-stroke" if i % 2 else "accent-stroke", rx=3, sw=1.2))
    tiles += [path("M 60 66 L 60 76 L 966 76 L 966 66", color=ACCENT, w=2, marker="", cls="accent-stroke"),
              text(513, 100, "one epoch: every training photo seen once, a batch at a time", size=17, weight="bold",
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
               "One epoch over 29 tiles standing for the training photos, in batches; an illustrative training loss "
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


# --- Parts 3 to 5: reused from the earlier draft -----------------------------------
def augment() -> str:
    """The same photo, flipped, cropped and recoloured: new pixels, the same label."""
    W, H = 1000, 250

    def frame(x, label, inner, sub=""):
        out = [rect(x - 85, 20, 170, 150, fill=WHITE, stroke=EDGE, rx=6, sw=1.6), inner,
               text(x, 200, label, size=18, weight="bold")]
        if sub:
            out.append(text(x, 224, sub, size=15, fill=MUTED))
        return out

    orig = frame(110, "a training photo", glyph(110, 100))
    var = (frame(370, "flipped", glyph(370, 100, flip=True), "left to right")
           + frame(610, "cropped", f'<g clip-path="url(#clipc)">{glyph(630, 110, s=1.45)}</g>', "75% of it kept, or more")
           + frame(850, "recoloured", glyph(850, 100, fill="#f0c46a", cls=""), "hue, contrast, brightness"))
    clip = '<clipPath id="clipc"><rect x="525" y="20" width="170" height="150" rx="6"/></clipPath>'
    body = [clip, step(1, orig), step(2, [line(205, 95, 270, 95, color=ACCENT, w=2.4, marker="ahA", cls="accent-stroke")] + var)]
    return svg(W, H, body, "Data augmentation: one abstract training image flipped, cropped (Dataiku's default minimum "
               "kept ratio, 0.75) and recoloured; the label does not change. Illustrative. " + LICENCE)


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


# --- Part 3: borrowing a trained network -------------------------------------------
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
    out += [text(360, 90, "EfficientNet B0, trained on ImageNet", size=19, weight="bold"),
            line(682, 165, 722, 165, color=INK, w=1.6)]
    return out


def head(lit=True):
    if not lit:
        return [rect(728, 110, 230, 110, fill=WHITE, stroke=GREY_INK, rx=8, sw=1.6),
                text(843, 160, "1,000 outputs", size=19), text(843, 186, "ImageNet's classes", size=16, fill=MUTED)]
    return [rect(728, 110, 230, 110, fill=A_LIGHT, stroke=ACCENT, rx=8, sw=2.4, cls="accent-a-light-fill accent-stroke"),
            text(843, 152, "a new head", size=20, weight="bold"), text(843, 180, "lion, tiger", size=18),
            text(843, 204, "learns from the photos", size=15, fill=MUTED)]


def transfer() -> str:
    """Keep the pretrained blocks frozen; replace the last layer by a new head."""
    W, H = 1000, 300
    cap = [text(360, 258, "frozen: the weights learned on ImageNet stay as they are", size=17, fill=MUTED),
           text(843, 258, "the only weights that learn", size=17, weight="bold", fill=ACCENT, cls="accent-fill")]
    body = [step(1, backbone(0)), step(1, head(lit=False), hide="2-end"), step(2, head()), step(3, cap)]
    return svg(W, H, body, "Transfer learning: a backbone pretrained on ImageNet, frozen, its 1,000-class output "
               "replaced by a new two-class head that alone is trained. Schematic. " + LICENCE)


def finetune() -> str:
    """The same network with its last two blocks unlocked: fine-tuning."""
    W, H = 1000, 300
    br = [path("M 500 240 L 500 250 L 674 250 L 674 240", color=ACCENT, w=2.2, marker="", cls="accent-stroke"),
          text(587, 278, "fine-tuned: 2 blocks learn too", size=17, fill=ACCENT, cls="accent-fill", weight="bold"),
          text(240, 278, "still frozen", size=17, fill=MUTED)]
    body = [step(1, backbone(0) + head()), step(2, backbone(2) + br)]
    return svg(W, H, body, "Fine-tuning: the same backbone with its last two blocks unfrozen and trained with the "
               "new head. Schematic. " + LICENCE)


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
    """CLIP's zero-shot: the photo and each class name become vectors; the closest name wins."""
    W, H = 1000, 340

    def vec(x, y, lit=False):
        return [rect(x + i * 18, y, 14, 22, fill=ACCENT if lit else A_LIGHT, stroke=None, rx=2,
                     cls="accent-fill" if lit else "accent-a-light-fill") for i in range(6)]

    def enc(y, name):
        return [rect(200, y, 160, 46, fill=WHITE, stroke=ACCENT, cls="accent-stroke", rx=6),
                text(280, y + 29, name, size=16, weight="bold")]

    img = [rect(20, 14, 150, 100, fill=WHITE, stroke=EDGE, rx=6), glyph(95, 66, s=0.7),
           line(172, 64, 196, 64, color=INK, w=1.6)] + enc(41, "image encoder") + [
        line(362, 64, 392, 64, color=INK, w=1.6)] + vec(396, 53) + [
        text(396, 36, "the photo, as numbers", size=15, fill=MUTED, anchor="start")]
    names = [("lion", 0.21), ("tiger", 0.31), ("cat", 0.18)]
    txt = []
    for k, (n, _) in enumerate(names):
        y = 160 + k * 60
        txt += [rect(20, y, 150, 40, fill="#f4f6f7", stroke=EDGE, rx=20),
                text(95, y + 26, f"“a photo of a {n}”", size=15),
                line(172, y + 20, 196, y + 20, color=INK, w=1.6)] + enc(y - 3, "text encoder") + [
            line(362, y + 20, 392, y + 20, color=INK, w=1.6)] + vec(396, y + 9)
    match = []
    for k, (n, s_) in enumerate(names):
        y = 160 + k * 60
        lit = n == "tiger"
        match += [line(512, y + 20, 560, y + 20, color=MUTED, w=1.2, marker="", dash="3 3"),
                  text(570, y + 26, f"closeness to the photo: {s_:.2f}", size=16, anchor="start",
                       weight="bold" if lit else "normal", fill=ACCENT if lit else INK, cls="accent-fill" if lit else "")]
    match += [text(570, 120, "the closest class name wins: tiger", size=19, weight="bold", anchor="start", fill=ACCENT,
                   cls="accent-fill")]
    return svg(W, H, [step(1, img), step(2, txt), step(3, match)],
               "Zero-shot classification as in CLIP (Radford et al. 2021): an image encoder and a text encoder map the "
               "photo and each class name to vectors, and the closest name wins. Illustrative values. " + LICENCE)


# --- Part 4: the lab --------------------------------------------------------------
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


# --- Part 5: reading the result ----------------------------------------------------
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
LONESTAR5_PEAK = 1.25e15          # FLOP per second at peak (TACC); one day of it is 1.08e20 FLOP
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
        ls = [f'<line x1="{_cx(2016):.1f}" y1="{ly:.1f}" x2="{_cx(2025.5):.1f}" y2="{ly:.1f}" stroke="{ALERT}" '
              f'stroke-width="3"/>',
              line(_cx(2008.2), ly, _cx(2016), ly, color=ALERT, w=1.6, marker="", dash="4 4"),
              text(_cx(2008.4), ly - 30, "one day of Lonestar 5", size=17, weight="bold", fill=ALERT, anchor="start"),
              text(_cx(2008.4), ly - 10, "at peak, from 2016", size=16, fill=ALERT, anchor="start")]
        notes = [text(_cx(ax_) + 14, _cy(al) + 46, f"{mins:.0f} minutes of it", size=16, weight="bold", anchor="start"),
                 text(_cx(gx) - 12, _cy(gl) - 22, f"{yrs:.0f} years of it", size=17, weight="bold", anchor="end",
                      fill=ACCENT, cls="accent-fill")]
        body = [step(1, _axes() + _dots(muted=True, only={"AlexNet", "GPT-3", "Llama 3.1"})), step(2, ls), step(3, notes)]
        what = (f"one day of Lonestar 5 at its peak of {LONESTAR5_PEAK:.3g} FLOP/s ({day:.3g} FLOP): AlexNet in "
                f"{mins:.1f} minutes, GPT-3 in {yrs:.1f} years; peak and training arithmetic differ, so an order of "
                f"magnitude only")
    return svg(W, H, body, f"Training compute of milestone models, log scale, broken time axis; {what}. Data: Epoch AI, "
               "Data on Notable AI Models, CC BY 4.0 (src/compute.csv). " + LICENCE)


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"deep-features.svg": deep_features, "timeline-1.svg": lambda: timeline(1),
               "timeline-2.svg": lambda: timeline(2), "tasks.svg": tasks, "unit.svg": unit, "layers.svg": layers,
               "forward.svg": forward, "softmax.svg": softmax, "loss.svg": loss, "descent.svg": descent,
               "backprop.svg": backprop, "epochs.svg": epochs, "early-stop.svg": early_stop,
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
