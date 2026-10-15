#!/usr/bin/env python3
"""Render the data figures of the day-1 decks.

Every chart in day1/0[2-5]-*/images is drawn here from the data,
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
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    average_precision_score, confusion_matrix, f1_score, precision_recall_curve,
    precision_score, recall_score, roc_auc_score, roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
AM = ROOT / "day1" / "02-model" / "images"
CV = ROOT / "day1" / "03-cv" / "images"
WINE = ROOT / "day1" / "04-multiclass" / "images"
DL = ROOT / "day1" / "05-dl" / "images"

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

    # 4. ROC and PR side by side
    fpr, tpr, _ = roc_curve(y, p)
    pr, rc, _ = precision_recall_curve(y, p)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2))
    a1.plot(fpr, tpr, color=ACCENT, lw=2.4)
    a1.plot([0, 1], [0, 1], color=GRAY, ls="--", lw=1)
    a1.set_xlabel("false-positive rate\n(good applicants refused)")
    a1.set_ylabel("true-positive rate\n(bad applicants caught)")
    a1.set_title(f"ROC · AUC {roc_auc_score(y, p):.2f}", color=DARK)
    a2.plot(rc, pr, color=CYAN, lw=2.4)
    a2.axhline(y.mean(), color=GRAY, ls="--", lw=1)
    a2.text(0.02, y.mean() + 0.02, f"share of bad = {y.mean():.2f}", color=GRAY, fontsize=11)
    a2.set_xlabel("recall")
    a2.set_ylabel("precision")
    a2.set_ylim(0, 1.02)
    a2.set_title("Precision-recall", color=DARK)
    fig.tight_layout(w_pad=3)
    save(fig, AM / "roc-pr.svg")

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

    # 6. one split is one draw: test AUC over 200 random 50/50 splits, and 5-fold
    aucs = []
    for s in range(200):
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.5, stratify=y, random_state=s)
        m = rf(200).fit(Xtr, ytr)
        aucs.append(roc_auc_score(yte, m.predict_proba(Xte)[:, 1]))
    aucs = np.array(aucs)
    folds = []
    for tr, te in cv.split(X, y):
        m = rf().fit(X.iloc[tr], y[tr])
        folds.append(roc_auc_score(y[te], m.predict_proba(X.iloc[te])[:, 1]))
    NUMBERS["credit"]["split_auc_min"] = round(float(aucs.min()), 3)
    NUMBERS["credit"]["split_auc_max"] = round(float(aucs.max()), 3)
    NUMBERS["credit"]["fold_aucs"] = [round(float(a), 3) for a in folds]
    for name, with_folds in (("split-variability.svg", False), ("split-variability-folds.svg", True)):
        fig, ax = plt.subplots(figsize=(8, 3.4))
        ax.hist(aucs, bins=24, color=LIGHT)
        note = "grey: 200 random 50/50 splits"
        if with_folds:
            for a in folds:
                ax.axvline(a, color=ACCENT, lw=2)
            note += "\nblue: the 5 test folds of one cross-validation"
        ax.set_xlabel("test AUC")
        ax.set_ylabel("random splits")
        ax.text(0.01, 0.97, note, transform=ax.transAxes, ha="left", va="top", fontsize=11, color=DARK)
        save(fig, CV / name)


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


def cv_diagram() -> None:
    fig, ax = plt.subplots(figsize=(9, 3.6))
    k = 5
    for i in range(k):
        for j in range(k):
            test = i == j
            ax.add_patch(plt.Rectangle((j, k - 1 - i), 0.94, 0.8,
                                       color=ACCENT if test else LIGHT))
        ax.text(-0.15, k - 1 - i + 0.4, f"run {i + 1}", ha="right", va="center", fontsize=13)
        ax.text(k + 0.1, k - 1 - i + 0.4, f"score {i + 1}", ha="left", va="center", fontsize=13)
    ax.text(k / 2, -0.45, "the data, cut into 5 folds (each keeps the 70/30 mix)",
            ha="center", fontsize=12, color=GRAY)
    ax.set_xlim(-1.2, k + 1.4)
    ax.set_ylim(-0.7, k)
    ax.axis("off")
    save(fig, CV / "cross-validation.svg")


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
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.bar(counts.index.astype(str), counts.values, color=[ACCENT if q in (5, 6) else LIGHT for q in counts.index])
    for q, n in counts.items():
        ax.text(str(q), n + 40, str(n), ha="center", fontsize=12)
    ax.set_xlabel("quality score (as rated by tasters)")
    ax.set_ylabel("wines")
    save(fig, WINE / "wine-classes.svg")

    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    # the same model with the duplicates left in: copies of a test row sit in training
    yd = w["quality"].to_numpy()
    pd_ = cross_val_predict(rf(), pd.get_dummies(w.drop(columns=["quality"])), yd, cv=cv)
    acc_with_dups = round(float((pd_ == yd).mean()), 3)

    w = w.drop_duplicates()
    y = w["quality"].to_numpy()
    X = pd.get_dummies(w.drop(columns=["quality"]))
    # class 9 has 5 rows (5 after dedup?): stratified 5-fold needs >= 5 per class
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


def network_diagram() -> None:
    """Schematic network: pixels in, three class probabilities out (illustrative values)."""
    fig, ax = plt.subplots(figsize=(10, 4.6))
    layers = [6, 7, 7, 3]
    xs = [0, 2.6, 5.2, 7.8]
    pos = []
    for x, n in zip(xs, layers):
        ys = np.linspace(-(n - 1) / 2, (n - 1) / 2, n) * 0.62
        pos.append([(x, yy) for yy in ys])
    for a, b in zip(pos[:-1], pos[1:]):
        for (x0, y0) in a:
            for (x1, y1) in b:
                ax.plot([x0, x1], [y0, y1], color=LIGHT, lw=0.7, zorder=1)
    for li, layer in enumerate(pos):
        for (x, yy) in layer:
            ax.add_patch(plt.Circle((x, yy), 0.17, color=ACCENT if li == 3 else (CYAN if li == 0 else GRAY),
                                    zorder=2))
    for (x, yy), lab, pr in zip(pos[3], ["cat", "tiger", "lion"], [0.04, 0.15, 0.81]):
        ax.text(x + 0.35, yy, f"{lab}  {pr:.2f}", va="center", fontsize=14, color=DARK)
    ax.text(xs[0], -2.45, "inputs\n(pixel values)", ha="center", va="top", fontsize=13)
    ax.text((xs[1] + xs[2]) / 2, -2.45, "hidden layers\n(learned features)", ha="center", va="top", fontsize=13)
    ax.text(xs[3], -2.45, "softmax output\n(probabilities, sum = 1)", ha="center", va="top", fontsize=13)
    ax.set_xlim(-0.8, 10.2)
    ax.set_ylim(-3.4, 2.3)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, DL / "network.svg")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--credit", type=Path, required=True)
    ap.add_argument("--wine", type=Path)
    ap.add_argument("--zalaxus", type=Path)
    a = ap.parse_args()
    out = ROOT / "day1" / "figures-numbers.json"
    credit(a.credit)
    boundary(a.credit)
    cv_diagram()
    if a.wine is None:                      # credit only: keep the other keys
        NUMBERS.update({k: v for k, v in json.loads(out.read_text()).items() if k != "credit"})
    else:
        network_diagram()
        wine(a.wine)
    if a.zalaxus:
        zalaxus(a.zalaxus)
    out.write_text(json.dumps(NUMBERS, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
