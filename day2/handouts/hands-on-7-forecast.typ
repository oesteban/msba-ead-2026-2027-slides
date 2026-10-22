// ---------------------------------------------------------------------------
// hands-on-7-forecast.typ: the group's sheet for Hands-on 7, 23.10.2026 PM.
//
// One sheet per group of three, both sides. Page 1 is the data card. The core
// (steps 1 to 3, about 25 minutes) follows slide 18 of "Forecasting a time
// series": the group opens a time series forecasting analysis on the Dow Jones
// close dated in Hands-on 6, fills the days without a close with the previous
// value, forecasts seven days ahead on ten time-ordered folds scored by MASE,
// trains the baselines first and the models after, and sets each beside
// Trivial identity. From panel 4 (slide 19) the group runs the same
// session on the casual riders of the bike rentals, then decides what the
// treasury team is told. The previous teacher's 2025 lab forecast the same
// index with no baseline; this sheet puts the baseline first.
//
// The data: dowjones102425.csv (stooq, symbol ^DJI; its licence is not
// recorded: handed out on the learning platform, never republished) and
// bike-rentals.csv (Capital Bikeshare daily rentals, H. Fanaee-T 2013, UCI
// dataset 275, CC BY 4.0), built by 2026-2027/tools/build-datasets.py in the
// private wrapper.
//
// DSS screen paths drafted from the Dataiku DSS 13 documentation (time series
// forecasting) and the previous teacher's 2025 captures of the course server
// (settings, metrics, ETS, ARIMA orders). AUTHORING.md F1: to be run on the
// course server and corrected before printing, in particular the analysis
// presets, the label of the previous-value interpolation, the fold offset, the
// MASE in the metric list, the season length fields, ETS among the algorithms,
// whether Trivial identity is the last value, and where the ARIMA orders are.
// Server: DSS 15.0.0. Verified on: DSS ____ , __.__.2026.
//
// Handed out, kept by the group, never collected: it carries no name.
//
//   typst compile --root ../.. hands-on-7-forecast.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 7 · Day 2 / Afternoon · Group's sheet\nDoes any model beat the last value?",
  date: datetime(year: 2026, month: 10, day: 23),
)

*The case.* The treasury team of Hands-on 6 buys an index fund once a month, on
a day of its choosing, and now asks for next week's closes of the Dow Jones.
Dataiku offers baselines, which fit nothing, and models, which do. A model earns
its place only if it forecasts the closes better than the last close, on the
same days.

#v(4pt)

#block(width: 100%, inset: (x: 6pt, y: 5pt), radius: 2pt, stroke: 1pt + accent)[
  #lbl("Data card · dowjones102425.csv")
  #v(3pt)
  #grid(
    columns: (1fr, 1fr), column-gutter: 10pt,
    [
      *What a row is.* One trading day of the Dow Jones Industrial Average:
      256 rows, no missing value. Used here: `Date`, read as a date in
      Hands-on 6 (step 1.2), and `Close`, the index at the day's end, in
      points. `Open`, `High`, `Low` and `Volume` are left aside.

      *The series forecast.* `Close`, seven days ahead. No other column
      enters: a model fed `Volume` would need next week's volume too.

      *How the rows were chosen.* Every trading day from 1 October 2024 to
      8 October 2025: 373 calendar days, of which 117 have no close (the
      weekends and 11 market holidays).
    ],
    [
      *Its history.* Downloaded for the previous edition of the module and
      used unchanged. A one-day time step adds the 117 days without a close;
      step 1.3 fills each with the previous close.

      *Source and licence.* stooq.com, symbol `^DJI`, daily. No licence is
      recorded: used in class, never republished.

      *From panel 4.* `bike-rentals.csv`, uploaded in Hands-on 6:
      Capital Bikeshare's daily rentals in Washington DC, 2011 and 2012;
      `Casual` counts the riders who were not registered. H. Fanaee-T (2013),
      UCI dataset 275, CC BY 4.0.
    ],
  )
  #v(3pt)
  #set text(size: 7.5pt)
  #table(
    columns: (auto, auto, auto, 1fr, auto), inset: (x: 3pt, y: 2.2pt), stroke: hair,
    [*file*], [*rows*], [*period*], [*series forecast*], [*used in*],
    [`dowjones102425.csv`], [256 trading days], [10.2024 to 10.2025], [`Close`, by `Date`], [steps 1 to 3],
    [`bike-rentals.csv`], [731 days], [2011 and 2012], [`Casual`, by `Date`], [panel 4],
  )
]

