#!/usr/bin/env python3
"""Check the verbatim quotes in a deck's notes against the textbook's transcription.

    python3 tools/check-quotes.py <transcription.md> day1/02-model [day1/03-cv ...]

The transcription is private and never enters this repository: it lives in the course
wrapper, at `../../.wiki/refs/sources/provost-2013-data-science-business.md` from this
repository's root. Its pages are separated by form feeds, and book page b is
`text.split("\\f")[b + 23]`.

A quote is "..." or “...” followed within 40 characters by a citation ending in
"verbatim)". For each slide's notes (after `???`), it prints every quote with its word
count; a quote marked (Provost & Fawcett, 2013, p. N, verbatim) is also looked up on
that page of the transcription and its neighbours, and any other source (another work,
a Roman page) is listed as not checked. It flags more than two quotes on a slide, a
quote that is not found, a quote of 15 words or more
(AUTHORING.md, "On slides"), an em or en dash, a second `???`, and a `--` line, which
remark reads as an incremental step. Slides are numbered as on screen; an uncounted
slide is shown as `+N`, after slide N.

Exits non-zero if anything is flagged.
"""
import re
import sys
from pathlib import Path

if len(sys.argv) < 3:
    sys.exit(__doc__)
pages = Path(sys.argv[1]).read_text(encoding="utf-8").split("\f")


def norm(t: str) -> str:
    t = t.replace("‐\n", "").replace("-\n", "").replace("‐", "-")
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", t).strip().lower()


def slides(deck: Path):
    """Yield (label, notes) per slide, numbered as remark numbers them on screen."""
    src = deck.read_text(encoding="utf-8")
    md = src[src.index("<textarea"):src.index("</textarea>")]
    n = 0
    for s in re.split(r"\n---\n", md):
        head = s.lstrip("\n").split("\n\n")[0]
        if re.search(r"^layout:\s*true", head, re.M):
            continue
        if re.search(r"^count:\s*false", head, re.M):
            label = f"+{n}"
        else:
            n += 1
            label = str(n)
        parts = re.split(r"^\?\?\?$", s, flags=re.M)
        yield label, parts[1:]


bad = 0
for arg in sys.argv[2:]:
    deck = Path(arg)
    if deck.is_dir():
        deck = deck / "index.html"
    print(f"== {deck}")
    for key, notes in slides(deck):
        if len(notes) > 1:
            print(f"[{key}] {len(notes)} notes blocks (a second ???)"); bad += 1
        body = "\n".join(notes)
        for ln in body.splitlines():
            if ln.strip() == "--":
                print(f"[{key}] INCREMENTAL STEP IN THE NOTES: {ln!r}"); bad += 1
            if "—" in ln or "–" in ln:
                print(f"[{key}] DASH: {ln.strip()[:80]}"); bad += 1
        qs = re.findall(r"[\"“]([^\"”]+)[\"”][^()]{0,40}\(([^()]*?),? verbatim\)", body)
        if len(qs) > 2:
            print(f"[{key}] {len(qs)} QUOTES (max 2)"); bad += 1
        for q, cite in qs:
            words = len(q.split())
            m = re.match(r"Provost (?:&|&amp;|and) Fawcett,? 2013, pp?\. ?(\d+)$", cite.strip())
            if m:
                page = int(m.group(1))
                hay = norm(" ".join(pages[page + 22: page + 25]))     # the page and its neighbours
                found = norm(q).strip(" .,;:") in hay
                status = "found" if found else "NOT FOUND"
            else:
                found, status = True, f"not checked ({cite.strip()})"
            flag = "" if found and words < 15 else "  <-- CHECK"
            if flag:
                bad += 1
            print(f"[{key}] {words:2d}w {status}: {q}{flag}")
        n_verb = body.count("verbatim)")
        if n_verb != len(qs):
            print(f"[{key}] 'verbatim)' appears {n_verb} times but {len(qs)} quotes parsed  <-- CHECK"); bad += 1
print(f"{bad} problem(s)")
sys.exit(1 if bad else 0)
