# Methodology

OPE prices a European or American **vanilla option** on a single underlying and
computes its risk sensitivities (the Greeks). All pricing functions live in
`ope.option`.

## Conventions

- **Underlying** follows geometric Brownian motion under the risk-neutral
  measure: `dS = (r − q)S dt + σS dW`, with continuous risk-free rate `r`,
  continuous dividend yield `q`, and constant volatility `σ`.
- **Time** `T` is in years; **rate/vol/dividend** are annualized decimals
  (`0.05` = 5%).
- **Greeks are returned as raw partial derivatives** (per unit of the underlying
  variable). Presentation-unit conversions — vega per 1% of vol, theta per
  calendar day, rho per 100 bp — happen in the reporting layer, never in the
  pricers, so the finite-difference tests can check the true derivatives.

## Black-Scholes (closed form) — `ope.option.black_scholes`

With `d₁ = [ln(S/K) + (r − q + ½σ²)T] / (σ√T)` and `d₂ = d₁ − σ√T`:

```
Call = S e^(−qT) N(d₁) − K e^(−rT) N(d₂)
Put  = K e^(−rT) N(−d₂) − S e^(−qT) N(−d₁)
```

`N` is the standard-normal CDF (`scipy.stats.norm.cdf`). As `σ√T → 0` the price
degenerates to the **discounted forward intrinsic** `max(φ(F − K), 0)·e^(−rT)`
with forward `F = S e^((r−q)T)` and `φ = ±1` for call/put — the `T=0` or `σ=0`
guard returns exactly this.

### Greeks (analytic partials)

```
Δ_call = e^(−qT) N(d₁)          Δ_put = −e^(−qT) N(−d₁)
Γ      = e^(−qT) n(d₁) / (S σ√T)          (same for call/put)
ν      = S e^(−qT) n(d₁) √T                (vega, per unit vol — same for call/put)
Θ      = ∂V/∂t = −∂V/∂T          (time decay; negative for a long vanilla)
ρ_call = K T e^(−rT) N(d₂)       ρ_put = −K T e^(−rT) N(−d₂)
```

`n` is the standard-normal PDF. **Theta is `∂V/∂t`, the derivative with respect
to *calendar time*, which is `−∂V/∂T`** — the single most common sign error in
option code, and the reason the finite-difference test checks it explicitly.

### Implied volatility

Given a market price, `implied_volatility` solves `BS(σ) = market_price` for `σ`
with Brent's method (`scipy.brentq`) on `[1e-6, 5.0]`. The BS price is strictly
increasing in `σ`, so the root is unique; a price outside the no-arbitrage
bounds raises a clear `ValueError`.

## Binomial tree (Cox-Ross-Rubinstein) — `ope.option.binomial`

`N` steps of width `dt = T/N`, with

```
u = e^(σ√dt)      d = 1/u      p = (e^((r−q)dt) − d) / (u − d)
```

Terminal payoffs are discounted back one layer at a time by `e^(−r·dt)`. For an
**American** option each node takes `max(continuation, intrinsic)`, capturing the
early-exercise premium; a **European** option discounts continuation only. The
tree converges to Black-Scholes as `N → ∞` (see `docs/validation.md`).

## Monte-Carlo — `ope.option.monte_carlo`

Simulates `n` risk-neutral terminal prices
`Sₜ = S·exp((r − q − ½σ²)T + σ√T·Z)`, `Z ∼ N(0,1)` (seeded `np.random.default_rng`),
discounts the mean payoff by `e^(−rT)`, and reports the **standard error**
`stderr = e^(−rT)·s / √n` (sample s.d. `s`, `ddof=1`). European exercise only —
the estimate must agree with Black-Scholes to within a few standard errors.

## Why three methods

Each is an independent implementation of the same risk-neutral value: a
closed-form integral, a discrete-tree expectation, and a simulation. Their
agreement (reported as `methods_agree`) is a cross-check that the number is right
— and the tree extends naturally to American exercise, which Black-Scholes cannot
price.
