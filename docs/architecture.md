# Architecture

OPE is a small, layered Python package. Data flows one way: inputs → pricing →
explanation → storage/reporting.

```
                 ┌──────────────────────────────────────────────┐
   ticker ──────▶│ source.market.market_inputs                  │
 (optional)      │   fmde.run_pipeline → latest adj_close (spot) │
                 │   pae.annualized_volatility → realized vol    │
                 └───────────────────────┬──────────────────────┘
                                         │ spot, vol
  spot, vol ─────────────────────────────┤ (or supplied directly)
                                         ▼
                 ┌──────────────────────────────────────────────┐
                 │ option.instrument.Option (frozen dataclass)   │
                 └───────────────────────┬──────────────────────┘
                                         ▼
        ┌────────────────────────────────────────────────────────────┐
        │ pipeline.run_option_analysis                               │
        │   black_scholes.price / greeks / implied_volatility        │
        │   binomial.binomial_price   (European + American)          │
        │   monte_carlo.monte_carlo_price (price, stderr)            │
        └───────────────┬─────────────────────────┬──────────────────┘
                        ▼                          ▼
             explain.explain()          storage.save_all() → CSV + JSON
             (findings + limitations)   reporting.generate_report() → .md
                        │
                        ▼
                  OptionResult  (returned; explanation on every report)
```

## Packages

| Module | Responsibility |
|---|---|
| `ope.option.instrument` | `Option` — frozen, validated contract spec (spot, strike, T, r, σ, q, kind, exercise). |
| `ope.option.black_scholes` | Closed-form price, the five Greeks (raw partials), and implied volatility. |
| `ope.option.binomial` | Cox-Ross-Rubinstein tree; European and American exercise. |
| `ope.option.monte_carlo` | Seeded risk-neutral simulation; returns `(price, stderr)`. |
| `ope.source.market` | The composition point — spot from `fmde`, realized vol from `pae`. |
| `ope.explain` | Deterministic decision narrative + limitations. |
| `ope.storage.manager` | Analysis CSV + JSON run-metadata (checksum, versions). |
| `ope.reporting.report` | Markdown report; Greeks converted to conventional units here. |
| `ope.pipeline` | `run_option_analysis` — orchestrates all of the above, returns `OptionResult`. |
| `ope.main` | Typer CLI (`ope price`, `ope info`). |
| `ope.config` | `Settings` (rates, tree steps, MC paths/seed, output directories). |

## Design principles

- **Pure math core.** `option/` has no I/O and no cross-project imports; it is
  tested in isolation against textbook values and finite-difference oracles.
- **Raw partials in, conventional units out.** Pricers return true derivatives;
  the reporting layer converts to per-1%/per-day so tests can validate the
  derivatives directly.
- **Composition is optional and pinned.** The `fmde`/`pae` dependency is only
  touched when a `ticker` is supplied; everything else runs offline.
- **Reproducibility.** Seeded Monte-Carlo, pinned git dependencies, and a JSON
  metadata sidecar (input checksum + package/option versions) on every run.
