#!/usr/bin/env python3
"""Draw the hand-authored figures of the deep-learning deck as themeable, stepwise SVGs.

    python3 day2/05-dl/src/draw.py day2/05-dl/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), loaded from there so the decks draw alike. No
figure shows a photo of the course's photo sets: their licences are unknown.
Every number is either a count from the photo sets' wiki page or marked
illustrative in the figure's comment and on its slide.
"""

from __future__ import annotations

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


# ---------------------------------------------------------------------------
def network() -> str:
    """Layers, a loss, gradient descent: one photo through a small network, then the weights corrected."""
    W, H = 1000, 460
    cols = {"in": (130, [80, 130, 180, 260, 310, 360]), "h1": (380, [100, 160, 220, 280, 340]),
            "h2": (580, [100, 160, 220, 280, 340]), "out": (790, [140, 220, 300])}
    edges = []
    for a, b in (("in", "h1"), ("h1", "h2"), ("h2", "out")):
        xa, ya = cols[a]
        xb, yb = cols[b]
        edges += [f'<line x1="{xa}" y1="{y1}" x2="{xb}" y2="{y2}" stroke="{EDGE}" stroke-width="1.1"/>'
                  for y1 in ya for y2 in yb]
    nodes = [node(x, y) for k, (x, ys) in cols.items() if k != "out" for y in ys]
    nodes.append(text(130, 226, "⋮", size=26, fill=MUTED))
    names, probs = ["lion", "tiger", "cat"], [0.81, 0.15, 0.04]
    xo, yo = cols["out"]
    outs = []
    for y, n, p in zip(yo, names, probs):
        outs += [node(xo, y, r=16, fill=A_LIGHT, cls="accent-a-light-fill"),
                 text(xo + 30, y + 6, f"{n} {p:.2f}", size=19, anchor="start", weight="bold" if n == "lion" else "normal")]
    labels = [text(130, 40, "inputs: a tiger photo's pixels", size=17, fill=MUTED),
              text(480, 40, "hidden layers: weighted sums, then an activation", size=17, fill=MUTED),
              text(850, 40, "outputs: one per class", size=17, fill=MUTED)]
    loss = [rect(660, 372, 320, 62, fill="#fdecee", stroke=ALERT, rx=8),
            text(820, 398, "label: tiger. The loss is high", size=18, weight="bold", fill=ALERT),
            text(820, 422, "the network said lion, 0.81", size=16, fill=ALERT),
            line(820, 318, 820, 366, color=ALERT, w=1.8)]
    back = [line(652, 403, 150, 403, color=ACCENT, w=2.8, marker="ahA", cls="accent-stroke", dash="9 6"),
            text(400, 393, "gradient descent: every weight moves a little to lower the loss", size=17,
                 fill=ACCENT, cls="accent-fill", weight="bold"),
            text(400, 430, "batch after batch; one pass over all the training photos is an epoch", size=15, fill=MUTED)]
    body = [step(1, edges + nodes + outs + labels), step(2, loss), step(3, back)]
    return svg(W, H, body, "A small network: six of a photo's pixel values, two hidden layers, three class outputs "
               "with illustrative probabilities; the loss on a tiger called lion; gradient descent sends the "
               "correction back. Illustrative. " + LICENCE)


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


def convolution() -> str:
    """The same small filter slides over the pixels; stacked layers go from edges to objects."""
    W, H = 1000, 400
    c, gx, gy, n = 30, 30, 70, 7
    grid = [rect(gx + i * c, gy + j * c, c, c, fill=GREY, stroke=WHITE, rx=0, sw=1.5) for i in range(n) for j in range(n)]
    win1 = rect(gx, gy, 3 * c, 3 * c, fill="none", stroke=ACCENT, cls="accent-stroke", rx=2, sw=3.5)
    win2 = rect(gx + 4 * c, gy + 3 * c, 3 * c, 3 * c, fill="none", stroke=ACCENT, cls="accent-stroke", rx=2, sw=3.5,
                extra=' stroke-dasharray="6 4"')
    fm_x, fm_y, fc = 330, 100, 26
    fmap = [rect(fm_x + i * fc, fm_y + j * fc, fc, fc, fill=WHITE, stroke=EDGE, rx=0, sw=1.2) for i in range(5) for j in range(5)]
    fmap += [rect(fm_x, fm_y, fc, fc, fill=ACCENT, stroke=None, rx=0, cls="accent-fill"),
             rect(fm_x + 4 * fc, fm_y + 3 * fc, fc, fc, fill=A_LIGHT, stroke=None, rx=0, cls="accent-a-light-fill")]
    left = grid + [win1, win2] + fmap + [
        line(gx + 3 * c + 6, gy + 45, fm_x - 8, fm_y + 13, color=ACCENT, w=2, marker="ahA", cls="accent-stroke"),
        text(gx + 105, 48, "the pixels", size=17, fill=MUTED),
        text(fm_x + 65, 84, "a feature map", size=17, fill=MUTED),
        text(gx, gy + n * c + 34, "the same 9 weights, at every position", size=17, weight="bold", anchor="start"),
    ]
    stages = [("edges", "and colour blobs"), ("motifs", "corners, stripes"), ("parts", "an eye, an ear"),
              ("the object", "a tiger's face")]
    right = []
    for i, (t1, t2) in enumerate(stages):
        y = 40 + i * 84
        lit = i == 3
        right += [rect(560, y, 300, 62, fill=A_LIGHT if lit else WHITE, stroke=ACCENT,
                       cls="accent-a-light-fill accent-stroke" if lit else "accent-stroke"),
                  text(710, y + 27, t1, size=20, weight="bold"), text(710, y + 50, t2, size=16, fill=MUTED)]
        if i < 3:
            right.append(line(710, y + 64, 710, y + 82, color=INK, w=1.6))
    right.append(text(930, 200, "layer", size=15, fill=MUTED))
    right.append(text(930, 220, "after", size=15, fill=MUTED))
    right.append(text(930, 240, "layer", size=15, fill=MUTED))
    body = [step(1, left), step(2, right)]
    return svg(W, H, body, "A 3 by 3 filter slid over a 7 by 7 grid of pixels gives a 5 by 5 feature map; stacked "
               "convolutional layers build edges, motifs, parts and objects (LeCun et al. 2015). Illustrative. " + LICENCE)


