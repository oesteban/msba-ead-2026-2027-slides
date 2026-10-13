#!/usr/bin/env python3
"""Roll the deck set over to a new cohort.

Everything year-bound in these decks (session dates, roulette seeds, countdown
timers, deck URLs, QR codes, the module name) is derived from ``course.yml``.
Edit that file, run this script, review the diff.

The script is deliberately narrow. It rewrites *mechanical* state only; it
never touches prose, slide titles or schedules, because those are content
decisions that belong in the planning notes, kept outside this repository.

    python3 tools/reyear.py              rewrite in place, then self-update
    python3 tools/reyear.py --dry-run    report what would change
    python3 tools/reyear.py --check      fail if year-bound leftovers remain
    python3 tools/reyear.py --no-qr      skip QR regeneration

Idempotent: a successful run rewrites each ``replaces:`` to equal its ``date:``,
so running twice is a no-op and next year you edit ``date:`` alone.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "course.yml"

# Years that legitimately appear in the decks and must never be rewritten:
# the papers the course is built on, and pinned tool versions.
CITATION_SAFE = re.compile(
    r"\b(19\d\d|200\d|201\d|202[0-4])\b"
)


def die(msg: str) -> None:
    sys.exit(f"reyear: {msg}")


def load_config() -> dict:
    if not CONFIG.exists():
        die(f"{CONFIG} not found")
    cfg = yaml.safe_load(CONFIG.read_text())
    for key in ("base_url", "repo_url", "previous_base_url", "previous_repo_url", "days"):
        if not cfg.get(key):
            die(f"course.yml is missing required key: {key}")
    return cfg


def date_tokens(d: dt.date) -> dict[str, str]:
    """The three textual shapes a date takes in these decks."""
    out = {
        "padded": f"{d.day:02d}.{d.month:02d}.{d.year}",   # 18.09.2025  (seeds, sidebars)
        "iso": d.isoformat(),                               # 2025-09-18  (data-until)
    }
    if d.day < 10:
        # The decks are inconsistent: week3/day2 writes both 2.10.2025 and
        # 02.10.2025. Carry the unpadded shape only when it actually differs.
        out["bare"] = f"{d.day}.{d.month:02d}.{d.year}"      # 2.10.2025
    return out


def build_substitutions(cfg: dict) -> dict[str, str]:
    """Map every old token to its replacement. Longest-first application is
    handled by the single-pass regex in :func:`apply`, so a replaced span can
    never be rewritten a second time."""
    subs: dict[str, str] = {}

    for day in cfg["days"]:
        old, new = day.get("replaces"), day.get("date")
        if old is None or new is None:
            die(f"day {day.get('id')!r} needs both 'date' and 'replaces'")
        if not isinstance(old, dt.date) or not isinstance(new, dt.date):
            die(f"day {day.get('id')!r}: dates must be unquoted YYYY-MM-DD")
        if old == new:
            continue  # already rolled over
        o, n = date_tokens(old), date_tokens(new)
        for shape, token in o.items():
            # If the new date has no bare shape (day >= 10), fall back to padded.
            subs[token] = n.get(shape, n["padded"])

    # URLs: the repo URL is not a prefix of the pages URL, so no ordering hazard,
    # but keep them explicit anyway.
    if cfg["previous_base_url"] != cfg["base_url"]:
        subs[cfg["previous_base_url"]] = cfg["base_url"]
    if cfg["previous_repo_url"] != cfg["repo_url"]:
        subs[cfg["previous_repo_url"]] = cfg["repo_url"]

    prev_mod, mod = cfg.get("previous_module_name"), cfg.get("module_name")
    if prev_mod and mod and prev_mod != mod:
        subs[prev_mod] = mod

    return subs


def apply(text: str, subs: dict[str, str]) -> tuple[str, int]:
    """Single pass, longest pattern first, so no span is rewritten twice."""
    if not subs:
        return text, 0
    pattern = re.compile("|".join(re.escape(k) for k in sorted(subs, key=len, reverse=True)))
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        return subs[m.group(0)]

    return pattern.sub(repl, text), count


def deck_dirs(cfg: dict) -> list[Path]:
    return [ROOT / day["id"] for day in cfg["days"]]


def rewrite_decks(cfg: dict, subs: dict[str, str], dry_run: bool) -> int:
    total = 0
    for path in sorted(ROOT.glob("day*/*/index.html")):
        original = path.read_text()
        updated, n = apply(original, subs)
        rel = path.relative_to(ROOT)
        if n:
            total += n
            print(f"  {rel}: {n} replacement{'s' if n != 1 else ''}")
            if not dry_run:
                path.write_text(updated)
        else:
            print(f"  {rel}: unchanged")
    return total


def regenerate_qr(cfg: dict, dry_run: bool) -> None:
    if not shutil.which("qrencode"):
        print("  qrencode not found; QR codes NOT regenerated.")
        print("  Install it (brew install qrencode) and re-run, or the QRs will")
        print("  still point at the previous cohort's URLs.")
        return

    base, repo = cfg["base_url"].rstrip("/"), cfg["repo_url"]
    for day in cfg["days"]:
        images = ROOT / day["id"] / "images"
        talk = images / "qr-talk-url.svg"
        if talk.exists():
            url = f"{base}/{day['id']}/index.html"
            print(f"  {talk.relative_to(ROOT)} -> {url}")
            if not dry_run:
                subprocess.run(["qrencode", "-t", "SVG", "-o", str(talk), url], check=True)
        slides = images / "qr-slides-url.svg"
        if slides.exists():
            print(f"  {slides.relative_to(ROOT)} -> {repo}")
            if not dry_run:
                subprocess.run(["qrencode", "-t", "SVG", "-o", str(slides), repo], check=True)


def self_update(cfg: dict) -> None:
    """Set every ``replaces:`` to its block's ``date:`` so the run is idempotent."""
    lines = CONFIG.read_text().splitlines(keepends=True)
    current: str | None = None
    out = []
    for line in lines:
        m = re.match(r"^(\s*)date:\s*(\d{4}-\d{2}-\d{2})\s*$", line)
        if m:
            current = m.group(2)
        m = re.match(r"^(\s*)replaces:\s*(\d{4}-\d{2}-\d{2})\s*(.*)$", line)
        if m and current:
            trailing = f"  {m.group(3)}" if m.group(3) else ""
            line = f"{m.group(1)}replaces: {current}{trailing}\n"
        out.append(line)
    text = "".join(out)
    text = text.replace(
        f'previous_base_url: "{cfg["previous_base_url"]}"',
        f'previous_base_url: "{cfg["base_url"]}"',
    ).replace(
        f'previous_repo_url: "{cfg["previous_repo_url"]}"',
        f'previous_repo_url: "{cfg["repo_url"]}"',
    )
    if cfg.get("previous_module_name") and cfg.get("module_name"):
        text = text.replace(
            f'previous_module_name: "{cfg["previous_module_name"]}"',
            f'previous_module_name: "{cfg["module_name"]}"',
        )
    CONFIG.write_text(text)


