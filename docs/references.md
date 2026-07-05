# References & Further Reading

## Foundational

- Black, F. & Scholes, M. (1973). "The Pricing of Options and Corporate
  Liabilities." *Journal of Political Economy* 81(3). The closed-form model.
- Merton, R. C. (1973). "Theory of Rational Option Pricing." *Bell Journal of
  Economics* 4(1). The continuous-dividend extension used here (`q`).
- Cox, J., Ross, S. & Rubinstein, M. (1979). "Option Pricing: A Simplified
  Approach." *Journal of Financial Economics* 7(3). The binomial tree.
- Boyle, P. (1977). "Options: A Monte Carlo Approach." *Journal of Financial
  Economics* 4(3). Simulation pricing.

## Textbook

- Hull, J. C. *Options, Futures, and Other Derivatives*. The `S=K=100, T=1,
  r=5%, σ=20%` → call 10.4506 / put 5.5735 reference values and the Greeks come
  from the standard treatment here.
- Wilmott, P. *Paul Wilmott on Quantitative Finance*. Greeks, hedging, and the
  model's limitations.

## Beyond this engine (extensions)

- **Volatility smile / surface** — Black-Scholes assumes constant σ; real markets
  price a strike- and maturity-dependent implied-vol surface. Dupire local vol,
  SABR, and Heston stochastic vol address this.
- **Discrete dividends** — a real single stock pays lumpy cash dividends on
  ex-dates, better handled by an escrowed-dividend or discrete-dividend tree than
  a continuous yield.
- **American Monte-Carlo** — Longstaff-Schwartz least-squares MC prices American
  exercise by simulation, complementing the tree.
- **Jumps / fat tails** — Merton jump-diffusion and Lévy models capture the
  crash risk that a lognormal diffusion misses.

## AIFEL portfolio

- Project 1 — Financial Market Data Engine (`fmde`): supplies the spot price.
- Project 2 — Portfolio Analytics Engine (`pae`): supplies the realized-volatility
  metric reused here.
- Portfolio index: https://github.com/HoGSwain/AIFEL-Portfolio
