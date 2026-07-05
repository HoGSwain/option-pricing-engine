"""Market-input adapter — the fmde + pae composition."""

from ope.source.market import market_inputs


def test_market_inputs_returns_spot_and_realized_vol():
    spot, vol = market_inputs("AAA", start="2022-01-01", end="2022-12-31", source="synthetic")
    assert spot > 0.0
    assert 0.0 < vol < 2.0  # a sane annualized volatility
