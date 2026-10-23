// ---------------------------------------------------------------------------
// hands-on-6-dowjones.typ: the group's sheet for Hands-on 6, 23.10.2026 PM.
//
// One sheet per group of three, both sides. Page 1 is the data card. The core
// (steps 1 to 3, about 22 minutes) and the tail follow Column types, slide 24 of
// "Reading a time series", and are debriefed live: the group charts the Dow Jones
// close, puts each trading day beside the two before with the Window recipe,
// correlates the close with the day before and the change with the change
// before, averages the change by weekday against its spread, and answers
// the treasury team. From panel 4 the group runs the same check on the bike
// rentals, by weekday and by month, to see what a pattern that stands out of
// its spread looks like. The
// index is the previous teacher's 2025 file; his lab forecast it, which this
// course does after the break.
//
// The data: dowjones102425.csv (stooq, symbol ^DJI; its licence is not
// recorded: handed out on the learning platform, never republished) and
// bike-rentals.csv (Capital Bikeshare daily rentals, H. Fanaee-T 2013, UCI
// dataset 275, CC BY 4.0), built by 2026-2027/tools/build-datasets.py in the
// private wrapper.
//
// DSS screen paths drafted from the Dataiku DSS documentation (Window recipe,
// Prepare processors, Group recipe, Statistics worksheets) and the previous
// teacher's 2025 captures of the course server (date parsing). AUTHORING.md
// F1: to be run on the course server and corrected before printing, in
// particular the Window recipe's lag labels and
// output column names, the Statistics correlation card and its Pearson
// setting, and the Group
// recipe's standard deviation. `Date` is read as a date on upload (meaning
// "Date only", Oscar, 23.10.2026): no parsing step. Server: DSS 15.0.0. Verified on: DSS ____ ,
// __.__.2026.
//
// Handed out, kept by the group, never collected: it carries no name.
//
//   typst compile --root ../.. hands-on-6-dowjones.typ
// ---------------------------------------------------------------------------
#import "../../templates/ead-worksheet.typ": *

#show: worksheet.with(
  title: "Hands-on 6 · Day 2 / Afternoon · Group's sheet\nDo the past days tell the next one?",
  date: datetime(year: 2026, month: 10, day: 23),
)

*The case.* A treasury team buys an index fund once a month, on a day of its
choosing. If the Dow Jones's past days told whether the next trading day will
be lower, the team could pick a cheaper day. Before anyone builds a forecast,
read the series: how much does each day resemble the one before, and does any
weekday stand out?

#v(4pt)

#block(width: 100%, inset: (x: 6pt, y: 5pt), radius: 2pt, stroke: 1pt + accent)[
  #lbl("Data card · dowjones102425.csv")
  #v(3pt)
  #grid(
    columns: (1fr, 1fr), column-gutter: 10pt,
    [
      *What a row is.* One trading day of the Dow Jones Industrial Average.
      256 rows, 6 columns, no missing value: `Date` (year-month-day), `Open`,
      `High`, `Low` and `Close`, the index's first, highest, lowest and last
      price of the day in points, and `Volume`, the shares traded.

      *The series read.* `Close`, the index at the day's end. There is no
      target: this hands-on reads the series, it trains no model.

      *How the rows were chosen.* Every trading day from 1 October 2024 to
      8 October 2025: no weekend, and 11 weekdays absent, the market's
      holidays (25 December, 1 January, 4 July, ...).
    ],
    [
      *Its history.* Downloaded for the previous edition of the module and
      used unchanged. A day's change is its close minus the previous trading
      day's: after a weekend, Monday minus Friday.

      *Source and licence.* stooq.com, symbol `^DJI`, daily. No licence is
      recorded: used in class, never republished.

      *From panel 4.* `bike-rentals.csv`: Capital Bikeshare's daily
      rentals in Washington DC, every day of 2011 and 2012; `Casual` and
      `Registered` riders add up to `Rentals`. H. Fanaee-T (2013), UCI
      dataset 275, CC BY 4.0.
    ],
  )
  #v(3pt)
  #set text(size: 7.5pt)
  #table(
    columns: (auto, auto, auto, 1fr, auto), inset: (x: 3pt, y: 2.2pt), stroke: hair,
    [*file*], [*rows*], [*period*], [*columns*], [*used in*],
    [`dowjones102425.csv`], [256 trading days], [10.2024 to 10.2025], [`Date`, `Open`, `High`, `Low`, `Close`, `Volume`], [steps 1 to 3],
    [`bike-rentals.csv`], [731 days], [2011 and 2012], [`Date`, `Rentals`, `Casual`, `Registered`], [panel 4],
  )
]

