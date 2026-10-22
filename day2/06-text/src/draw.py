#!/usr/bin/env python3
"""Draw the hand-authored figures of the text-mining deck as themeable, stepwise SVGs.

    python3 day2/06-text/src/draw.py day2/06-text/images

The drawing helpers and the phase thumbnails are the intro deck's
(`day1/01-intro/src/draw.py`), and the pretrained network is the deep-learning
deck's (`day2/05-dl/src/draw.py`), both loaded from there so the decks draw
alike. The general figures run on three short reviews of a phone written for
this deck; no review of the course's files is drawn, since their licences are
not recorded. Stop lists and accuracy figures come from the works named in each
figure's comment. What real tools make of the review (VADER's scores, Porter's
stems, BERT's tokens and its guesses for a hidden word, GloVe's vectors) is
computed by `text.py` into `text.json`, read here. The linear model's weights and
the prompted model's answer are illustrative, and say so in the comment and on
the slide.
"""

from __future__ import annotations

import importlib.util
import json
import math
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
dl = _load("dl_draw", HERE.parents[2] / "day2" / "05-dl" / "src" / "draw.py")
svg, step, rect, text, line, path = d.svg, d.step, d.rect, d.text, d.line, d.path
INK, MUTED, WHITE, ACCENT, A_LIGHT = d.INK, d.MUTED, d.WHITE, d.ACCENT, d.A_LIGHT
GREY, GREY_INK, EDGE, ALERT = "#e9edf0", "#9aa4a8", "#c9cfd2", "#da232f"
PANEL = "#f4f6f7"
LICENCE = "Oscar Esteban, CC BY 4.0."

# the deck's running review, then the two others of its small collection
REVIEW = "Great screen, but the battery does not last a day."
REVIEWS = [REVIEW, "Not a great screen, but the battery is good.", "Good battery, good screen."]
# what real tools make of them, computed by text.py
T = json.loads((HERE / "text.json").read_text(encoding="utf-8"))
assert T["reviews"] == REVIEWS, "text.json was computed on other reviews: rerun text.py"
# cut into words, nothing else done: the bag of words before any choice of what counts as one term
WORDS = [[w.strip(",.") for w in r.split()] for r in REVIEWS]
RAW_TERMS = list(dict.fromkeys(w for ws in WORDS for w in ws))
# after normalisation and a stop list that keeps "not"
BAGS = [["great", "screen", "battery", "not", "last", "day"],
        ["not", "great", "screen", "battery", "good"],
        ["good", "battery", "good", "screen"]]
TERMS = sorted({t for b in BAGS for t in b})


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tw(s: str, size: float) -> float:
    """A rough width of a string set in the deck's sans serif."""
    return sum(0.33 if c in "il.,'! " else 0.62 if c.isupper() else 0.56 for c in s) * size


def chip(x, y, s, size=22, fill=WHITE, stroke=ACCENT, ink=INK, cls="accent-stroke", strike=False, dash="", w=None):
    w = w or tw(s, size) + 26
    h = size * 1.75
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, rx=6, sw=2, cls=cls, extra=extra),
           text(x + w / 2, y + h / 2 + size * 0.36, esc(s), size=size, fill=ink)]
    if strike:
        out.append(line(x + 6, y + h / 2, x + w - 6, y + h / 2, color=GREY_INK, w=2, marker=""))
    return out, w


def chip_row(words, y, size=22, gap=12, cx=500, style=None):
    """A centred row of chips; `style(i, word)` returns chip keyword arguments. Returns items and x spans."""
    style = style or (lambda i, s: {})
    widths = [tw(s, size) + 26 for s in words]
    x = cx - (sum(widths) + gap * (len(words) - 1)) / 2
    items, spans = [], []
    for i, (s, w) in enumerate(zip(words, widths)):
        c, _ = chip(x, y, s, size=size, w=w, **style(i, s))
        items += c
        spans.append((x, x + w))
        x += w + gap
    return items, spans


def ghost():
    return {"fill": GREY, "stroke": GREY_INK, "ink": GREY_INK, "cls": "", "strike": True, "dash": "5 4"}


def lit():
    return {"fill": A_LIGHT, "cls": "accent-a-light-fill accent-stroke"}


def alert():
    return {"stroke": ALERT, "ink": ALERT, "cls": ""}


def label(x, y, s, size=17, anchor="start", **kw):
    return text(x, y, esc(s), size=size, fill=kw.pop("fill", MUTED), anchor=anchor, **kw)


# --- Part 1 -----------------------------------------------------------------------
def review() -> str:
    """A review is a string of characters: no columns yet."""
    W, H = 1000, 300
    box = [rect(60, 40, 880, 96, fill=PANEL, stroke=EDGE, rx=10), text(500, 100, esc(REVIEW), size=30)]
    cells, x = [], 52
    for c in REVIEW[:26]:
        cells += [rect(x, 178, 30, 44, fill=WHITE, stroke=GREY_INK, rx=3, sw=1.2),
                  text(x + 15, 208, "␣" if c == " " else esc(c), size=19, fill=MUTED if c == " " else INK)]
        x += 33
    cells += [text(x + 14, 208, "…", size=22, fill=MUTED),
              label(500, 268, f"{len(REVIEW)} characters in a row, and the next review has another length", anchor="middle")]
    return svg(W, H, [step(1, box), step(2, cells)],
               f"The deck's review, written for it, as a string of {len(REVIEW)} characters. " + LICENCE)


