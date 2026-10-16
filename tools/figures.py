#!/usr/bin/env python3
"""Render the data figures of the day-1 decks.

Every chart in day1/0[2-4]-*/images is drawn here from the data,
so every number on a slide can be traced to a computation. (Figures drawn by
others appear only in day1/01-intro, each with its licence on the slide.)

    python3 tools/figures.py --credit south_german_credit.csv --wine winequality_all.csv \
        [--zalaxus Zalaxus.zip]
    python3 tools/figures.py --credit south_german_credit.csv     # credit only

The datasets are not in this repository. south_german_credit.csv is the
corrected South German Credit data (Groemping 2019; UCI dataset 573, CC BY 4.0)
with English column names and labels and a `credit_risk` column (good/bad),
built by build-datasets.py in the private wrapper; the 2025-26 Statlog file
with its `Score` column is still read. winequality_all.csv is UCI Wine Quality
(CC BY 4.0), red and white together with a `color` column. Without --wine, the
credit numbers are merged into the existing figures-numbers.json. Zalaxus is the module's teaching
dataset and is only read to measure the leakage example (two numbers).

Models are scikit-learn, cross-validated with 5 stratified folds and a fixed
seed. They stand in for what Dataiku computes; the decks say so.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    average_precision_score, confusion_matrix, f1_score, precision_recall_curve,
    precision_score, recall_score, roc_auc_score, roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.svm import SVC  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
AM = ROOT / "day1" / "02-model" / "images"
CV = ROOT / "day1" / "03-cv" / "images"
WINE = ROOT / "day1" / "04-multiclass" / "images"

ACCENT = "#00609c"
DARK = "#1a1a1a"
GRAY = "#8a8a8a"
LIGHT = "#d9d9d9"
CYAN = "#25bcca"
# the four cells of the confusion matrix, as on the decks: right decisions in the accent,
# errors in the warning hue, the costly one (a bad credit granted) the darkest
TP_C, TN_C, FP_C, FN_C = ACCENT, "#8cb3cf", "#f0a3a8", "#da232f"
SEED = 1337

plt.rcParams.update({
    "svg.fonttype": "none",
    "font.family": "sans-serif",
    "font.sans-serif": ["Arimo", "Liberation Sans", "Arial", "DejaVu Sans"],
    "font.size": 14,
    "axes.edgecolor": GRAY,
    "axes.labelcolor": DARK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": DARK,
    "ytick.color": DARK,
    "legend.frameon": False,
    "figure.dpi": 100,
    "svg.hashsalt": "ead-figures",          # stable clip-path ids, so reruns diff clean
})

NUMBERS: dict = {}


def save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", transparent=True, metadata={"Date": None})
    plt.close(fig)
    # an artist given gid "step-N-..." becomes a group the deck reveals at step N
    # (remark-engine's stepwise-svg.js reads data-step)
    svg = path.read_text()
    stepped = re.sub(r'<g id="step-(\d+)-([^"]*)"', r'<g id="step-\1-\2" data-step="\1"', svg)
    if stepped != svg:
        path.write_text(stepped)
    print(f"wrote {path.relative_to(ROOT)}")


_gid = iter(range(10**6))


def at_step(n: int, *artists) -> None:
    """Reveal these artists at step n of the slide."""
    for a in artists:
        for x in (a if isinstance(a, (list, tuple)) else [a]):
            x.set_gid(f"step-{n}-{next(_gid)}")


def rf(n=500, **kw):
    return RandomForestClassifier(n_estimators=n, min_samples_leaf=3, n_jobs=-1,
                                  random_state=SEED, **kw)


# --------------------------------------------------------------------------
# Morning: german credit, positive class = bad
# --------------------------------------------------------------------------
def credit(path: Path) -> None:
    d = pd.read_csv(path)
    target = "credit_risk" if "credit_risk" in d else "Score"
    y = (d[target] == "bad").astype(int).to_numpy()
    X = pd.get_dummies(d.drop(columns=["row ID", target], errors="ignore"))
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    p = cross_val_predict(rf(), X, y, cv=cv, method="predict_proba")[:, 1]
    ts = np.round(np.arange(0.02, 0.981, 0.01), 2)

    # precision is undefined once nobody is flagged: leave those points out
    prec = np.array([precision_score(y, p > t) if (p > t).any() else np.nan for t in ts])
    rec = np.array([recall_score(y, p > t) for t in ts])
    f1 = np.array([f1_score(y, p > t) for t in ts])
    # Statlog cost matrix: lending to a bad applicant costs 5, refusing a good one costs 1
    cost = np.array([5 * ((p <= t) & (y == 1)).sum() + ((p > t) & (y == 0)).sum() for t in ts])
    t_f1, t_cost = ts[f1.argmax()], ts[cost.argmin()]

    def cm(t):
        tn, fp, fn, tp = confusion_matrix(y, p > t).ravel()
        return dict(tp=int(tp), fp=int(fp), fn=int(fn), tn=int(tn))

    NUMBERS["credit"] = dict(
        n=len(y), bad=int(y.sum()), good=int((1 - y).sum()),
        auc=round(roc_auc_score(y, p), 3), ap=round(average_precision_score(y, p), 3),
        acc_05=round(((p > 0.5) == y).mean(), 3), baseline=round(1 - y.mean(), 3),
        t_f1=float(t_f1), t_cost=float(t_cost),
        cost_05=int(cost[ts == 0.5][0]), cost_best=int(cost.min()), cost_lend_all=int(5 * y.sum()),
        cm_05=cm(0.5), cm_f1=cm(t_f1), cm_cost=cm(t_cost),
        precision_05=round(float(precision_score(y, p > 0.5)), 3),
        recall_05=round(float(recall_score(y, p > 0.5)), 3),
        f1_05=round(float(f1_score(y, p > 0.5)), 3),
        fpr_05=round(float(((p > 0.5) & (y == 0)).sum() / (y == 0).sum()), 3),
        cost_rule=int(cost[ts == 0.17][0]),            # the threshold 1/(1+5) of the expected-cost rule
        cost_refuse_all=int((1 - y).sum()),             # every good customer turned away, at 1 each
        exp_cost_05=round(float(cost[ts == 0.5][0]) / len(y), 3),
        exp_cost_best=round(float(cost.min()) / len(y), 3),
    )

    bins = np.linspace(0, 1, 26)


    # 1. score distributions, stacked (bad below, good above), built in steps: the scores, the cut
    # at 0.5, then the four outcomes coloured as on the decks' confusion matrices
    fig, ax = plt.subplots(figsize=(8.6, 4.3))
    t = 0.5
    nb, _ = np.histogram(p[y == 1], bins=bins)
    ng, _ = np.histogram(p[y == 0], bins=bins)
    w = bins[1] - bins[0]
    left = bins[:-1]
    at_step(1, list(ax.bar(left, nb, width=w, align="edge", color=GRAY, edgecolor="white", lw=0.6)),
            list(ax.bar(left, ng, width=w, bottom=nb, align="edge", color=LIGHT, edgecolor="white", lw=0.6)))
    top = (nb + ng).max()
    ax.set_ylim(0, top * 1.62)
    stacked = ax.text(0.66, top * 0.78, f"bars stacked:\nbad credits ({y.sum()}) below,\ngood ones ({(y == 0).sum()}) above",
            color=DARK, fontsize=11, va="top")
    at_step(1, stacked)
    cut = ax.axvline(t, ymax=1.04 / 1.62, color=DARK, lw=1.6, ls="--")
    cut_lab = ax.text(t, top * 1.08, "threshold 0.5", color=DARK, fontsize=12, ha="center")
    at_step(2, cut, cut_lab)
    for x0, b_, g_ in zip(left, nb, ng):
        right = x0 >= t
        at_step(3, ax.add_patch(plt.Rectangle((x0, 0), w, b_, color=TP_C if right else FN_C, ec="white", lw=0.6)),
                ax.add_patch(plt.Rectangle((x0, b_), w, g_, color=FP_C if right else TN_C, ec="white", lw=0.6)))
    m = NUMBERS["credit"]["cm_05"]
    key = ((0.02, 1.48, TN_C, f"{m['tn']} true negatives: good, granted"),
           (0.02, 1.33, FN_C, f"{m['fn']} false negatives: bad, granted"),
           (0.55, 1.48, FP_C, f"{m['fp']} false positives: good, refused"),
           (0.55, 1.33, TP_C, f"{m['tp']} true positives: bad, refused"))
    for x, yy, c, lab in key:
        at_step(3, ax.add_patch(plt.Rectangle((x, top * yy - top * 0.035), 0.022, top * 0.07, color=c)),
                ax.text(x + 0.03, top * yy, lab, va="center", fontsize=12, color=DARK))
    ax.set_xlabel("predicted probability of “bad”")
    ax.set_ylabel("applicants")
    save(fig, AM / "threshold-regions.svg")

    # 2. precision / recall / F1 against the threshold
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(ts, prec, color=CYAN, lw=2.2, label="precision")
    ax.plot(ts, rec, color=ACCENT, lw=2.2, label="recall")
    ax.plot(ts, f1, color=GRAY, lw=1.6, ls="--", label="F1")
    ax.axvline(0.5, color=DARK, lw=1, ls=":")
    ax.set_xlabel("threshold on P(bad)")
    ax.set_ylim(0, 1.02)
    ax.legend(loc="center right")
    save(fig, AM / "threshold-tradeoff.svg")

    # 3. total cost against the threshold
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(ts, cost, color=ACCENT, lw=2.4)
    ax.axhline(5 * y.sum(), color=GRAY, lw=1, ls="--")
    ax.text(0.97, 5 * y.sum() + 25, "lend to everyone", color=GRAY, ha="right", fontsize=12)
    ax.axhline((1 - y).sum(), color=GRAY, lw=1, ls=":")
    ax.text(0.97, (1 - y).sum() + 25, "refuse everyone", color=GRAY, ha="right", fontsize=12)
    for t, lab in ((0.5, "0.5"), (t_cost, f"{t_cost:.2f}")):
        c = cost[ts == t][0]
        ax.plot([t], [c], "o", color=DARK)
        ax.annotate(f"t = {lab}\ncost {c}", (t, c), xytext=(8, -34), textcoords="offset points",
                    fontsize=12, color=DARK)
    ax.set_xlabel("threshold on P(bad)")
    ax.set_ylabel("total cost (units)")
    ax.set_ylim(0, 5 * y.sum() * 1.12)
    save(fig, AM / "cost-vs-threshold.svg")

    # 4. ROC, built from three thresholds, then every threshold; the AUC; and what a rarer
    #    bad credit does to precision while the ROC curve stays put
    fpr, tpr, _ = roc_curve(y, p)
    auc = roc_auc_score(y, p)
    pts = {t: (float(((p > t) & (y == 1)).sum() / y.sum()), float(((p > t) & (y == 0)).sum() / (1 - y).sum()))
           for t in (0.6, 0.4, 0.2)}
    NUMBERS["credit"]["roc_points"] = {str(t): [round(a, 3), round(b, 3)] for t, (a, b) in pts.items()}

    def roc_axes(ax):
        ax.plot([0, 1], [0, 1], color=GRAY, ls="--", lw=1)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)
        ax.set_aspect("equal")
        ax.set_xlabel("false-positive rate\n(good applicants refused)")
        ax.set_ylabel("true-positive rate = recall\n(bad applicants refused)")

    fig, ax = plt.subplots(figsize=(5.6, 5.4))
    roc_axes(ax)
    at_step(1, ax.text(0.62, 0.50, "guessing", color=GRAY, fontsize=12, rotation=45),
            ax.plot([0], [1], "*", color=DARK, ms=12)[0],
            ax.text(0.04, 0.95, "perfect: every bad credit\nrefused, no good one", fontsize=11, va="top", color=DARK))
    for k, (t, (tp_r, fp_r)) in enumerate(sorted(pts.items(), reverse=True)):
        at_step(2 + k, ax.plot([fp_r], [tp_r], "o", color=FN_C, ms=9)[0],
                ax.annotate(f"t = {t}", (fp_r, tp_r), xytext=(10, -14), textcoords="offset points",
                            fontsize=12, color=FN_C, fontweight="bold"))
    at_step(5, ax.plot(fpr, tpr, color=ACCENT, lw=2.4)[0])
    save(fig, AM / "roc-build.svg")

    fig, ax = plt.subplots(figsize=(5.6, 5.4))
    roc_axes(ax)
    ax.plot(fpr, tpr, color=ACCENT, lw=2.4)
    at_step(2, ax.fill_between(fpr, tpr, step="post", color=ACCENT, alpha=0.18),
            ax.text(0.55, 0.30, f"AUC = {auc:.2f}", fontsize=16, color=ACCENT, fontweight="bold"),
            ax.text(0.55, 0.20, "guessing: 0.50", fontsize=12, color=GRAY))
    save(fig, AM / "roc-auc.svg")

    # precision at another mix of bad credits, from the same ROC points:
    # precision = pi * TPR / (pi * TPR + (1 - pi) * FPR)
    def prec_at(pi, t_r, f_r):
        return pi * t_r / (pi * t_r + (1 - pi) * f_r)

    keep = (tpr > 0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.6))
    roc_axes(a1)
    a1.plot(fpr, tpr, color=ACCENT, lw=2.4)
    a1.set_title("ROC: the same at 30% and at 5% bad", color=DARK, fontsize=13)
    r_at = float(((p > 0.5) & (y == 1)).sum() / y.sum())
    f_at = float(((p > 0.5) & (y == 0)).sum() / (1 - y).sum())
    for pi, colour, step_n in ((y.mean(), ACCENT, 1), (0.05, FN_C, 2)):
        pr_curve = prec_at(pi, tpr[keep], fpr[keep])
        p05 = prec_at(pi, r_at, f_at)
        at_step(step_n, a2.plot(tpr[keep], pr_curve, color=colour, lw=2.4)[0],
                a2.axhline(pi, color=colour, ls="--", lw=1),
                a2.text(0.02, pi + 0.02, f"{pi:.0%} bad: floor {pi:.2f}", color=colour, fontsize=11, ha="left"),
                a2.plot([r_at], [p05], "o", color=colour, ms=8)[0],
                a2.annotate(f"t = 0.5: precision {p05:.0%}", (r_at, p05), xytext=(10, 4),
                            textcoords="offset points", fontsize=11, color=colour))
        NUMBERS["credit"][f"precision_05_at_{round(pi * 100)}"] = round(float(p05), 3)
    a2.set_xlim(0, 1)
    a2.set_ylim(0, 1.02)
    a2.set_xlabel("recall")
    a2.set_ylabel("precision")
    a2.set_title("Precision-recall: moves with the mix", color=DARK, fontsize=13)
    fig.tight_layout(w_pad=3)
    save(fig, AM / "pr-imbalance.svg")

    # 5. cumulative gains: review the riskiest k% first
    order = np.argsort(-p)
    caught = np.cumsum(y[order]) / y.sum()
    share = np.arange(1, len(y) + 1) / len(y)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.plot(share * 100, caught * 100, color=ACCENT, lw=2.4, label="model")
    ax.plot([0, 100], [0, 100], color=GRAY, ls="--", lw=1, label="random order")
    k = int(0.2 * len(y))
    ax.plot([20], [caught[k - 1] * 100], "o", color=DARK)
    ax.annotate(f"top 20% → {caught[k - 1] * 100:.0f}% of the bad", (20, caught[k - 1] * 100),
                xytext=(12, -6), textcoords="offset points", fontsize=12)
    ax.set_xlabel("% of applicants reviewed, riskiest first")
    ax.set_ylabel("% of bad applicants found")
    ax.legend(loc="lower right")
    NUMBERS["credit"]["gain_top20"] = round(float(caught[k - 1]), 3)
    save(fig, AM / "cumulative-gains.svg")

    # 6. one split is one draw: test AUC over 200 random 80/20 splits (Dataiku's default ratio,
    #    200 test credits); the first five drawn row by row, then all 200 as a histogram
    rows = np.arange(len(y))
    aucs, draws = [], []
    for s in range(200):
        tr, te = train_test_split(rows, test_size=0.2, stratify=y, random_state=s)
        m = rf(200).fit(X.iloc[tr], y[tr])
        aucs.append(roc_auc_score(y[te], m.predict_proba(X.iloc[te])[:, 1]))
        if s < 5:
            draws.append(np.sort(te))
    aucs = np.array(aucs)
    folds = []
    for tr, te in cv.split(X, y):
        m = rf().fit(X.iloc[tr], y[tr])
        folds.append(roc_auc_score(y[te], m.predict_proba(X.iloc[te])[:, 1]))
    NUMBERS["credit"]["split_auc_min"] = round(float(aucs.min()), 3)
    NUMBERS["credit"]["split_auc_max"] = round(float(aucs.max()), 3)
    NUMBERS["credit"]["split_draws"] = [round(float(a), 3) for a in aucs[:5]]
    NUMBERS["credit"]["fold_aucs"] = [round(float(a), 3) for a in folds]
    NUMBERS["credit"]["fold_mean"] = round(float(np.mean(folds)), 3)
    NUMBERS["credit"]["fold_2sd"] = round(float(2 * np.std(folds)), 3)

    # the five draws: each row is the 1,000 credits in file order, the 200 drawn for the test
    # in the accent; one compound path per row keeps the SVG small
    fig, ax = plt.subplots(figsize=(9, 3.3))
    n = len(y)
    for i, te in enumerate(draws):
        y0 = len(draws) - 1 - i
        ax.add_patch(plt.Rectangle((0, y0 + 0.12), n, 0.76, color=LIGHT, lw=0))
        verts, codes = [], []
        for r in te:
            verts += [(r, y0 + 0.12), (r + 1, y0 + 0.12), (r + 1, y0 + 0.88), (r, y0 + 0.88), (r, y0 + 0.12)]
            codes += [MPath.MOVETO, MPath.LINETO, MPath.LINETO, MPath.LINETO, MPath.CLOSEPOLY]
        at_step(i + 1, ax.add_patch(PathPatch(MPath(verts, codes), color=ACCENT, lw=0)),
                ax.text(n + 18, y0 + 0.5, f"test AUC {aucs[i]:.2f}", va="center", fontsize=14, color=DARK,
                        fontweight="bold"),
                ax.text(-18, y0 + 0.5, f"draw {i + 1}", va="center", ha="right", fontsize=13, color=DARK))
    ax.text(n / 2, -0.35, "the 1,000 credits, in file order: grey for training (800), blue for the test (200)",
            ha="center", va="top", fontsize=12, color=GRAY)
    ax.set_xlim(-130, n + 190)
    ax.set_ylim(-0.9, len(draws))
    ax.axis("off")
    save(fig, CV / "split-draws.svg")

    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.hist(aucs, bins=24, color=LIGHT)
    for a in aucs[:5]:
        ax.axvline(a, color=ACCENT, lw=2)
    ax.set_xlabel("test AUC")
    ax.set_ylabel("random splits")
    ax.set_title("grey: 200 random 80/20 splits\nblue: the five draws of the previous slide",
                 loc="left", fontsize=11, color=DARK)
    save(fig, CV / "split-variability.svg")

    # the five fold scores of one cross-validation, their mean and Dataiku's ± (twice the SD)
    mu, sd2 = float(np.mean(folds)), float(2 * np.std(folds))
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    ax.axvspan(mu - sd2, mu + sd2, color=ACCENT, alpha=0.12, lw=0)
    ax.axvline(mu, ymax=(len(folds) + 0.45 - 0.3) / (len(folds) + 0.9), color=ACCENT, lw=1.6, ls="--")
    for i, a in enumerate(folds):
        ax.plot([a], [len(folds) - i], "o", color=ACCENT, ms=10)
        ax.text(a + 0.004, len(folds) - i, f"{a:.3f}", va="center", fontsize=12, color=DARK)
    ax.set_yticks(range(len(folds), 0, -1), [f"fold {i + 1}" for i in range(len(folds))])
    ax.set_ylim(0.3, len(folds) + 1.2)
    ax.text(mu, len(folds) + 0.75, f"mean {mu:.3f} (± {sd2:.3f})", ha="center", fontsize=13, color=ACCENT,
            fontweight="bold")
    ax.set_xlim(mu - 0.07, mu + 0.07)
    ax.set_xlabel("test AUC of each fold")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, CV / "fold-dots.svg")


def boundary(path: Path) -> None:
    """Two of the twenty attributes, and where a threshold puts the boundary between them.

    A logistic regression on duration and amount alone (fitted on all rows: the figure
    shows a boundary, not a score). The line where P(bad) equals the threshold splits
    the plane; lowering the threshold moves it and refuses more applicants.
    """
    d = pd.read_csv(path)
    target = "credit_risk" if "credit_risk" in d else "Score"
    y = (d[target] == "bad").astype(int).to_numpy()
    X = d[["duration", "amount"]].to_numpy(float)
    mu, sd = X.mean(0), X.std(0)
    lr = LogisticRegression().fit((X - mu) / sd, y)
    prob = lr.predict_proba((X - mu) / sd)[:, 1]
    # the same model in the data's own units: score = intercept + a * duration + b * amount
    w = lr.coef_[0] / sd
    c = lr.intercept_[0] - (lr.coef_[0] * mu / sd).sum()
    NUMBERS["credit"]["boundary_model"] = dict(
        intercept=round(float(c), 2), per_month=round(float(w[0]), 3),
        per_thousand_dm=round(float(w[1] * 1000), 3), score_03=round(float(np.log(0.3 / 0.7)), 2))

    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    at_step(1, ax.scatter(X[y == 0, 0], X[y == 0, 1], s=14, color=LIGHT),
            ax.scatter(X[y == 1, 0], X[y == 1, 1], s=14, color=GRAY, alpha=0.8))
    ax.text(0.99, 0.98, "grey: good · dark: bad", transform=ax.transAxes, ha="right", va="top",
            fontsize=11, color=DARK)
    gx, gy = np.meshgrid(np.linspace(0, 75, 300), np.linspace(0, 19000, 300))
    gp = lr.predict_proba((np.c_[gx.ravel(), gy.ravel()] - mu) / sd)[:, 1].reshape(gx.shape)
    refused = {}
    for step, t, colour in ((2, 0.5, ACCENT), (3, 0.3, FN_C)):
        cs = ax.contour(gx, gy, gp, levels=[t], colors=[colour], linewidths=2.4)
        refused[t] = int((prob > t).sum())
        xs = cs.allsegs[0][0]
        k = int(len(xs) * (0.62 if step == 2 else 0.30))
        lab = ax.text(xs[k, 0] + 1.5, xs[k, 1], f"P(bad) = {t}: {refused[t]} refused",
                      color=colour, fontsize=12, fontweight="bold", va="bottom",
                      bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
        at_step(step, cs, lab)
    ax.set_xlim(0, 75)
    ax.set_ylim(0, 19000)
    ax.set_xlabel("duration (months)")
    ax.set_ylabel("amount (DM)")
    NUMBERS["credit"]["boundary_refused"] = {str(t): n for t, n in refused.items()}
    save(fig, AM / "boundary.svg")


def duration_model(path: Path) -> None:
    """One attribute, as the intro deck did with heights: how many good and bad credits per duration.

    The two curves are kernel density estimates scaled to the class counts (700 good, 300 bad), so
    where they cross, a credit is as likely bad as good. The points go to the JSON; the deck's
    draw script draws them (day1/02-model/src/draw.py).
    """
    from scipy.stats import gaussian_kde
    d = pd.read_csv(path)
    target = "credit_risk" if "credit_risk" in d else "Score"
    y = (d[target] == "bad").astype(int).to_numpy()
    x = d["duration"].to_numpy(float)
    xs = np.linspace(4, 60, 113)
    for bw in (0.3, 0.4, 0.5, 0.6, 0.8):              # widen until the curves cross once
        good = gaussian_kde(x[y == 0], bw_method=bw)(xs) * (y == 0).sum()
        bad = gaussian_kde(x[y == 1], bw_method=bw)(xs) * y.sum()
        cross = [i for i in range(1, len(xs)) if (bad[i] - good[i]) * (bad[i - 1] - good[i - 1]) < 0]
        if len(cross) == 1:
            break
    i = cross[0]
    t = xs[i - 1] + (xs[i] - xs[i - 1]) * (good[i - 1] - bad[i - 1]) / ((bad[i] - bad[i - 1]) - (good[i] - good[i - 1]))
    new = 24
    g24, b24 = np.interp(new, xs, good), np.interp(new, xs, bad)
    NUMBERS["credit"]["duration_model"] = dict(
        bandwidth=bw, months=[round(float(v), 1) for v in xs],
        good=[round(float(v), 3) for v in good], bad=[round(float(v), 3) for v in bad],
        threshold=round(float(t), 1), beyond=int((x > t).sum()),
        new_case=new, p_bad_new=round(float(b24 / (b24 + g24)), 2))


def metric_grid(path: Path) -> None:
    """The same six forests, ranked by four metrics: each metric picks its own winner."""
    d = pd.read_csv(path)
    target = "credit_risk" if "credit_risk" in d else "Score"
    y = (d[target] == "bad").astype(int).to_numpy()
    X = pd.get_dummies(d.drop(columns=["row ID", target], errors="ignore"))
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    rows = []
    for weights in (None, "balanced"):
        for leaf in (1, 10, 40):
            p = cross_val_predict(rf(300, class_weight=weights).set_params(min_samples_leaf=leaf), X, y, cv=cv,
                                  method="predict_proba")[:, 1]
            yh = p > 0.5
            rows.append(dict(class_weights="balanced" if weights else "none", min_leaf=leaf,
                             accuracy=round(float((yh == y).mean()), 3), roc_auc=round(roc_auc_score(y, p), 3),
                             recall=round(float(recall_score(y, yh)), 3), f1=round(float(f1_score(y, yh)), 3),
                             precision=round(float(precision_score(y, yh, zero_division=0)), 3)))
    NUMBERS["credit"]["metric_grid"] = rows


def model_boundaries(path: Path) -> None:
    """Four algorithms on the plane of deck 2: where each refuses (P(bad) > 0.3), and its score.

    Each model is fitted on duration and amount alone, on all rows, to show the shape of its
    boundary; its score is a 5-fold cross-validated AUC on all twenty attributes, on the same folds.
    For the pictures only, the two tree ensembles keep leaves of at least 25 credits: with the
    scored settings their boundary breaks into islands around single credits, too small to read.
    """
    d = pd.read_csv(path)
    target = "credit_risk" if "credit_risk" in d else "Score"
    y = (d[target] == "bad").astype(int).to_numpy()
    X = pd.get_dummies(d.drop(columns=["row ID", target], errors="ignore"))
    two = d[["duration", "amount"]].to_numpy(float)
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    models = {
        "linear": ("logistic regression", lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))),
        "svm": ("SVM (rbf kernel)", lambda: make_pipeline(StandardScaler(), SVC(probability=True, random_state=SEED))),
        "forest": ("random forest", lambda: rf()),
        "boosting": ("gradient-boosted trees", lambda: GradientBoostingClassifier(random_state=SEED)),
    }
    gx, gy = np.meshgrid(np.linspace(0, 75, 220), np.linspace(0, 19000, 220))
    grid = np.c_[gx.ravel(), gy.ravel()]
    NUMBERS["credit"]["models"] = {}
    for key, (label, make) in models.items():
        scores = [roc_auc_score(y[te], make().fit(X.iloc[tr], y[tr]).predict_proba(X.iloc[te])[:, 1])
                  for tr, te in cv.split(X, y)]
        NUMBERS["credit"]["models"][key] = dict(
            name=label, fold_aucs=[round(float(a), 3) for a in scores],
            mean=round(float(np.mean(scores)), 3), pm=round(float(2 * np.std(scores)), 3))
        shape = {"forest": lambda: RandomForestClassifier(300, min_samples_leaf=25, n_jobs=-1, random_state=SEED),
                 "boosting": lambda: GradientBoostingClassifier(min_samples_leaf=25, random_state=SEED)}
        m = shape.get(key, make)().fit(two, y)
        gp = m.predict_proba(grid)[:, 1].reshape(gx.shape)
        fig, ax = plt.subplots(figsize=(4.6, 3.8))
        ax.contourf(gx, gy, gp, levels=[0.3, 1.01], colors=[ACCENT], alpha=0.22)
        ax.contour(gx, gy, gp, levels=[0.3], colors=[ACCENT], linewidths=1.8)
        ax.scatter(two[y == 0, 0], two[y == 0, 1], s=6, color=LIGHT)
        ax.scatter(two[y == 1, 0], two[y == 1, 1], s=6, color=GRAY, alpha=0.8)
        ax.set_title(label, loc="left", fontsize=19, color=DARK)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 19000)
        ax.set_xticks([0, 20, 40, 60])
        ax.set_yticks([0, 5000, 10000, 15000], ["0", "5k", "10k", "15k"])
        ax.set_xlabel("duration (months)", fontsize=17)
        ax.set_ylabel("amount (DM)", fontsize=17)
        ax.tick_params(labelsize=16)
        save(fig, CV / f"model-{key}.svg")


def tree_splits(path: Path) -> None:
    """A depth-2 classification tree on all twenty attributes: its questions and its leaves.

    Recorded for the forest slide, where the deck's draw script draws it (day1/03-cv/src/draw.py).
    """
    d = pd.read_csv(path)
    target = "credit_risk" if "credit_risk" in d else "Score"
    y = (d[target] == "bad").astype(int).to_numpy()
    X = pd.get_dummies(d.drop(columns=["row ID", target], errors="ignore"))
    t = DecisionTreeClassifier(max_depth=2, min_samples_leaf=30, random_state=SEED).fit(X, y).tree_
    nodes = []
    for i in range(t.node_count):
        n_bad = int(round(t.value[i][0][1] * t.n_node_samples[i])) if t.value[i].sum() <= 1.0001 else int(t.value[i][0][1])
        nodes.append(dict(feature=None if t.feature[i] < 0 else str(X.columns[t.feature[i]]),
                          threshold=None if t.feature[i] < 0 else round(float(t.threshold[i]), 2),
                          left=int(t.children_left[i]), right=int(t.children_right[i]),
                          n=int(t.n_node_samples[i]), bad=n_bad))
    NUMBERS["credit"]["tree"] = nodes


def zalaxus(path: Path) -> None:
    z = zipfile.ZipFile(path)

    def rd(n):
        df = pd.read_csv(io.TextIOWrapper(z.open(n), encoding="utf-16"), sep="|", low_memory=False)
        df.columns = [c.strip() for c in df.columns]
        return df

    c, o = rd("ZalaxusCustomer.csv"), rd("ZalaxusOrder.csv")
    y = c["BikeBuyer"].astype(int).to_numpy()
    c["age"] = 2025 - pd.to_datetime(c["BirthDate"].astype(str).str[:10], errors="coerce").dt.year
    feats = ["Gender", "Language", "State", "age", "Height", "MaritalStatus", "YearlyIncome",
             "TotalChildren", "NumberChildrenAtHome", "Education", "Occupation",
             "HomeOwnerFlag", "NumberCarsOwned", "EmailPromotion"]
    X = pd.get_dummies(c[feats]).fillna(-1)
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    a1 = roc_auc_score(y, cross_val_predict(rf(300), X, y, cv=cv, method="predict_proba")[:, 1])
    n_orders = c["CustomerID"].map(o.groupby("CustomerID")["SalesOrderID"].nunique()).fillna(0)
    a2 = roc_auc_score(y, cross_val_predict(rf(300), X.assign(n_orders=n_orders), y, cv=cv,
                                            method="predict_proba")[:, 1])
    NUMBERS["zalaxus"] = dict(auc_customer=round(a1, 3), auc_with_orders=round(a2, 3))
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.barh([1, 0], [a1, a2], color=[LIGHT, ACCENT], height=0.55)
    ax.set_yticks([1, 0], ["customer columns", "+ number of orders"])
    for yy, a in ((1, a1), (0, a2)):
        ax.text(a + 0.01, yy, f"{a:.2f}", va="center", fontsize=14, color=DARK)
    ax.axvline(0.5, color=GRAY, ls="--", lw=1)
    ax.set_xlim(0.4, 1.0)
    ax.set_xlabel("cross-validated AUC, predicting BikeBuyer")
    save(fig, CV / "zalaxus-leak.svg")


# --------------------------------------------------------------------------
# Afternoon: wine quality, multi-class
# --------------------------------------------------------------------------
def wine(path: Path) -> None:
    w = pd.read_csv(path)
    n_all, n_dup = len(w), int(w.duplicated().sum())
    counts = w["quality"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.bar(counts.index.astype(str), counts.values, color=[ACCENT if q in (5, 6) else LIGHT for q in counts.index])
    for q, n in counts.items():
        ax.text(str(q), n + 50, f"{n:,}", ha="center", fontsize=16)
    ax.set_xlabel("grade (median of the tasters' scores)", fontsize=16)
    ax.set_ylabel("wines", fontsize=16)
    ax.tick_params(labelsize=16)
    ax.set_ylim(0, counts.max() * 1.12)
    save(fig, WINE / "wine-classes.svg")

    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    # the same model with the duplicates left in: copies of a test row sit in training
    yd = w["quality"].to_numpy()
    pd_ = cross_val_predict(rf(), pd.get_dummies(w.drop(columns=["quality"])), yd, cv=cv)
    acc_with_dups = round(float((pd_ == yd).mean()), 3)

    w = w.drop_duplicates()
    y = w["quality"].to_numpy()
    X = pd.get_dummies(w.drop(columns=["quality"]))
    # grade 9 keeps its 5 rows after deduplication: just enough for 5 stratified folds
    pred = cross_val_predict(rf(), X, y, cv=cv)
    labels = sorted(np.unique(y))
    cmn = confusion_matrix(y, pred, labels=labels, normalize="true")
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    ax.imshow(cmn, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("a", ["#ffffff", ACCENT]),
              vmin=0, vmax=1)
    for i in range(len(labels)):
        for j in range(len(labels)):
            v = cmn[i, j]
            if v >= 0.005:
                ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=11,
                        color="white" if v > 0.55 else DARK)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("predicted quality")
    ax.set_ylabel("actual quality")
    for s in ax.spines.values():
        s.set_visible(False)
    save(fig, WINE / "wine-confusion.svg")

    per_class = dict(zip(labels, [round(float(r), 2) for r in recall_score(y, pred, labels=labels, average=None)]))
    NUMBERS["wine"] = dict(
        n_all=n_all, duplicates=n_dup, n_dedup=len(w), accuracy_with_duplicates=acc_with_dups,
        counts_dedup={int(k): int(v) for k, v in pd.Series(y).value_counts().sort_index().items()},
        accuracy=round(float((pred == y).mean()), 3),
        f1_macro=round(f1_score(y, pred, average="macro"), 3),
        f1_micro=round(f1_score(y, pred, average="micro"), 3),
        f1_weighted=round(f1_score(y, pred, average="weighted"), 3),
        recall_per_class={int(k): v for k, v in per_class.items()},
        majority_share=round(float(pd.Series(y).value_counts(normalize=True).max()), 3),
    )
    wine_lines(w, X, cv)


LINES = ["low", "medium", "high"]


def wine_lines(w: pd.DataFrame, X: pd.DataFrame, cv) -> None:
    """The deck's running example: three lines, low (grade 5 or less), medium (6), high (7 or more).

    Deduplicated wines, `quality` left out of the inputs, the same forest and folds as above.
    """
    q = w["quality"].to_numpy()
    y = np.where(q <= 5, "low", np.where(q == 6, "medium", "high"))
    proba = cross_val_predict(rf(), X, y, cv=cv, method="predict_proba")
    classes = sorted(np.unique(y))                       # the column order of predict_proba
    proba = proba[:, [classes.index(c) for c in LINES]]
    pred = np.array(LINES)[proba.argmax(axis=1)]
    cm = confusion_matrix(y, pred, labels=LINES)
    p, r, f = (precision_score(y, pred, labels=LINES, average=None),
               recall_score(y, pred, labels=LINES, average=None),
               f1_score(y, pred, labels=LINES, average=None))
    support = cm.sum(axis=1)
    # one wine to show three probabilities: the first in the file with all three above 0.15
    # and two-decimal values that still add up to 1
    ok = (proba > 0.15).all(axis=1) & np.isclose(proba.round(2).sum(axis=1), 1)
    i = int(np.flatnonzero(ok)[0])
    aucs = {}
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    ax.plot([0, 1], [0, 1], color=LIGHT, lw=1.5, ls="--")
    for c, col in zip(LINES, ["#8cb3cf", GRAY, ACCENT]):
        k = LINES.index(c)
        fpr, tpr, _ = roc_curve(y == c, proba[:, k])
        aucs[c] = round(float(roc_auc_score(y == c, proba[:, k])), 3)
        ax.plot(fpr, tpr, color=col, lw=3, label=f"{c} vs the rest: {aucs[c]:.2f}")
    ax.set_xlabel("false-positive rate", fontsize=15)
    ax.set_ylabel("recall (true-positive rate)", fontsize=15)
    ax.tick_params(labelsize=14)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.01)
    ax.set_aspect("equal")
    ax.legend(loc="lower right", fontsize=14, title="class: AUC", title_fontsize=14)
    save(fig, WINE / "roc-ovr.svg")
    NUMBERS["wine"]["three"] = dict(
        labels=LINES,
        confusion=cm.tolist(),
        support=[int(n) for n in support],
        precision=[round(float(v), 2) for v in p],
        recall=[round(float(v), 2) for v in r],
        f1=[round(float(v), 2) for v in f],
        accuracy=round(float((pred == y).mean()), 3),
        f1_micro=round(f1_score(y, pred, average="micro"), 3),
        f1_weighted=round(f1_score(y, pred, average="weighted"), 3),
        f1_macro=round(f1_score(y, pred, average="macro"), 3),
        baseline_medium=round(float((y == "medium").mean()), 3),
        auc=aucs,
        auc_mean=round(float(np.mean(list(aucs.values()))), 3),
        example=dict(row=int(w.index[i]) + 2, grade=int(q[i]), color=str(w["color"].iloc[i]),
                     line=str(y[i]), proba=[round(float(v), 2) for v in proba[i]]),
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--credit", type=Path, required=True)
    ap.add_argument("--wine", type=Path)
    ap.add_argument("--zalaxus", type=Path)
    a = ap.parse_args()
    out = ROOT / "day1" / "figures-numbers.json"
    credit(a.credit)
    boundary(a.credit)
    duration_model(a.credit)
    metric_grid(a.credit)
    model_boundaries(a.credit)
    tree_splits(a.credit)
    if a.wine is None:                      # credit only: keep the other keys
        NUMBERS.update({k: v for k, v in json.loads(out.read_text()).items() if k != "credit"})
    else:
        wine(a.wine)
    if a.zalaxus:
        zalaxus(a.zalaxus)
    out.write_text(json.dumps(NUMBERS, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
