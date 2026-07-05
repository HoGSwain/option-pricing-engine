# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-07-05
### Added
- Initial release of the Option Pricing Engine (OPE), AIFEL Project 6.
- **Three independent pricing methods**, cross-checked against each other:
  Black-Scholes (closed form), a Cox-Ross-Rubinstein **binomial tree** (European
  and American exercise), and a seeded **Monte-Carlo** engine with a reported
  standard error.
- **The full Greeks** — delta, gamma, vega, theta, rho — as analytic partials,
  each validated against a finite-difference oracle (including theta's sign).
- **Implied volatility** backed out from a market price via `scipy.brentq`.
- **Composition** — prices an option on a real ticker by sourcing the spot from
  Project 1 (`fmde`) and a realized-volatility estimate from Project 2 (`pae`),
  the genuine equity→option link. Both dependencies are pinned to commit SHAs.
- Deterministic explainability layer (`ope.explain`): the option decision
  narrative ("delta 0.64 ⇒ ≈$0.64 per $1 move; three methods agree; realized ≠
  implied volatility"), exposed on `OptionResult.explanation`.
- Storage: `option_analytics.csv` + JSON metadata (checksum, versions). Reporting:
  Markdown report with Greeks in conventional units.
- Typer CLI (`ope price`, `ope info`).
- Test suite (39 tests) validating every method and Greek against textbook values
  (BS call 10.4506 / put 5.5735), put-call parity, a finite-difference Greeks
  oracle, binomial→BS convergence, Monte-Carlo within 3 standard errors, and
  American-exercise invariants.
- CI on GitHub Actions (Linux + Windows × Python 3.10/3.12): pytest, ruff, black.