def aspects() -> str:
    """One review, two opinions: the screen praised, the battery condemned."""
    W, H = 1000, 340
    top = [rect(60, 30, 880, 86, fill=PANEL, stroke=EDGE, rx=10), text(500, 85, esc(REVIEW), size=28)]
    a = [rect(60, 170, 300, 74, fill=WHITE, stroke=ACCENT, rx=8, sw=2.2, cls="accent-stroke"),
         text(210, 216, "Great screen,", size=26),
         text(210, 284, "the screen: positive", size=21, weight="bold", fill=ACCENT, cls="accent-fill")]
    b = [rect(400, 170, 540, 74, fill=WHITE, stroke=ALERT, rx=8, sw=2.2),
         text(670, 216, "but the battery does not last a day.", size=26),
         text(670, 284, "the battery: negative", size=21, weight="bold", fill=ALERT)]
    return svg(W, H, [step(1, top), step(2, a), step(3, b)],
               "One review holding two opinions, one per aspect (Pang & Lee 2008; Zhang et al. 2024, aspect-level "
               "tasks). The review is written for the deck. " + LICENCE)


# --- Part 2 -----------------------------------------------------------------------
RAW = ["Great", "screen", ",", "but", "the", "battery", "does", "not", "last", "a", "day", "."]
NORM = [w.lower() for w in RAW if w not in ",."]


def normalise() -> str:
    """Cut into words, then each written one way."""
    W, H = 1000, 370
    s1 = [text(500, 56, esc(REVIEW), size=28)]
    r2, _ = chip_row(RAW, 112, size=22, gap=10,
                     style=lambda i, s: {"stroke": GREY_INK, "cls": ""} if s in ",." else {})
    s2 = [label(40, 100, "cut into words and punctuation")] + r2
    r3, _ = chip_row(NORM, 222, size=22, gap=10, style=lambda i, s: lit() if s == "great" else {})
    s3 = [label(40, 210, "each written one way: lower case, no punctuation")] + r3
    s4 = [label(500, 335, "thrown away: one capital, a comma and a full stop", anchor="middle", style="italic")]
    return svg(W, H, [step(1, s1), step(2, s2), step(3, s3), step(4, s4)],
               "Tokenising and normalising the deck's review: case folded, punctuation dropped (Provost & Fawcett "
               "2013, p. 253; Manning et al. 2008, section 2.2). " + LICENCE)


SHORT_STOP = {"the", "a"}            # both in Manning et al.'s list of 25 (2008, Figure 2.5)
LONG_STOP = SHORT_STOP | {"but", "does", "not"}


def stopwords() -> str:
    """A short stop list drops two words; a longer one may drop the verdict."""
    W, H = 1000, 380
    r1, _ = chip_row(NORM, 40, size=22, gap=10)
    r2, _ = chip_row(NORM, 150, size=22, gap=10, style=lambda i, s: ghost() if s in SHORT_STOP else {})
    s2 = [label(40, 138, "a short stop list, 25 words long, drops: the, a")] + r2
    r3, _ = chip_row(NORM, 260, size=22, gap=10,
                     style=lambda i, s: dict(ghost(), stroke=ALERT, ink=ALERT) if s == "not"
                     else ghost() if s in LONG_STOP else {})
    s3 = [label(40, 248, "a list that also holds but, does and not leaves: great screen battery last day")] + r3
    s4 = [text(500, 352, "the complaint is gone with “not”", size=20, weight="bold", fill=ALERT)]
    return svg(W, H, [step(1, r1), step(2, s2), step(3, s3), step(4, s4)],
               "Stop lists on the deck's review: the 25-word list of Manning et al. (2008, Figure 2.5) holds 'the' "
               "and 'a'; the longer list is illustrative. " + LICENCE)


STEM_GROUPS = [["battery", "batteries"], ["day", "days"], ["last", "lasts", "lasting"], ["screen", "screens"]]


def stemming() -> str:
    """The forms of one word cut to one stem by Porter's rules; a stem need not be a word."""
    W, H = 1000, 390
    s1, s2 = [label(40, 34, "forms of the review's words", size=17)], []
    for i, grp in enumerate(STEM_GROUPS):
        cx = 130 + i * 247
        for k, w in enumerate(grp):
            c, _ = chip(cx - 75, 52 + k * 46, w, size=20, w=150)
            s1 += c
        stem = T["porter"][grp[0]]
        assert all(T["porter"][w] == stem for w in grp), grp
        s2 += [line(cx, 196, cx, 238, color=INK, w=1.6)]
        c, _ = chip(cx - 75, 244, stem, size=21, w=150, **(lit() if stem not in grp else {}))
        s2 += c
    s2.append(label(40, 316, "their stem, by Porter's rules", size=17))
    s3 = [label(500, 368, "“batteri” and “dai” are not words: a stem only has to be the same for every form",
                anchor="middle", fill=INK)]
    return svg(W, H, [step(1, s1), step(2, s2), step(3, s3)],
               "Porter's original algorithm (Porter 1980), as implemented by NLTK and run by text.py, on forms of the "
               "review's words. " + LICENCE)


