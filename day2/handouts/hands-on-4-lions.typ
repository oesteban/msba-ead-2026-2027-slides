// ---------------------------------------------------------------------------
// hands-on-4-lions.typ: the group's sheet for Hands-on 4, 23.10.2026 AM.
//
// One sheet per group of three, both sides. Page 1 is the data card. The core
// (steps 1 to 3, about 25 minutes) follows slide 53 of "Deep learning for
// decisions", and the Flow it builds is drawn on slide 52: the group loads the
// photos and reads their labels from the file names, trains a new head on a
// pretrained network (zero fine-tuned layers), follows its training, scores the
// 57 test photos and counts the errors. Below the checkpoint bar (slide 54)
// the group fine-tunes two layers and compares, adds the cats, a third and
// larger class, then decides. The flow follows the previous teacher's 2025 lab.
//
// The data: lion-tiger-train.zip and lion-tiger-test.zip (web photos whose
// licences are unknown: handed out on the learning platform, never
// republished) and cats-train.zip and cats-test.zip (the cat class of Natural
// Images, Roy et al. 2018), built by ../../tools/build-datasets.py in the
// private wrapper.
//
// DSS screen paths drafted from the Dataiku DSS 13 documentation (Computer
// vision) and the previous teacher's 2025 captures of the course server, which
// label the setting "Number of fine-tuned layers" (the DSS 13 documentation
// says "Number of retrained layers"). AUTHORING.md F1: to be run on the course
// server and corrected before printing. Server: DSS 15.0.0. Verified on:
// DSS ____ , __.__.2026.
//
// Handed out, kept by the group, never collected: it carries no name.
//
//   typst compile --root ../.. hands-on-4-lions.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 4 · Day 2 / Morning · Group's sheet\nLion or tiger: what can 58 photos teach a pretrained network?",
  date: datetime(year: 2026, month: 10, day: 23),
)

*The case.* A firm wants its photos sorted into classes (products, defects,
species) but holds only a few dozen labelled examples of each. Three questions:
can it use a network already trained on ImageNet, training only a new head?
Can it follow how that training goes? And how far can the test score be
trusted?

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
    [`cats-train.zip`], [120], [], [], [120], [`train`, panel 5],
    [`cats-test.zip`], [80], [], [], [80], [`test`, panel 5],
  )
]

#v(5pt)

#panel("Step 1 · Load the photos and their labels")[
  #step(1, "Upload the training photos")[In a new project, on the Flow: #dss("+ Dataset", "Folder"), named `train`; upload the 58 photos unzipped from `lion-tiger-train.zip`.]
  #v(2pt)
  #step(2, "List the files")[On the folder `train`: #dss("+ Recipe", "List Contents"), *Run*. One row per photo, with its `path`.]
  Rows: #rule(1.6cm)
  #v(2pt)
  #step(3, "Read the label from the name")[On the listing: #dss("+ Recipe", "Prepare"), a step *Extract with regular expression* on `path`, pattern `([a-z]+)_[0-9]+`, output column `label`; *Run*.]
  Lions: #rule(1.4cm) #h(8pt) tigers: #rule(1.4cm)
]

#v(5pt)

#panel("Step 2 · Train a new head on a pretrained network")[
  #step(1, "Create the analysis")[Select the labelled dataset, then #dss("Lab", "Image classification"): target `label`, the images in the folder `train`.]
  #v(2pt)
  #step(2, "Reuse it, do not fine-tune")[#dss("Design", "Train/Test set"): *Split the dataset*, train ratio 0.8. #dss("Design", "Training"): pretrained model *EfficientNet B0*, *Number of fine-tuned layers* 0; leave the epochs at their default. *Train*.]
  Training time: #rule(1.6cm) #h(8pt) epochs run: #rule(1.2cm)
  #v(2pt)
  #step(3, "Follow the training, then read its own test")[#dss("Results"): the training curve, if shown, then the confusion matrix; click a cell to see its photos in the image feed.]
  Accuracy: #rule(1.6cm) #h(8pt) on how many photos? #rule(1.6cm)
]

#v(5pt)

#panel("Step 3 · Score photos it has never seen")[
  #step(1, "Load the test photos")[A second folder `test` with the 57 photos of `lion-tiger-test.zip`; list and label them as in steps 1.2 and 1.3.]
  #v(2pt)
  #step(2, "Score them")[In the analysis: #dss("Deploy"), model name `model_lions`. Then on the labelled test listing: #dss("+ Recipe", "Score"), with that model and the managed folder `test`; *Run*.]
  #v(2pt)
  #step(3, "Count the errors")[On the scored dataset, a Prepare step *Formula* into `check`: `if(label == prediction, "right", "wrong")`.]
  Wrong: #rule(1.2cm) of 57 #h(8pt) accuracy: #rule(1.6cm) #h(8pt) lion-always baseline: 67%

  What do the wrong photos have in common? Is any of them wrongly labelled?
  #writing(1)
]

#v(6pt)

#checkpoint(
  msg: [Reached this line? Stop here: the debrief reads every group's test score, with its 1.75 points a photo.],
  note: [Panels 4 to 6 follow slide 54 of *Deep learning for decisions*.],
)

#v(6pt)

#panel("4 · Fine-tune two layers, and compare")[
  #step(1, "Unlock two layers")[In the same analysis: #dss("Design", "Training"), *Number of fine-tuned layers* 2, the rest unchanged. *Train*.]
  #v(2pt)
  #table(
    columns: (1.6fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [*fine-tuned layers*], [*training time*], [*accuracy in Results*],
    [0 (step 2)], [], [],
    [2], [], [],
  )
  Both accuracies come from Dataiku's own test split: how many photos is that, and what is one photo worth?
  #rule(4cm)
]

#v(5pt)

#panel("5 · Add a third, larger class: cats")[
  #step(1, "Upload the cats")[The 120 photos of `cats-train.zip` into `train`, the 80 of `cats-test.zip` into `test`; rebuild the listings and their Prepare recipes: the pattern reads `cat` too.]
  #v(2pt)
  #step(2, "Retrain")[In the same analysis, 0 fine-tuned layers: *Train*. Three classes now.]
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

#panel("6 · Decide")[
  Which model would the firm deploy, with 0 or 2 fine-tuned layers, and why? For the three classes, which score would you report, the macro or the weighted average?
  #writing(2)
]
