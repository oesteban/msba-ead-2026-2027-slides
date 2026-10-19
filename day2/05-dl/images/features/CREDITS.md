# Feature visualisation credits


Source article: Olah, C., Mordvintsev, A. and Schubert, L. (2017). "Feature
Visualization". Distill. https://distill.pub/2017/feature-visualization/,
doi:10.23915/distill.00007

Licence wording, copied verbatim from the article's "Reuse" section:

> Diagrams and text are licensed under Creative Commons Attribution CC-BY 4.0 with the source available on GitHub, unless noted otherwise. The figures that have been reused from other sources don’t fall under this license and can be recognized by a note in their caption: “Figure from …”.

Licence URL: https://creativecommons.org/licenses/by/4.0/
Repository: https://github.com/distillpub/post--feature-visualization (its LICENSE file is CC BY 4.0)

Origin: the article's opening figure (`#googlenet-examples`, captioned "Feature
visualization allows us to see how GoogLeNet, trained on the ImageNet dataset,
builds up its understanding of images over many layers.") is drawn by the
article's script from one sprite sheet:

- https://distill.pub/2017/feature-visualization/images/sprite_hero.png
  (1000x1200 px, 5 columns by 6 rows of 200 px tiles; column = stage, row = example)
- identical to `public/images/sprite_hero.png` in the GitHub repository
  (git blob fbebcd4ecc4cfa3c62123ae26badf70e9e519a68, added by Ludwig Schubert
  on 2017-11-07 in commit 73bf8b692e, "Add build results for publication")

The figure's caption has no "Figure from …" note, so the article's CC BY 4.0
licence covers it. The authors made these visualisations with their own
optimisation code (Lucid), as the article's "Author Contributions" section states.

Each file below is a single 200x200 px tile, cut from the sprite at its native
resolution and otherwise unchanged (saved as PNG).

| File | Stage label in the figure | Tile (column, row) |
|---|---|---|
| features-edges.png | Edges (layer conv2d0) | (0, 1) |
| features-textures.png | Textures (layer mixed3a) | (1, 0) |
| features-patterns.png | Patterns (layer mixed4a) | (2, 0) |
| features-parts.png | Parts (layers mixed4b & mixed4c) | (3, 4) |
| features-objects.png | Objects (layers mixed4d & mixed4e) | (4, 5) |

Tile (c, r) covers pixels x = 200c to 200c+199, y = 200r to 200r+199 of the sprite.
For "Parts" and "Objects", the figure gives two layers per column and does not say
which layer each tile comes from.

Credit line for a slide: Olah, Mordvintsev & Schubert (2017), "Feature
Visualization", Distill, CC BY 4.0 (tiles cropped from the opening figure).