def _table(x0, y0, rows, cols, cell, colw, rowh=44, first=150, head_size=19, size=21, styles=None, marked=False):
    """A small document-term table: `cell(r, c)` gives the string; `styles(r, c)` a fill. With `marked`, only the
    filled cells, each redrawn with its value, for a later step over the plain table."""
    if marked:
        out = []
        for i, _ in enumerate(rows):
            y = y0 + 14 + rowh * (i + 1)
            for j, _ in enumerate(cols):
                fill = styles(i, j)
                if fill:
                    out += [rect(x0 + first + colw * j + 6, y - rowh + 6, colw - 12, rowh - 8, fill=fill[0],
                                 stroke=None, rx=4, cls=fill[1]),
                            text(x0 + first + colw * j + colw / 2, y - 14, cell(i, j), size=size,
                                 weight="bold" if fill[0] == A_LIGHT else "normal")]
        return out
    out = []
    for j, c in enumerate(cols):
        out.append(text(x0 + first + colw * j + colw / 2, y0, esc(c), size=head_size, weight="bold"))
    out.append(line(x0, y0 + 14, x0 + first + colw * len(cols), y0 + 14, color=INK, w=1.4, marker=""))
    for i, r in enumerate(rows):
        y = y0 + 14 + rowh * (i + 1)
        out.append(label(x0, y - 14, r, size=19, fill=INK))
        for j, _ in enumerate(cols):
            fill = styles(i, j) if styles else None
            if fill:
                out.append(rect(x0 + first + colw * j + 6, y - rowh + 6, colw - 12, rowh - 8, fill=fill[0], stroke=None,
                                rx=4, cls=fill[1]))
            out.append(text(x0 + first + colw * j + colw / 2, y - 14, cell(i, j), size=size))
        out.append(line(x0, y + 4, x0 + first + colw * len(cols), y + 4, color=EDGE, w=1, marker=""))
    return out


def _sentences(y0):
    return [label(60, y0 + 34 * i, f"{i + 1}   {r}", size=20, fill=INK) for i, r in enumerate(REVIEWS)]


def bow() -> str:
    """One column per word, one row per review, a count in each cell, before any choice of what counts as a word."""
    W, H = 1000, 440
    x0, first, colw, rowh, y0 = 40, 110, 56, 44, 200
    counts = [[ws.count(w) for w in RAW_TERMS] for ws in WORDS]
    hit = {RAW_TERMS.index("Great"), RAW_TERMS.index("great")}
    head = [line(x0, y0 + 14, x0 + first + colw * len(RAW_TERMS), y0 + 14, color=INK, w=1.4, marker=""),
            label(x0, y0 - 78, "one column per term, here each word as written", size=16)]
    for j, w in enumerate(RAW_TERMS):
        x = x0 + first + colw * j + colw / 2 - 4
        head.append(f'<text x="{x}" y="{y0}" font-size="18" font-weight="bold" text-anchor="start" fill="{INK}" '
                    f'transform="rotate(-50 {x} {y0})">{esc(w)}</text>')
    body, marks = [], []
    for i in range(3):
        y = y0 + 14 + rowh * (i + 1)
        body.append(label(x0, y - 14, f"review {i + 1}", size=19, fill=INK))
        for j in range(len(RAW_TERMS)):
            cx = x0 + first + colw * j + colw / 2
            body.append(text(cx, y - 14, str(counts[i][j]), size=19))
            if j in hit:
                marks += [rect(cx - colw / 2 + 5, y - rowh + 6, colw - 10, rowh - 8, fill=A_LIGHT, stroke=None, rx=4,
                               cls="accent-a-light-fill"),
                          text(cx, y - 14, str(counts[i][j]), size=19, weight="bold")]
        body.append(line(x0, y + 4, x0 + first + colw * len(RAW_TERMS), y + 4, color=EDGE, w=1, marker=""))
    sents = [label(40, 30 + 30 * i, f"{i + 1}   {r}", size=19, fill=INK) for i, r in enumerate(REVIEWS)]
    cap = [label(500, 412, "“Great” and “great”: one word, two columns", anchor="middle", fill=INK)]
    return svg(W, H, [step(1, sents), step(2, head + body), step(3, marks + cap)],
               f"A bag of words of the deck's three reviews, cut into words and nothing else: {len(RAW_TERMS)} columns, "
               "as term counts (Provost & Fawcett 2013, pp. 252 to 253). " + LICENCE)


def pairs(bag):
    return [f"{a} {b}" for a, b in zip(bag, bag[1:])]


