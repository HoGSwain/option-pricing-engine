"""Reporting layer: the Markdown report renders the expected sections."""

from ope.config import SETTINGS
from ope.option import black_scholes as BS
from ope.reporting.report import generate_report


def test_report_contains_expected_sections(call_opt):
    g = BS.greeks(call_opt)
    path = generate_report(
        option=call_opt,
        bs_price=BS.price(call_opt),
        greeks=g,
        binomial_price=10.4486,
        binomial_european=10.4486,
        mc_price=10.4205,
        mc_stderr=0.05,
        early_exercise_premium=0.0,
        implied_vol=None,
        output_dir=SETTINGS.reports_dir,
    )
    text = path.read_text(encoding="utf-8")
    assert "# Option Analytics Report" in text
    assert "Black-Scholes" in text
    assert "## Greeks" in text
    assert "Delta" in text
    assert "per 1% of volatility" in text  # vega shown in conventional units
