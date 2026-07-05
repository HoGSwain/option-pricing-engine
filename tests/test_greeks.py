"""Greeks validated against a finite-difference oracle — an independent check
that the closed-form partials are the actual sensitivities of the price."""

from dataclasses import replace

import pytest

from ope.option import black_scholes as BS


def _central(opt, attr, h):
    up = replace(opt, **{attr: getattr(opt, attr) + h})
    dn = replace(opt, **{attr: getattr(opt, attr) - h})
    return (BS.price(up) - BS.price(dn)) / (2 * h)


def test_delta_matches_fd(call_opt):
    h = 0.01 * call_opt.spot
    assert BS.delta(call_opt) == pytest.approx(_central(call_opt, "spot", h), rel=1e-3)


def test_gamma_matches_fd(call_opt):
    h = 0.01 * call_opt.spot
    p = BS.price(call_opt)
    p_up = BS.price(replace(call_opt, spot=call_opt.spot + h))
    p_dn = BS.price(replace(call_opt, spot=call_opt.spot - h))
    fd = (p_up - 2 * p + p_dn) / h**2
    assert BS.gamma(call_opt) == pytest.approx(fd, rel=1e-3)


def test_vega_matches_fd(call_opt):
    assert BS.vega(call_opt) == pytest.approx(_central(call_opt, "volatility", 1e-4), rel=1e-4)


def test_theta_matches_fd_and_is_negative(call_opt):
    # theta = −∂V/∂T; the sign trap — a long option loses value as expiry nears.
    h = 1e-4
    up = BS.price(replace(call_opt, maturity=call_opt.maturity + h))
    dn = BS.price(replace(call_opt, maturity=call_opt.maturity - h))
    fd = -(up - dn) / (2 * h)
    assert BS.theta(call_opt) == pytest.approx(fd, rel=1e-3)
    assert BS.theta(call_opt) < 0.0


def test_rho_matches_fd(call_opt):
    assert BS.rho(call_opt) == pytest.approx(_central(call_opt, "rate", 1e-4), rel=1e-4)
