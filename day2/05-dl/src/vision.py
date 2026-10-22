#!/usr/bin/env python3
"""Compute the deck's vision figures on two openly licensed tiger photos.

    micromamba run -n ead-vision python -I day2/05-dl/src/vision.py day2/05-dl/images

Reads `images/photos/tiger-224.jpg` (S. Taheri, edited by Fir0002, CC BY-SA 2.5) and
`images/photos/tiger-2.jpg` (Charles J. Sharp, CC BY-SA 4.0); see `images/photos/CREDITS.md`.
Writes small PNGs and `vision.json` into `images/vision/`, which `draw.py` places in its figures:

- a gradient saliency map of ResNet-18's tiger score on the first photo (Simonyan et al. 2014);
- the same map, and a Guided Backprop map, before and after the network's top layers (its last
  block and its output layer) are re-initialised at random (Adebayo et al. 2018, cascading
  randomisation, top layers only);
- ResNet-18's top class for the second photo, and the highest-scoring box and mask of a Mask
  R-CNN trained on COCO, whose 80 classes hold no tiger: the box and mask are the model's, the
  label on the slide is ours.

Each map is the largest absolute gradient over the three colour channels, averaged over 4 by 4
pixel blocks (56 by 56 blocks) so that it reads on a slide; the rank correlations in `vision.json`
are given for both the pixels and the blocks. ResNet-18 rather than Hands-on 4's EfficientNet B0:
Guided Backprop is defined through ReLU units, which EfficientNet does not use. Pretrained weights
are torchvision's (ResNet18_Weights.IMAGENET1K_V1, MaskRCNN_ResNet50_FPN_Weights.COCO_V1), downloaded on first use into the torch cache, anonymously. The maps derive from CC BY-SA
photos and stay under CC BY-SA. Needs torch, torchvision, Pillow and numpy, in the separate
micromamba environment `ead-vision`; run with `-I`, the photos being downloaded files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision.models import ResNet18_Weights, resnet18
from torchvision.models.detection import MaskRCNN_ResNet50_FPN_Weights, maskrcnn_resnet50_fpn

ACCENT = (0, 96, 156)          # the theme's accent, #00609c
TIGER = 292                    # ImageNet class "tiger, Panthera tigris"
torch.manual_seed(0)


def blocks(m: np.ndarray, k: int = 4) -> np.ndarray:
    """A 224 by 224 map averaged over k by k pixel blocks."""
    return m.reshape(m.shape[0] // k, k, m.shape[1] // k, k).mean((1, 3))


def heat_png(m: np.ndarray, path: Path, size: int) -> None:
    """A map averaged over 4 by 4 blocks, scaled to its 99th percentile, drawn in the accent colour
    with the map as its opacity."""
    m = blocks(m)
    v = np.clip(m / np.percentile(m, 99), 0, 1)
    rgba = np.zeros(m.shape + (4,), dtype=np.uint8)
    rgba[..., :3] = ACCENT
    rgba[..., 3] = (255 * v).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").resize((size, size), Image.NEAREST).save(path, optimize=True)


def rank_corr(a: np.ndarray, b: np.ndarray) -> float:
    ra, rb = a.ravel().argsort().argsort(), b.ravel().argsort().argsort()
    return float(np.corrcoef(ra, rb)[0, 1])


class Guided:
    """Guided Backprop: through every ReLU, only positive gradients pass back."""

    def __init__(self, net):
        self.handles = []
        for mod in net.modules():
            if isinstance(mod, torch.nn.ReLU):
                mod.inplace = False
                self.handles.append(mod.register_full_backward_hook(
                    lambda m, gi, go: (torch.clamp(gi[0], min=0.0),)))

    def remove(self):
        for h in self.handles:
            h.remove()


def maps(net, x) -> tuple[np.ndarray, np.ndarray]:
    """The plain gradient map and the Guided Backprop map of the tiger score, each the largest
    absolute value over the three colour channels."""
    out = []
    for guided in (False, True):
        g = Guided(net) if guided else None
        xi = x.clone().requires_grad_(True)
        net(xi)[0, TIGER].backward()
        out.append(xi.grad[0].abs().amax(0).numpy())
        if g:
            g.remove()
    return out[0], out[1]


def main(images: Path) -> int:
    out = images / "vision"
    out.mkdir(exist_ok=True)
    photos = images / "photos"
    w = ResNet18_Weights.IMAGENET1K_V1
    net = resnet18(weights=w).eval()
    for mod in net.modules():
        if isinstance(mod, torch.nn.ReLU):
            mod.inplace = False
    prep = w.transforms()
    cats = w.meta["categories"]
    res: dict = {"classifier": "torchvision ResNet-18, IMAGENET1K_V1", "map_blocks": "4 by 4 pixels"}

    # the first photo, already 224 by 224: normalise only, so that the map fits it pixel for pixel
    im1 = Image.open(photos / "tiger-224.jpg").convert("RGB")
    t = torch.from_numpy(np.asarray(im1, dtype=np.float32) / 255).permute(2, 0, 1)
    mean, std = torch.tensor(prep.mean)[:, None, None], torch.tensor(prep.std)[:, None, None]
    x = ((t - mean) / std)[None]
    with torch.no_grad():
        p = net(x).softmax(1)[0]
    res["photo1"] = {"top": cats[int(p.argmax())], "p_top": round(float(p.max()), 3),
                     "p_tiger": round(float(p[TIGER]), 3)}
    grad, guided = maps(net, x)
    heat_png(grad, out / "saliency.png", 448)
    heat_png(guided, out / "guided.png", 448)

    # the top layers re-initialised at random: the last block (layer4) and the output layer
    rnd = resnet18(weights=w).eval()
    for mod in rnd.modules():
        if isinstance(mod, torch.nn.ReLU):
            mod.inplace = False
    for mod in list(rnd.layer4.modules()) + [rnd.fc]:
        if hasattr(mod, "reset_parameters"):
            mod.reset_parameters()
    grad_r, guided_r = maps(rnd, x)
    heat_png(grad_r, out / "saliency-random.png", 448)
    heat_png(guided_r, out / "guided-random.png", 448)
    res["randomised"] = {"layers": "layer4 and fc re-initialised",
                         "rank_corr_gradient": round(rank_corr(grad, grad_r), 3),
                         "rank_corr_guided": round(rank_corr(guided, guided_r), 3),
                         "rank_corr_gradient_blocks": round(rank_corr(blocks(grad), blocks(grad_r)), 3),
                         "rank_corr_guided_blocks": round(rank_corr(blocks(guided), blocks(guided_r)), 3)}

    # the second photo: what (ResNet-18), where and which pixels (Mask R-CNN on COCO)
    im2 = Image.open(photos / "tiger-2.jpg").convert("RGB")
    with torch.no_grad():
        p2 = net(prep(im2)[None]).softmax(1)[0]
    res["photo2"] = {"size": list(im2.size), "top": cats[int(p2.argmax())], "p_top": round(float(p2.max()), 3)}
    mw = MaskRCNN_ResNet50_FPN_Weights.COCO_V1
    det = maskrcnn_resnet50_fpn(weights=mw).eval()
    t2 = torch.from_numpy(np.asarray(im2, dtype=np.float32) / 255).permute(2, 0, 1)
    with torch.no_grad():
        r = det([t2])[0]
    i = int(r["scores"].argmax())
    box = [round(float(v), 1) for v in r["boxes"][i]]
    mask = (r["masks"][i, 0].numpy() > 0.5)
    rgba = np.zeros(mask.shape + (4,), dtype=np.uint8)
    rgba[..., :3] = ACCENT
    rgba[..., 3] = np.where(mask, 170, 0).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").resize((600, 400), Image.NEAREST).save(out / "tiger-mask.png", optimize=True)
    res["detection"] = {"model": "torchvision Mask R-CNN ResNet-50 FPN, COCO_V1",
                        "coco_label": mw.meta["categories"][int(r["labels"][i])],
                        "score": round(float(r["scores"][i]), 3), "box_xyxy": box,
                        "mask_share": round(float(mask.mean()), 3)}
    (out / "vision.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1])))
