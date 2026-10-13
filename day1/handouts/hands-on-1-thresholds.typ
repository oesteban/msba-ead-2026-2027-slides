// ---------------------------------------------------------------------------
// hands-on-1-thresholds.typ: the pair's sheet for Hands-on 1, 16.10.2026 AM.
//
// One A4 sheet per pair, both sides. The core (steps 1 to 3, about 30 minutes,
// block 1) trains a model on german_credit and watches the threshold move
// precision and recall. Below the checkpoint bar (block 2, about 25 minutes)
// the pair enters the cost matrix, switches to 5-fold and reads the gains chart.
//
// The answers the pair records come from Dataiku DSS, not from this sheet: the
// deck's figures were computed with scikit-learn and will differ slightly.
//
// DSS screen paths drafted from the 2025-26 screenshots (DSS 13) and the
// Dataiku documentation; AUTHORING.md F1: to be run on the course server and
// corrected before printing. Verified on: DSS ____ , __.__.2026.
//
// Handed out, kept by the pair, never collected: it carries no name. Committed
// BLANK all the same, as every instrument here.
//
//   typst compile --root ../.. hands-on-1-thresholds.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 1 · Day 1 / Morning · Pair's sheet\nWatching the threshold, then choosing it",
  date: datetime(year: 2026, month: 10, day: 16),
)

#let cell(w: 1fr) = box(width: 100%, height: 13pt, stroke: (bottom: 0.5pt + luma(140)))

*The case.* A bank grants consumer loans. Its data science team has 1,000
past applicants in `german_credit.csv`: 22 columns describing each applicant,
and a column `Score` saying whether the loan was repaid (`good`, 700) or not
(`bad`, 300). The risk committee wants to see what a model would decide
before it approves one.

#v(4pt)

#panel("Step 1 · Train a first model")[
  #step(1, "Load the data")[In your project: #dss("+ Dataset", "Upload your files"), choose `german_credit.csv`, create the dataset.]
  #v(2pt)
  #step(2, "Create the analysis")[Select the dataset, then #dss("Lab", "AutoML prediction"). Target `Score`. Keep *Quick prototypes*, create.]
  #v(2pt)
  #step(3, "Drop the identifier")[#dss("Design", "Features handling"): set `row ID` to *Reject*. An identifier describes nobody.]
  #v(2pt)
  #step(4, "Train")[Keep the default split and algorithms. Click *Train*, wait for the models to finish.]
]

#v(5pt)

#panel("Step 2 · Name the positive class, then read the matrix")[
  #step(1, "Open the best model")[#dss("Results"), click the model with the highest score, then #dss("Performance", "Confusion matrix").]
  #v(3pt)
  Which value of `Score` does Dataiku treat as *positive*? Read it from the
  row and column labels of the confusion matrix. #h(4pt) #rule(4cm)

  #v(4pt)
  At the threshold Dataiku shows by default (#rule(1.2cm)), record the four cells:

  #v(2pt)
  #table(
    columns: (1.6fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [], [*predicted bad*], [*predicted good*],
    [*actually bad*], [TP #rule(1.3cm)], [FN #rule(1.3cm)],
    [*actually good*], [FP #rule(1.3cm)], [TN #rule(1.3cm)],
  )
  Precision = TP / (TP + FP) = #rule(2cm) #h(12pt) Recall = TP / (TP + FN) = #rule(2cm)
]

#v(5pt)

#panel("Step 3 · Move the threshold")[
  Drag the *threshold* slider above the confusion matrix and record what the
  same screen shows:

  #v(2pt)
  #table(
    columns: (1fr, 1fr, 1fr, 1.4fr, 1.4fr), inset: 4pt, stroke: hair,
    [*threshold*], [*precision*], [*recall*], [*good applicants refused (FP)*], [*bad applicants granted (FN)*],
    [0.3], [], [], [], [],
    [0.5], [], [], [], [],
    [0.7], [], [], [], [],
  )
  #v(2pt)
  Lowering the threshold refuses more applicants. In the table, which of the
  two errors grows, and which shrinks?
  #writing(1)
]

#v(6pt)

#checkpoint(
  msg: [Reached this line? Stop here and wait for the costs.],
  note: [The rest is for block 2, after the slides on costs, ROC and k-fold.],
)

#v(6pt)

#panel("4 · Enter what each error costs")[
  The committee fixes the costs: granting a loan to a *bad* applicant costs 5,
  refusing a *good* applicant costs 1, a right decision costs 0.

  #step(1, "Set the cost matrix")[#dss("Design", "Metrics"): under threshold optimization, optimize for *Cost matrix gain*. Enter the costs as negative gains: bad predicted good #sym.arrow.r −5, good predicted bad #sym.arrow.r −1, both right decisions #sym.arrow.r 0. Train again.]
  #v(3pt)
  Threshold Dataiku now selects (#dss("Performance", "Confusion matrix")): #rule(2cm) #h(10pt)
  The rule from the slides gives 1 / (1 + 5) ≈ 0.17. Why might the two differ?
  #writing(1)
]

#v(5pt)

#panel("5 · Replace one split by five folds")[
  #step(1, "Switch to k-fold")[#dss("Design", "Train/Test set"): *K-fold cross-test*, 5 folds, stratified. Keep two algorithms: Logistic Regression and Random Forest. Train.]
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

#v(5pt)

#panel("6 · Read the gains chart")[
  On the best model: #dss("Performance", "Lift charts"). If analysts can only
  review the 20% of applicants the model finds riskiest, what share of the bad
  applicants will they see? #h(4pt) #rule(2.2cm)
]
