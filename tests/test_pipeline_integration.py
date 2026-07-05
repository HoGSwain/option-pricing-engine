"""End-to-end pipeline: given inputs, ticker-sourced inputs, and persistence."""

import pytest

from ope.pipeline import run_option_analysis


def test_run_from_given_inputs():
    r = run_option_analysis(strike=100, maturity=1, spot=100, volatility=0.20)
    assert r.bs_price == pytest.approx(10.4506, abs=1e-3)
    assert r.methods_agree
    assert r.storage_paths["analytics_csv"].exists()
    assert r.storage_paths["metadata"].exists()
    assert r.report_path.exists()
    assert "Option Analytics Report" in r.report_path.read_text(encoding="utf-8")


def test_run_from_ticker_sources_inputs():
    r = run_option_analysis(strike=100, maturity=0.5, ticker="AAA", source="synthetic")
    assert "AAA" in r.spot_source
    assert "pae" in r.vol_source
    assert r.option.spot > 0.0
    assert r.option.volatility > 0.0


def test_american_put_early_exercise_premium_non_negative():
    r = run_option_analysis(
        strike=100, maturity=1, spot=90, volatility=0.30, kind="put", exercise="american"
    )
    assert r.early_exercise_premium >= 0.0
    assert r.binomial_price >= r.binomial_european - 1e-9


def test_requires_inputs_or_ticker():
    with pytest.raises(ValueError):
        run_option_analysis(strike=100, maturity=1)


def test_implied_vol_from_market_price():
    r = run_option_analysis(strike=100, maturity=1, spot=100, volatility=0.20, market_price=12.0)
    assert r.implied_vol is not None
    assert r.implied_vol > 0.0
