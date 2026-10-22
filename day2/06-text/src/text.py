#!/usr/bin/env python3
"""Compute what the text-mining deck shows of real tools on its own review, for `draw.py` to draw.

    micromamba run -n ead-text python -I day2/06-text/src/text.py day2/06-text/src/text.json

Runs in its own micromamba environment, `ead-text` (python, pytorch, transformers, nltk, numpy,
and vaderSentiment from pip). On first use it downloads, anonymously, BERT base uncased from
Hugging Face (Apache 2.0; J. Devlin et al. 2019) into the Hugging Face cache, and the 50-dimension
GloVe vectors of 6 billion tokens (PDDL; J. Pennington et al. 2014), as repackaged by gensim-data,
into `~/.cache/ead-text/`. Neither enters git. It writes one small JSON file:

- `vader`: VADER's valence of each listed word of the deck's reviews, and each review's scores
  (C. Hutto and E. Gilbert 2014; the vaderSentiment package, MIT).
- `porter`: stems by Porter's original algorithm (M. F. Porter 1980; NLTK's implementation).
- `wordpiece`: BERT's WordPiece tokens of the review and of a few rarer words.
- `masked`: BERT's five likeliest words for a hidden word of the review, with their probabilities.
- `glove`: the deck's words in two dimensions (principal components of their 50-dimension GloVe
  vectors), with the cosine similarities the slide names.
"""

from __future__ import annotations

import gzip
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np

REVIEW = "Great screen, but the battery does not last a day."
REVIEWS = [REVIEW, "Not a great screen, but the battery is good.", "Good battery, good screen."]
STEM_WORDS = ["battery", "batteries", "day", "days", "does", "last", "lasts", "lasting", "screen", "screens",
              "great", "generalizations"]
RARE_WORDS = ["smartphone", "unchargeable", "overheating", "touchscreen"]
MASKED = "Great screen, but the battery does not last a [MASK]."
EMB_WORDS = ["battery", "charger", "power", "screen", "display", "great", "good", "excellent", "awful", "bad",
             "poor"]
PAIRS = [("good", "bad"), ("good", "great"), ("good", "excellent"), ("bad", "awful"), ("battery", "charger"),
         ("good", "battery")]
GLOVE_URL = ("https://github.com/RaRe-Technologies/gensim-data/releases/download/"
             "glove-wiki-gigaword-50/glove-wiki-gigaword-50.gz")
CACHE = Path.home() / ".cache" / "ead-text"


def vader() -> dict:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    a = SentimentIntensityAnalyzer()
    words = sorted({w.strip(",.").lower() for r in REVIEWS for w in r.split()})
    return {"lexicon": {w: a.lexicon[w] for w in words if w in a.lexicon},
            "reviews": [{"text": r, **{k: round(v, 4) for k, v in a.polarity_scores(r).items()}} for r in REVIEWS],
            "clauses": [{"text": c, **{k: round(v, 4) for k, v in a.polarity_scores(c).items()}}
                        for c in ("Great screen,", "but the battery does not last a day.")]}


def porter() -> dict:
    from nltk.stem.porter import PorterStemmer
    s = PorterStemmer(mode=PorterStemmer.ORIGINAL_ALGORITHM)
    return {w: s.stem(w) for w in STEM_WORDS}


def bert() -> tuple[dict, dict]:
    import torch
    from transformers import AutoModelForMaskedLM, AutoTokenizer
    torch.manual_seed(0)
    tok = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModelForMaskedLM.from_pretrained("bert-base-uncased").eval()
    pieces = {"review": tok.tokenize(REVIEW), **{w: tok.tokenize(w) for w in RARE_WORDS},
              "vocabulary": tok.vocab_size}
    enc = tok(MASKED, return_tensors="pt")
    with torch.no_grad():
        logits = model(**enc).logits
    pos = int((enc["input_ids"][0] == tok.mask_token_id).nonzero()[0, 0])
    p = torch.softmax(logits[0, pos], dim=-1)
    top = torch.topk(p, 5)
    guesses = [{"word": tok.convert_ids_to_tokens(int(i)), "p": round(float(v), 4)}
               for v, i in zip(top.values, top.indices)]
    return pieces, {"text": MASKED, "top": guesses}


def glove() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    gz = CACHE / "glove-wiki-gigaword-50.gz"
    if not gz.exists():
        urllib.request.urlretrieve(GLOVE_URL, gz)
    want, vec = set(EMB_WORDS), {}
    with gzip.open(gz, "rt", encoding="utf-8") as f:
        next(f)                                   # word2vec header: vocabulary size and dimension
        for line in f:
            w, rest = line.split(" ", 1)
            if w in want:
                vec[w] = np.array(rest.split(), dtype=float)
                if len(vec) == len(want):
                    break
    X = np.array([vec[w] for w in EMB_WORDS])
    Xc = X - X.mean(axis=0)
    _, sv, vt = np.linalg.svd(Xc, full_matrices=False)
    xy = Xc @ vt[:2].T
    # principal axes have no sign: fix it, battery to the left and great to the top
    if xy[EMB_WORDS.index("battery"), 0] > 0:
        xy[:, 0] *= -1
    if xy[EMB_WORDS.index("great"), 1] < 0:
        xy[:, 1] *= -1

    def cos(a, b):
        return float(vec[a] @ vec[b] / np.linalg.norm(vec[a]) / np.linalg.norm(vec[b]))

    return {"dimensions": int(X.shape[1]),
            "explained": [round(float(v), 3) for v in (sv[:2] ** 2 / (sv ** 2).sum())],
            "points": {w: [round(float(x), 3), round(float(y), 3)] for w, (x, y) in zip(EMB_WORDS, xy)},
            "cosine": {f"{a} {b}": round(cos(a, b), 3) for a, b in PAIRS},
            "battery": [round(float(v), 2) for v in vec["battery"][:4]]}


def main(out: Path) -> int:
    pieces, masked = bert()
    data = {"reviews": REVIEWS, "vader": vader(), "porter": porter(), "wordpiece": pieces, "masked": masked,
            "glove": glove()}
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(data, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