def ngrams() -> str:
    """Pairs of adjacent words keep a little order: not last, not great."""
    W, H = 1000, 380
    out1, out2 = [], []
    for k, (y, bag, key) in enumerate(((60, BAGS[0], "not last"), (200, BAGS[1], "not great"))):
        row, spans = chip_row(bag, y, size=22, gap=14)
        out1 += [label(40, y - 12, f"review {k + 1}")] + row
        i = bag.index("not")
        x0, x1 = spans[i][0], spans[i + 1][1]
        out2 += [path(f"M {x0} {y + 50} L {x0} {y + 62} L {x1} {y + 62} L {x1} {y + 50}", color=ACCENT, w=2.4,
                      marker="", cls="accent-stroke"),
                 text((x0 + x1) / 2, y + 90, f"“{key}”", size=21, weight="bold", fill=ACCENT, cls="accent-fill")]
    n_pairs = len({p for b in BAGS for p in pairs(b)})
    cap = [label(500, 352, f"the three reviews: {len(TERMS)} words, plus {n_pairs} pairs, make "
                 f"{len(TERMS) + n_pairs} columns", anchor="middle", fill=INK)]
    return svg(W, H, [step(1, out1), step(2, out2), step(3, cap)],
               f"Word pairs (bi-grams) of the deck's reviews after stop words but 'not' are removed; {n_pairs} "
               "distinct pairs (Provost & Fawcett 2013, pp. 263 to 264). " + LICENCE)


def idf(t: str) -> float:
    df = sum(t in b for b in BAGS)
    return 1 + math.log(len(BAGS) / df)


def tfidf() -> str:
    """A term weighs most when frequent in this review and rare in the others: count times IDF."""
    W, H = 1000, 530
    w = [[b.count(t) * idf(t) for t in TERMS] for b in BAGS]
    form = [text(500, 36, "TF-IDF: term frequency × inverse document frequency (IDF)", size=22, weight="bold"),
            text(500, 72, "count in the review × IDF,    IDF = 1 + ln(N / reviews holding the term)", size=21)]
    head = _table(60, 158, ["IDF"], TERMS, lambda r, c: f"{idf(TERMS[c]):.2f}", 112, size=20)
    head.append(label(500, 112, f"“day” is in 1 of the N = {len(BAGS)} reviews: IDF = 1 + ln 3 = {idf('day'):.2f}",
                      anchor="middle", size=19))
    tab = _table(60, 280, [f"review {i + 1}" for i in range(3)], TERMS,
                 lambda r, c: f"{w[r][c]:.2f}" if w[r][c] else "0", 112, size=20)
    common = {TERMS.index("battery"), TERMS.index("screen")}
    top = {(r, c) for r in range(3) for c in range(len(TERMS)) if w[r][c] and w[r][c] == max(w[r])}
    marks = _table(60, 280, [f"review {i + 1}" for i in range(3)], TERMS,
                   lambda r, c: f"{w[r][c]:.2f}" if w[r][c] else "0", 112, size=20,
                   styles=lambda r, c: (A_LIGHT, "accent-a-light-fill") if (r, c) in top
                   else (GREY, "") if c in common else None, marked=True)
    cap = [label(500, 502, "in every review, battery and screen weigh least; a term of one review weighs most",
                 anchor="middle", fill=INK)]
    return svg(W, H, [step(1, form), step(2, head), step(3, tab), step(4, marks + cap)],
               "TF-IDF of the deck's three reviews: term count times IDF(t) = 1 + ln(N / documents containing t), "
               "Provost & Fawcett (2013), pp. 255 to 256, with the natural logarithm. " + LICENCE)


# --- Part 3 -----------------------------------------------------------------------
def lexicon() -> str:
    """VADER scores the words it lists; the review's complaint holds none, so the verdict is positive."""
    W, H = 1000, 390
    lex = T["vader"]["lexicon"]
    rv, cl = T["vader"]["reviews"][0], T["vader"]["clauses"]
    row, spans = chip_row(RAW, 110, size=22, gap=10,
                          style=lambda i, s: lit() if s.lower() in lex else {"stroke": GREY_INK, "cls": ""})
    g = spans[0]
    s1 = row + [text((g[0] + g[1]) / 2, 92, f"+{lex['great']}", size=22, weight="bold", fill=ACCENT,
                     cls="accent-fill"),
                label(40, 40, "VADER lists about 7,500 entries, each scored from −4 to +4; of this review it lists "
                      "“great” alone")]
    b = spans[RAW.index("but")]
    s2 = [rect(b[0] - 3, 107, b[1] - b[0] + 6, 44, fill="none", stroke=ACCENT, rx=7, sw=2.6, cls="accent-stroke"),
          label(b[0] - 3, 92, "“but”: the clause after it dominates", fill=ACCENT, cls="accent-fill",
                weight="bold")]
    n0, n1 = spans[RAW.index("battery")][0], spans[-1][1]
    assert cl[1]["compound"] == 0
    s3 = [path(f"M {n0} 162 L {n0} 236 L {n1} 236 L {n1} 162", color=ALERT, w=2.2, marker=""),
          text((n0 + n1) / 2, 268, "no listed word: the complaint scores 0", size=19, fill=ALERT, weight="bold")]
    s4 = [rect(250, 304, 500, 64, fill=A_LIGHT, stroke=ACCENT, rx=10, sw=2, cls="accent-a-light-fill accent-stroke"),
          text(500, 345, f"VADER's verdict: {rv['compound']:+.2f}, positive", size=24, weight="bold")]
    return svg(W, H, [step(1, s1), step(2, s2), step(3, s3), step(4, s4)],
               f"VADER (Hutto & Gilbert 2014, section 3; the vaderSentiment package) run on the deck's review by "
               f"text.py: 'great' {lex['great']}, the compound score, between -1 and +1, "
               f"{rv['compound']:+.4f}. " + LICENCE)


