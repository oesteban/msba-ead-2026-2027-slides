// ---------------------------------------------------------------------------
// hands-on-7-window.typ: the fallback group's sheet for Hands-on 7, 23.10.2026
// PM, for a server with no code environment for time series forecasting.
//
// On 23.10.2026 the course server's Lab could not train a forecast: no code
// environment offers GluonTS ("No module named 'gluonts'"). This sheet replaces
// hands-on-7-forecast.typ until one does: the same case, data and lesson, with
// the Window recipe instead of the Lab. One sheet per group of three, both
// sides. Page 1 is the data card. The core (steps 1 to 3, about 25 minutes)
// follows slide 21 of "Forecasting a time series": the group lags the Dow
// Jones close five trading days, builds four one-day-ahead forecasts from the
// days before (the last close, the same weekday last week, the average of the
// last five, the last close plus the last change), and sets each one's mean
// absolute error beside the last close's, on the same days. From panel 4
// (slide 21 too) the group builds the same forecasts for the casual riders of
// the bike rentals, then decides what the treasury team is told.
//
// The data: dowjones102425.csv (stooq, symbol ^DJI; its licence is not
// recorded: handed out on the learning platform, never republished) and
// bike-rentals.csv (Capital Bikeshare daily rentals, H. Fanaee-T 2013, UCI
// dataset 275, CC BY 4.0), built by 2026-2027/tools/build-datasets.py in the
// private wrapper.
//
// AUTHORING.md F1: drafted, not run. To check on the course server before
// printing: the Window recipe's labels as in Hands-on 6 and the names of its
// lag columns (the sheet writes them as ‹lag 1› to ‹lag 7›), the Prepare
// processor "Remove rows where cell is empty", and the mean under a column's
// Analyze. Server: DSS 15.0.0. Verified on: DSS ____ , __.__.2026.
//
// Handed out, kept by the group, never collected: it carries no name.
//
//   typst compile --root ../.. hands-on-7-window.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 7 · Day 2 / Afternoon · Group's sheet\nDoes any forecast beat the last value?",
  date: datetime(year: 2026, month: 10, day: 23),
)

*The case.* The treasury team of Hands-on 6 buys an index fund once a month, on
a day of its choosing, and now asks whether anything forecasts tomorrow's close
of the Dow Jones better than today's close. Four simple forecasts can be built
from the days before. One earns its place only if its errors are smaller than
the last close's, on the same days.

#v(4pt)

#block(width: 100%, inset: (x: 6pt, y: 5pt), radius: 2pt, stroke: 1pt + accent)[
  #lbl("Data card · dowjones102425.csv")
  #v(3pt)
  #grid(
    columns: (1fr, 1fr), column-gutter: 10pt,
    [
      *What a row is.* One trading day of the Dow Jones Industrial Average:
      256 rows, no missing value. Used here: `Date`, read as a date on
      upload in Hands-on 6, and `Close`, the index at the day's end, in
      points. `Open`, `High`, `Low` and `Volume` are left aside.

      *The series forecast.* `Close`, one trading day ahead, from the closes
      before it. The days before are trading days: a Monday's day before is
      the Friday.

      *How the rows were chosen.* Every trading day from 1 October 2024 to
      8 October 2025, with no weekend and no market holiday.
    ],
    [
      *Its history.* Downloaded for the previous edition of the module and
      used unchanged.

      *Source and licence.* stooq.com, symbol `^DJI`, daily. No licence is
      recorded: used in class, never republished.

      *From panel 4.* `bike-rentals.csv`, uploaded in Hands-on 6:
      Capital Bikeshare's daily rentals in Washington DC, every day of 2011
      and 2012, so the same day last week is seven rows back; `Casual` counts
      the riders who were not registered. H. Fanaee-T (2013), UCI dataset
      275, CC BY 4.0.
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

#panel("Step 1 · Put each day beside the five before")[
  #step(1, "Lag the close")[On the Dow Jones dataset uploaded in Hands-on 6: #dss("+ Recipe", "Window"). In *Windows definitions*, order the rows by `Date`, ascending; in *Aggregations*, on `Close`, tick *Lag* with offsets `1,2,3,4,5`; *Run*.]
  Names of the lag-1 and lag-5 columns: #rule(6cm)
  #v(2pt)
  #step(2, "Keep the days that have five days before")[On the lagged dataset: #dss("+ Recipe", "Prepare"), a step *Remove rows where cell is empty* on the lag-5 column, so that every forecast is scored on the same days.]
  Rows left: #rule(1.6cm)
]

#v(5pt)

#panel("Step 2 · Build four forecasts and their errors")[
  #step(1, "Write each forecast's error")[In the same Prepare recipe, four steps *Formula*, one per forecast; ‹lag 1› stands for the lag-1 column's name, and so on. *Run*.]
  #table(
    columns: (auto, 1.5fr, 2.6fr), inset: 4pt, stroke: hair,
    [*new column*], [*the forecast of today's close*], [*formula*],
    [`err_last`], [the last close], [`abs(Close - ‹lag 1›)`],
    [`err_week`], [the same weekday last week], [`abs(Close - ‹lag 5›)`],
    [`err_avg`], [the average of the last five], [`abs(Close - (‹lag 1› + ‹lag 2› + ‹lag 3› + ‹lag 4› + ‹lag 5›) / 5)`],
    [`err_trend`], [the last close plus the last change], [`abs(Close - (2 * ‹lag 1› - ‹lag 2›))`],
  )
  #step(2, "Read each mean error")[On the prepared dataset, on each `err_` column: its header, *Analyze*, the *Mean*.]
]

#v(5pt)

#panel("Step 3 · Set each beside the last close")[
  #step(1, "Divide by the last close's error")[Below 1, a forecast beats the last close; this is the scaling MASE uses.]
  #table(
    columns: (2fr, 1.2fr, 1.2fr, 1.4fr), inset: 4pt, stroke: hair,
    [*forecast*], [*mean absolute error*], [*÷ `err_last`'s*], [*beats the last close?*],
    [the last close], [], [1], [(the benchmark)],
    [the same weekday last week], [], [], [],
    [the average of the last five], [], [], [],
    [the last close plus the last change], [], [], [],
  )
  Does any forecast beat the last close? Why might the index behave so?
  #writing(1)
]

#v(5pt)

#panel("4 · Build the same forecasts for the casual riders")[
  #step(1, "Lag and score the riders")[On the bike rentals dataset uploaded in Hands-on 6: #dss("+ Recipe", "Window") ordered by `Date`, on `Casual`, *Lag* with offsets `1,2,3,4,5,6,7`; then #dss("+ Recipe", "Prepare"): *Remove rows where cell is empty* on the lag-7 column, and `err_last` = `abs(Casual - ‹lag 1›)`, `err_week` = `abs(Casual - ‹lag 7›)`, `err_avg` = the distance to the average of the seven lags; *Run*.]
  #table(
    columns: (2fr, 1.2fr, 1.2fr, 1.4fr), inset: 4pt, stroke: hair,
    [*`Casual`*], [*mean absolute error*], [*÷ `err_last`'s*], [*beats the last value?*],
    [the last value], [], [1], [(the benchmark)],
    [the same day last week], [], [], [],
    [the average of the last seven], [], [], [],
  )
]

#v(5pt)

#panel("5 · Decide")[
  What do you tell the treasury team about tomorrow's close? Where did a forecast beat the last value, and what does that series have that the index lacks?
  #writing(2)
]