#v(5pt)

#panel("Step 1 · Load and chart the index")[
  #step(1, "Upload the index")[In a new project: #dss("+ Dataset", "Upload your files"), `dowjones102425.csv`.]
  Rows: #rule(1.6cm) #h(8pt) first and last `Date`: #rule(3.6cm)
  #v(2pt)
  #step(2, "Check that the date is a date")[In the dataset, under each column's name, Dataiku shows the kind of value it found there. Under `Date` it should read *Date only* (it may show *Text* for a moment): the chart's time axis and the weekday in step 2.2 need a date.]
  #v(2pt)
  #step(3, "Chart the close")[On the dataset: #dss("Charts"), a *Lines* chart, `Date` on the X axis, `Close` on the Y axis.]
  Does the close come back to one level, or wander? #rule(5.2cm)
]

#v(5pt)

#panel("Step 2 · Put each day beside the days before")[
  #step(1, "Lag the close")[On the uploaded dataset: #dss("+ Recipe", "Window"). In *Windows definitions*, order the rows by `Date`, ascending; in *Aggregations*, on `Close`, tick *Lag* with offsets `1,2`; *Run*.]
  Names of the two new columns: #rule(5.2cm)
  #v(2pt)
  #step(2, "Compute the changes")[On the lagged dataset: #dss("+ Recipe", "Prepare"), a step *Formula* `change` = `Close` minus the lag-1 column, a step *Formula* `previous_change` = the lag-1 column minus the lag-2 column, then *Extract date elements* on `Date`, the day of week; *Run*. Then #dss("Charts"): a *Lines* chart of `change` by `Date`.]
  #v(2pt)
  #step(3, "Correlate")[On the dataset of changes: #dss("Statistics", "+ Card", "Correlation matrix") on `Close`, the lag-1 column, `change` and `previous_change`; in the card's settings, *Pearson* (Spearman is the default).]
  Close with the day before: #rule(1.6cm) #h(8pt) change with the change before: #rule(1.6cm)
]

#v(5pt)

#panel("Step 3 · The weekday check")[
  #step(1, "Average the change by weekday")[On the dataset of changes: #dss("+ Recipe", "Group"), grouped by the day of week; on `change`: *Avg*, *Std. dev.* and *Count*; *Run*. In its output, `day_of_week` 1 is Monday; the days are `change_count` (`count` also counts the first day, which has no change).]
  #table(
    columns: (1.4fr, 1fr, 1fr, 1fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [*`change`*], [*Mon*], [*Tue*], [*Wed*], [*Thu*], [*Fri*],
    [mean], [], [], [], [], [],
    [std. dev.], [], [], [], [], [],
    [days], [], [], [], [], [],
  )
  #step(2, "Compare each mean with its spread")[On the Group recipe's output dataset.]
  Does any weekday's mean stand out of its standard deviation? #rule(4.2cm)
  #v(2pt)
  #step(3, "Answer the treasury team")[From the table and the correlations of step 2.3.]
  What do you tell the treasury team: do the past days point to a cheaper day to buy, and why?
  #writing(2)
]

#v(5pt)

#panel("4 · Run the same check on the bike rentals")[
  #step(1, "Upload the rentals and read their dates")[#dss("+ Dataset", "Upload your files"), `bike-rentals.csv` (its `Date` reads *Date only*, as in step 1.2); then #dss("+ Recipe", "Prepare"): *Extract date elements* on `Date`, the day of week and the month; *Run*.]
  #v(2pt)
  #step(2, "Average by weekday, then by month")[#dss("+ Recipe", "Group") grouped by the day of week (1 is Monday), on `Rentals`: *Avg* and *Std. dev.*; then a second Group recipe on the same dataset, grouped by the month.]
  #table(
    columns: (1.6fr, 1fr, 1fr, 1fr), inset: 4pt, stroke: hair,
    [*`Rentals`*], [*lowest mean*], [*highest mean*], [*a typical std. dev.*],
    [by weekday], [], [], [],
    [by month], [], [], [],
  )
  Does a weekday or a season stand out of its spread here? What would such a pattern have looked like in the index's weekday table of step 3?
  #writing(2)
]
