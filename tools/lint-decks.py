#!/usr/bin/env python3
"""Structural lint for the remark decks.

Every check here exists because the mistake it catches is **invisible**: the
deck still opens, the slide still looks right on screen, and the damage shows
up somewhere else entirely, usually in the printed PDF.

    python3 tools/lint-decks.py                 lint every day*/*/index.html
    python3 tools/lint-decks.py day1/am          lint one deck

Exits non-zero if anything is found, so it can gate a commit.

The checks, and the bug each one is a memorial to:

1. **Separator whitespace.** `--- ` is not a slide separator to remark, it is
   ordinary text. On 2026-09-11 a single trailing space merged the topics slide
   into the QR slide on day 0: the deck reported 22 slides where it had 23 and
   printed 21 pages, because the merged container held an <object> that never
   finished loading and ext/svg-preload.js left it parked off-screen, painting
   nothing at all. Two pages lost to one space.

2. **Content-class brackets.** `.card[` ... `]` is remark's own syntax, and an
   unbalanced bracket swallows the rest of the slide silently rather than
   erroring. Fenced code blocks are excluded, since brackets there are code.

3. **A missing separator.** The mirror image of 1, and just as quiet: delete or
   fail to write a `---` and two slides become one, which still renders and
   still lints. Two h1 headings in a slide is the tell. An icon-only heading
   (`# <i class="fa-brands fa-docker"></i>`) does not count, because that is a
   real pattern in these decks.

4. **A feature without its extension.** `class: stepwise` and `.step-3` do
   nothing at all unless the deck loads `ext/stepwise-svg.js`; same for the
   roulette and the countdown timers. The slide still renders, in its final
   state, so the only symptom is that pressing the arrow does not step. Day 1
   carried a stepwise slide for a day before anyone noticed the deck had never
   loaded the script.

5. **Stray property lines.** `class:`, `count:` and friends are only properties
   when they open a slide. Anywhere else they render as literal text, or do
   nothing at all, which is how a `class: stepwise` can appear to be ignored.

6. **Missing assets.** A relative src/href/data that does not resolve on disk
   is a broken image or a dead stylesheet in the published deck.

7. **Untracked assets.** A file that exists here but is not committed is a 404
   for everyone else, and the deck looks fine locally. Paths inside a submodule
   are skipped; they are tracked in their own repository.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SEPARATOR_WS = re.compile(r'^\s*-{3,}\s+$|^\s+-{3,}\s*$')
PROPERTY = re.compile(r'^(class|count|name|layout|template):', re.IGNORECASE)
ASSET = re.compile(r'(?:src|href|data)\s*=\s*["\']([^"\']+)["\']')
FENCE = re.compile(r'```.*?```', re.S)
H1 = re.compile(r'^# (.+)$', re.M)

# feature in the markdown -> extension the page has to load for it to do
# anything. The markdown is happy either way; only the behaviour goes missing.
NEEDS_EXT = (
    (re.compile(r'^\s*class:.*\bstepwise\b|(?<![\w-])\.step-\d', re.M),
     'ext/stepwise-svg.js', 'stepwise slides'),
    (re.compile(r'^\s*class:.*\b(?:group-)?roulette\b', re.M),
     'ext/roulette.js', 'roulette slides'),
    (re.compile(r'(?<![\w-])\.timer\[|class="timer"', re.M),
     'ext/timer.js', 'countdown timers'),
)
TAG = re.compile(r'<[^>]+>')


def submodule_paths() -> list[str]:
    gitmodules = ROOT / '.gitmodules'
    if not gitmodules.is_file():
        return []
    return [m.strip() for m in
            re.findall(r'^\s*path\s*=\s*(.+)$', gitmodules.read_text(), re.M)]


def tracked_files() -> set[str]:
    out = subprocess.run(['git', 'ls-files'], cwd=ROOT,
                         capture_output=True, text=True)
    return set(out.stdout.split()) if out.returncode == 0 else set()


def source_of(deck: Path) -> tuple[list[str], int]:
    """The markdown inside <textarea id="source">, and its first line number."""
    text = deck.read_text()
    open_tag = '<textarea id="source">'
    start = text.index(open_tag) + len(open_tag)
    end = text.index('</textarea>', start)
    first_line = text[:start].count('\n') + 1
    return text[start:end].splitlines(), first_line


def lint(deck: Path, tracked: set[str], subs: list[str]) -> list[str]:
    found = []
    rel = deck.relative_to(ROOT)
    lines, offset = source_of(deck)

    def say(i: int, msg: str) -> None:
        found.append(f"{rel}:{offset + i}: {msg}")

    # 1. separators that are not separators
    for i, line in enumerate(lines):
        if SEPARATOR_WS.match(line):
            say(i, f"slide separator has stray whitespace: {line!r}. "
                   "remark will not split here and two slides become one")

    # 2. unbalanced content-class brackets, per slide
    slide_start, chunk = 0, []
    slides = []
    for i, line in enumerate(lines):
        if line.strip() == '---':
            slides.append((slide_start, chunk))
            slide_start, chunk = i + 1, []
        else:
            chunk.append(line)
    slides.append((slide_start, chunk))
    for start, chunk in slides:
        body = FENCE.sub('', "\n".join(chunk))
        if body.count('[') != body.count(']'):
            say(start, f"unbalanced brackets in this slide: "
                       f"{body.count('[')} '[' against {body.count(']')} ']'")

    # 3. two titled slides in one, i.e. a separator that never got written
    for start, chunk in slides:
        body = FENCE.sub('', "\n".join(chunk))
        titles = [t for t in H1.findall(body) if TAG.sub('', t).strip()]
        if len(titles) > 1:
            say(start, "this slide has %d headings (%s): a '---' is missing "
                       "above the second one" % (len(titles),
                                                 ", ".join(repr(t) for t in titles)))

    # 4. a feature used in the markdown whose extension is never loaded
    page = deck.read_text()
    for pattern, script, what in NEEDS_EXT:
        m = pattern.search("\n".join(lines))
        if m and script not in page:
            line = "\n".join(lines[:m.start()]).count("\n")
            say(line, f"this deck uses {what} but never loads {script}, "
                      "so the markup renders and does nothing")

    # 5. property lines that are not opening a slide
    #
    # Fenced code is exempt. A workflow file, a compose file or any other YAML
    # on a slide legitimately starts with `name:`, and flagging that would push
    # authors into contorting real file contents to please the linter.
    fenced, in_fence = set(), False
    for i, line in enumerate(lines):
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            fenced.add(i)
        elif in_fence:
            fenced.add(i)
    for i, line in enumerate(lines):
        if i in fenced or not PROPERTY.match(line):
            continue
        j = i - 1
        while j >= 0 and (PROPERTY.match(lines[j]) or not lines[j].strip()):
            # a run of property lines, and any blank lines before the first one
            if lines[j].strip() and not PROPERTY.match(lines[j]):
                break
            j -= 1
        # valid if it opens a slide, or opens the source (the first slide has
        # no separator above it). `--` counts: an incremental step takes its own
        # property block, which is how a step carries `count: false`.
        if j >= 0 and lines[j].strip() not in ('---', '--'):
            say(i, f"property line outside a property block: {line.strip()!r}")

    # 6 and 7. assets
    text = deck.read_text()
    for m in ASSET.findall(text):
        if m.startswith(('http://', 'https://', '#', 'data:', 'mailto:', '//')):
            continue
        ref = urllib.parse.urlparse(m).path
        if not ref:
            continue
        target = os.path.normpath(str(deck.parent / ref))
        rel_target = os.path.relpath(target, ROOT)
        if any(rel_target == s or rel_target.startswith(s + os.sep)
               for s in subs):
            continue
        line = text[:text.index(m)].count('\n') + 1
        if not os.path.exists(target):
            found.append(f"{rel}:{line}: referenced file does not exist: {m}")
        elif rel_target not in tracked and not os.path.islink(target):
            found.append(f"{rel}:{line}: referenced file is not committed, so "
                         f"it will 404 once published: {m}")
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('decks', nargs='*',
                    help='deck directories to lint (default: all)')
    args = ap.parse_args()

    if args.decks:
        paths = [ROOT / d / 'index.html' if (ROOT / d).is_dir() else ROOT / d
                 for d in args.decks]
    else:
        paths = sorted(ROOT.glob('day*/*/index.html'))

    tracked, subs = tracked_files(), submodule_paths()
    problems = []
    for deck in paths:
        if not deck.is_file():
            print(f"no such deck: {deck}", file=sys.stderr)
            return 2
        problems += lint(deck, tracked, subs)

    if problems:
        for p in problems:
            print(p, file=sys.stderr)
        print(f"\n{len(problems)} problem(s) in {len(paths)} deck(s)",
              file=sys.stderr)
        return 1
    print(f"ok: {len(paths)} decks, no structural problems")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
