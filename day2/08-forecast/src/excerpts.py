#!/usr/bin/env python3
"""Compute every number the forecasting deck prints, and the small file its figures read.

    <python_cmd> -I day2/08-forecast/src/excerpts.py <datasets-src> <dowjones.csv>

<datasets-src> is the course exchange's `2026-2027/datasets/src/` (private wrapper), holding
`bike-sharing-uci275.zip` (Capital Bikeshare daily rentals, UCI dataset 275, CC BY 4.0).
<dowjones.csv> is the module's Dow Jones extract, whose licence is not recorded: only
statistics computed from it are written (scores, folds won, orders, mean errors), never its
values.

The scores follow the K-fold cross-test of Dataiku DSS as its documentation describes it: the
last horizon is the first test set, each next one is shifted back by one horizon, and the fold
offset adds one more horizon between them; every fold trains on all the days before its test
set. The series is put on a one-day step, missing days repeating the previous value; MASE
divides each fold's mean absolute error by the mean absolute one-step change of its training
days. The models are fitted with statsmodels, not by DSS: the server's own scores are read in
class.

Writes, next to this script: `bike.csv` (the daily total rentals) and `numbers.json`.
`draw.py` reads them with the standard library alone. Needs numpy, pandas and statsmodels
(the interpreter named by `python_cmd` in the wrapper's `.local.yaml`). Run with `-I`: the
inputs are downloaded files.
"""

from __future__ import annotations

import io
import itertools
import json
import sys
import warnings
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from statsmodels.tsa.stattools import kpss

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
H, K, SEASON = 7, 10, 7          # horizon in days, folds, weekly season
ORIGIN = "2011-04-30"            # the last training day of every drawn forecast
SANDY = "2012-10-27"             # the last training day before the hurricane week


# --- forecasts ----------------------------------------------------------------------
def f_mean(tr, h):
    return np.repeat(tr.mean(), h)


def f_naive(tr, h):
    return np.repeat(tr.iloc[-1], h)


def f_snaive(tr, h, m=SEASON):
    return np.array([tr.iloc[-m + (i % m)] for i in range(h)])


def f_drift(tr, h):
    slope = (tr.iloc[-1] - tr.iloc[0]) / (len(tr) - 1)
    return tr.iloc[-1] + slope * np.arange(1, h + 1)


def ets_fit(tr, error, trend, damped, seasonal):
    return ETSModel(tr.astype(float).reset_index(drop=True), error=error, trend=trend, damped_trend=damped,
                    seasonal=seasonal, seasonal_periods=SEASON if seasonal else None).fit(disp=False)


def f_ets(tr, h, forms=None):
    """ETS chosen by AICc among the stable forms (Hyndman and Athanasopoulos 2021, section 8.6)."""
    positive = bool((tr > 0).all())
    best = None
    for error, (trend, damped), seasonal in itertools.product(
            ("add", "mul") if positive else ("add",), ((None, False), ("add", False), ("add", True)),
            (None, "add", "mul") if positive else (None, "add")):
        if error == "add" and seasonal == "mul":
            continue
        try:
            r = ets_fit(tr, error, trend, damped, seasonal)
        except Exception:
            continue
        if np.isfinite(r.aicc) and (best is None or r.aicc < best[0]):
            best = (r.aicc, (error, trend, damped, seasonal), r)
    if forms is not None:
        e, t, dmp, s = best[1]
        forms.append("ETS(" + {"add": "A", "mul": "M"}[e] + "," + ("N" if t is None else "Ad" if dmp else "A") + ","
                     + {None: "N", "add": "A", "mul": "M"}[s] + ")")
    return np.asarray(best[2].forecast(h))


def ndiffs(x) -> int:
    """Differences until the KPSS test no longer rejects at 5%, at most two (section 9.1)."""
    for d in range(3):
        y = np.diff(x, n=d) if d else x
        if kpss(y, regression="c", nlags="auto")[1] >= 0.05:
            return d
    return 2


