// ---------------------------------------------------------------------------
// hands-on-5-reviews.typ: the group's sheet for Hands-on 5, 23.10.2026 AM.
//
// One sheet per group of three, both sides. Page 1 is the data card. The core
// (steps 1 to 3, about 25 minutes) follows slide 32 of "Text mining and
// sentiment analysis", and the Flow it builds is drawn on slide 31: the group
// simplifies the IMDb reviews and checks what happens to "not", trains a
// logistic regression on TF-IDF with five folds grouped by film, reads it at
// the care team's threshold of 0.2 and reads its heaviest terms. Below the
// checkpoint bar (slide 33) the group scores Pang and Lee's reviews with its
// model and with Dataiku's sentiment plugin, counts each one's errors at the
// same costs, then decides. The flow follows the previous teacher's 2025 lab.
//
// The data: imdb-reviews.csv (a subset of Maas et al. 2011) and
// polarity-reviews.csv (Pang and Lee 2004, polarity dataset v2.0), whose
// licences are not recorded: handed out on the learning platform, never
// republished. Built by 2026-2027/tools/build-datasets.py in the private
// wrapper.
//
// DSS screen paths drafted from the Dataiku DSS 13 documentation (Text
// variables, Sentiment analysis) and the previous teacher's 2025 captures of
// the course server. AUTHORING.md F1: to be run on the course server and
// corrected before printing, in particular whether Simplify text keeps "not",
// whether DSS takes 1 as the positive class, where the K-fold group column is
// set, and the plugin's output column. Server: DSS 15.0.0. Verified on:
// DSS ____ , __.__.2026.
//
// Handed out, kept by the group, never collected: it carries no name.
//
//   typst compile --root ../.. hands-on-5-reviews.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 5 · Day 2 / Morning · Group's sheet\nWhich reviews should the care team read first?",
  date: datetime(year: 2026, month: 10, day: 23),
)

*The case.* A streaming service receives more reviews than its care team can
read. The team wants the unhappy ones first: missing an unhappy review costs it
four times as much as reading a happy one by mistake. Can a model trained on
2,000 labelled reviews pick the reviews to read? And would Dataiku's ready-made
sentiment plugin do as well, on 2,000 reviews from another source?

#v(4pt)

#block(width: 100%, inset: (x: 6pt, y: 5pt), radius: 2pt, stroke: 1pt + accent)[
  #lbl("Data card · imdb-reviews.csv")
  #v(3pt)
  #grid(
    columns: (1fr, 1fr), column-gutter: 10pt,
    [
      *What a row is.* One review of one film, written by an IMDb user. 2,000
      rows, 3 columns, no missing value: `Text`, the review; `URL`, the film's
      IMDb page; `unhappy`, the target. The median review has 177 words, the
      shortest 14, the longest 1,827.

      *The target.* `unhappy`: 1 for a negative review (1,000 rows), 0 for a
      positive one (1,000), so always guessing one class is right half the
      time.

      *How the rows were chosen.* A subset of the 50,000 labelled reviews of
      Maas et al., who kept only clear verdicts (4 or less out of 10 for a
      negative review, 7 or more for a positive one) and at most 30 reviews a
      film. Here 1,247 films, up to 7 reviews each: 1,225 reviews share their
      film with another.
    ],
    [
      *Its history.* The inherited copy repeated the opening sentence at the
      end of 1,988 texts, 168 of those copies followed by a cut HTML tag `<br`:
      both removed. 161 texts stated a rating ("8/10", "9 out of 10"), which
      gives the label away: stripped. The labels `POS` and `NEG` became
      `unhappy`; the column `Index`, not a row key, was dropped.

      *Source and licence.* A. L. Maas, R. E. Daly, P. T. Pham, D. Huang,
      A. Y. Ng and C. Potts (2011), Learning word vectors for sentiment
      analysis, ACL-HLT 2011, 142 to 150. No licence is recorded for the
      texts: used in class, never republished. After the checkpoint:
      B. Pang and L. Lee (2004), polarity dataset v2.0, reviews from before
      2002, already in lower case; 60 of them stated a rating, stripped.
    ],
  )
  #v(3pt)
  #set text(size: 7.5pt)
  #table(
    columns: (auto, auto, auto, auto, 1fr), inset: (x: 3pt, y: 2.2pt), stroke: hair,
    [*file*], [*reviews*], [*unhappy*], [*columns*], [*used in*],
    [`imdb-reviews.csv`], [2,000], [1,000], [`URL`, `Text`, `unhappy`], [steps 1 to 3],
    [`polarity-reviews.csv`], [2,000], [1,000], [`filename`, `Text`, `unhappy`], [panel 4],
  )
]

