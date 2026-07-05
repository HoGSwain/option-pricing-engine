# Dataset Report — AAPL

**Source:** synthetic  
**Rows (final):** 2220  
**Date range:** 2018-01-01 to 2026-07-03

## Validation Summary
- Valid: **True**
- Duplicate dates found: 0
- Missing dates (calendar gaps): 0
- Negative prices: 0
- Zero prices: 0
- Large trading gaps (>7 days): 0
- Warnings: None

## Cleaning Summary
- Rows before: 2220
- Rows after: 2220
- Duplicates removed: 0
- Rows dropped (negative price): 0
- Values forward-filled: 0
- Actions log:
  -   (no corrective actions required)

## Latest Observation
- Date: 2026-07-03
- Adjusted Close: 173.56
- Rolling Volatility (annualized): 26.33%
- Cumulative Return since start: 71.61%
- Current Drawdown: -25.96%
- Max Drawdown to date: -31.43%

## Return / Risk Summary Statistics

|       |   arithmetic_return |     log_return |   rolling_volatility |     drawdown |
|:------|--------------------:|---------------:|---------------------:|-------------:|
| count |      2219           | 2219           |         2200         | 2220         |
| mean  |         0.000360241 |    0.000243366 |            0.239106  |   -0.130296  |
| std   |         0.0152908   |    0.01529     |            0.0414708 |    0.0745628 |
| min   |        -0.0513847   |   -0.0527519   |            0.120018  |   -0.314319  |
| 25%   |        -0.00961275  |   -0.00965925  |            0.212029  |   -0.186857  |
| 50%   |         0.000403497 |    0.000403415 |            0.236119  |   -0.131625  |
| 75%   |         0.0103638   |    0.0103105   |            0.266648  |   -0.0731131 |
| max   |         0.0550601   |    0.0535977   |            0.427956  |    0         |


## Explanation

- AAPL: 2220 cleaned daily observations from 2018-01-01 to 2026-07-03, sourced from the 'synthetic' provider.
- Raw-data validation passed: no negative or zero prices and no schema/dtype problems were detected.
- No corrective cleaning was required — the raw data was already clean.
- Over the sample the price compounded +71.6%; the worst peak-to-trough decline (maximum drawdown) was -31.4%.
- The most recent 20-day annualized volatility is 26.3%.

## Limitations & assumptions

- Annualized volatility uses the √252 rule, which assumes returns are independent and identically distributed; it understates risk when volatility clusters.
- This is SYNTHETIC (seeded geometric Brownian motion) data for offline reproducibility — not real market data. Every metadata file and report records `source: synthetic`, so it is always traceable.
- All figures describe the historical sample only and are not forecasts of future return or risk.
- This engine supports human analysis; it does not make investment decisions.