def new_head() -> str:
    """Keep the pretrained layers, replace the last one, retrain only what the data allow."""
    W, H = 1000, 330
    blocks = []
    for i in range(7):
        x = 40 + i * 92
        blocks.append(rect(x, 110, 76, 110, fill=GREY, stroke=GREY_INK, rx=6, sw=1.6))
        blocks.append(text(x + 38, 172, f"{i + 1}", size=18, fill=GREY_INK))
        if i < 6:
            blocks.append(line(x + 78, 165, x + 90, 165, color=GREY_INK, w=1.4, marker=""))
    backbone = blocks + [text(360, 90, "EfficientNet B0, trained on ImageNet", size=19, weight="bold"),
                         line(682, 165, 722, 165, color=INK, w=1.6)]
    old = [rect(728, 110, 230, 110, fill=WHITE, stroke=GREY_INK, rx=8, sw=1.6),
           text(843, 160, "1,000 outputs", size=19), text(843, 186, "ImageNet's classes", size=16, fill=MUTED)]
    new = [rect(728, 110, 230, 110, fill=A_LIGHT, stroke=ACCENT, rx=8, sw=2.4, cls="accent-a-light-fill accent-stroke"),
           text(843, 152, "a new head", size=20, weight="bold"), text(843, 180, "lion, tiger", size=18),
           text(843, 204, "trained on the photos", size=15, fill=MUTED),
           text(360, 252, "frozen: the weights learned on ImageNet are kept", size=17, fill=MUTED)]
    retrain = [path("M 500 300 L 500 290 L 674 290 L 674 300", color=ACCENT, w=2.2, marker="", cls="accent-stroke"),
               text(587, 322, "retrained layers: 0 in Hands-on 4; more only if the data allow", size=16,
                    fill=ACCENT, cls="accent-fill", weight="bold")]
    body = [step(1, backbone), step(1, old, hide="2-end"), step(2, new), step(3, retrain)]
    return svg(W, H, body, "Transfer learning: a backbone pretrained on ImageNet, its 1,000-class output replaced by "
               "a new two-class head; Dataiku's number of retrained layers sets how many backbone layers are "
               "fine-tuned. Schematic. " + LICENCE)


def augment() -> str:
    """The same photo, flipped, cropped and recoloured: new pixels, the same label."""
    W, H = 1000, 250

    def glyph(x, y, s=1.0, flip=False, fill=A_LIGHT, cls="accent-a-light-fill"):
        sx = -s if flip else s
        g = (f'<g transform="translate({x},{y}) scale({sx},{s})">'
             f'<polygon class="{cls}" points="-50,40 -10,-40 50,40" fill="{fill}"/>'
             f'<circle cx="18" cy="-18" r="14" fill="{INK}"/></g>')
        return g

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


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"network.svg": network, "softmax.svg": softmax, "convolution.svg": convolution,
               "new-head.svg": new_head, "augment.svg": augment, "hygiene.svg": hygiene}
    for name, lit in (("mo", {"MO"}), ("du", {"DU"}), ("dp", {"DP"}), ("ev", {"EV"}), ("de", {"DE"}),
                      ("du-mo", {"DU", "DP", "MO"})):
        figures[f"phase-{name}.svg"] = lambda lit=lit: d.phase_thumb(lit)
    for name, fn in figures.items():
        (out / name).write_text(fn(), encoding="utf-8")
        print(out / name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
