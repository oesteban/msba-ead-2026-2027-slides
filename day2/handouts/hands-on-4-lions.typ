// ---------------------------------------------------------------------------
// hands-on-4-lions.typ: the group's sheet for Hands-on 4, 23.10.2026 AM.
//
// One sheet per group of three, both sides. Page 1 is the data card. The core
// (steps 1 to 3, about 20 minutes) follows slide 14 of "Deep learning for
// decisions": the group loads the photos and reads their labels from the file
// names, trains an image classifier on a pretrained network with no retrained
// layers, scores the 57 test photos and looks at the errors. Below the
// checkpoint bar (slide 15) the group adds the cats, a third and larger class,
// reads the averages and decides.
//
// The data: lion-tiger-train.zip and lion-tiger-test.zip (web photos whose
// licences are unknown: handed out on the learning platform, never
// republished) and cats-train.zip and cats-test.zip (the cat class of Natural
// Images, Roy et al. 2018), built by ../../tools/build-datasets.py in the
// private wrapper.
//
// DSS screen paths drafted from the Dataiku DSS 13 documentation (Computer
// vision); AUTHORING.md F1: to be run on the course server and corrected before
// printing. Server: DSS 15.0.0. Verified on: DSS ____ , __.__.2026.
//
// Handed out, kept by the group, never collected: it carries no name.
//
//   typst compile --root ../.. hands-on-4-lions.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 4 · Day 2 / Morning · Group's sheet\nLion or tiger: what can 58 photos teach a borrowed network?",
  date: datetime(year: 2026, month: 10, day: 23),
)

*The case.* A firm wants its photos sorted into classes (products, defects,
species) but holds only a few dozen labelled examples of each. Training a
network from scratch would need far more. Can a network pretrained on ImageNet,
given a new head, tell a lion from a tiger after 58 photos, and how far can its
test score be trusted?

#v(4pt)

#block(width: 100%, inset: (x: 6pt, y: 5pt), radius: 2pt, stroke: 1pt + accent)[
  #lbl("Data card · lion-tiger-train.zip, lion-tiger-test.zip")
  #v(3pt)
  #grid(
    columns: (1fr, 1fr), column-gutter: 10pt,
    [
      *What a row is.* One photo, a JPEG file in a folder; the network reads
      its pixels and nothing else. 58 training photos and 57 test photos. The
      label is the word before the underscore of the file name:
      `lion_001.jpg`, `tiger_001.jpg`.

      *The target.* `label`, `lion` or `tiger`. Training: 30 lions and 28
      tigers. Test: 38 lions and 19 tigers, so always saying `lion` is right
      67% of the time, and one test photo is worth 1.75 points.

      *How the photos were chosen.* Taken from the web for a course exercise.
      No source, photographer or licence is recorded with them. They are not
      a sample of any population of photos.
    ],
    [
      *Its history.* The inherited test set held 65 photos, 8 of them
      byte-identical copies of training photos: they were removed. Two
      training photos carried the other animal's label: they were corrected.
      Every photo was renamed `<label>_<nnn>.jpg`, so that one rule reads all
      the labels.

      *Source and licence.* Lions and tigers: web photos, licences unknown,
      used in class and never republished. Cats, after the checkpoint: the
      cat class of Natural Images, P. Roy, S. Ghosh, S. Bhattacharya and
      U. Pal (2018), Effects of degradations on deep neural network
      architectures, arXiv:1807.10108; 120 training and 80 test photos of its
      885. The licence of its public copy is not verified.
    ],
  )
  #v(3pt)
  #set text(size: 7.5pt)
  #table(
    columns: (auto, auto, auto, auto, auto, 1fr), inset: (x: 3pt, y: 2.2pt), stroke: hair,
    [*archive*], [*photos*], [*lions*], [*tigers*], [*cats*], [*used in*],
    [`lion-tiger-train.zip`], [58], [30], [28], [], [the folder `train`, steps 1 and 2],
    [`lion-tiger-test.zip`], [57], [38], [19], [], [the folder `test`, step 3],
    [`cats-train.zip`], [120], [], [], [120], [`train`, panel 4],
    [`cats-test.zip`], [80], [], [], [80], [`test`, panel 4],
  )
]

