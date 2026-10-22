// ---------------------------------------------------------------------------
// hands-on-3-wine.typ: the group's sheet for Hands-on 3, 16.10.2026 PM.
//
// One sheet per group of three, both sides. Page 1 is
// the data card. The core (panels 1 to 3, about 25 minutes) follows slide 13 of
// "Beyond binary classification": the group explores the wines, removes the
// copies, trains a multiclass model on the seven grades and reads it class by
// class. From panel 4 (slide 14, 15 minutes) the group regroups the
// grades into three lines, meets the leak, and decides what the winery deploys.
//
// The data: winequality_all.csv, the two UCI Wine Quality files (dataset 186,
// CC BY 4.0) joined with a `color` column, as copied by
// ../../tools/build-datasets.py in the private wrapper.
//
// DSS screen paths drafted from the DSS 13 documentation and D. Genoud's 2025
// run; AUTHORING.md F1: to be run on the course server and corrected before
// printing. Server: DSS 15.0.0. Verified on: DSS ____ , __.__.2026.
//
// Handed out, kept by the group, never collected: it carries no name.
//
//   typst compile --root ../.. hands-on-3-wine.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 3 · Day 1 / Afternoon · Group's sheet\nGrading wines: from seven grades to three lines",
  date: datetime(year: 2026, month: 10, day: 16),
)

*The case.* A winery sells its wines in three lines: low, medium and high.
Today each wine waits for a tasting panel before it is placed. The winery asks
whether its laboratory measurements could place a new wine first, and how far
such a model can be trusted, class by class.

#v(4pt)

#block(width: 100%, inset: (x: 6pt, y: 5pt), radius: 2pt, stroke: 1pt + accent)[
  #lbl("Data card · winequality_all.csv")
  #v(3pt)
  #grid(
    columns: (1fr, 1fr), column-gutter: 10pt,
    [
      *What a row is.* One sample of vinho verde, red or white, from northern
      Portugal, tested at the region's official certification body between
      May 2004 and February 2007. 6,497 rows, 13 columns, no missing values.

      *The target.* `quality`: the median of the scores of at least three
      blind tasters, from 0 (very bad) to 10 (excellent). Only grades 3 to 9
      occur, and 5 and 6 hold 77% of the wines.

      *How the rows were chosen.* Wines with a protected designation of
      origin, sent by their producers for certification. 4,898 are white,
      1,599 red. Only lab measurements are given: no grape, brand or price.
    ],
    [
      *Its history.* The authors modelled red and white apart, as a
      regression of the grade. The course file joins their two files and adds
      `color`. 1,177 rows (18%) are exact copies of another row; the paper
      does not mention them. Step 1 removes them.

      *Source and licence.* P. Cortez, A. Cerdeira, F. Almeida, T. Matos and
      J. Reis (2009), Modeling wine preferences by data mining from
      physicochemical properties, _Decision Support Systems_ 47(4):547 to 553.
      UCI Machine Learning Repository, dataset 186, doi:10.24432/C56S3T,
      CC BY 4.0.
    ],
  )
  #v(3pt)
  #set text(size: 7.5pt)
  #table(
    columns: (auto, 1fr, auto, 1fr), inset: (x: 3pt, y: 2.2pt), stroke: hair,
    [*column*], [*what it measures*], [*column*], [*what it measures*],
    [`fixed acidity`], [tartaric acid, g/dm³], [`total sulfur dioxide`], [mg/dm³, free and bound],
    [`volatile acidity`], [acetic acid, g/dm³], [`density`], [g/cm³],
    [`citric acid`], [g/dm³], [`pH`], [acidity on the pH scale],
    [`residual sugar`], [sugar left after fermentation, g/dm³], [`sulphates`], [potassium sulphate, g/dm³],
    [`chlorides`], [sodium chloride, g/dm³], [`alcohol`], [% of volume],
    [`free sulfur dioxide`], [mg/dm³], [`color`], [`red` or `white`],
    [`quality`], [*the target*: the grade, 0 to 10], [], [],
  )
]


#v(5pt)

#panel("Step 1 · Explore the wines, then remove the copies")[
  #step(1, "Load the data")[In a new project, on the Flow: #dss("+ Dataset", "Upload your files"), choose `winequality_all.csv`, then *Create*.]
  #v(2pt)
  #step(2, "Count the grades")[Open the dataset: #dss("Explore"), click the header of `quality`, then *Analyze*; the same for `color`.]
  Wines graded 3: #rule(1.2cm) #h(6pt) graded 9: #rule(1.2cm) #h(6pt) share of grade 6: #rule(1.4cm) #h(6pt) white wines: #rule(1.4cm)
  #v(2pt)
  #step(3, "Remove the copies")[Select the dataset, then #dss("+ Recipe", "Distinct"). Keep every column, *Create*, then *Run*.]
  Rows after *Distinct*: #rule(1.6cm) #h(10pt) copies removed: #rule(1.6cm)
]

