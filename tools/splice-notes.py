#!/usr/bin/env python3
"""Splice speaker notes written apart into a deck's `???` blocks.

    python3 tools/splice-notes.py day2/05-dl/index.html notes-part1.md [notes-part2.md ...]

A notes file has one section per slide, headed `### cover` or `### slide N`,
where N is the slide number remark shows (the cover and any `count: false`
slide are not counted); the text under a heading replaces whatever follows
that slide's `???`. Slides without a section keep their notes. The deck-notes
writer agent produces such files. Run lint-decks.py and check-quotes.py after.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def read_notes(paths: list[Path]) -> dict[str, str]:
    notes = {}
    for p in paths:
        for m in re.finditer(r"^### (cover|slide \d+)\n(.*?)(?=^### |\Z)", p.read_text(), flags=re.M | re.S):
            notes[m.group(1)] = m.group(2).strip()
    return notes


def main(deck: Path, paths: list[Path]) -> int:
    notes = read_notes(paths)
    html = deck.read_text()
    a = html.index('<textarea id="source">') + len('<textarea id="source">')
    b = html.index("</textarea>")
    chunks = html[a:b].split("\n---\n")
    counted, done = 0, []
    for i, c in enumerate(chunks):
        if re.search(r"^layout: true", c, flags=re.M):
            continue
        if re.search(r"^count: false", c, flags=re.M):
            key = "cover" if "cover" not in done else None
        else:
            counted += 1
            key = f"slide {counted}"
        if key in notes:
            if "???" not in c:
                sys.exit(f"{key} has no ??? block")
            tail = "\n" if i < len(chunks) - 1 else ""
            chunks[i] = c[: c.index("???") + 3] + "\n\n" + notes[key] + "\n" + tail
            done.append(key)
    missing = set(notes) - set(done)
    if missing:
        sys.exit(f"no such slide in {deck}: {', '.join(sorted(missing))}")
    deck.write_text(html[:a] + "\n---\n".join(chunks) + html[b:])
    print(f"{deck}: notes spliced into {', '.join(done)} ({counted} counted slides)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]))
