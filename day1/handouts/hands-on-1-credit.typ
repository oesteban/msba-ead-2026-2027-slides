// ---------------------------------------------------------------------------
// hands-on-1-credit.typ: the group's sheet for Hands-on 1, 16.10.2026 AM.
//
// One sheet per group of three (Driver, Mapper, Referee), both sides. Page 1 is
// the data card. The core (panels 1 to 3, about 40 minutes, block 1) comes
// before any theory: the group explores South German Credit, trains a first
// model with the defaults, looks at its result pages and writes three notes,
// each placed on a phase of the CRISP-DM map. The evaluation deck starts from
// those notes. Below the checkpoint bar (block 2) the group moves the threshold,
// enters the cost matrix and reads the gains chart (Evaluating a classifier),
// then switches to five folds (Model selection and cross-validation).
//
// The data: south_german_credit.csv, built by ../../tools/build-datasets.py in
// the private wrapper from UCI dataset 573 (CC BY 4.0), English names and labels.
//
// DSS screen paths drafted from the 2025-26 screenshots (DSS 13) and the
// Dataiku documentation; AUTHORING.md F1: to be run on the course server and
// corrected before printing. Server: DSS 15.0.0; panel 2, step 2 from its
// Features handling screen. Verified on: DSS ____ , __.__.2026.
//
// Handed out, kept by the group, never collected: it carries no name.
//
//   typst compile --root ../.. hands-on-1-credit.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 1 · Day 1 / Morning · Group's sheet\nA first model on South German Credit",
  date: datetime(year: 2026, month: 10, day: 16),
)

#let phases = [BU #h(3pt) DU #h(3pt) DP #h(3pt) M #h(3pt) E #h(3pt) D]
#let note-line = grid(
  columns: (1fr, auto), column-gutter: 8pt, align: (bottom, bottom),
  block(width: 100%, height: 15pt, stroke: (bottom: hair))[],
  text(size: 7.5pt, fill: luma(90))[phase: #phases],
)

*The case.* A bank decides whether to grant consumer credits. It holds 1,000
past credits whose outcome is known, and asks whether a model could help it
decide on the next applications. This sheet comes before any slide on
evaluation: explore, train, look, and write down what you see. The debrief
starts from your notes.

#v(4pt)

#block(width: 100%, inset: (x: 6pt, y: 5pt), radius: 2pt, stroke: 1pt + accent)[
  #lbl("Data card · south_german_credit.csv")
  #v(3pt)
  #grid(
    columns: (1fr, 1fr), column-gutter: 10pt,
    [
      *What a row is.* One consumer credit granted between 1973 and 1975 by a
      regional bank in southern Germany. 1,000 rows, 21 columns, no missing values.

      *The target.* `credit_risk`: `good` if the credit contract was complied
      with (700 rows), `bad` if not (300 rows).

      *How the rows were chosen.* A stratified sample: bad credits were
      deliberately over-represented. In the bank's portfolio about 5% of
      credits went bad; here 30% did. Every debtor had already passed the
      bank's checks: refused applicants are not in the data.
    ],
    [
      *Its history.* Published in 1994 as "Statlog German Credit" with a code
      table that mixed up the categories of eight columns (for example, it made
      963 of the 1,000 debtors foreign workers; 37 were). Grömping corrected it
      in 2019. This file is the corrected version, with English labels.

      *Source and licence.* U. Grömping (2019), South German Credit Data:
      Correcting a Widely Used Data Set, Report 4/2019, Beuth Hochschule für
      Technik Berlin. UCI Machine Learning Repository, dataset 573,
      doi:10.24432/C5QG88, CC BY 4.0.
    ],
  )
  #v(3pt)
  #set text(size: 7.5pt)
  #table(
    columns: (auto, 1fr, auto, 1fr), inset: (x: 3pt, y: 2.2pt), stroke: hair,
    [*column*], [*what it describes*], [*column*], [*what it describes*],
    [`status`], [the debtor's checking account with the bank], [`present_residence`], [years at the present address (bands)],
    [`duration`], [credit duration, months], [`property`], [the debtor's most valuable property],
    [`credit_history`], [how earlier credits were paid back], [`age`], [age, years],
    [`purpose`], [what the credit is for], [`other_installment_plans`], [instalment plans with other providers],
    [`amount`], [credit amount in DM, rescaled (true values unknown)], [`housing`], [rent, own, or for free],
    [`savings`], [the debtor's savings (bands)], [`number_credits`], [credits at this bank, this one included],
    [`employment_duration`], [time with the current employer (bands)], [`job`], [kind of job, from unskilled to manager],
    [`installment_rate`], [instalments as a share of disposable income], [`people_liable`], [persons who depend on the debtor],
    [`personal_status_sex`], [sex and marital status combined; sex cannot be recovered from it], [`telephone`], [a landline in the debtor's name],
    [`other_debtors`], [a co-applicant or a guarantor, if any], [`foreign_worker`], [whether the debtor is a foreign worker],
  )
]

#v(5pt)

#block(width: 100%, inset: (x: 6pt, y: 5pt), radius: 2pt, stroke: hair)[
  #lbl("Three roles, one screen")
  #v(3pt)
  #grid(
    columns: (1fr, 1fr, 1fr), column-gutter: 10pt,
    [*Driver.* Works Dataiku, and only Dataiku: says aloud what each screen shows before clicking on.],
    [*Mapper.* Keeps this sheet: writes the answers and the three notes, and places each note on a phase of the map (BU business understanding, DU data understanding, DP data preparation, M modeling, E evaluation, D deployment).],
    [*Referee.* Checks every step against this sheet and challenges every conclusion: is it true of the data, or of the tool? Speaks for the group in the debrief.],
  )
]

#pagebreak()

