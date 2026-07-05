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


def test_american_agreement_line_uses_european_not_american_price():
    # The cross-check must compare three EUROPEAN prices; the American value goes
    # on its own premium line (regression: the agreement line once showed the
    # American price and self-contradicted).
    r = run_option_analysis(
        strike=100, maturity=1, spot=90, volatility=0.30, kind="put", exercise="american"
    )
    assert r.early_exercise_premium > 0.01  # the two binomial prices genuinely differ
    agreement = next(f for f in r.explanation.findings if f.startswith("Three independent"))
    assert f"${r.binomial_european:.2f}" in agreement
    assert f"${r.binomial_price:.2f}" not in agreement
    premium_line = next(f for f in r.explanation.findings if "early-exercise premium" in f)
    assert f"${r.binomial_price:.2f}" in premium_line


def test_no_synthetic_caveat_on_explicit_inputs():
    r = run_option_analysis(strike=100, maturity=1, spot=100, volatility=0.20)
    assert not any("synthetic" in lim.lower() for lim in r.explanation.limitations)