#v(5pt)

#panel("Step 2 · Train on the seven grades")[
  #step(1, "Create the analysis")[Select the *distinct* dataset, then #dss("Lab", "AutoML Prediction"). Target `quality`. Keep *Quick prototypes*, then *Create*.]
  #v(2pt)
  #step(2, "Say that the grades are classes")[#dss("Design", "Target"): if Dataiku proposes *Regression* (the grades are numbers), set the prediction type to *Multiclass classification*.]
  #v(2pt)
  #step(3, "Use five folds, then train")[#dss("Design", "Train/Test set"): *K-fold cross-test*, 5 folds, stratified. Click *Train*.]
  #v(2pt)
  Metric #dss("Results") ranks by: #rule(2.6cm) #h(8pt) best model: #rule(2.8cm) #h(8pt) score and ±: #rule(2cm)
]

#v(5pt)

#panel("Step 3 · Read the model class by class")[
  #step(1, "The confusion matrix")[#dss("Results", "model", "Performance", "Confusion matrix"). Rows are actual grades, columns predicted ones.]
  Grades never predicted: #rule(2.4cm) #h(6pt) share of the 6s predicted 6: #rule(1.3cm) #h(6pt) of the 7s predicted 7: #rule(1.3cm)
  #v(2pt)
  #step(2, "One ROC curve per grade")[#dss("Performance", "ROC & PR curves"): choose the class 8.]
  AUC of grade 8: #rule(1.6cm) #h(8pt) How can a grade be ranked well and yet never be predicted?
  #writing(1)
]

#v(5pt)

#panel("4 · Three lines instead of seven grades")[
  #step(1, "Regroup the grades")[On the distinct dataset: #dss("+ Recipe", "Prepare"), add a *Formula* step with output column `grade`, then run the recipe:]
  #align(center)[`if(quality <= 5, "low", if(quality == 6, "medium", "high"))`]
  #v(2pt)
  #step(2, "Train on the lines")[On the prepared dataset: a new #dss("Lab", "AutoML Prediction"), target `grade`, the settings of Step 2. *Train*.]
  Best score: #rule(1.6cm) #h(6pt) All at 1.000? #dss("Design", "Features handling"): which column gives `grade` away? #rule(2.2cm)
  #v(2pt)
  #step(3, "Remove the leak")[Reject that column, and *Train* again.]
  Best score now, and its ±: #rule(2.4cm)
]

#v(5pt)

#panel("5 · Decide for the winery")[
  #step(1, "Put the two models side by side")[Step 2 predicts seven grades, panel 4 three lines. For the best model of each: #dss("Performance", "Detailed metrics"), and #dss("Confusion matrix") for the last row.]
  #v(2pt)
  #table(
    columns: (2.3fr, 1fr, 1fr), inset: 3.5pt, stroke: hair,
    [], [*Seven grades* (Step 2)], [*Three lines* (panel 4)],
    [*Accuracy*: wines in the right class (slide 6: micro)], [], [],
    [*F1*: one per class, averaged by Dataiku], [], [],
    [*Top wines found*: % of actual 8s (highs) predicted 8 (high)], [], [],
  )
  #v(2pt)
  #step(2, "Find how Dataiku averages the F1")[#dss("Design", "Metrics"). Weighted by class size, grades 5 and 6 (three wines in four) decide the average; unweighted, grade 8 counts as much as grade 6.]
  #tick #h(2pt) weighted by class size (slide 6: weighted) #h(14pt) #tick #h(2pt) every class the same (slide 6: macro)
  #v(2pt)
  #step(3, "Decide")[The winery wants each new wine placed in a line before the tasting panel. Which model would it deploy, and which number of the table should it watch? Why that one?]
  #writing(2)
  #v(3pt)
  #text(size: 8pt)[
    *If time allows.* (a) Merge only the rare grades, 3 into 4 and 9 into 8: Formula `if(quality == 3, 4, if(quality == 9, 8, quality))`, Multiclass again, `quality` rejected. Does the F1 rise? \
    (b) #dss("Design", "Train/Test set"), *Sampling method*: *Class rebalance*, train again. The rare grades' recall, and accuracy? Does the score still describe the wines the winery makes?
  ]
]