WEIGHTS = {"great": -1.5, "screen": 0.0, "battery": 0.1, "not": 1.1, "last": 0.2, "day": 0.3}   # illustrative


def linear() -> str:
    """One weight per term; the score adds the weights of the review's terms."""
    W, H = 1000, 380
    terms = BAGS[0]
    s1, s2, ys = [label(60, 36, "review 1's terms")], [label(260, 36, "weights, towards negative")], []
    for i, t in enumerate(terms):
        y = 54 + i * 50
        c, _ = chip(60, y, t, size=21, w=150)
        s1 += c
        wt = WEIGHTS[t]
        s2.append(text(300, y + 26, f"{wt:+.1f}" if wt else "0.0", size=22, weight="bold",
                       fill=ALERT if wt > 0.5 else ACCENT if wt < 0 else INK, cls="" if wt >= 0 else "accent-fill"))
        ys.append(y + 18)
    z = sum(WEIGHTS[t] for t in terms)
    p = 1 / (1 + math.exp(-z))
    s3 = [line(345, y, 520, 190, color=EDGE, w=1.4, marker="") for y in ys]
    s3 += [f'<circle class="accent-stroke" cx="560" cy="190" r="40" fill="{WHITE}" stroke="{ACCENT}" '
           f'stroke-width="2.4"/>', text(560, 200, "Σ", size=30, weight="bold"),
           label(560, 258, f"sum = {z:+.1f}", anchor="middle", fill=INK, size=19)]
    s4 = [line(602, 190, 690, 190, color=INK, w=2),
          rect(696, 140, 260, 100, fill=A_LIGHT, stroke=ACCENT, rx=10, sw=2.2, cls="accent-a-light-fill accent-stroke"),
          text(826, 182, "P(negative)", size=21), text(826, 220, f"{p:.2f}", size=30, weight="bold"),
          label(826, 274, "the logistic function of the sum", anchor="middle", size=16)]
    return svg(W, H, [step(1, s1), step(2, s2), step(3, s3), step(4, s4)],
               f"A linear model on the terms of review 1: illustrative weights summed to {z:+.1f}, a probability of "
               f"{p:.2f} through the logistic function (Jurafsky & Martin 2026, chapter 4). " + LICENCE)


def tokens() -> str:
    """BERT reads WordPiece tokens: whole common words, and known pieces of rarer ones."""
    W, H = 1000, 360
    wp = T["wordpiece"]
    rows = [("the review", wp["review"], "every word and mark is one token"),
            ("“touchscreen”", wp["touchscreen"], "a rarer word: two known pieces"),
            ("“overheating”", wp["overheating"], "pieces need not mean anything")]
    steps = []
    for i, (name, toks, why) in enumerate(rows):
        y = 40 + i * 104
        r, _ = chip_row(toks, y + 20, size=20, gap=8, style=lambda k, s: lit() if i else {})
        steps.append(step(i + 1, [label(40, y + 6, name, size=18, fill=INK, weight="bold"),
                                  label(960, y + 6, why, size=17, anchor="end")] + r))
    steps.append(step(4, [label(500, 346, f"BERT's vocabulary: {wp['vocabulary']:,} tokens; “##” marks a piece that "
                                "continues a word", anchor="middle", fill=INK)]))
    return svg(W, H, steps,
               f"BERT base uncased's WordPiece tokenizer (Devlin et al. 2019, p. 4), run by text.py: lower case, then "
               f"whole words or pieces from a vocabulary of {wp['vocabulary']:,}. " + LICENCE)


def language_model() -> str:
    """A language model guesses a hidden word from the words around it; BERT's five guesses for the review."""
    W, H = 1000, 400
    m = T["masked"]
    before = REVIEW.rsplit(" ", 1)[0]
    xb = 40 + tw(before, 25) * 0.86 + 12
    s1 = [text(40, 52, esc(before), size=25, anchor="start"),
          rect(xb, 22, 110, 44, fill=WHITE, stroke=ACCENT, rx=6, sw=2.4, cls="accent-stroke",
               extra=' stroke-dasharray="6 4"'),
          text(xb + 55, 52, "?", size=26, weight="bold", fill=ACCENT, cls="accent-fill"),
          text(xb + 118, 52, ".", size=25)]
    s2 = [label(40, 112, "BERT's five likeliest words, with their probabilities", size=18)]
    for k, g in enumerate(m["top"]):
        y = 136 + k * 44
        own = g["word"] == "day"
        s2 += [text(250, y + 26, esc(g["word"]), size=22, anchor="end", weight="bold" if own else "normal"),
               rect(266, y + 6, 620 * g["p"], 30, fill=A_LIGHT if not own else ACCENT, stroke=None, rx=4,
                    cls="accent-a-light-fill" if not own else "accent-fill"),
               label(276 + 620 * g["p"], y + 28, f"{g['p']:.2f}", size=19, fill=INK)]
    s3 = [label(500, 378, "the review's own word, “day”, comes fourth; no label was ever needed", anchor="middle",
                fill=INK)]
    return svg(W, H, [step(1, s1), step(2, s2), step(3, s3)],
               "BERT base uncased (Devlin et al. 2019), pretrained to guess hidden words, run by text.py on the deck's "
               "review with its last word hidden: the five likeliest tokens and their probabilities. " + LICENCE)


