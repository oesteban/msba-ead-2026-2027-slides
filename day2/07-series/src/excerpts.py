#!/usr/bin/env python3
"""Cut the open recordings and the bike rentals into the small files the deck's figures read.

    <python_cmd> -I day2/07-series/src/excerpts.py <datasets-src> <dowjones.csv>

<datasets-src> is the course exchange's `2026-2027/datasets/src/` (private wrapper), holding
`bike-sharing-uci275.zip` (UCI dataset 275, CC BY 4.0), `mitdb-100/` (PhysioNet MIT-BIH
Arrhythmia Database, record 100, ODC-By 1.0), `eegmmidb-S001R02/` (PhysioNet EEG Motor
Movement/Imagery Dataset, run S001R02, ODC-By 1.0) and `ds000114/` (OpenNeuro ds000114, CC0).
<dowjones.csv> is the module's Dow Jones extract, whose licence is not recorded: only
statistics computed from it are written (autocorrelations, weekday means), never its values.

Writes, next to this script: `bike.csv` (the daily rentals with their STL components),
`ecg.csv`, `eeg.csv`, `fmri.csv` (short excerpts) and `numbers.json` (every number the deck
prints from these data). `draw.py` reads them with the standard library alone. Needs numpy,
pandas, statsmodels and nibabel (the interpreter named by `python_cmd` in the wrapper's
`.local.yaml`). Run with `-I`: the inputs are downloaded files.
"""

from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

import nibabel as nb
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

HERE = Path(__file__).resolve().parent
WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def acf(x, nlags: int) -> list[float]:
    """The sample autocorrelation, as Hyndman and Athanasopoulos define it (whole-series mean)."""
    x = np.asarray(x, dtype=float)
    x = x - x.mean()
    den = (x * x).sum()
    return [round(float((x[k:] * x[:len(x) - k]).sum() / den), 3) for k in range(nlags + 1)]


def strength(r) -> float:
    """Seasonal strength of an STL fit: max(0, 1 - Var(R) / Var(S + R))."""
    return round(max(0.0, 1 - np.var(r.resid) / np.var(r.seasonal + r.resid)), 2)


def bike(src: Path) -> dict:
    with zipfile.ZipFile(src / "bike-sharing-uci275.zip") as z:
        d = pd.read_csv(io.BytesIO(z.read("day.csv")), parse_dates=["dteday"])
    d = d.rename(columns={"dteday": "date", "cnt": "rentals"}).set_index("date")
    assert len(d) == 731 and (d.casual + d.registered == d.rentals).all()
    total = STL(d.rentals.astype(float), period=7, robust=True).fit()
    # slide 6's trend-cycle: the same fit with its trend smoothed over 91 days, about a season
    slow = STL(d.rentals.astype(float), period=7, trend=91, robust=True).fit()
    cas = STL(d.casual.astype(float), period=7, robust=True).fit()
    reg = STL(d.registered.astype(float), period=7, robust=True).fit()
    out = pd.DataFrame({"rentals": d.rentals, "casual": d.casual, "registered": d.registered,
                        "rentals_trend": slow.trend.round(1), "casual_trend": cas.trend.round(1),
                        "casual_season": cas.seasonal.round(1), "casual_remainder": cas.resid.round(1)})
    out.index = out.index.strftime("%Y-%m-%d")
    out.to_csv(HERE / "bike.csv", index_label="date")
    wd = d.index.day_name()
    weekend = d.index.dayofweek >= 5
    months = []
    for (y, m), g in d.groupby([d.index.year, d.index.month]):
        we = g.index.dayofweek >= 5
        months.append({"month": f"{y}-{m:02d}", "weekday": round(float(g.casual[~we].mean()), 1),
                       "weekend": round(float(g.casual[we].mean()), 1)})
    by = lambda col: {k: round(float(v)) for k, v in d[col].groupby(wd).mean().reindex(WEEK).items()}
    sd = lambda col: {k: round(float(v)) for k, v in d[col].groupby(wd).std().reindex(WEEK).items()}
    lowest = d.rentals.idxmin()
    return {
        "days": len(d), "first": str(d.index.min().date()), "last": str(d.index.max().date()),
        "year_mean": {str(y): round(float(v)) for y, v in d.rentals.groupby(d.index.year).mean().items()},
        "month_mean": [round(float(v)) for v in d.rentals.groupby(d.index.month).mean()],
        "month_sd": [round(float(v)) for v in d.rentals.groupby(d.index.month).std()],
        "weekday_mean": {"rentals": by("rentals"), "casual": by("casual"), "registered": by("registered")},
        "weekday_sd": {"rentals": sd("rentals"), "casual": sd("casual"), "registered": sd("registered")},
        "casual_by_month": months,
        "casual_weekend_ratio": [round(min(m["weekend"] / m["weekday"] for m in months), 1),
                                 round(max(m["weekend"] / m["weekday"] for m in months), 1)],
        "stl_strength": {"rentals": strength(total), "casual": strength(cas), "registered": strength(reg)},
        "acf_rentals": acf(d.rentals, 28), "acf_casual": acf(d.casual, 28),
        "acf_rentals_change": acf(d.rentals.diff().dropna(), 28),
        "acf_casual_week_change": acf(d.casual.diff(7).dropna(), 28),
        "bound": round(1.96 / np.sqrt(len(d)), 3),
        "lag1_corr": round(float(d.rentals.corr(d.rentals.shift(1))), 2),
        "lowest": {"date": str(lowest.date()), "rentals": int(d.rentals.min())},
        "weekend_share_of_casual": round(float(d.casual[weekend].sum() / d.casual.sum()), 2),
    }


