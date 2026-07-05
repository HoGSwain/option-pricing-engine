"""Binomial (CRR) tree: convergence to Black-Scholes and American invariants.

American vs European comparisons are made on the *same tree* (same step count),
so they test the early-exercise logic itself, not discretization differences."""

from dataclasses import replace

import pytest

from ope.option import binomial as BN
from ope.option import black_scholes as BS
from ope.option.instrument import Option


def test_european_binomial_converges_to_bs(call_opt):
    assert BN.binomial_price(call_opt, 1000) == pytest.approx(BS.price(call_opt), abs=0.01)


def test_european_put_binomial_converges_to_bs(put_opt):
    assert BN.binomial_price(put_opt, 1000) == pytest.approx(BS.price(put_opt), abs=0.01)


def test_american_put_ge_european_put_same_tree(put_opt):
    am = BN.binomial_price(replace(put_opt, exercise="american"), 500)
    eu = BN.binomial_price(put_opt, 500)
    assert am >= eu


def test_american_call_equals_european_call_without_dividends(call_opt):
    # No dividends → never optimal to exercise an American call early.
    am = BN.binomial_price(replace(call_opt, exercise="american"), 500)
    eu = BN.binomial_price(call_opt, 500)
    assert am == pytest.approx(eu, abs=1e-9)


def test_binomial_zero_time_is_intrinsic():
    itm = Option(100.0, 90.0, 0.0, 0.05, 0.20, 0.0, "call")
    assert BN.binomial_price(itm, 100) == pytest.approx(10.0)