def f_arima(tr, h, orders=None):
    """ARIMA with a weekly seasonal part, the order of differencing by KPSS, the rest by AICc."""
    x = tr.astype(float).to_numpy()
    d = ndiffs(x)
    best = None
    for p, q, P, Q in itertools.product(range(3), range(3), range(2), range(2)):
        try:
            r = ARIMA(x, order=(p, d, q), seasonal_order=(P, 0, Q, SEASON),
                      trend="c" if d == 0 else "n").fit()
        except Exception:
            continue
        if np.isfinite(r.aicc) and (best is None or r.aicc < best[0]):
            best = (r.aicc, (p, d, q, P, Q), r)
    if orders is not None:
        orders.append("({},{},{})({},0,{})7".format(*best[1]))
    return np.asarray(best[2].forecast(h))


# --- folds --------------------------------------------------------------------------
def origins(n: int, h: int = H, k: int = K, offset: bool = True) -> list[int]:
    """First test index of each fold, oldest first, as DSS's K-fold cross-test lays them out."""
    stride = 2 * h if offset else h
    return [n - h - stride * j for j in range(k)][::-1]


def cross_test(y: pd.Series, methods: dict) -> dict:
    org = origins(len(y))
    out = {m: {"mase": [], "mae": [], "mape": []} for m in methods}
    for o in org:
        tr, te = y.iloc[:o], y.iloc[o:o + H].to_numpy(dtype=float)
        scale = float(np.mean(np.abs(np.diff(tr.to_numpy(dtype=float)))))
        for m, f in methods.items():
            e = te - f(tr, H)
            out[m]["mae"].append(float(np.mean(np.abs(e))))
            out[m]["mape"].append(float(100 * np.mean(np.abs(e) / te)))
            out[m]["mase"].append(float(np.mean(np.abs(e)) / scale))
    base = np.array(out["naive"]["mase"])
    res = {"folds": K, "horizon": H, "offset": True, "test_from": str(y.index[org[0]].date()),
           "test_to": str(y.index[-1].date())}
    for m, s in out.items():
        v = np.array(s["mase"])
        res[m] = {"mase": round(float(v.mean()), 2), "pm": round(float(2 * v.std(ddof=1)), 2),
                  "folds_mase": [round(float(a), 2) for a in v],
                  "wins": int((v < base).sum()) if m != "naive" else None,
                  "mae": round(float(np.mean(s["mae"])), 1), "mape": round(float(np.mean(s["mape"])), 2)}
    return res


# --- data ---------------------------------------------------------------------------
def read_bike(src: Path) -> pd.DataFrame:
    with zipfile.ZipFile(src / "bike-sharing-uci275.zip") as z:
        d = pd.read_csv(io.BytesIO(z.read("day.csv")), parse_dates=["dteday"])
    d = d.rename(columns={"dteday": "date", "cnt": "rentals"}).set_index("date")
    assert len(d) == 731 and (d.casual + d.registered == d.rentals).all()
    return d


