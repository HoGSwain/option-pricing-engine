# Assumptions & Design Decisions

Every significant modelling and engineering choice, with its reasoning.

## Modelling assumptions

- **Geometric Brownian motion / Black-Scholes world.** Constant volatility and
  interest rate, lognormal prices, no jumps, continuous and costless hedging,
  no transaction costs or taxes. This is the standard baseline; its known gaps
  (volatility smile, fat tails, discrete dividends) are listed in
  `docs/explainability.md` and `docs/references.md`.
- **Continuous dividend yield `q`.** Dividends are modelled as a continuous
  yield, not discrete cash payments on ex-dates. Appropriate for an index or a
  yield-quoted underlying; a real single stock with lumpy dividends would need a
  discrete-dividend tree.
- **European Greeks even for American options.** The reported Greeks are the
  Black-Scholes (European) sensitivities — a standard, well-understood
  approximation. The American *price* is the binomial value; the Greeks label in
  every report says "Black-Scholes" so this is never ambiguous.
- **Risk-neutral pricing.** All three methods price under the risk-neutral
  measure; no view on the real-world drift is taken or needed.

## Numerical choices

- **Binomial default 500 steps** — a balance of accuracy (sub-cent vs BS for the
  reference option) and speed. The CLI/pipeline expose `steps` to override.
- **Monte-Carlo default 100,000 paths, seed 42** — enough that the standard error
  is small, seeded so every run is reproducible. MC prices the European contract
  (the tree already handles American), and the pipeline compares BS to MC within
  `3·stderr`.
- **CRR parameterization** (`u = e^(σ√dt)`, `d = 1/u`) — the classic recombining
  tree; the risk-neutral `p` uses `(r−q)` so dividends are handled consistently
  with Black-Scholes.
- **`brentq` brackets** — implied vol on `[1e-6, 5.0]`; a 500% vol ceiling covers
  any realistic quote, and a price outside the arbitrage bounds raises rather
  than returning a garbage root.

## Composition decision — why OPE depends on Projects 1-2

Unlike Project 5 (bonds, deliberately standalone), an option is written **on an
equity**, so pricing one on a real ticker genuinely needs that equity's spot and
volatility. OPE therefore sources:

- the **spot** from Project 1 (`fmde`) — the latest cleaned adjusted close, and
- a **realized-volatility** estimate by reusing Project 2's
  `pae.metrics.annualized_volatility` on the return series.

This is a *real* dependency, not decoration — the same judgement that kept BAE
standalone. Both dependencies are **pinned to commit SHAs** so the composition is
reproducible. The pure option math still runs with no ticker at all (pass `spot`
and `vol` directly), so the engine is usable offline and in isolation.

## Realized vs implied volatility

When volatility is sourced from a ticker it is a **historical (realized)**
estimate, **not the market's implied volatility**. The result answers "what
Black-Scholes says at historical vol", which will differ from a traded option's
price. The explanation layer states this explicitly on every ticker-sourced run,
and `implied_volatility` is provided to back out the market-consistent number
from a live quote.

## Scope

Vanilla European/American calls and puts on one underlying. No exotic payoffs
(barriers, Asians, lookbacks), no stochastic volatility or local-vol surface, no
American Monte-Carlo (Longstaff-Schwartz). These are natural extensions, noted in
`docs/references.md` and the README's Future Improvements.
