# Validation

Every pricer and Greek is checked against a textbook value, a closed-form
invariant, or an **independent oracle** — not merely that the code runs. 39 tests
(`pytest`), green in CI on Linux + Windows × Python 3.10/3.12.

## Reference values (textbook)

The canonical Hull example — `S = K = 100`, `T = 1`, `r = 5%`, `σ = 20%`, `q = 0`:

| Quantity | Expected | Test |
|---|---|---|
| Call price | 10.4506 | `test_call_reference_value` |
| Put price | 5.5735 | `test_put_reference_value` |

## Closed-form invariants

- **Put-call parity** `C − P = S e^(−qT) − K e^(−rT)` holds to `1e-10`
  (`test_put_call_parity`).
- **Δ_call − Δ_put = e^(−qT)** exactly (`test_call_minus_put_delta_is_discount_factor`).
- **Delta bounds** `0 < Δ_call < 1`, `−1 < Δ_put < 0` (`test_delta_bounds`).
- **Degenerate limits** — `T=0` gives the intrinsic value; `σ=0` gives the
  discounted forward intrinsic (`test_zero_time_is_intrinsic`,
  `test_zero_vol_is_discounted_forward_intrinsic`).
- **Implied-vol round-trip** — pricing at σ=20% then backing σ out returns 0.20
  to `1e-6`; an out-of-range price raises (`test_implied_vol_round_trip`,
  `test_implied_vol_out_of_range_raises`).

## Finite-difference Greeks oracle

Each analytic Greek is compared to a central finite difference of the price
function — an implementation-independent numerical derivative:

| Greek | Oracle | Test |
|---|---|---|
| Delta | `[P(S+h) − P(S−h)] / 2h` | `test_delta_matches_fd` |
| Gamma | `[P(S+h) − 2P(S) + P(S−h)] / h²` | `test_gamma_matches_fd` |
| Vega | `[P(σ+h) − P(σ−h)] / 2h` | `test_vega_matches_fd` |
| Theta | `−[P(T+h) − P(T−h)] / 2h` | `test_theta_matches_fd_and_is_negative` |
| Rho | `[P(r+h) − P(r−h)] / 2h` | `test_rho_matches_fd` |

The theta test also asserts `Θ < 0` — pinning down the `∂V/∂t = −∂V/∂T` sign that
option code so often gets backwards.

## Cross-method convergence

- **Binomial → Black-Scholes** — a 1000-step CRR tree matches BS to `< 0.01` for
  both call and put (`test_european_binomial_converges_to_bs`,
  `test_european_put_binomial_converges_to_bs`).
- **Monte-Carlo → Black-Scholes** — 100k seeded paths land within `3·stderr` of
  BS for call and put (`test_mc_within_three_stderr_of_bs`, and the put variant).
- **Monte-Carlo determinism** — same seed, same price (`test_mc_is_deterministic_for_a_seed`).

## American-exercise invariants (same tree)

Compared on an identical step count, so they test the early-exercise logic, not
discretization:

- **American put ≥ European put** (`test_american_put_ge_european_put_same_tree`).
- **American call = European call without dividends** — never optimal to exercise
  early, so the premium is zero (`test_american_call_equals_european_call_without_dividends`).

## End-to-end & explainability

`test_pipeline_integration.py` runs `run_option_analysis` from both explicit
inputs and a sourced ticker (exercising the fmde→pae chain), checks the CSV +
metadata + report are written, and that the American path reports a non-negative
premium. `test_explain.py` checks the explanation states the price and Greeks, is
deterministic, is embedded in the report, and — on any ticker-sourced run —
surfaces the **realized ≠ implied volatility** caveat and the "does not make
trading decisions" disclaimer.
