"""
Reporting layer.

Renders the option analysis into a human-readable Markdown report. Greeks are
shown in their conventional presentation units (vega per 1% of volatility, theta
per calendar day) — the conversion happens *here*, not in the pricing functions
(which return raw partials for finite-difference testing).
"""

from pathlib import Path
from typing import Optional

from ope.explain import Explanation
from ope.option.black_scholes import Greeks
from ope.option.instrument import Option


def generate_report(
    option: Option,
    bs_price: float,
    greeks: Greeks,
    binomial_price: float,
    binomial_european: float,
    mc_price: float,
    mc_stderr: float,
    early_exercise_premium: float,
    implied_vol: Optional[float],
    output_dir: Path,
    explanation: Optional[Explanation] = None,
    filename: str = "option_report.md",
) -> Path:
    o = option
    lines = [
        "# Option Analytics Report",
        "",
        f"**Contract:** {o.maturity:g}-year {o.exercise} {o.kind}, strike ${o.strike:,.2f}  ",
        f"**Underlying:** ${o.spot:,.2f} · volatility {o.volatility:.2%} · rate {o.rate:.2%}"
        + (f" · dividend {o.dividend:.2%}" if o.dividend else ""),
        "",
        "## Price by method",
        "",
        "| Method | Price |",
        "|---|---|",
        f"| Black-Scholes (European, analytic) | ${bs_price:.4f} |",
        f"| Binomial ({o.exercise}) | ${binomial_price:.4f} |",
        f"| Monte Carlo (European) | ${mc_price:.4f} ± {mc_stderr:.4f} |",
    ]
    if o.exercise == "american":
        # For an American option the European tree is the benchmark the premium is measured against.
        lines.append(f"| Binomial (European benchmark) | ${binomial_european:.4f} |")
        lines.append(f"| Early-exercise premium | ${early_exercise_premium:.4f} |")
    if implied_vol is not None:
        lines.append(f"| Implied volatility (from market price) | {implied_vol:.4%} |")

    lines += [
        "",
        "## Greeks (Black-Scholes)",
        "",
        "| Greek | Value | Interpretation |",
        "|---|---|---|",
        f"| Delta | {greeks.delta:+.4f} | price change per $1 in the underlying |",
        f"| Gamma | {greeks.gamma:.5f} | delta change per $1 in the underlying |",
        f"| Vega | {greeks.vega / 100:+.4f} | price change per 1% of volatility |",
        f"| Theta | {greeks.theta / 365:+.4f} | price change per calendar day (decay) |",
        f"| Rho | {greeks.rho / 100:+.4f} | price change per 1% (100bp) of rate |",
        "",
        "## Notes",
        "",
        "- Black-Scholes prices European exercise; the binomial tree also prices "
        "American exercise (the difference is the early-exercise premium). "
        "Agreement across the three methods is a cross-check.",
        "- Greeks above are shown in conventional units; the engine computes raw "
        "partials internally. All formulas are in "
        "[`docs/methodology.md`](../docs/methodology.md).",
        "",
    ]
    if explanation is not None:
        lines += [explanation.to_markdown(), ""]

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