#panel("Step 1 · Explore the data before modelling it")[
  #step(1, "Load the data")[In your project, on the Flow: #dss("+ Dataset", "Upload your files"), choose `south_german_credit.csv`, then *Create*.]
  #v(2pt)
  #step(2, "Count the bad credits")[Open the dataset: #dss("Explore"), click the header of `credit_risk`, then *Analyze*.]
  Share of `bad`: #rule(1.6cm) #h(10pt) The bank's own rate was about 5%. Why would a sample hold six times more?
  #writing(1)
  #v(2pt)
  #step(3, "Set one column against the target")[#dss("Charts"): chart type *Stacked bars 100%*; drag `status` to the X axis, *Count of records* to the Y axis, and `credit_risk` to the colour.]
  Which value of `status` carries the largest share of `bad`? #h(4pt) #rule(5cm)
]

#v(5pt)

#panel("Step 2 · Train a first model on all 20 columns")[
  #step(1, "Create the analysis")[Select the dataset, then #dss("Lab", "AutoML Prediction"). Target `credit_risk`. Keep *Quick prototypes*, then *Create*.]
  #v(2pt)
  #step(2, "Bring back five columns")[#dss("Design", "Features handling"): five rows read *Rejected, text feature* (`status`, `credit_history`, `savings`, `personal_status_sex`, `property`). Dataiku took their long labels for free text (intro deck, slide 15). Tick the five, set their type to *Categorical*, and switch them on.]
  #v(2pt)
  #step(3, "Train")[Change nothing else in #dss("Design"). Click *Train* and wait for every model to finish.]
  #v(2pt)
  How many models did Dataiku train? #rule(1.2cm) #h(8pt) By which metric does #dss("Results") rank them? #rule(2.6cm) #h(8pt) Best score: #rule(1.4cm)
]

#v(5pt)

#panel("Step 3 · Look at the result, then write three notes")[
  #step(1, "Open the best model")[#dss("Results"), click the best model, then #dss("Performance", "Confusion matrix"). Copy the table as Dataiku labels it:]
  #v(2pt)
  #table(
    columns: (1.6fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [], [*predicted* #rule(1.2cm)], [*predicted* #rule(1.2cm)],
    [*actually* #rule(1.2cm)], [], [],
    [*actually* #rule(1.2cm)], [], [],
  )
  Which value of `credit_risk` does Dataiku treat as *positive*? #rule(2.4cm) #h(8pt)
  Drag the *threshold* slider above the table: what changes? #rule(4cm)
  #v(2pt)
  #step(2, "Ask which columns weigh most")[#dss("Interpretation", "Variable importance"). The first three: #rule(6cm)]
  Does your chart of step 1 agree?
  #writing(1)
  #v(2pt)
  #step(3, "Write three notes")[Three things you noticed, or cannot explain yet, on any screen of this sheet. The Mapper circles the phase each one belongs to; the Referee picks the one to say first.]
  #note-line
  #note-line
  #note-line
]

#v(6pt)

#checkpoint(
  msg: [Reached this line? Stop here: the Referee reports in the debrief.],
  note: [Panels 4 to 7 are for block 2, each after its slides: 4 to 6 in *Evaluating a classifier*, 7 in *Model selection and cross-validation*.],
)

#v(6pt)

#panel("4 · Move the threshold")[
  TP: bad, refused. FP: good, refused. FN: bad, granted. TN: good, granted.

  #step(1, "Reopen the model of panel 3")[#dss("Results", "model", "Performance", "Confusion matrix"). Set the cut-off with the slider above the table to each value below, and copy the counts.]
  #v(2pt)
  #table(
    columns: (auto, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1.3fr), inset: 4pt, stroke: hair,
    [*cut-off*], [*TP*], [*FP*], [*FN*], [*TN*], [*precision*], [*recall*], [*false-positive rate*],
    [0.6], [], [], [], [], [], [], [],
    [0.4], [], [], [], [], [], [], [],
    [0.2], [], [], [], [], [], [], [],
  )
  Each row is a point of the ROC curve: recall up, false-positive rate across (slide 12 of *Evaluating a classifier*).

  Which cut-off would you put in production, and why? #rule(7cm)
]

#v(5pt)

#panel("5 · Enter what each error costs")[
  The committee fixes the costs: granting a credit that goes *bad* costs 5,
  refusing a *good* one costs 1, a right decision costs 0.

  #step(1, "Set the cost matrix")[#dss("Design", "Metrics"): under threshold optimization, optimize for *Cost matrix gain*. Enter the costs as negative gains: bad predicted good #sym.arrow.r −5, good predicted bad #sym.arrow.r −1, both right decisions #sym.arrow.r 0. Train again.]
  #v(3pt)
  Threshold Dataiku now selects (#dss("Performance", "Confusion matrix")): #rule(2cm) #h(10pt)
  The rule from the slides gives 1 / (1 + 5) ≈ 0.17. Why might the two differ?
  #writing(1)
]

#v(5pt)

#panel("6 · Read the gains chart")[
  On the best model: #dss("Performance", "Lift charts"). If analysts can only
  review the 20% of applicants the model finds riskiest, what share of the bad
  credits will they see? #h(4pt) #rule(2.2cm)
]

#v(5pt)

#panel("7 · Replace one split by five folds")[
  #step(1, "Switch to cross-validation")[#dss("Design", "Train/Test set"): *K-fold cross-test*, 5 folds, stratified. Keep two algorithms: Logistic Regression and Random Forest. Train.]
  #v(3pt)
  #table(
    columns: (1.6fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [*algorithm*], [*ROC AUC*], [*±*],
    [Logistic Regression], [], [],
    [Random Forest], [], [],
  )
  Does the ± let you say one algorithm is better? What would you need to see?
  #writing(1)
]
