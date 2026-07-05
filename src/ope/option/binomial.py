"""
Cox-Ross-Rubinstein binomial tree pricing (European and American).

``u = e^(σ√dt)``, ``d = 1/u``, risk-neutral up-probability
``p = (e^((r−q)dt) − d) / (u − d)``. Backward induction discounts the
risk-neutral expected payoff; for American options each node also takes the
maximum of continuation value and immediate exercise (intrinsic) value.

A European binomial price converges to Black-Scholes as steps → ∞ (oscillating
by even/odd step count); the American price adds the early-exercise premium.
"""

import numpy as np

from ope.option.instrument import Option


def binomial_price(opt: Option, steps: int = 500) -> float:
    S, K, T, r, sig, q = (
        opt.spot,
        opt.strike,
        opt.maturity,
        opt.rate,
        opt.volatility,
        opt.dividend,
    )
    if T == 0 or sig == 0:
        intrinsic = max(S - K, 0.0) if opt.is_call else max(K - S, 0.0)
        return float(intrinsic)

    dt = T / steps
    u = np.exp(sig * np.sqrt(dt))
    d = 1.0 / u
    disc = np.exp(-r * dt)
    p = (np.exp((r - q) * dt) - d) / (u - d)
    american = opt.exercise == "american"

    # Terminal underlying prices and payoffs.
    j = np.arange(steps + 1)
    st = S * u**j * d ** (steps - j)
    values = np.maximum(st - K, 0.0) if opt.is_call else np.maximum(K - st, 0.0)

    for i in range(steps, 0, -1):
        values = disc * (p * values[1:] + (1.0 - p) * values[:-1])  # length i
        if american:
            jj = np.arange(i)
            s_nodes = S * u**jj * d ** (i - 1 - jj)  # underlying at time-step i-1
            intrinsic = (
                np.maximum(s_nodes - K, 0.0) if opt.is_call else np.maximum(K - s_nodes, 0.0)
            )
            values = np.maximum(values, intrinsic)

    return float(values[0])