def wfdb_212(src: Path, rec: str):
    """Read a two-signal MIT format 212 record and its header; physical units (mV)."""
    head = (src / f"{rec}.hea").read_text().split("\n")
    _, nsig, fs, n = head[0].split()[:4]
    sig = [ln.split() for ln in head[1:1 + int(nsig)]]
    raw = np.fromfile(src / f"{rec}.dat", dtype=np.uint8).reshape(-1, 3).astype(np.int32)
    a = raw[:, 0] | ((raw[:, 1] & 0x0F) << 8)
    b = raw[:, 2] | ((raw[:, 1] & 0xF0) << 4)
    a, b = np.where(a > 2047, a - 4096, a), np.where(b > 2047, b - 4096, b)
    chans = []
    for x, s in zip((a, b), sig):
        gain, zero = float(s[2].split("(")[0].split("/")[0]), int(s[4])
        chans.append((x - zero) / gain)
    return int(fs), [s[-1] for s in sig], chans


def beats(src: Path, rec: str) -> np.ndarray:
    """Sample numbers of the beat annotations of an MIT annotation file."""
    w = np.fromfile(src / f"{rec}.atr", dtype="<u2")
    t, i, out = 0, 0, []
    beat = set(range(1, 14)) | {30, 31, 34, 35, 38, 41}
    while i < len(w):
        code, val = int(w[i]) >> 10, int(w[i]) & 0x3FF
        i += 1
        if code == 0 and val == 0:
            break
        if code == 59:                      # SKIP: a 32-bit interval follows
            t += (int(w[i]) << 16) | int(w[i + 1])
            i += 2
        elif code == 63:                    # AUX: val bytes of text, padded to a word
            i += (val + 1) // 2
        elif code in (60, 61, 62):          # NUM, SUB, CHN
            pass
        else:
            t += val
            if code in beat:
                out.append(t)
    return np.array(out)


def ecg(src: Path) -> dict:
    fs, names, chans = wfdb_212(src / "mitdb-100", "100")
    x = chans[names.index("MLII")]
    seg = x[: 10 * fs]
    pd.DataFrame({"time_s": np.round(np.arange(len(seg)) / fs, 4), "mv": np.round(seg, 3)}).to_csv(
        HERE / "ecg.csv", index=False)
    r = acf(seg, 2 * fs)
    lo = int(0.4 * fs)                          # past the beat's own width
    peak = lo + int(np.argmax(r[lo:]))
    b = beats(src / "mitdb-100", "100")
    rr = np.diff(b[b < len(seg)]) / fs
    rr_all = np.diff(b) / fs
    return {"fs": fs, "lead": "MLII", "seconds": 10, "acf_step": 1, "acf": r,
            "peak_lag_s": round(peak / fs, 3), "peak_acf": r[peak], "peak_bpm": round(60 * fs / peak),
            "rr_mean_s": round(float(rr.mean()), 3), "beats_in_excerpt": int((b < len(seg)).sum()),
            "rr_mean_s_record": round(float(rr_all.mean()), 3), "minutes": round(len(x) / fs / 60, 1)}


def edf(path: Path):
    raw = path.read_bytes()
    nrec, dur, ns = int(raw[236:244]), float(raw[244:252]), int(raw[252:256])
    f = lambda off, w: [raw[off + i * w: off + (i + 1) * w].decode().strip() for i in range(ns)]
    o = 256
    labels = f(o, 16); o += 16 * ns
    o += 80 * ns                                # transducer
    o += 8 * ns                                 # physical dimension
    pmin = [float(v) for v in f(o, 8)]; o += 8 * ns
    pmax = [float(v) for v in f(o, 8)]; o += 8 * ns
    dmin = [float(v) for v in f(o, 8)]; o += 8 * ns
    dmax = [float(v) for v in f(o, 8)]; o += 8 * ns
    o += 80 * ns                                # prefiltering
    spr = [int(v) for v in f(o, 8)]; o += 8 * ns
    o += 32 * ns
    data = np.frombuffer(raw[o:o + nrec * sum(spr) * 2], dtype="<i2").reshape(nrec, sum(spr))
    sigs, at = {}, 0
    for k in range(ns):
        d = data[:, at:at + spr[k]].reshape(-1).astype(float)
        sigs[labels[k].rstrip(".")] = (d - dmin[k]) * (pmax[k] - pmin[k]) / (dmax[k] - dmin[k]) + pmin[k]
        at += spr[k]
    return spr[0] / dur, sigs


