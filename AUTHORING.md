# Authoring the EAD material

The rule catalogue is the one written for the 302 decks and handouts,
[`isc-302-2026-2027-slides/AUTHORING.md`](https://github.com/oesteban/isc-302-2026-2027-slides/blob/main/AUTHORING.md).
Rules are cited by the same ids (A1, B2, F1, …). This page records only where
EAD differs: the students are business profiles working in **Dataiku DSS**
through its visual interface, so most of what 302 says about command lines
applies to screens and clicks instead.

## The short form

- **A1/A2** A title names its content and carries a verb.
- **B1** State the aim of a step before the action that performs it.
- **B2, for DSS** Every step names its full screen path, with the template's
  `#dss(...)` helper on paper and the same arrows on slides:
  **Lab → Visual ML → Results → Performance**. Every setting a step changes is
  named with the value to set, exactly as the DSS screen labels it.
- **B3, for DSS** Every step says which object it acts on: the project, the
  dataset, the analysis, the model. Two analyses on one dataset look identical
  until the wrong one is open.
- **B4** Before an exercise, give the need and the reason, never the outcome.
- **C1** Every question names the screen, panel or chart that answers it.
- **C2/C3** Never ask about an undefined term; define every word the reader
  sees on screen, including DSS's own labels ("Cost matrix", "Optimal
  threshold", "Lift").
- **D1** Define what a thing is and does. No metaphor, no simile.
- **E1** Impersonal for facts, second person for actions and questions.
- **F1, for DSS** **Every step is run on the course DSS server before it is
  printed**, and the values quoted are those observed there (version, labels,
  defaults, numbers). The DSS version is recorded in the handout banner.
- **F2** Render the PDF or slide to an image and read it back.
- **G1** A core sized for the time on the run sheet, a checkpoint bar, then
  marked extensions.
- **G3** Never remove or move an existing slide without warning first.

## On slides

Less is better: a slide is a visual aid for a person speaking. One idea per
slide; cut text rather than shrink type. Presenter notes (`???`) are empty by
default: a note is only a fact said out loud that does not fit on the slide,
never a stage direction or a design rationale.

Say **cross-validation**, never k-fold, on slides and on paper; define it on a
slide before any slide uses it (C2/C3). DSS's own setting "K-fold cross-test"
appears only inside a screen path, as its label. The linters enforce the word.

## Material from the previous edition

The 2025-26 decks of this slot are the content source, not a template.
Nothing is copied verbatim: this repository is public. Figures are redrawn or
regenerated from open data. A figure by someone else appears only under an open
licence (CC BY, CC BY-SA, BSD), credited with that licence on its slide.
