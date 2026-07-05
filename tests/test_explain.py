"""Explainability layer: deterministic, honest, and human-in-the-loop."""

from ope.pipeline import run_option_analysis


def test_explanation_states_price_and_greeks():
    r = run_option_analysis(strike=100, maturity=1, spot=100, volatility=0.20)
    findings = " ".join(r.explanation.findings)
    assert "Black-Scholes" in findings
    assert "Delta" in findings


def test_explanation_flags_realized_vs_implied_vol_when_ticker_sourced():
    # Sourcing vol from history must surface the realized≠implied caveat.
    r = run_option_analysis(strike=100, maturity=0.5, ticker="AAA", source="synthetic")
    limitations = " ".join(r.explanation.limitations).lower()
    assert "realized" in limitations
    assert "implied volatility" in limitations
    assert "does not make trading decisions" in limitations


def test_report_embeds_explanation():
    r = run_option_analysis(strike=100, maturity=1, spot=100, volatility=0.20)
    text = r.report_path.read_text(encoding="utf-8")
    assert "## Explanation" in text
    assert "## Limitations & assumptions" in text


def test_explanation_is_deterministic():
    a = run_option_analysis(strike=100, maturity=1, spot=100, volatility=0.20).explanation
    b = run_option_analysis(strike=100, maturity=1, spot=100, volatility=0.20).explanation
    assert a.findings == b.findings
    assert a.limitations == b.limitations