def check(cfg: dict) -> int:
    """Validate the decks against course.yml.

    This runs *after* a rollover, when the ``previous_*`` keys have already been
    self-updated, so it cannot work by looking for old values. Instead it asserts
    the invariant that actually matters: every session date and every deck URL in
    the tree must be one that course.yml declares.
    """
    valid_dates: set[str] = set()
    for day in cfg["days"]:
        valid_dates.update(date_tokens(day["date"]).values())

    base = cfg["base_url"].rstrip("/")
    valid_urls = {cfg["repo_url"]} | {f"{base}/{d['id']}/index.html" for d in cfg["days"]} | {base}
    # Lab starting points students fork, or instantiate from a template, are
    # legitimate own-host links.
    for lab in cfg.get("lab_urls") or []:
        valid_urls.add(lab.rstrip("/"))
        valid_urls.add(f"{lab.rstrip('/')}/fork")
        valid_urls.add(f"{lab.rstrip('/')}/generate")

    # Session dates are written as DD.MM.YYYY / D.MM.YYYY, or ISO inside data-until.
    date_re = re.compile(r"\b\d{1,2}\.\d{2}\.\d{4}\b|\bdata-until=\"(\d{4}-\d{2}-\d{2})")
    # Only our own hosts; third-party links are none of this script's business.
    url_re = re.compile(r"https://(?:oesteban\.github\.io|github\.com/oesteban)/[^\"'>)` ]*")

    # A deck's absolute own-host URL is its cover link; nav arrows are relative.
    # Renaming a directory left the cover pointing at the old path while --check
    # stayed green, because that path was still a valid URL for another deck.
    deck_urls = {f"{base}/{d['id']}/index.html" for d in cfg["days"]}

    problems = 0
    for path in sorted(ROOT.glob("day*/*/index.html")):
        own = f"{base}/{path.parent.relative_to(ROOT).as_posix()}/index.html"
        for i, line in enumerate(path.read_text().splitlines(), 1):
            for m in date_re.finditer(line):
                token = m.group(1) or m.group(0)
                if token not in valid_dates:
                    problems += 1
                    print(f"  {path.relative_to(ROOT)}:{i}: date {token!r} is not in course.yml")
            for m in url_re.finditer(line):
                url = m.group(0).rstrip("/")
                if url not in valid_urls:
                    problems += 1
                    print(f"  {path.relative_to(ROOT)}:{i}: url {url!r} is not in course.yml")
                elif url in deck_urls and url != own:
                    problems += 1
                    print(f"  {path.relative_to(ROOT)}:{i}: url {url!r} is another deck's; this one is {own!r}")

    if problems:
        print(f"\n{problems} inconsistenc{'ies' if problems != 1 else 'y'} with course.yml.")
    else:
        print(f"  all session dates and deck URLs match course.yml (cohort {cfg['cohort']}).")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report changes without writing")
    ap.add_argument("--check", action="store_true", help="fail if year-bound leftovers remain")
    ap.add_argument("--no-qr", action="store_true", help="skip QR regeneration")
    args = ap.parse_args()

    cfg = load_config()

    if args.check:
        print(f"Validating decks against course.yml (cohort {cfg['cohort']})...")
        return 1 if check(cfg) else 0

    subs = build_substitutions(cfg)

    # A QR payload is built from base_url and the deck's id, not from its date.
    # Renaming a deck directory therefore changes the QR without changing any
    # date, so regeneration must not sit behind the date substitutions: that
    # left every code pointing at the old path, silently.
    if not subs:
        print("No date substitutions: course.yml is already rolled over.")
        if not args.no_qr:
            print("\nQR codes:")
            regenerate_qr(cfg, args.dry_run)
        return 0

    print(f"Rolling over to cohort {cfg['cohort']} ({len(subs)} substitution rules)\n")
    print("Decks:")
    total = rewrite_decks(cfg, subs, args.dry_run)
    if not args.no_qr:
        print("\nQR codes:")
        regenerate_qr(cfg, args.dry_run)

    if args.dry_run:
        print(f"\nDry run: {total} replacements would be made. Nothing written.")
        return 0

    self_update(cfg)
    print(f"\n{total} replacements written; course.yml self-updated (run is now idempotent).")
    print("Review with: git diff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