def eeg(src: Path) -> dict:
    fs, sigs = edf(src / "eegmmidb-S001R02" / "S001R02.edf")
    fs = int(fs)
    name = "Oz"
    x = sigs[name]
    seg = x[10 * fs: 14 * fs] - x[10 * fs: 14 * fs].mean()
    pd.DataFrame({"time_s": np.round(np.arange(len(seg)) / fs, 4), "uv": np.round(seg, 2)}).to_csv(
        HERE / "eeg.csv", index=False)
    spec = np.abs(np.fft.rfft(x - x.mean())) ** 2
    freq = np.fft.rfftfreq(len(x), 1 / fs)
    band = (freq > 2) & (freq < 40)
    return {"fs": fs, "channel": name, "run": "S001R02, eyes closed", "excerpt_s": [10, 14],
            "peak_hz": round(float(freq[band][np.argmax(spec[band])]), 1), "channels": len(sigs)}


def fmri(src: Path) -> dict:
    from scipy.stats import gamma
    img = nb.load(src / "ds000114" / "sub-01_ses-test_task-fingerfootlips_bold.nii.gz")
    data = np.asarray(img.dataobj, dtype=float)
    tr = float(img.header.get_zooms()[3])
    T = data.shape[-1]
    t = np.arange(T) * tr
    ht = np.arange(0, 32, tr)
    hrf = gamma.pdf(ht, 6) - gamma.pdf(ht, 16) / 6
    box = np.zeros(T)
    for on in np.arange(70, T * tr, 90):        # the lips blocks: 15 s, every 90 s (events file)
        box[(t >= on) & (t < on + 15)] = 1
    keep = slice(4, None)                       # the first volumes, before the signal settles
    reg = np.convolve(box, hrf / hrf.sum())[:T][keep]
    mean = data.mean(-1)
    mask = mean > 0.3 * np.percentile(mean, 99)
    X = data[mask][:, keep]
    B = np.c_[np.ones(T - 4), t[keep]]
    Xd = X - (X @ np.linalg.pinv(B).T) @ B.T
    rd = reg - B @ (np.linalg.pinv(B) @ reg)
    r = (Xd @ rd) / (np.linalg.norm(Xd, axis=1) * np.linalg.norm(rd) + 1e-9)
    i = int(np.argmax(r))
    vox = np.argwhere(mask)[i]
    y = data[tuple(vox)][keep]
    pd.DataFrame({"time_s": t[keep], "bold": np.round(y, 1), "lips": box[keep].astype(int)}).to_csv(
        HERE / "fmri.csv", index=False)
    return {"tr_s": tr, "volumes": T, "kept_from_volume": 4, "voxel": vox.tolist(), "r": round(float(r[i]), 2),
            "voxels_above_0_5": int((r > 0.5).sum()), "shape": list(data.shape[:3]),
            "voxel_mm": [round(float(z), 1) for z in img.header.get_zooms()[:3]]}


def dowjones(path: Path) -> dict:
    d = pd.read_csv(path, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    c = d.Close
    ch = c.diff().dropna()
    g = ch.groupby(ch.index.day_name())
    return {
        "rows": len(d), "first": str(d.index.min().date()), "last": str(d.index.max().date()),
        "acf_close": acf(c, 10), "acf_change": acf(ch, 10),
        "bound_close": round(1.96 / np.sqrt(len(c)), 3), "bound_change": round(1.96 / np.sqrt(len(ch)), 3),
        "corr_close_lag1": round(float(c.corr(c.shift(1))), 3),
        "corr_change_prev": round(float(ch.corr(ch.shift(1))), 3),
        "mean_abs_change": round(float(ch.abs().mean()), 1),
        "weekday": {k: {"mean": round(float(g.mean()[k]), 1), "sd": round(float(g.std()[k]), 1),
                        "count": int(g.count()[k])} for k in WEEK[:5]},
        "calendar_days": len(pd.date_range(d.index.min(), d.index.max())),
    }


def main(src: Path, dj: Path) -> int:
    numbers = {"bike": bike(src), "ecg": ecg(src), "eeg": eeg(src), "fmri": fmri(src), "dowjones": dowjones(dj)}
    (HERE / "numbers.json").write_text(json.dumps(numbers, indent=1) + "\n", encoding="utf-8")
    for k, v in numbers.items():
        print(k, {a: b for a, b in v.items() if not isinstance(b, (list, dict)) or a in ("weekday", "year_mean")})
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
