"""
Black-Scholes-Merton analytic pricing and Greeks (European options, continuous
dividend yield ``q``).

Greeks are returned as **raw partial derivatives** (per 1.0 of the variable):
vega is ∂V/∂σ, theta is ∂V/∂t = −∂V/∂T (negative for long options). Presentation
conversions (vega per 1% vol, theta per calendar day) live in the report layer,
never here — so the Greeks can be checked directly against a finite-difference
oracle in the tests.
"""

from dataclasses import dataclass, replace

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

from ope.option.instrument import Option

_EPS = 1e-12


def _discounted_intrinsic(opt: Option) -> float:
    """Value when σ√T ≈ 0: the deterministic-forward payoff, discounted."""
    fwd_call = opt.spot * np.exp(-opt.dividend * opt.maturity) - opt.strike * np.exp(
        -opt.rate * opt.maturity
    )
    return max(fwd_call, 0.0) if opt.is_call else max(-fwd_call, 0.0)


def _d1_d2(opt: Option):
    srt = opt.volatility * np.sqrt(opt.maturity)
    d1 = (
        np.log(opt.spot / opt.strike)
        + (opt.rate - opt.dividend + 0.5 * opt.volatility**2) * opt.maturity
    ) / srt
    return d1, d1 - srt


def price(opt: Option) -> float:
    """Black-Scholes price."""
    if opt.volatility * np.sqrt(opt.maturity) < _EPS:
        return _discounted_intrinsic(opt)
    S, K, T, r, q = opt.spot, opt.strike, opt.maturity, opt.rate, opt.dividend
    d1, d2 = _d1_d2(opt)
    if opt.is_call:
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)


def delta(opt: Option) -> float:
    d1, _ = _d1_d2(opt)
    disc_q = np.exp(-opt.dividend * opt.maturity)
    return disc_q * norm.cdf(d1) if opt.is_call else disc_q * (norm.cdf(d1) - 1.0)


def gamma(opt: Option) -> float:
    d1, _ = _d1_d2(opt)
    return (
        np.exp(-opt.dividend * opt.maturity)
        * norm.pdf(d1)
        / (opt.spot * opt.volatility * np.sqrt(opt.maturity))
    )


def vega(opt: Option) -> float:
    """∂V/∂σ (per 1.0 of volatility)."""
    d1, _ = _d1_d2(opt)
    return opt.spot * np.exp(-opt.dividend * opt.maturity) * norm.pdf(d1) * np.sqrt(opt.maturity)


def theta(opt: Option) -> float:
    """∂V/∂t = −∂V/∂T (per year); negative for a long option."""
    S, K, T, r, q = opt.spot, opt.strike, opt.maturity, opt.rate, opt.dividend
    d1, d2 = _d1_d2(opt)
    decay = -np.exp(-q * T) * S * norm.pdf(d1) * opt.volatility / (2.0 * np.sqrt(T))
    if opt.is_call:
        return decay - r * K * np.exp(-r * T) * norm.cdf(d2) + q * S * np.exp(-q * T) * norm.cdf(d1)
    return decay + r * K * np.exp(-r * T) * norm.cdf(-d2) - q * S * np.exp(-q * T) * norm.cdf(-d1)


def rho(opt: Option) -> float:
    """∂V/∂r (per 1.0 of rate)."""
    _, d2 = _d1_d2(opt)
    K, T, r = opt.strike, opt.maturity, opt.rate
    if opt.is_call:
        return K * T * np.exp(-r * T) * norm.cdf(d2)
    return -K * T * np.exp(-r * T) * norm.cdf(-d2)


@dataclass
class Greeks:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float

    def to_dict(self) -> dict:
        return {
            "delta": self.delta,
            "gamma": self.gamma,
            "vega": self.vega,
            "theta": self.theta,
            "rho": self.rho,
        }


def greeks(opt: Option) -> Greeks:
    """All Black-Scholes Greeks (raw partials)."""
    return Greeks(delta(opt), gamma(opt), vega(opt), theta(opt), rho(opt))


def implied_volatility(opt: Option, market_price: float) -> float:
    """The volatility that reproduces ``market_price`` under Black-Scholes,
    via Brent root-finding on ``[1e-6, 5.0]``. Raises if the price is outside
    the attainable (no-arbitrage) range."""

    def objective(sigma: float) -> float:
        return price(replace(opt, volatility=sigma)) - market_price

    try:
        return float(brentq(objective, 1e-6, 5.0, xtol=1e-10, maxiter=200))
    except ValueError as exc:
        lo = price(replace(opt, volatility=1e-6))
        hi = price(replace(opt, volatility=5.0))
        raise ValueError(
            f"no implied volatility for price {market_price:.4f}; attainable range is "
            f"[{lo:.4f}, {hi:.4f}] (below intrinsic or above the no-arbitrage bound)."
        ) from exc
