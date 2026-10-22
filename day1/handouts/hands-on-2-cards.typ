// ---------------------------------------------------------------------------
// hands-on-2-cards.typ: the group's sheet for Hands-on 2, 16.10.2026 PM.
//
// One sheet per group of three, both sides. Page 1 is the data card. The core
// (steps 1 to 3, about 40 minutes) follows slide 25 of "Model selection and cross-validation": the group
// explores the card clients, trains three algorithms on five folds before the
// break, lets them train on through it, and compares their scores and their ±.
// From panel 4 (slide 26) the group checks whether the folds
// overlap, asks which columns lead, and decides; the group gives its choice at
// the debrief, 15:00.
//
// The data: credit_card_default.csv, UCI dataset 350 (Yeh and Lien 2009, CC BY
// 4.0) with English names and labels, built by ../../tools/build-datasets.py in
// the private wrapper; its numbers are those of credit_card_default.yaml there.
//
// DSS screen paths drafted from the Dataiku documentation and the paths of
// sheets 1 and 3; AUTHORING.md F1: to be run on the course server and corrected
// before printing. Server: DSS 15.0.0. Verified on: DSS ____ , __.__.2026.
//
// Handed out, kept by the group, never collected: it carries no name.
//
//   typst compile --root ../.. hands-on-2-cards.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 2\nWhich algorithm for card defaults?",
  date: datetime(year: 2026, month: 10, day: 16),
)

*The case.* A card issuer wants to flag, each month, the clients likely to miss
next month's payment, so that its team calls them first. Three algorithms could
score them. Which one should it use, and is its lead real or luck of the folds?

#v(4pt)


#block(width: 100%, inset: (x: 6pt, y: 5pt), radius: 2pt, stroke: 1pt + accent)[
  #lbl("Data card · credit_card_default.csv")
  #v(3pt)
  #grid(
    columns: (1fr, 1fr), column-gutter: 10pt,
    [
      *What a row is.* One credit-card client in Taiwan, with the credit
      granted, four facts about the client, and for each month from April to
      September 2005 the repayment status, the bill and the amount paid.
      30,000 rows, 24 columns, no missing values.

      *The target.* `default_next_month`: whether the client defaulted on the
      next payment (`default`) or not (`paid`). 6,636 clients defaulted: 22.1%.

      *How the rows were chosen.* The UCI record does not say how the clients
      were selected, nor whether they come from one bank. All are in Taiwan.
    ],
    [
      *Its history.* Collected for a study comparing six data mining methods
      on how well they estimate the probability of default. The course file
      gives English names, the month in each. Codes UCI does not document:
      education 0, 5, 6 and marriage 0 read `unknown`; status −2 and 0 stay
      numbers. 35 rows are exact copies of another; they are kept.

      *Source and licence.* I.-C. Yeh and C.-H. Lien (2009), The comparisons
      of data mining techniques for the predictive accuracy of probability of
      default of credit card clients, _Expert Systems with Applications_
      36(2):2473 to 2480. UCI Machine Learning Repository, dataset 350,
      doi:10.24432/C55S3H, CC BY 4.0.
    ],
  )
  #v(3pt)
  #set text(size: 7.5pt)
  #table(
    columns: (auto, 1fr, auto, 1fr), inset: (x: 3pt, y: 2.2pt), stroke: hair,
    [*column*], [*what it records*], [*column*], [*what it records*],
    [`credit_limit`], [credit granted, with family cards, NT dollars], [`pay_status_sep` … `_apr`], [status each month: −1 paid duly, 1 to 9 months late; −2, 0 undocumented],
    [`sex`], [`male` or `female`: a protected attribute], [`bill_sep` … `bill_apr`], [bill statement each month, NT dollars; negative when in credit],
    [`education`], [graduate school, university, high school, others, unknown], [`paid_sep` … `paid_apr`], [amount paid each month, NT dollars],
    [`marriage`], [married, single, others, unknown], [`default_next_month`], [*the target*: `default` or `paid`],
    [`age`], [years], [], [],
  )
]


#v(5pt)

#panel("Step 1 · Explore the clients")[
  #step(1, "Load the data")[In a new project, on the Flow: #dss("+ Dataset", "Upload your files"), choose `credit_card_default.csv`, then *Create*.]
  #v(2pt)
  #step(2, "Count the defaults")[Open the dataset: #dss("Explore"), click the header of `default_next_month`, then *Analyze*.]
  Rows: #rule(1.6cm) #h(8pt) clients who defaulted: #rule(1.6cm) #h(8pt) share of `default`: #rule(1.4cm)
  #v(2pt)
  #step(3, "Read the types")[Under each column header, #dss("Explore") shows what Dataiku made of it: a number, or text?]
  `pay_status_sep`: #rule(2cm) #h(8pt) `education`: #rule(2cm) #h(8pt) `sex`: #rule(2cm)
  #v(1pt)
  As a number, `pay_status_sep` puts −2 and 0, which no one has documented, in an order below 1 month of delay. As a category, it assumes no order. Which would you keep, and why?
  #writing(1)
]

#v(5pt)

#panel("Step 2 · Train three algorithms on five folds")[
  #step(1, "Create the analysis")[Select the dataset, then #dss("Lab", "AutoML Prediction"). Target `default_next_month`. Keep *Quick prototypes*, then *Create*.]
  Which value does Dataiku treat as *positive*? #rule(2.4cm)
  #v(2pt)
  #step(2, "Use five folds")[#dss("Design", "Train/Test set"): *K-fold cross-test*, 5 folds, stratified.]
  #v(2pt)
  #step(3, "Keep three algorithms, then train")[#dss("Design", "Algorithms"): Logistic Regression, Random Forest and XGBoost only; the SVM stays off, its training time grows fast with 30,000 rows. Click *Train* before 14:45: the models train on through the break.]
]

#v(5pt)

#panel("Step 3 · Compare the scores and their ±")[
  #step(1, "Read the results")[#dss("Results"): each model's ROC AUC and its ±, the spread over the five folds.]
  #v(2pt)
  #table(
    columns: (1.6fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [*algorithm*], [*ROC AUC*], [*±*],
    [Logistic Regression], [], [],
    [Random Forest], [], [],
    [XGBoost], [], [],
  )
  Is the best one's lead over the second larger than their ±? Your choice for now, in one sentence:
  #writing(1)
]

#v(5pt)

#panel("4 · Do the folds overlap?")[
  #step(1, "One curve per fold")[On each of the two best models: #dss("Performance", "ROC & PR curves"), one curve per fold.]
  Do the two models' curves overlap? #rule(3cm) #h(8pt) Is the best one better on every fold? #rule(3cm)
]

#v(5pt)

#panel("5 · Ask which columns lead")[
  #step(1, "Feature importance")[On the best model: #dss("Explainability", "Feature importance").]
  The first three: #rule(8cm)
  #v(1pt)
  Would a credit officer accept them as reasons to call a client? Is `sex` among the first ten, and should a model use it at all?
  #writing(1)
]

#v(5pt)

#panel("6 · Decide")[
  The model you would deploy: #rule(3.4cm) #h(8pt) its ROC AUC and ±: #rule(3cm)

  Why this one: its score and ±, and how well it explains itself.
  #writing(2)
]
