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
| From a business question to a first model | Fri 16 Oct 2026, morning, first | `day1/intro/` |
| Measuring a classifier: metrics, thresholds and k-fold | Fri 16 Oct 2026, morning | `day1/am/` |
| Beyond two classes, and into deep learning | Fri 16 Oct 2026, afternoon | `day1/pm/` |

Navigation: arrow keys, `P` for presenter view, `C` to clone the window onto a
second screen, `?` for the full list.

## Running locally

```bash
git clone https://github.com/oesteban/msba-ead-2026-2027-slides.git
cd msba-ead-2026-2027-slides
git submodule update --init remark
python3 -m http.server 8000
```

Then open <http://localhost:8000/day1/am/index.html>. Serve over HTTP rather
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
```

## Publishing

Pushing to `main` runs [`.github/workflows/pages.yml`](.github/workflows/pages.yml),
which checks out the engine submodule only and deploys to Pages.

## License

Slide and handout content is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The engine submodule is MIT.
