// ---------------------------------------------------------------------------
// hands-on-4-lions.typ: the group's sheet for Hands-on 4, 23.10.2026 AM.
//
// One sheet per group of three, both sides. Page 1 is the data card. The core
// (steps 1 to 3, about 25 minutes) builds the Flow of slide 51 of "Deep
// learning", a capture of Oscar's: the group uploads the four archives into
// one folder, lists the files, reads each photo's label from its file name and
// its archive from its subfolder, splits the listing by archive, trains a new
// head on a pretrained network (zero fine-tuned layers), follows its training,
// scores the 56 test photos and counts the errors. From panel 4
// the group fine-tunes two layers and rescores, stacks the cats in
// as a third and larger class, then decides. The Flow is Oscar's, built on the
// course server on 22.10.2026.
//
// The data: lion-tiger-train.zip and lion-tiger-test.zip (web photos whose
// licences are unknown: handed out on the learning platform, never
// republished) and cats-train.zip and cats-test.zip (the cat class of Natural
// Images, Roy et al. 2018), built by ../../tools/build-datasets.py in the
// private wrapper.
//
// AUTHORING.md F1: steps 1 to 3 and panel 4 run by Oscar on the course server,
// whose Design → Training screen reads "Lighter / Faster (EfficientNet B0)" and
// "Number of fine-tuned layers" (defaults: 50 epochs, early stopping, patience
// 5). Panel 5's Stack recipes are on Oscar's Flow of 23.10.2026; still to
// run: its three-class analysis; to confirm: the Flow's add button (+ Dataset
// or + Add Item), the decompress button's label, the Deploy dialog's update
// option. Server: DSS 15.0.0.
// Verified on: DSS 15.0.0, 22.10.2026, except panel 5.
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
      its pixels and nothing else. 58 training photos and 56 test photos. The
      label is the word before the underscore of the file name:
      `lion_001.jpg`, `tiger_001.jpg`.

      *The target.* `label`, `lion` or `tiger`. Training: 30 lions and 28
      tigers. Test: 38 lions and 18 tigers, so always saying `lion` is right
      68% of the time, and one test photo is worth 1.79 points.

      *How the photos were chosen.* Taken from the web for a course exercise.
      No source, photographer or licence is recorded with them. They are not
      a sample of any population of photos.
    ],
    [
      *Its history.* The inherited test set held 65 photos, 8 of them
      byte-identical copies of training photos: they were removed, and one
      more was withdrawn. Two
      training photos carried the other animal's label: they were corrected.
      Every photo was renamed `<label>_<nnn>.jpg`, so that one rule reads all
      the labels.

      *Source and licence.* Lions and tigers: web photos, licences unknown,
      used in class and never republished. Cats, in panel 5: the
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
    [*archive*], [*photos*], [*lions*], [*tigers*], [*cats*], [*dataset after step 1, used in*],
    [`lion-tiger-train.zip`], [58], [30], [28], [], [`lion-tiger-train`, step 2],
    [`lion-tiger-test.zip`], [56], [38], [18], [], [`lion-tiger-test`, step 3],
    [`cats-train.zip`], [120], [], [], [120], [`cats-train`, panel 5],
    [`cats-test.zip`], [80], [], [], [80], [`cats-test`, panel 5],
  )
]

#v(5pt)

#panel("Step 1 · Load the photos and their labels")[
  #step(1, "Upload the four archives into one folder")[In a new project, on the Flow: #dss("+ Dataset", "Folder"), the one under *Dataiku Managed* (not *Files in Folder*), named `dataset`. Open it, upload the four zips as they are, and decompress each where Dataiku offers it: one subfolder per archive.]
  #v(2pt)
  #step(2, "List the files")[Back on the Flow, click the folder `dataset` once; in the right panel, *List Contents*, output `paths`; *Run*. One row per photo of every subfolder, with its `path` and its `basename` (the file name).]
  Rows: #rule(1.6cm)
  #v(2pt)
  #step(3, "Read the label and the archive")[On `paths`: *Prepare*, output `labels`, a step *Extract with regular expression* on `basename`, pattern `^([a-z]+)_[0-9]+`, output column `label`; *Run*. On `labels`: *Prepare*, output `sets`, the same step on `path`, pattern `([a-z-]+)/[^/]+$` (the subfolder), output column `set`; *Run*.]
  #v(2pt)
  #step(4, "One dataset per archive")[On `sets`: *Split*, *Map values of a single column* on `set`, four outputs named as its values: `lion-tiger-train`, `lion-tiger-test`, `cats-train`, `cats-test`; *Run*.]
  In `lion-tiger-train`, lions: #rule(1.4cm) #h(8pt) tigers: #rule(1.4cm)
]