#v(5pt)

#panel("Step 1 · Load the photos and their labels")[
  #step(1, "Upload the training photos")[On the Flow: #dss("+ Dataset", "Folder"), named `train`; upload the 58 photos unzipped from `lion-tiger-train.zip`.]
  #v(2pt)
  #step(2, "List the files")[#dss("+ Recipe", "List Contents") on the folder `train`: one row per photo, with its `path`.]
  Rows: #rule(1.6cm)
  #v(2pt)
  #step(3, "Read the label from the name")[On the listing: #dss("+ Recipe", "Prepare"), a step *Extract with regular expression* on `path`, pattern `([a-z]+)_[0-9]+`, output column `label`; *Run*.]
  Lions: #rule(1.4cm) #h(8pt) tigers: #rule(1.4cm)
]

#v(5pt)

#panel("Step 2 · Train on a borrowed network")[
  #step(1, "Create the analysis")[Select the labelled dataset, then #dss("Lab", "Image classification"): target `label`, the images in the folder `train`.]
  #v(2pt)
  #step(2, "Borrow, do not retrain")[#dss("Design", "Training"): pretrained model *EfficientNet B0*, *Number of retrained layers* 0. *Train*.]
  Training time: #rule(1.6cm)
  #v(2pt)
  #step(3, "Read its own test")[#dss("Results"): the confusion matrix, then a cell's photos in the image feed.]
  Accuracy: #rule(1.6cm) #h(8pt) on how many photos? #rule(1.6cm)
]

#v(5pt)

#panel("Step 3 · Score photos it has never seen")[
  #step(1, "Load the test photos")[A second folder `test` with the 57 photos of `lion-tiger-test.zip`; list and label them as in steps 1.2 and 1.3.]
  #v(2pt)
  #step(2, "Score them")[Deploy the model to the Flow, then #dss("+ Recipe", "Score") on the labelled test listing, with the deployed model.]
  #v(2pt)
  #step(3, "Count the errors")[On the scored dataset, a Prepare step *Formula* into `check`: `if(label == prediction, "right", "wrong")`.]
  Wrong: #rule(1.2cm) of 57 #h(8pt) accuracy: #rule(1.6cm) #h(8pt) lion-always baseline: 67%

  What do the wrong photos have in common? Is any of them wrongly labelled?
  #writing(1)
]

#v(6pt)

#checkpoint(
  msg: [Reached this line? Stop here: the debrief reads every group's test score, with its 1.75 points a photo.],
  note: [Panels 4 and 5 follow slide 15 of *Deep learning for decisions*.],
)

#v(6pt)

#panel("4 · Add a third, larger class: cats")[
  #step(1, "Upload the cats")[The 120 photos of `cats-train.zip` into `train`, the 80 of `cats-test.zip` into `test`; rebuild the listings and their Prepare recipes: the pattern reads `cat` too.]
  #v(2pt)
  #step(2, "Retrain")[In the same analysis, the same settings: *Train*. Three classes now.]
  #v(2pt)
  #table(
    columns: (1.4fr, 1fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [*class*], [*training photos*], [*test photos*], [*recall*],
    [lion], [30], [38], [],
    [tiger], [28], [19], [],
    [cat], [120], [80], [],
  )
  #step(3, "Read the averages")[#dss("Results", "Metrics"): the averaged scores.]
  Macro average: #rule(1.6cm) #h(8pt) weighted average: #rule(1.6cm)
]

#v(5pt)

#panel("5 · Decide")[
  Which score would you report for the three classes, the macro or the weighted average, and why? Which class would you check first in the image feed?
  #writing(2)
]
