# EAD · Evaluation, multi-class and deep learning · 2026-2027

Slide decks and handouts for Oscar Esteban's sessions in the module **EAD,
Exploration avancée de données et intelligence décisionnelle**, MSc in Business
Administration, HES-SO Master (Lausanne). Published at
<https://oesteban.github.io/msba-ead-2026-2027-slides/>.

Built on [remark.js](https://remarkjs.com/) through the shared
[remark-engine](https://github.com/oesteban/remark-engine) submodule. Every
deck is a single HTML file with its Markdown source inside a `<textarea>`.

## The decks

Dates and titles come from [`course.yml`](course.yml).

| Session | Date | Directory |
|---|---|---|
| From a business question to a first model | Fri 16 Oct 2026, morning | `day1/01-intro/` |
| Evaluating a classifier | Fri 16 Oct 2026, morning | `day1/02-model/` |
| Model selection and cross-validation | Fri 16 Oct 2026, morning and afternoon | `day1/03-cv/` |
| Beyond binary classification | Fri 16 Oct 2026, afternoon | `day1/04-multiclass/` |
| Deep learning for decisions | Fri 23 Oct 2026 | `day2/05-dl/` |

Navigation: arrow keys, `P` for presenter view, `C` to clone the window onto a
second screen, `?` for the full list.

## Running locally

```bash
git clone https://github.com/oesteban/msba-ead-2026-2027-slides.git
cd msba-ead-2026-2027-slides
git submodule update --init remark
python3 -m http.server 8000
```

Then open <http://localhost:8000/day1/01-intro/index.html>. Serve over HTTP rather
than opening the files directly, or the browser blocks the inline SVGs.

## Handouts

Typst sheets in `day<N>/handouts/`, on the HES-SO Master frame in
[`templates/ead-worksheet.typ`](templates/ead-worksheet.typ). The built PDFs
are committed **blank**; a filled sheet never enters git.

```bash
typst compile --root . day1/handouts/<file>.typ
```

## Checking

```bash
python3 tools/lint-decks.py
python3 tools/reyear.py --check
python3 tools/lint-handouts.py
tools/render-deck.sh day1/02-model        # PDF and contact sheets in _preview/
tools/check-steps.sh day1/02-model 11 4   # which steps show, press by press
python3 tools/check-quotes.py <transcription.md> day1/02-model   # verbatim quotes in the notes
```

## Publishing

Pushing to `main` runs [`.github/workflows/pages.yml`](.github/workflows/pages.yml),
which checks out the engine submodule only and deploys to Pages.

## License

Slide and handout content is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
except figures by others (CC BY, CC BY-SA or BSD), each credited with its licence
on its slide.
The engine submodule is MIT.
