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

Read [`AUTHORING.md`](AUTHORING.md): the 302 rule catalogue, with the deltas
for Dataiku DSS.

## Before committing

```bash
python3 tools/lint-decks.py      # deck structure
python3 tools/reyear.py --check  # dates and URLs against course.yml
python3 tools/lint-handouts.py   # handout structure, cross-references, stale PDFs
```

Handout PDFs are committed built: `typst compile --root . <file>.typ`, then
stage the PDF with its source.

## Sources of truth

| what | where |
|---|---|
| Anything year-bound | `course.yml`, propagated by `tools/reyear.py` |
| Handout layout | `templates/ead-worksheet.typ` (HES-SO Master frame, not the ISC template) |
| Slide engine | `remark/` submodule, `oesteban/remark-engine`, theme `hes-so.css` |