#v(5pt)

#panel("Step 2 · Train a new head on a pretrained network")[
  #step(1, "Create the analysis")[Select `lion-tiger-train`, then #dss("Lab", "Image classification"): target `label`, the images at `path` in the folder `dataset`.]
  #v(2pt)
  #step(2, "Reuse it, do not fine-tune")[#dss("Design", "Train/Test set"): *Split the dataset*, train ratio 0.8. #dss("Design", "Training"): *Pretrained model* *Lighter / Faster (EfficientNet B0)*, *Number of fine-tuned layers* 0; the rest at its default (50 epochs, early stopping). *Train*.]
  Training time: #rule(1.6cm) #h(8pt) epochs run: #rule(1.2cm)
  #v(2pt)
  #step(3, "Follow the training, then read its own test")[#dss("Results"): the training curve, if shown, then the confusion matrix; click a cell to see its photos in the image feed.]
  Accuracy: #rule(1.6cm) #h(8pt) on how many photos? #rule(1.6cm)
]

#v(5pt)

#panel("Step 3 · Score photos it has never seen")[
  #step(1, "Deploy the model")[In the analysis, on the model: #dss("Deploy"), model name `model_lions_tigers`. It appears on the Flow.]
  #v(2pt)
  #step(2, "Score them")[Click `lion-tiger-test` once; in the right panel, *Score*, with the model `model_lions_tigers` and the folder `dataset`, output `lion-tiger-test_scored`; *Run*.]
  #v(2pt)
  #step(3, "Count the errors")[On `lion-tiger-test_scored`: *Prepare*, output `lion-tiger-test_scored_errors`, a step *Formula* into `check`: `if(label == prediction, "right", "wrong")`; *Run*.]
  Wrong: #rule(1.2cm) of 56 #h(8pt) accuracy: #rule(1.6cm) #h(8pt) lion-always baseline: 68%

  What do the wrong photos have in common? Is any of them wrongly labelled?
  #writing(1)
]

#v(5pt)

#panel("4 · Fine-tune two layers, and compare")[
  #step(1, "Unlock two layers")[In the same analysis: #dss("Design", "Training"), *Number of fine-tuned layers* 2, the rest unchanged. *Train*.]
  #v(2pt)
  #step(2, "Score with the new model")[On the new model: #dss("Deploy"), updating the existing model `model_lions_tigers`. On the Flow, open `model_lions_tigers`: the new version must be the active one, or the Score recipe still uses the old model. Run the Score recipe again and count as in step 3.3.]
  #v(2pt)
  #table(
    columns: (1.6fr, 1fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [*fine-tuned layers*], [*training time*], [*accuracy in Results*], [*wrong of 56*],
    [0 (step 2)], [], [], [],
    [2], [], [], [],
  )
  Both accuracies come from Dataiku's own test split: how many photos is that, and what is one photo worth?
  #rule(4cm)
]

#v(5pt)

#panel("5 · Add a third, larger class: cats")[
  #step(1, "Stack the cats in")[Select `lion-tiger-train` and `cats-train`; in the right panel, *Stack*, output `felines-train`; *Run*. The same for `lion-tiger-test` and `cats-test`, output `felines-test`.]
  #v(2pt)
  #step(2, "Retrain")[An analysis is tied to its dataset, so a new one: on `felines-train`, as in steps 2.1 and 2.2, 0 fine-tuned layers; *Train*. Three classes now.]
  #v(2pt)
  #table(
    columns: (1.4fr, 1fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [*class*], [*training photos*], [*test photos*], [*recall*],
    [lion], [30], [38], [],
    [tiger], [28], [18], [],
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