#v(5pt)

#panel("Step 1 · Set up the forecast")[
  #step(1, "Open a forecasting analysis")[On the dated Dow Jones dataset of Hands-on 6: #dss("Lab", "Time Series Forecasting"), target `Close`, time variable `Date`, a single time series; *Create*.]
  #v(2pt)
  #step(2, "Set the step and the horizon")[#dss("Design", "General settings"): *Time step* `1` *Day*; *Forecast horizon* `7`; *Skipped time steps in evaluation* `0`.]
  #v(2pt)
  #step(3, "Fill the missing days, split in time")[#dss("Design", "Train / Test Set"): *Numerical interpolation* set to the previous value, never *Linear*, which would borrow the next trading day's close; *K-fold cross-test* ticked, *Number of folds* `10`, *Fold offset* ticked.]
  #v(2pt)
  #step(4, "Score with MASE")[#dss("Design", "Metrics"): *Mean Absolute Scaled Error*.]
]

#v(5pt)

#panel("Step 2 · Train the baselines first")[
  #step(1, "Choose the baselines")[#dss("Design", "Algorithms"): *Trivial identity* and *Seasonal naive*, season length `7`, and nothing else; *Train*.]
  Trivial identity forecasts every day ahead with: #rule(5.4cm)
]

#v(5pt)

#panel("Step 3 · Then the models")[
  #step(1, "Add the models")[#dss("Design", "Algorithms"): *AutoARIMA*, season length `7`, and *ETS*, the baselines unticked; *Train*.]
  #v(2pt)
  #step(2, "Set each beside Trivial identity")[#dss("Results"): each model's MASE and its ±, on the same folds.]
  #table(
    columns: (1.6fr, 1fr, 1fr, 1.8fr), inset: 4pt, stroke: hair,
    [*forecast*], [*MASE*], [*±*], [*below Trivial identity by more than the ±?*],
    [Trivial identity], [], [], [ (the benchmark)],
    [Seasonal naive], [], [], [],
    [AutoARIMA], [], [], [],
    [ETS], [], [], [],
  )
  #step(3, "Read AutoARIMA's orders")[On the AutoARIMA model: #dss("Model information", "ARIMA orders").]
  p, d, q: #rule(2.4cm) #h(8pt) P, D, Q: #rule(2.4cm) #h(8pt) which simple forecast is that? #rule(3.2cm)
]

#v(5pt)

#panel("4 · Run the same session on the casual riders")[
  #step(1, "Open the riders' forecast")[On `bike-rentals.csv` (parse `Date` as in Hands-on 6 if needed): #dss("Lab", "Time Series Forecasting"), target `Casual`, time variable `Date`; the settings of steps 1.2 to 1.4.]
  #v(2pt)
  #step(2, "Train the baselines and ETS")[#dss("Design", "Algorithms"): *Trivial identity*, *Seasonal naive* (season length `7`) and *ETS*; *Train*.]
  #table(
    columns: (1.6fr, 1fr, 1fr, 1.8fr), inset: 4pt, stroke: hair,
    [*`Casual`*], [*MASE*], [*±*], [*below Trivial identity by more than the ±?*],
    [Trivial identity], [], [], [ (the benchmark)],
    [Seasonal naive], [], [], [],
    [ETS], [], [], [],
  )
]

#v(5pt)

#panel("5 · Decide")[
  What do you tell the treasury team about next week's closes? Where did a model beat the last value, and what does that series have that the index lacks?
  #writing(2)
]