def embeddings() -> str:
    """GloVe places words used alike close together: 'good' as close to 'bad' as to 'great'."""
    W, H = 1000, 400
    g = T["glove"]
    pts = g["points"]
    xs, ys = [v[0] for v in pts.values()], [v[1] for v in pts.values()]
    px = lambda x: 70 + (x - min(xs)) / (max(xs) - min(xs)) * 340
    py = lambda y: 330 - (y - min(ys)) / (max(ys) - min(ys)) * 250
    left = {"power", "awful", "screen", "excellent"}
    frame = [rect(30, 40, 470, 320, fill=PANEL, stroke=EDGE, rx=8),
             label(265, 388, f"a flat view of {g['dimensions']} numbers per word: distances only roughly kept",
                   anchor="middle", size=16)]
    dots = []
    for w, (x, y) in pts.items():
        dots.append(f'<circle class="accent-fill" cx="{px(x):.1f}" cy="{py(y):.1f}" r="6" fill="{ACCENT}"/>')
        if w == "charger":
            dots.append(text(px(x) + 6, py(y) + 30, w, size=19, anchor="start"))
        else:
            dots.append(text(px(x) + (-10 if w in left else 10), py(y) + 6, w, size=19,
                             anchor="end" if w in left else "start"))
    c = g["cosine"]
    side = [label(560, 70, "how close, on all 50 numbers (cosine):", fill=INK, weight="bold", size=19),
            label(560, 96, "1 when they point the same way, 0 when unrelated", size=16)]
    for k, (pair, col) in enumerate((("good great", ACCENT), ("good bad", ALERT), ("good battery", INK))):
        y = 140 + k * 40
        side += [label(580, y, pair.replace(" ", " and "), size=20, fill=INK),
                 text(940, y, f"{c[pair]:.2f}", size=22, weight="bold", anchor="end", fill=col)]
    vec = [label(560, 290, "one word, one vector, learned from 6 billion tokens:", size=17, fill=INK),
           text(560, 322, "battery → " + ", ".join(f"{v:.2f}".replace("-", "−") for v in g["battery"])
                + ", … (50 numbers)",
                size=19, anchor="start")]
    return svg(W, H, [step(1, frame + dots), step(2, side), step(3, vec)],
               f"GloVe vectors, 50 dimensions, 6 billion tokens (Pennington et al. 2014), of eleven words, run by "
               f"text.py: their first two principal components ({g['explained'][0] + g['explained'][1]:.0%} of their "
               f"spread) and cosine similarities (Jurafsky & Martin 2026, p. 135). " + LICENCE)


def transfer_text() -> str:
    """A network pretrained on text, given a new head for sentiment."""
    W, H = 1000, 300
    inp = [rect(10, 128, 140, 78, fill=PANEL, stroke=EDGE, rx=8), text(80, 162, "a review", size=19, weight="bold"),
           text(80, 188, "as tokens", size=16, fill=MUTED), line(152, 167, 184, 167, color=INK, w=1.6)]
    body = (f'<g transform="translate(150,26) scale(0.84)">' + "\n".join(dl.backbone(0)) + "</g>")
    hd = f'<g transform="translate(150,26) scale(0.84)">' + "\n".join(dl.head()) + "</g>"
    cap = [label(420, 266, "pretrained on billions of words; kept, or fine-tuned", anchor="middle", size=17),
           text(858, 266, "positive or negative", size=17, weight="bold", fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, inp + [body]), step(2, [hd]), step(3, cap)],
               "Transfer learning for text: a transformer pretrained on unlabelled text (BERT: BooksCorpus and English "
               "Wikipedia, 3.3 billion words) given a new output layer for sentiment (Devlin et al. 2019, p. 1). "
               "Schematic, after the deep-learning deck's figure. " + LICENCE)


def prompt() -> str:
    """The classes described in words, no training."""
    W, H = 1000, 250
    p = [rect(20, 30, 470, 180, fill=PANEL, stroke=EDGE, rx=10),
         label(42, 72, "Is this review positive or negative?", size=19, fill=INK, weight="bold"),
         label(42, 116, "“Great screen, but the battery", size=19, fill=INK),
         label(42, 144, "does not last a day.”", size=19, fill=INK),
         label(42, 190, "the task in words; no labelled example", size=15)]
    m = [line(496, 120, 552, 120, color=INK, w=2),
         rect(558, 72, 200, 96, fill=WHITE, stroke=ACCENT, rx=8, sw=2, cls="accent-stroke"),
         text(658, 112, "a language", size=19, weight="bold"), text(658, 138, "model", size=19, weight="bold"),
         label(658, 196, "no weight changes", anchor="middle", size=15)]
    a = [line(764, 120, 812, 120, color=INK, w=2),
         rect(818, 90, 160, 60, fill=A_LIGHT, stroke=ACCENT, rx=30, cls="accent-a-light-fill accent-stroke"),
         text(898, 128, "negative", size=21, weight="bold")]
    return svg(W, H, [step(1, p), step(2, m), step(3, a)],
               "Zero-shot classification by prompting (Brown et al. 2020, p. 7; Zhang et al. 2024). The review is the "
               "deck's; the answer is illustrative. " + LICENCE)


