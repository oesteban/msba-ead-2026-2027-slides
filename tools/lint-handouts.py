#!/usr/bin/env python3
"""Structural lint for the Typst handouts.

The companion to lint-decks.py, and it exists for the same reason: every check
here catches a mistake that **compiles cleanly**. `typst compile` succeeding
says nothing about whether the sheet is correct, and the damage lands on paper,
in front of sixteen students, after the printing is done.

    python3 tools/lint-handouts.py               lint every day*/handouts/*.typ
    python3 tools/lint-handouts.py day1          lint one day

Exits non-zero if an error is found, so it can gate a commit. Warnings are
reported separately and do not fail: they are heuristics for the rules in
AUTHORING.md that cannot be decided mechanically.

The checks, and the bug each one is a memorial to:

1. **Cross-references resolve.** A sheet that says "the figures come back in
   panel 4" has to have a panel 4. On 2026-09-20 the µLab 1 worksheet had its
   panels renumbered 5→4 through 12→11; the file compiled, the PDF looked
   right, and two references (`Panel 12` and `panel 5`) still pointed at panels
   that no longer existed. Nothing in the toolchain noticed. AUTHORING.md F3.

2. **Panel numbers contiguous from 1.** The other half of the same renumbering:
   delete a panel and the sequence gains a hole, which nobody sees while
   scrolling but every reader hits when told to go to panel 7.

3. **Stale PDF.** The PDFs are committed built so that printing needs no
   toolchain. That convenience is also the trap: edit the `.typ`, forget to
   recompile, and the printed sheet is the previous draft. Silent, and only
   discovered in the room.

   Compared by **commit time, not mtime**. The first draft of this check used
   `os.path.getmtime` and reported three of the six handouts as stale on
   2026-09-20; all three were false. Git does not record mtimes, so a checkout
   stamps every file with the time it was written to disk and the comparison
   is noise. Mtime is used only while a source is uncommitted, where it is the
   only signal there is.

4. **Template drift.** Every handout imports the shared
   `templates/ead-worksheet.typ` (EAD is not an ISC module, so the ISC
   `isc-hei-document` package does not apply). A sheet that re-types the
   preamble instead drifts from the set.

5. **The PII banner.** Filled worksheets carry student names and GitHub handles
   and must never enter git; the blank PDFs are what is committed. That rule
   currently lives in a comment block that a new file can simply omit. Any
   instrument collected from students has to carry it. A sheet that is handed
   out and never comes back says so instead, in the same banner, which is why
   `flipped-worksheets.typ` passes without the paragraph.

6. *(warning)* **The checkpoint bar.** µLabs stopped being micro and students
   stopped finishing them. The structural fix is a ten-minute core, a
   checkpoint the referee ticks on the spot, then marked extensions. A ulab
   worksheet without one has no core/extension boundary at all.

   A warning rather than an error, for one reason: the two week1/day2 sheets
   were delivered before the checkpoint existed and are not being rewritten. A
   linter that is red on a clean tree stops being read, and then checks 1 to 5
   stop being read with it. AUTHORING.md G1.

7. *(warning)* **A console block with no flag table.** AUTHORING.md B2: every
   argument of every command line is explained. Three separate commits on
   2026-09-20 went back and added tables that should have been in the first
   draft. The heuristic looks for the two-column `#grid` idiom near a
   multi-line console block. Only blocks whose **first** line is a command are
   considered: a pasted `watch` screen is expected output, not something to
   tabulate. It still cannot tell a deliberate omission from a forgotten one,
   so it warns.

9. **The core is at most three panels.** The 21.09 sheets put five and six
   panels above the checkpoint bar, and groups ran out of clock reading rather
   than working. AUTHORING.md G1 sizes a core for ten minutes; three panels is
   what ten minutes holds. Everything else belongs below the bar, where it is
   not deleted and not optional, merely not in the way.

   An error, not a warning, with an explicit exemption list: the five sheets
   delivered before this rule existed keep their cores, because rewriting a
   printed instrument after the fact is not a lint fix. New sheets have no
   excuse and get none.

8. *(warning)* **Rejected title forms.** AUTHORING.md A1 and A2. Not a grammar
   check: an explicit list of the constructions that were actually rejected,
   which recur because they are the shapes a draft falls into. "Two lines from
   the watch, and the reason", "What you started", "A wish is not a command".
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_PIN = '#import "../../templates/ead-worksheet.typ"'

# The PII paragraph: any instrument that is collected from students carries it.
# Matched loosely, because the wording varies slightly between sheets.
PII_MARKER = re.compile(r"[Cc]ommitted\s+BLANK", re.S)

# The opt-out: a sheet that is handed out and never comes back carries no
# student data, so it states that instead of the paragraph above.
HANDED_OUT = re.compile(r"[Hh]anded out\b", re.S)

# The title forms that were rejected in review, as patterns rather than a
# blacklist of exact strings, since each recurs in new wording.
BAD_TITLE = [
    (re.compile(r'"'), 'a quoted slogan'),
    (re.compile(r"\bis a .+,? not a\b", re.I), '"X is a Y, not a Z"'),
    (re.compile(r"^\s*\d+\s*·\s*What you\b", re.I), '"What you …"'),
    (re.compile(r",\s*and (the reason|what it|why)\b", re.I), '", and the reason/what it …"'),
    (re.compile(r"\bown account\b|\bremembers\b|\bwish\b", re.I), 'a metaphor in the title'),
    (re.compile(r"^\s*\d+\s*·\s*(Whose|What|Which|How|Why)\b.*\?\s*$", re.I), 'a riddle title'),
]


def sessions():
    """Every day*/handouts directory that holds at least one .typ."""
    out = []
    for day in sorted(os.listdir(ROOT)):
        if not re.fullmatch(r"day\d+", day):
            continue
        hdir = os.path.join(ROOT, day, "handouts")
        if os.path.isdir(hdir) and any(f.endswith(".typ") for f in os.listdir(hdir)):
            out.append(day)
    return out


def typ_files(rel_session):
    hdir = os.path.join(ROOT, rel_session, "handouts")
    if not os.path.isdir(hdir):
        return []
    return [os.path.join(hdir, f) for f in sorted(os.listdir(hdir)) if f.endswith(".typ")]


def git_ct(path):
    """Commit time of the last commit touching `path`, or None if untracked."""
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "-1", "--format=%ct", "--", path],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return int(out.stdout.strip()) if out.returncode == 0 and out.stdout.strip() else None


def dirty(path):
    """True if `path` has uncommitted changes, or git cannot say."""
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "status", "--porcelain", "--", path],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return True
    return out.returncode != 0 or bool(out.stdout.strip())


def stale(typ, pdf):
    """Is the built PDF older than its source?

    Commit time decides whenever both files are committed and unmodified:
    git does not preserve mtimes, so on a fresh checkout mtime comparison is
    pure noise (it reported three false positives on 2026-09-20). Mtime is
    consulted only while the source is uncommitted, where nothing else exists.
    """
    if dirty(typ) or dirty(pdf):
        return os.path.getmtime(pdf) < os.path.getmtime(typ)
    t, p = git_ct(typ), git_ct(pdf)
    if t is None or p is None:
        return False
    return p < t


def lineno(src, idx):
    return src.count("\n", 0, idx) + 1


# Sheets delivered before a core-size rule existed keep their cores: a printed
# instrument is not re-cut after the room has used it. None so far.
CORE_CAP = 3
CORE_CAP_EXEMPT: set[str] = set()


def check(path, errors, warnings):
    rel = os.path.relpath(path, ROOT)
    src = open(path, encoding="utf-8").read()
    base = os.path.basename(path)

    def err(line, msg):
        errors.append(f"{rel}:{line}: {msg}")

    def warn(line, msg):
        warnings.append(f"{rel}:{line}: {msg}")

    # -- the panels this file declares -------------------------------------
    panels = []  # (number, title, line)
    for m in re.finditer(r'#panelb?\(\s*"([^"]*)"', src):
        title = m.group(1)
        # Core panels are titled "Step N · ...", tail panels "N · ...". Both
        # carry the same panel number, and "panel N" references resolve to either.
        num = re.match(r"\s*(?:[Ss]tep\s+)?(\d+)\s*·", title)
        panels.append((int(num.group(1)) if num else None, title, lineno(src, m.start())))

    steps = set()
    for m in re.finditer(r'#step\(\s*"(\d+)"', src):
        steps.add(int(m.group(1)))

    numbered = [p for p in panels if p[0] is not None]
    have = {p[0] for p in numbered}

    # -- 1. cross-references resolve ---------------------------------------
    if numbered:
        for m in re.finditer(r"\b[Pp]anels?\s+(\d+)(?:\s+to\s+(\d+))?", src):
            lo = int(m.group(1))
            hi = int(m.group(2)) if m.group(2) else lo
            for n in range(lo, hi + 1):
                if n not in have:
                    err(lineno(src, m.start()),
                        f"reference to panel {n}, which does not exist "
                        f"(panels present: {sorted(have)})")
    if steps:
        for m in re.finditer(r"\bsteps?\s+(\d+)(?:\s+to\s+(\d+))?\b", src):
            lo = int(m.group(1))
            hi = int(m.group(2)) if m.group(2) else lo
            for n in range(lo, hi + 1):
                if n not in steps:
                    err(lineno(src, m.start()),
                        f"reference to step {n}, which does not exist "
                        f"(steps present: {sorted(steps)})")

    # -- 2. panel numbers contiguous from 1 --------------------------------
    if numbered:
        got = [p[0] for p in numbered]
        want = list(range(1, len(got) + 1))
        if got != want:
            err(numbered[0][2],
                f"panel numbers are {got}, expected {want} "
                "(contiguous from 1, in document order)")

    # -- 4. template drift -------------------------------------------------
    if TEMPLATE_PIN not in src:
        m = re.search(r'#import\s+"[^"]+"', src)
        err(lineno(src, m.start()) if m else 1,
            f"template is {m.group(0) if m else 'not imported'}, expected {TEMPLATE_PIN}")

    # -- 5. the PII banner -------------------------------------------------
    if "worksheet" in base or "grid" in base:
        if not PII_MARKER.search(src) and not HANDED_OUT.search(src):
            err(1, "the banner says neither that this sheet is committed BLANK "
                   "(collected from students) nor that it is handed out and never "
                   "returned; one of the two has to be stated")

    # -- 6. the checkpoint bar ---------------------------------------------
    if base.startswith(("ulab", "hands-on")):
        if "checkpoint" not in src:
            warn(1, "a ulab worksheet with no checkpoint bar: no boundary between "
                    "the ten-minute core and the extensions (AUTHORING.md G1)")

    # -- 9. the core is at most three panels -------------------------------
    if base.startswith(("ulab", "hands-on")) and "checkpoint" in src:
        bar = src.index("#checkpoint")
        core = [p for p in panels if lineno(src, src.index(f'"{p[1]}"')) <= lineno(src, bar)]
        if len(core) > CORE_CAP and rel.replace(os.sep, "/") not in CORE_CAP_EXEMPT:
            err(lineno(src, bar),
                f"{len(core)} panels above the checkpoint bar, at most {CORE_CAP} "
                f"allowed: a ten-minute core does not hold more "
                f"(AUTHORING.md G1). Move the rest below the bar")

    # -- 7. console block with no flag table (warning) ---------------------
    for m in re.finditer(r'#raw\(\s*"((?:[^"\\]|\\.)*)"', src):
        body = m.group(1)
        if "\\n" not in body:
            continue                      # single line, nothing to tabulate
        first = body.split("\\n", 1)[0].strip()
        if not re.match(r"(sudo\s+)?(docker|kubectl|git|make|spark-submit|sbatch|watch)\b",
                        first):
            continue                      # expected output, not a command block
        window = src[m.end():m.end() + 1400]
        if not re.search(r"#grid\(.*?\braw\(", window, re.S):
            warn(lineno(src, m.start()),
                 "multi-line command block with no flag table within ~15 lines "
                 "(AUTHORING.md B2: every argument is explained)")

    # -- 8. rejected title forms (warning) ---------------------------------
    for _, title, line in panels:
        for pat, why in BAD_TITLE:
            if pat.search(title):
                warn(line, f'panel title "{title}": {why} (AUTHORING.md A1/A2)')
                break

    # -- vocabulary: cross-validation, never k-fold (AUTHORING.md) -------
    for m in re.finditer(r"\bk-fold\b(?! cross-test)", src, re.I):
        err(lineno(src, m.start()),
            "say 'cross-validation', not 'k-fold'; DSS's 'K-fold cross-test' "
            "is the only exception (AUTHORING.md, On slides)")

    # -- 3. stale PDF ------------------------------------------------------
    pdf = path[:-4] + ".pdf"
    if not os.path.exists(pdf):
        err(1, "no built PDF beside the source; handouts are committed built")
    elif stale(path, pdf):
        err(1, "the built PDF is older than the source: run "
               f"`typst compile {base}` and stage the PDF with it")


def main(argv):
    targets = argv[1:] or sessions()
    files = []
    for t in targets:
        f = typ_files(t.rstrip("/"))
        if not f:
            print(f"lint-handouts: no .typ under {t}/handouts", file=sys.stderr)
            return 2
        files.extend(f)

    errors, warnings = [], []
    for path in files:
        check(path, errors, warnings)

    for w in warnings:
        print(f"warn: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    n = len(files)
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) in {n} handout(s)")
        return 1
    print(f"ok: {n} handouts, no structural problems"
          + (f" ({len(warnings)} warning(s))" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