def bike(d: pd.DataFrame) -> dict:
    y = d.rentals.astype(float)
    out = pd.DataFrame({"rentals": d.rentals})
    out.index = out.index.strftime("%Y-%m-%d")
    out.to_csv(HERE / "bike.csv", index_label="date")
    # the four simple forecasts, two weeks from ORIGIN
    tr = y.loc[:ORIGIN]
    simple = {k: [round(float(v), 1) for v in f(tr, 14)]
              for k, f in (("mean", f_mean), ("naive", f_naive), ("snaive", f_snaive), ("drift", f_drift))}
    # three ETS forms on the same history, their point forecasts only
    ets = {}
    for key, args in (("ANN", ("add", None, False, None)), ("AAN", ("add", "add", False, None)),
                      ("AAA", ("add", "add", False, "add"))):
        ets[key] = [round(float(v), 1) for v in ets_fit(tr, *args).forecast(14)]
    # what ARIMA's orders do to a forecast: the same history, 42 days ahead, each order fitted
    arima = {}
    for key, order, trend, seas in (("000c", (0, 0, 0), "c", (0, 0, 0, 0)), ("100c", (1, 0, 0), "c", (0, 0, 0, 0)),
                                    ("010", (0, 1, 0), "n", (0, 0, 0, 0)), ("010d", (0, 1, 0), "t", (0, 0, 0, 0)),
                                    ("110", (1, 1, 0), "n", (0, 0, 0, 0)), ("011", (0, 1, 1), "n", (0, 0, 0, 0)),
                                    ("000s010", (0, 0, 0), "n", (0, 1, 0, SEASON)),
                                    ("011s011", (0, 1, 1), "n", (0, 1, 1, SEASON))):
        m = ARIMA(tr.to_numpy(), order=order, trend=trend, seasonal_order=seas).fit()
        arima[key] = {"forecast": [round(float(v), 1) for v in m.forecast(42)],
                      "params": {k: round(float(v), 3) for k, v in zip(m.param_names, m.params)}}
    # the hurricane week, forecast by the last value
    tr2 = y.loc[:SANDY]
    te = y.loc[SANDY:].iloc[1:8]
    e = te.to_numpy() - tr2.iloc[-1]
    steps = np.abs(np.diff(tr2.to_numpy()))
    return {
        "days": len(d), "first": str(d.index.min().date()), "last": str(d.index.max().date()),
        "origin": ORIGIN, "simple": simple, "ets": ets, "arima": arima,
        "sandy": {"origin": SANDY, "last": int(tr2.iloc[-1]), "train_days": len(tr2),
                  "days": [str(t.date()) for t in te.index], "actual": [int(v) for v in te],
                  "abs_error": [int(round(abs(v))) for v in e],
                  "pct_error": [round(float(100 * abs(a) / b), 1) for a, b in zip(e, te)],
                  "mae": round(float(np.mean(np.abs(e))), 1), "rmse": round(float(np.sqrt(np.mean(e ** 2))), 1),
                  "mape": round(float(100 * np.mean(np.abs(e) / te.to_numpy())), 1),
                  "scale": round(float(steps.mean()), 1),
                  "mase": round(float(np.mean(np.abs(e)) / steps.mean()), 2),
                  "steps_recent": [int(v) for v in steps[-56:]]},
        "lowest": {"date": str(y.idxmin().date()), "rentals": int(y.min())},
    }


def casual(d: pd.DataFrame) -> dict:
    forms: list[str] = []
    res = cross_test(d.casual.astype(float), {"naive": f_naive, "snaive": f_snaive,
                                              "ets": lambda tr, h: f_ets(tr, h, forms)})
    res["ets_forms"] = dict(Counter(forms))
    return res


def dowjones(path: Path) -> dict:
    d = pd.read_csv(path, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    cal = d.Close.astype(float).asfreq("D")
    y = cal.ffill()
    forms: list[str] = []
    orders: list[str] = []
    res = cross_test(y, {"naive": f_naive, "snaive": f_snaive, "ets": lambda tr, h: f_ets(tr, h, forms),
                         "arima": lambda tr, h: f_arima(tr, h, orders)})
    res["ets_forms"] = dict(Counter(forms))
    res["arima_orders"] = dict(Counter(orders))
    res.update({"rows": len(d), "first": str(d.index.min().date()), "last": str(d.index.max().date()),
                "calendar_days": len(cal), "filled_days": int(cal.isna().sum())})
    return res


def main(src: Path, dj: Path) -> int:
    d = read_bike(src)
    numbers = {"bike": bike(d), "casual": casual(d), "dowjones": dowjones(dj)}
    (HERE / "numbers.json").write_text(json.dumps(numbers, indent=1) + "\n", encoding="utf-8")
    for k, v in numbers.items():
        print(k, {a: (b if not isinstance(b, dict) else {c: e for c, e in b.items() if c != "folds_mase"})
                  for a, b in v.items() if not (k == "bike" and a in ("simple", "ets", "arima", "sandy"))})
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