# --- Part 4 -----------------------------------------------------------------------
def costs() -> str:
    """Missing an unhappy review costs four wasted readings: read from 0.2."""
    W, H = 1000, 360
    c = [rect(60, 30, 400, 120, fill=WHITE, stroke=ALERT, rx=8, sw=2.4),
         label(84, 70, "missed: an unhappy review left unread", size=19, fill=INK),
         text(260, 128, "costs 4", size=30, weight="bold", fill=ALERT),
         rect(540, 30, 400, 120, fill=WHITE, stroke=GREY_INK, rx=8, sw=2),
         label(564, 70, "wasted: a happy review read", size=19, fill=INK),
         text(740, 128, "costs 1", size=30, weight="bold")]
    x0, x1, y = 80, 920, 250
    ax = [line(x0, y, x1, y, color=INK, w=2, marker="")]
    for v in (0, 0.2, 0.5, 1):
        x = x0 + (x1 - x0) * v
        ax += [line(x, y - 8, x, y + 8, color=INK, w=2, marker=""), text(x, y + 34, f"{v:g}", size=18)]
    ax.append(label(500, 316, "P(unhappy), the model's score for one review", anchor="middle", size=17))
    xd, xt = x0 + (x1 - x0) * 0.5, x0 + (x1 - x0) * 0.2
    d5 = [text(xd, y - 22, "default 0.5", size=17, fill=MUTED)]
    t = [path(f"M {xt} {y - 4} L {xt} {y - 46}", color=ACCENT, w=3, marker="", cls="accent-stroke"),
         text(xt, y - 56, "read from 0.2 = 1 / (1 + 4)", size=21, weight="bold", fill=ACCENT, cls="accent-fill")]
    return svg(W, H, [step(1, c), step(2, ax + d5), step(3, t)],
               "The care team's scenario: a missed unhappy review costs four times a wasted reading, so the threshold "
               "is cost(FP) / (cost(FP) + cost(FN)) = 1 / (1 + 4) = 0.2. A scenario, not data. " + LICENCE)


def dss_text() -> str:
    """A drawing of Dataiku's Design, Features handling panel for a text column."""
    W, H = 1000, 360
    nav = [rect(20, 20, 220, 320, fill=PANEL, stroke=EDGE, rx=4)]
    for i, n in enumerate(["Target", "Train / Test set", "Features handling", "Algorithms", "Metrics"]):
        yy = 60 + i * 46
        on = n == "Features handling"
        if on:
            nav += [rect(20, yy - 24, 220, 38, fill=A_LIGHT, stroke=None, rx=0, cls="accent-a-light-fill"),
                    rect(20, yy - 24, 6, 38, fill=ACCENT, stroke=None, rx=0, cls="accent-fill")]
        nav.append(text(42, yy, n, size=17, anchor="start", weight="bold" if on else "normal"))
    cols = [rect(256, 20, 210, 320, fill=WHITE, stroke=EDGE, rx=4)]
    for i, (n, on) in enumerate((("TextSimple", True), ("Text", False), ("URL", False))):
        yy = 62 + i * 44
        cols.append(text(276, yy, n, size=17, anchor="start", weight="bold" if on else "normal",
                         fill=INK if on else GREY_INK))
        if not on:
            cols.append(text(446, yy, "rejected", size=13, anchor="end", fill=GREY_INK))
    pane = [rect(482, 20, 498, 320, fill=WHITE, stroke=EDGE, rx=4),
            text(504, 58, "TextSimple · text", size=19, weight="bold", anchor="start")]
    f1 = [text(504, 110, "Text handling", size=17, anchor="start"),
          rect(684, 86, 276, 38, fill=WHITE, stroke=ACCENT, rx=4, sw=2.4, cls="accent-stroke"),
          text(698, 111, "TF/IDF vectorization", size=17, anchor="start", weight="bold")]
    f2 = []
    for i, (k, v) in enumerate((("Min. rows fraction %", "0.1"), ("Max. rows fraction %", "80"),
                                ("N-grams", "1 to 2"))):
        yy = 170 + i * 50
        f2 += [text(504, yy, k, size=17, anchor="start"), rect(800, yy - 25, 120, 36, fill=WHITE, stroke=GREY_INK,
                                                                 rx=4), text(860, yy, v, size=17, weight="bold")]
    f3 = [text(731, 324, "rarest and commonest terms cut; words and pairs", size=15, fill=MUTED, style="italic")]
    return svg(W, H, [step(1, nav + cols + pane + f1), step(2, f2), step(3, f3)],
               "A drawing, not a capture, of Dataiku DSS's Design, Features handling panel for a text column, labels "
               "and values as in the previous teacher's 2025 captures of the course server; to be checked on DSS "
               "15.0. " + LICENCE)


