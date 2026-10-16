# EAD slides and handouts, 2026-2027

Remark decks and Typst handouts for Oscar's sessions in the HES-SO Master MScBA
module EAD. Published from this repository to GitHub Pages.

> **Governance lives one level up.** `course-msba-ead/CLAUDE.md` loads with this
> file and owns the push policy (ask before every push), commit etiquette
> (conventional commits, no Claude attribution, body at most two lines) and the
> PII doctrine. None of it is repeated here.

**This repository is public.** Run sheets, cohort notes, anything about
individual students, and the previous teacher's decks stay in the private
wrapper (`../planning/`, `../../2025-2026/`, `../../intel/`).

## Before writing anything

Three files hold the standard every deck and sheet is built to; they are
imported here, so they load with this file:

- [`AUTHORING.md`](AUTHORING.md): the writing rules, the 302 rule catalogue
  with the deltas for Dataiku DSS.
- [`SLIDES_STANDARDS.md`](SLIDES_STANDARDS.md): how a deck is built and laid
  out, deck 1 as the reference, and what review has taught.
- [`HANDOUTS_STANDARDS.md`](HANDOUTS_STANDARDS.md): the same for the group
  sheets.

@AUTHORING.md
@SLIDES_STANDARDS.md
@HANDOUTS_STANDARDS.md

## Before committing

```bash
python3 tools/lint-decks.py      # deck structure
python3 tools/reyear.py --check  # dates and URLs against course.yml
python3 tools/lint-handouts.py   # handout structure, cross-references, stale PDFs
```

Then read the result back: `tools/render-deck.sh <deck>` for slides,
`tools/check-steps.sh` for every stepping slide touched, and
`tools/check-quotes.py` for notes (usage in SLIDES_STANDARDS.md, "Checking").

Handout PDFs are committed built: `typst compile --root . <file>.typ`, then
stage the PDF with its source.

## Sources of truth

| what | where |
|---|---|
| Anything year-bound | `course.yml`, propagated by `tools/reyear.py` |
| Handout layout | `templates/ead-worksheet.typ` (HES-SO Master frame, not the ISC template) |
| Slide engine | `remark/` submodule, `oesteban/remark-engine`, theme `hesso-master.css` |