#v(5pt)

#panel("Step 1 · Prepare the reviews")[
  #step(1, "Upload the reviews")[In a new project: #dss("+ Dataset", "Upload your files"), `imdb-reviews.csv`.]
  Rows: #rule(1.6cm) #h(8pt) unhappy: #rule(1.6cm)
  #v(2pt)
  #step(2, "Simplify the text")[On the dataset: #dss("+ Recipe", "Prepare"), a step *Simplify text* on `Text`, output column `TextSimple`, with *Normalize text*, *Stem words* and *Clear stop words*, language English; *Run*.]
  #v(2pt)
  #step(3, "Check what happens to \"not\"")[In the Prepare preview, find a review whose `Text` holds "not" and compare it with its `TextSimple`.]
  Is "not" still there? #rule(1.4cm) #h(8pt) If not, what did you change? #rule(3.6cm)
]

#v(5pt)

#panel("Step 2 · Train a model on the words")[
  #step(1, "Create the analysis")[Select the prepared dataset, then #dss("Lab", "AutoML prediction"): target `unhappy`, two classes.]
  #v(2pt)
  #step(2, "Read only the simplified text")[#dss("Design", "Features handling"): `Text` and `URL` rejected; `TextSimple` as text, *Text handling* *TF/IDF vectorization*, min. rows fraction 0.1%, max. rows fraction 80%, n-grams 1 to 2.]
  #v(2pt)
  #step(3, "Keep each film in one fold")[#dss("Design", "Train/Test set"): *K-fold cross-test*, 5 folds, grouped by `URL`. #dss("Design", "Algorithms"): *Logistic regression* only. *Train*.]
  Training time: #rule(1.6cm)
]

#v(5pt)

#panel("Step 3 · Read it at the care team's costs")[
  #step(1, "Read the score and its spread")[#dss("Results", "Performance"): the ROC AUC and its spread across the 5 folds.]
  AUC: #rule(1.4cm) ± #rule(1.2cm)
  #v(2pt)
  #step(2, "Set the threshold the costs give")[On the confusion matrix, move the threshold to 0.2; read the four cells, then the same at 0.5.]
  #table(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1.6fr), inset: 4pt, stroke: hair,
    [*threshold*], [*TP*], [*FP*], [*FN*], [*TN*], [*cost 4 × FN + FP*],
    [0.2], [], [], [], [], [],
    [0.5], [], [], [], [], [],
  )
  #step(3, "Read the heaviest terms")[#dss("Results", "model", "Regression coefficients"): the terms with the largest weights, each way.]
  Towards unhappy: #rule(4.6cm) #h(6pt) towards happy: #rule(4.6cm)

  Are they opinions, or the names of films and actors?
  #writing(1)
]

#v(6pt)

#checkpoint(
  msg: [Reached this line? Stop here: the debrief reads every group's cost at 0.2 and its heaviest terms.],
  note: [Panels 4 and 5 follow slide 33 of *Text mining and sentiment analysis*.],
)

#v(6pt)

#panel("4 · Score new reviews with your model and with the plugin")[
  #step(1, "Prepare the new reviews alike")[Upload `polarity-reviews.csv`; copy the Prepare recipe of step 1 onto it, so that it gets its own `TextSimple`; *Run*.]
  #v(2pt)
  #step(2, "Score them with your model")[In the analysis: #dss("Deploy"). On the prepared polarity reviews: #dss("+ Recipe", "Score") with that model, then *Run*. Is the threshold applied 0.2? #rule(1.4cm)]
  #v(2pt)
  #step(3, "Score them with the plugin")[On `polarity-reviews.csv`, the raw `Text`: #dss("+ Recipe", "Plugins", "Sentiment Analysis"), then *Run*.]
  #v(2pt)
  #step(4, "Count each one's errors")[On each scored dataset, a Prepare step *Formula* into `cell`, such as `if(prediction == 1, if(unhappy == 1, "TP", "FP"), if(unhappy == 1, "FN", "TN"))`, with the plugin's own output column for its rows; then count the values of `cell`.]
  #table(
    columns: (1.6fr, 1fr, 1fr, 1fr, 1fr, 1.6fr), inset: 4pt, stroke: hair,
    [*scorer*], [*TP*], [*FP*], [*FN*], [*TN*], [*cost 4 × FN + FP*],
    [your model], [], [], [], [], [],
    [the plugin], [], [], [], [], [],
  )
]

#v(5pt)

#panel("5 · Decide")[
  Which scorer would you give the care team, your model or the plugin, and why? What would you measure first on the team's own reviews before it goes live?
  #writing(2)
]
