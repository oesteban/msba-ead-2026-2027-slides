# Photo credits

Checked at the source on 2026-10-19 through the Wikimedia Commons API (`prop=imageinfo`, `iiprop=extmetadata`) and each file page's licence template.

Every photo below was resized (long side at most 1600 px) and re-encoded as
JPEG under 300 KB. Where marked, it was also converted from Adobe RGB to sRGB.
No crop, no other change.

### tiger-1.jpg

- Commons file: File:Sibirischer tiger de edit02.jpg
- URL: https://commons.wikimedia.org/wiki/File:Sibirischer_tiger_de_edit02.jpg
- Author (as Commons gives it): S. Taheri, edited by Fir0002
- Licence: CC BY-SA 2.5, https://creativecommons.org/licenses/by-sa/2.5
- Commons status: Featured picture
- Changes: resized from 1600x1200 to 1400x1050 px.

### tiger-2.jpg

- Commons file: File:Bengal tiger (Panthera tigris tigris) female 3.jpg
- URL: https://commons.wikimedia.org/wiki/File:Bengal_tiger_(Panthera_tigris_tigris)_female_3.jpg
- Author (as Commons gives it): Charles J. Sharp
- Licence: CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0
- Commons status: Featured picture, Quality image
- Changes: resized from 5100x3400 to 1200x800 px; Adobe RGB converted to sRGB.

### lion-1.jpg

- Commons file: File:Serengeti National Park 08 - lion - Panthera leo.jpg
- URL: https://commons.wikimedia.org/wiki/File:Serengeti_National_Park_08_-_lion_-_Panthera_leo.jpg
- Author (as Commons gives it): Thomas Fuhrmann
- Licence: CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0
- Commons status: Quality image
- Changes: resized from 2833x1889 to 1600x1067 px; Adobe RGB converted to sRGB.

`tiger-224.jpg` is `tiger-1.jpg` cropped to a centred square and resized to 224 by 224 by `../../src/draw.py`, for the pixel patch of `pixels.svg`; same author and licence.

## The timeline (slides 5 and 6)

Checked at the source on 2026-10-20 through the Wikimedia Commons API (`prop=imageinfo`,
`iiprop=extmetadata`). Each was cropped where noted, resized and re-encoded under 300 KB.
A crop of a CC BY-SA photo stays under CC BY-SA 4.0.

### perceptron.jpg

- Commons file: File:330-PSA-80-60 (USN 710739) (20897323365).jpg
- URL: https://commons.wikimedia.org/wiki/File:330-PSA-80-60_(USN_710739)_(20897323365).jpg
- Author (as Commons gives it): National Museum of the U.S. Navy
- Licence: public domain (U.S. Navy photo)
- Shows: the Mark I Perceptron, adjusted by an engineer
- Changes: cropped to the machine, resized to 420x398 px.

### hinton.jpg

- Commons file: File:Geoffrey E. Hinton, 2024 Nobel Prize Laureate in Physics (cropped1).jpg
- URL: https://commons.wikimedia.org/wiki/File:Geoffrey_E._Hinton,_2024_Nobel_Prize_Laureate_in_Physics_(cropped1).jpg
- Author (as Commons gives it): Arthur Petron
- Licence: CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0
- Changes: cropped to the head and shoulders, resized to 320x335 px.

### mnist.png

- Commons file: File:MnistExamples.png
- URL: https://commons.wikimedia.org/wiki/File:MnistExamples.png
- Author (as Commons gives it): Josef Steppan
- Licence: CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0
- Changes: none (594x361 px), re-encoded.

### gtx580.jpg

- Commons file: File:NVIDIA@40nm@Fermi@GF110@GeForce GTX 580@UA10B338 1041A1 N2Y540.000 GF110-375-A1 DSC04152 (27576804994).jpg
- URL: https://commons.wikimedia.org/wiki/File:NVIDIA@40nm@Fermi@GF110@GeForce_GTX_580@UA10B338_1041A1_N2Y540.000_GF110-375-A1_DSC04152_(27576804994).jpg
- Author (as Commons gives it): Fritzchens Fritz from Berlin
- Licence: CC0 1.0
- Shows: a GeForce GTX 580 board, its cooler lifted, with the GF110 chip
- Changes: cropped to the board, resized to 460x258 px.

## Figures adapted from the tiger photos

`tiger-224.jpg` and `tiger-2.jpg` are adapted, under their own licences (CC BY-SA 2.5 and 4.0), by
`../../src/draw.py` (the pixel patch, its colour channels, the flattened patch, the augmented copy,
the filter windows) and `../../src/vision.py` (saliency maps, box and mask, in `../vision/`).
