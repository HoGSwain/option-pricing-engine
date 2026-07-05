"""Black-Scholes: textbook reference values and closed-form invariants."""

from dataclasses import replace

import numpy as np
import pytest

from ope.option import black_scholes as BS
from ope.option.instrument import Option


def test_call_reference_value(call_opt):
    # Hull, *Options, Futures, and Other Derivatives*: S=K=100, T=1, r=5%, σ=20%.
    assert BS.price(call_opt) == pytest.approx(10.4506, abs=1e-4)


def test_put_reference_value(put_opt):
    assert BS.price(put_opt) == pytest.approx(5.5735, abs=1e-4)


def test_put_call_parity(call_opt, put_opt):
    S, K, T, r, q = (
        call_opt.spot,
        call_opt.strike,
        call_opt.maturity,
        call_opt.rate,
        call_opt.dividend,
    )
    parity = S * np.exp(-q * T) - K * np.exp(-r * T)
    assert BS.price(call_opt) - BS.price(put_opt) == pytest.approx(parity, abs=1e-10)


def test_delta_bounds(call_opt, put_opt):
    assert 0.0 < BS.delta(call_opt) < 1.0
    assert -1.0 < BS.delta(put_opt) < 0.0


def test_call_minus_put_delta_is_discount_factor(call_opt, put_opt):
    # Δ_call − Δ_put = e^{−qT} exactly.
    expected = np.exp(-call_opt.dividend * call_opt.maturity)
    assert BS.delta(call_opt) - BS.delta(put_opt) == pytest.approx(expected, abs=1e-12)


def test_zero_time_is_intrinsic():
    itm_call = Option(100.0, 90.0, 0.0, 0.05, 0.20, 0.0, "call")
    assert BS.price(itm_call) == pytest.approx(10.0)


def test_zero_vol_is_discounted_forward_intrinsic():
    o = Option(100.0, 100.0, 1.0, 0.05, 0.0, 0.0, "call")
    # σ=0: deterministic forward → payoff max(S e^{(r-q)T} − K, 0), discounted.
    expected = max(100.0 * np.exp(0.05) - 100.0, 0.0) * np.exp(-0.05)
    assert BS.price(o) == pytest.approx(expected, abs=1e-9)


def test_implied_vol_round_trip(call_opt):
    market = BS.price(call_opt)
    iv = BS.implied_volatility(replace(call_opt, volatility=0.5), market)
    assert iv == pytest.approx(0.20, abs=1e-6)


def test_implied_vol_out_of_range_raises(call_opt):
    with pytest.raises(ValueError):
        BS.implied_volatility(call_opt, market_price=1.0e6)
