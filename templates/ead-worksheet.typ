// ---------------------------------------------------------------------------
// ead-worksheet.typ: the document template for EAD handouts.
//
// EAD is a module of the HES-SO Master MSc in Business Administration, not of
// the ISC bachelor, so the ISC template (@preview/isc-hei-document) does not
// apply: its covers, logos and footers name the HEI and the ISC programme.
// This file keeps the house idiom of the 302 handouts (two-line title, bordered
// panels with an accent rule, numbered steps with tick boxes, a checkpoint bar)
// and swaps the institutional frame for HES-SO Master's.
//
// Usage, from a handout in day<N>/handouts/:
//
//   #import "../../templates/ead-worksheet.typ": *
//   #show: worksheet.with(
//     title: "Hands-on 1 · Day 1 / AM · Pair's sheet\nWhat the round is about",
//     date: datetime(year: 2026, month: 10, day: 16),
//   )
//
//   typst compile --root ../.. <file>.typ
//
// Fonts: Arimo (text) and Fira Code (raw), both SIL OFL. The logo is the
// generic HES-SO mark; replace assets/hes-so-logo.svg with the HES-SO Master
// mark when one is supplied, nothing else changes.
// ---------------------------------------------------------------------------

#let accent = rgb("#00609c")   // matches remark/themes/hesso-master.css
#let hair = 0.4pt + luma(190)

#let institution = [HES-SO Master · MSc in Business Administration]
#let module-name = [EAD · Exploration avancée de données et intelligence décisionnelle]

#let worksheet(
  title: "",
  date: none,
  revision: "1.0",
  logo: "../assets/hes-so-logo.svg",
  body,
) = {
  let lines = title.split("\n")
  let first = lines.first()
  let second = if lines.len() > 1 { lines.slice(1).join(" ") } else { none }
  let when = if date != none { date.display("[day].[month].[year]") } else { "" }

  set document(title: lines.join(" · "))
  set text(font: "Arimo", size: 9pt, lang: "en")
  set par(justify: false, leading: 0.55em)
  set heading(numbering: none)
  show raw: set text(font: "Fira Code", size: 8pt, ligatures: false, features: ("calt": 0))

  set page(
    paper: "a4",
    margin: (x: 1.6cm, top: 2.1cm, bottom: 1.7cm),
    header: context {
      grid(
        columns: (auto, 1fr), align: (left + horizon, right + horizon),
        image(logo, height: 0.75cm),
        text(size: 7pt, fill: luma(90))[#institution \ #module-name],
      )
      v(-4pt)
      line(length: 100%, stroke: 0.6pt + accent)
    },
    footer: context {
      set text(size: 7pt, fill: luma(110))
      grid(
        columns: (1fr, auto),
        [#first#if second != none [ – #second]],
        [#when · rev. #revision · #counter(page).display("1/1", both: true)],
      )
    },
  )

  block(below: 8pt)[
    #text(size: 9pt, weight: "bold", fill: accent, tracking: 0.04em, upper(first))
    #if second != none {
      v(-3pt)
      text(size: 15pt, weight: "bold", second)
    }
  ]
  body
}

// small uppercase tracked label in the accent colour
#let lbl(it, fill: accent) = text(size: 7pt, weight: "bold", tracking: 0.09em, fill: fill, upper(it))

// a line to write on, of width w
#let rule(w) = box(width: w, stroke: (bottom: 0.5pt + luma(120)), height: 9pt)

// bordered block with an accent top rule; panelb may break across pages
#let panel(title, body, breakable: false) = block(
  width: 100%, inset: (x: 6pt, y: 4pt), radius: 2pt, breakable: breakable,
  stroke: (top: 1.4pt + accent, rest: hair),
)[
  #lbl(title)
  #v(3pt)
  #body
]
#let panelb(title, body) = panel(title, body, breakable: true)

// n ruled writing lines
#let writing(n) = {
  for _ in range(n) {
    block(width: 100%, height: 15pt, above: 3pt, below: 0pt, stroke: (bottom: hair))[]
  }
}

#let tick = box(width: 8pt, height: 8pt, stroke: 0.6pt + luma(140), radius: 1pt)

// a numbered step with a tick box
#let step(n, title, body) = grid(
  columns: (auto, 1fr), column-gutter: 6pt, align: (top, top),
  text(size: 8pt, weight: "bold", fill: accent)[#n#h(3pt)#tick],
  [#text(size: 8.5pt, weight: "bold")[#title] \ #text(size: 8pt)[#body]],
)

// a Dataiku screen path, e.g. #dss("Lab", "Visual ML", "Results")
#let dss(..parts) = text(weight: "bold", parts.pos().join([ #sym.arrow.r ]))

// the bar between the core and the extensions
#let checkpoint(msg: [Reached this line? Then the core is done.], note: none) = block(
  width: 100%, inset: (x: 8pt, y: 7pt), radius: 3pt, breakable: false, fill: accent,
)[
  #grid(columns: (auto, 1fr), column-gutter: 9pt, align: (horizon, top),
    box(width: 15pt, height: 15pt, radius: 2pt, fill: white),
    [
      #text(size: 9.5pt, weight: "bold", fill: white, msg)
      #if note != none { v(2pt); text(size: 8.5pt, fill: white, note) }
    ],
  )
]
