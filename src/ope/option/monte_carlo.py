"""
Monte-Carlo pricing (European options).

Simulates the terminal underlying price under the risk-neutral measure,
``S_T = S·exp((r − q − σ²/2)T + σ√T·Z)`` with ``Z ~ N(0,1)``, and discounts the
mean payoff. Returns the price **and its standard error**, so estimation
uncertainty is explicit (validated in the tests as ``|MC − BS| < 3·stderr``).
The generator is seeded, so results are reproducible.

American exercise needs a regression method (Longstaff-Schwartz) and is out of
scope; use the binomial tree for American options.
"""

from typing import Tuple

import numpy as np

from ope.option.instrument import Option


def monte_carlo_price(opt: Option, n_paths: int = 100_000, seed: int = 42) -> Tuple[float, float]:
    """Return ``(price, standard_error)`` for a European option."""
    S, K, T, r, sig, q = (
        opt.spot,
        opt.strike,
        opt.maturity,
        opt.rate,
        opt.volatility,
        opt.dividend,
    )
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n_paths)
    st = S * np.exp((r - q - 0.5 * sig**2) * T + sig * np.sqrt(T) * z)
    payoff = np.maximum(st - K, 0.0) if opt.is_call else np.maximum(K - st, 0.0)
    disc = np.exp(-r * T)
    price = float(disc * payoff.mean())
    stderr = float(disc * payoff.std(ddof=1) / np.sqrt(n_paths))
    return price, stderr
