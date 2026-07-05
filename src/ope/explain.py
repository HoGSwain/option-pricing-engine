"""
Explainability layer.

Turns the option analysis into a deterministic, plain-language explanation — the
sixth AIFEL question. A price of "$10.45" means little without its Greeks (how
it moves) and its assumptions; and when volatility is sourced from history, the
key honest caveat is that **realized volatility is not the market's implied
volatility**.

Generated deterministically from the actual numbers, NOT by a language model.
See docs/explainability.md.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from ope.option.black_scholes import Greeks
from ope.option.instrument import Option


@dataclass
class Explanation:
    findings: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = ["## Explanation", ""]
        lines += [f"- {f}" for f in self.findings]
        lines += ["", "## Limitations & assumptions", ""]
        lines += [f"- {lim}" for lim in self.limitations]
        return "\n".join(lines)


def explain(
    opt: Option,
    bs_price: float,
    greeks: Greeks,
    binomial_price: float,
    mc_price: float,
    mc_stderr: float,
    early_exercise_premium: float,
    methods_agree: bool,
    vol_source: str,
    source: str,
    implied_vol: Optional[float] = None,
) -> Explanation:
    """Deterministic, plain-language explanation of an option analysis."""
    moneyness = (
        "in-the-money"
        if (opt.is_call and opt.spot > opt.strike) or (not opt.is_call and opt.spot < opt.strike)
        else ("at-the-money" if abs(opt.spot - opt.strike) < 1e-9 else "out-of-the-money")
    )
    div = f", dividend {opt.dividend:.1%}" if opt.dividend else ""
    findings = [
        f"A {opt.maturity:g}-year {moneyness} {opt.kind} (strike ${opt.strike:,.2f}) on a "
        f"${opt.spot:,.2f} underlying (volatility {opt.volatility:.1%}, rate {opt.rate:.1%}{div}) "
        f"is worth ${bs_price:.2f} under Black-Scholes."
    ]
    findings.append(
        f"Delta {greeks.delta:+.3f}: the value moves about ${greeks.delta:+.2f} per $1 change in "
        f"the underlying. Gamma {greeks.gamma:.4f}; vega ${greeks.vega / 100:.3f} per 1% of "
        f"volatility; theta ${greeks.theta / 365:.3f} per calendar day (time decay)."
    )
    findings.append(
        f"Three independent methods agree: Black-Scholes ${bs_price:.2f}, a binomial tree "
        f"${binomial_price:.2f}, and Monte Carlo ${mc_price:.2f} (± ${mc_stderr:.2f}) — a "
        f"cross-check that the price is right."
        if methods_agree
        else (
            f"Method prices: Black-Scholes ${bs_price:.2f}, binomial ${binomial_price:.2f}, "
            f"Monte Carlo ${mc_price:.2f} (± ${mc_stderr:.2f})."
        )
    )
    if opt.exercise == "american" and early_exercise_premium > 1e-6:
        findings.append(
            f"As an American option it is worth ${binomial_price:.2f}, an early-exercise premium "
            f"of ${early_exercise_premium:.2f} over the otherwise-identical European."
        )
    if implied_vol is not None:
        findings.append(
            f"The implied volatility backed out from the supplied market price is "
            f"{implied_vol:.1%}."
        )

    limitations = [
        "Black-Scholes assumes lognormal prices, constant volatility, no jumps, and continuous "
        "costless hedging; the analytic price and Greeks are for European exercise.",
    ]
    if "realized" in vol_source.lower():
        limitations.append(
            "Volatility here is a HISTORICAL (realized) estimate from past returns — NOT the "
            "market's implied volatility. This answers 'what Black-Scholes says at historical vol', "
            "which will differ from a traded option's price; back out implied volatility from a "
            "live quote for a market-consistent number."
        )
    if source == "synthetic":
        limitations.append(
            "Any ticker inputs come from synthetic (seeded GBM) data for offline reproducibility, "
            "not real market data."
        )
    limitations += [
        "Greeks are local sensitivities (first/second order); Monte Carlo carries the stated "
        "sampling standard error.",
        "This engine supports human derivatives analysis; it does not make trading decisions.",
    ]
    return Explanation(findings=findings, limitations=limitations)