def flow() -> str:
    """The Flow of Hands-on 5: the IMDb reviews to a model; Pang and Lee's reviews scored twice."""
    W, H = 1000, 400

    def dataset(x, y, name, sub=""):
        out = [rect(x, y, 56, 50, fill=A_LIGHT, stroke=ACCENT, rx=6, cls="accent-a-light-fill accent-stroke"),
               text(x + 28, y + 72, name, size=15)]
        if sub:
            out.append(text(x + 28, y + 90, sub, size=13, fill=MUTED))
        return out

    def recipe(x, y, name, fill="#f0c46a", below=False):
        return [f'<circle cx="{x}" cy="{y}" r="20" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>',
                text(x, y + 44 if below else y - 30, name, size=14, fill=MUTED)]

    def model(x, y):
        return [f'<polygon class="accent-fill" points="{x},{y - 30} {x + 30},{y} {x},{y + 30} {x - 30},{y}" '
                f'fill="{ACCENT}"/>', text(x + 40, y + 6, "the model", size=15, weight="bold", anchor="start")]

    def arr(x1, y1, x2, y2):
        return line(x1, y1, x2, y2, color=INK, w=1.6)

    y1, y2, y3 = 50, 200, 320
    row1 = (dataset(20, y1, "imdb-reviews") + [arr(80, y1 + 25, 124, y1 + 25)] + recipe(146, y1 + 25, "Prepare")
            + [arr(168, y1 + 25, 212, y1 + 25)] + dataset(216, y1, "prepared", "TextSimple")
            + [arr(276, y1 + 25, 330, y1 + 25)] + recipe(352, y1 + 25, "Lab", fill="#8fd19e")
            + [arr(374, y1 + 25, 430, y1 + 25)] + model(462, y1 + 25)
            + [text(20, 24, "panels 1 to 3", size=15, weight="bold", fill=ACCENT, cls="accent-fill", anchor="start")])
    row2 = (dataset(20, y2, "polarity-reviews") + [arr(80, y2 + 25, 124, y2 + 25)]
            + recipe(146, y2 + 25, "Prepare, copied") + [arr(168, y2 + 25, 212, y2 + 25)] + dataset(216, y2, "prepared")
            + [arr(276, y2 + 25, 440, y2 + 25)] + recipe(462, y2 + 25, "Score", fill="#8fd19e", below=True)
            + [arr(462, y1 + 57, 462, y2 + 3)]
            + [arr(484, y2 + 25, 530, y2 + 25)] + dataset(534, y2, "scored", "a probability each")
            + [arr(594, y2 + 25, 640, y2 + 25)] + recipe(662, y2 + 25, "Prepare")
            + [arr(684, y2 + 25, 730, y2 + 25)] + dataset(734, y2, "counted", "TP, FP, FN, TN")
            + [text(20, y2 - 26, "panel 4", size=15, weight="bold", fill=ACCENT, cls="accent-fill", anchor="start")])
    row3 = ([path(f"M 50 {y2 + 96} L 50 {y3 + 25} L 124 {y3 + 25}", color=INK, w=1.6)]
            + recipe(146, y3 + 25, "Sentiment plugin", fill="#c9a7e0", below=True) + [arr(168, y3 + 25, 530, y3 + 25)]
            + dataset(534, y3, "plugin-scored", "positive or negative")
            + [arr(594, y3 + 25, 640, y3 + 25)] + recipe(662, y3 + 25, "Prepare")
            + [arr(684, y3 + 25, 730, y3 + 25)] + dataset(734, y3, "counted", "TP, FP, FN, TN"))
    shift = lambda items: [f'<g transform="translate(40,0)">' + "\n".join(items) + "</g>"]
    return svg(W, H, [step(1, shift(row1)), step(2, shift(row2)), step(3, shift(row3))],
               "The Flow of Hands-on 5, drawn after Dataiku DSS's Flow (datasets, recipes, a model, a plugin recipe), "
               "with the sheet's panels; recipe colours schematic. " + LICENCE)


# Side margins cut from a figure's canvas, x from and x to, so that it draws larger at the slide's width.
CROP: dict[str, tuple[int, int]] = {}


def crop(s: str, x0: int, x1: int) -> str:
    """Narrow the viewBox of a figure drawn on a 0-based canvas to x0..x1, its full height kept."""
    return re.sub(r'viewBox="0 0 (\d+) (\d+)"', lambda m: f'viewBox="{x0} 0 {x1 - x0} {m.group(2)}"', s, count=1)


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    figures = {"review.svg": review, "aspects.svg": aspects, "normalise.svg": normalise, "stopwords.svg": stopwords,
               "stemming.svg": stemming, "bow.svg": bow, "ngrams.svg": ngrams, "tfidf.svg": tfidf,
               "lexicon.svg": lexicon, "linear.svg": linear, "lm.svg": language_model, "tokens.svg": tokens, "embeddings.svg": embeddings,
               "transfer-text.svg": transfer_text, "prompt.svg": prompt, "costs.svg": costs, "dss-text.svg": dss_text,
               "flow.svg": flow}
    for name, lit_ in (("bu", {"BU"}), ("du", {"DU"}), ("mo", {"MO"}), ("ev", {"EV"}), ("du-mo", {"DU", "DP", "MO"})):
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
