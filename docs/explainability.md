# Explainability & Governance

The sixth AIFEL question: **"Can you explain every financial conclusion the
system reaches?"** An option price of "$10.45" is meaningless without its Greeks
(how it moves), the agreement of independent methods (is it right), and its
assumptions (when does it break). Explainability = *understanding*; governance =
*accountability*.

## How explanations are produced (and why not an LLM)

`ope.explain.explain()` converts the analysis into a plain-language `Explanation`
(findings + limitations), exposed on `OptionResult.explanation` and appended to
every `reports/*.md`. Example:

> *"A 1-year at-the-money call (strike $100.00) on a $100.00 underlying
> (volatility 20.0%, rate 5.0%) is worth $10.45 under Black-Scholes. Delta
> +0.637: the value moves about $+0.64 per $1 change in the underlying. Gamma
> 0.0188; vega $0.375 per 1% of volatility; theta $-0.018 per calendar day. Three
> independent methods agree: Black-Scholes $10.45, a binomial tree $10.45, and
> Monte Carlo $10.42 (± $0.05) — a cross-check that the price is right."*

The narrative is generated **deterministically** from the actual numbers — not a
language model. An LLM narrating a pricer would itself be an unauditable black box
(an invented rationale replacing an auditable number with an unverifiable story).
Every sentence is a reproducible function of the inputs; an LLM may later
*rephrase* them but must never be their source.

## The three levels of explainability

- **Data** — the inputs are the option's own terms plus a spot and a volatility;
  when sourced from a ticker, the spot comes from `fmde` and the volatility is a
  labelled **realized** estimate from `pae` (synthetic data is flagged as such).
- **Model** — every formula, the risk-neutral/GBM assumptions, the CRR
  parameterization, and the finite-difference Greeks validation are in
  `docs/methodology.md` / `docs/validation.md`.
- **Decision** — the `Explanation` states the price, what each Greek *means* for a
  move, whether the three methods agree, the early-exercise premium (if
  American), and the assumptions behind those conclusions.

## Limitations & human oversight

- **Black-Scholes world** — constant volatility, lognormal prices, no jumps,
  continuous costless hedging; the analytic price and Greeks are European.
- **Realized ≠ implied volatility** — a ticker-sourced vol is historical, not the
  market's implied vol, so the BS number will differ from a traded quote. Back
  implied vol out of a live price for a market-consistent value.
- **Greeks are local** first/second-order sensitivities; **Monte-Carlo carries the
  stated sampling error**.
- **Continuous dividend yield**, not discrete cash dividends; no transaction
  costs, taxes, or liquidity effects.
- **This engine supports human derivatives analysis; it does not make trading
  decisions.**

## Explainability & governance checklist

**Explainability**
- [x] Problem clearly defined (README §1–2)
- [x] Concepts explained in plain language (`explain()`, `docs/methodology.md`)
- [x] Assumptions documented (`docs/methodology.md`, `docs/assumptions.md`)
- [x] Parameters/conventions justified (`docs/assumptions.md`)
- [x] Outputs interpreted for a human (`Explanation` in every report)
- [x] Limitations disclosed (this file, `Explanation.limitations`)
- [x] Alternatives / extensions discussed (`docs/assumptions.md`, `docs/references.md`)

**Governance**
- [x] Inputs and mode recorded in metadata (checksum, versions, sources)
- [x] Option-model version tagged (`OPTION_VERSION`)
- [x] Dependencies declared and **pinned to commit SHAs** (`fmde`, `pae`)
- [x] Tests pass in CI (Linux + Windows × Python 3.10/3.12)
- [x] Validation against textbook values + finite-difference oracle + cross-method convergence (`docs/validation.md`)
- [x] Reproduction steps complete (README §4)
- [ ] Fairness/bias assessment — **N/A**: OPE makes no decisions about people.
