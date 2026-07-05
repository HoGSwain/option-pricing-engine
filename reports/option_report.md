# Option Analytics Report

**Contract:** 1-year european call, strike $100.00  
**Underlying:** $100.00 · volatility 20.00% · rate 5.00%

## Price by method

| Method | Price |
|---|---|
| Black-Scholes (European, analytic) | $10.4506 |
| Binomial (european) | $10.4466 |
| Monte Carlo (European) | $10.4205 ± 0.0468 |

## Greeks (Black-Scholes)

| Greek | Value | Interpretation |
|---|---|---|
| Delta | +0.6368 | price change per $1 in the underlying |
| Gamma | 0.01876 | delta change per $1 in the underlying |
| Vega | +0.3752 | price change per 1% of volatility |
| Theta | -0.0176 | price change per calendar day (decay) |
| Rho | +0.5323 | price change per 1% (100bp) of rate |

## Notes

- Black-Scholes prices European exercise; the binomial tree also prices American exercise (the difference is the early-exercise premium). Agreement across the three methods is a cross-check.
- Greeks above are shown in conventional units; the engine computes raw partials internally. All formulas are in [`docs/methodology.md`](../docs/methodology.md).

## Explanation

- A 1-year at-the-money call (strike $100.00) on a $100.00 underlying (volatility 20.0%, rate 5.0%) is worth $10.45 under Black-Scholes.
- Delta +0.637: the value moves about $+0.64 per $1 change in the underlying. Gamma 0.0188; vega $0.375 per 1% of volatility; theta $-0.018 per calendar day (time decay).
- Three independent methods agree: Black-Scholes $10.45, a binomial tree $10.45, and Monte Carlo $10.42 (± $0.05) — a cross-check that the price is right.

## Limitations & assumptions

- Black-Scholes assumes lognormal prices, constant volatility, no jumps, and continuous costless hedging; the analytic price and Greeks are for European exercise.
- Any ticker inputs come from synthetic (seeded GBM) data for offline reproducibility, not real market data.
- Greeks are local sensitivities (first/second order); Monte Carlo carries the stated sampling standard error.
- This engine supports human derivatives analysis; it does not make trading decisions.
