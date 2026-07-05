"""
Pipeline orchestrator.

The single entry point for option analysis:
``from ope.pipeline import run_option_analysis``. It prices an option by three
methods (Black-Scholes, binomial, Monte-Carlo), computes the Greeks, optionally
backs out implied volatility, and persists the results plus a plain-language
explanation. Spot and volatility are supplied directly, or sourced for a ticker
from Projects 1-2 (``source.market``).
"""

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

from ope.config import SETTINGS
from ope.explain import Explanation, explain
from ope.option import binomial as BN
from ope.option import black_scholes as BS
from ope.option import monte_carlo as MC
from ope.option.black_scholes import Greeks
from ope.option.instrument import Option
from ope.reporting.report import generate_report
from ope.source.market import market_inputs
from ope.storage.manager import save_all
from ope.utils.logging import logger


@dataclass
class OptionResult:
    option: Option
    spot_source: str
    vol_source: str
    source: str
    bs_price: float
    greeks: Greeks
    binomial_price: float
    binomial_european: float
    mc_price: float
    mc_stderr: float
    early_exercise_premium: float
    implied_vol: Optional[float]
    methods_agree: bool
    storage_paths: dict
    report_path: Path
    explanation: Explanation


def run_option_analysis(
    strike: float,
    maturity: float,
    spot: Optional[float] = None,
    volatility: Optional[float] = None,
    rate: Optional[float] = None,
    dividend: float = 0.0,
    kind: str = "call",
    exercise: str = "european",
    ticker: Optional[str] = None,
    source: str = "synthetic",
    start: str = SETTINGS.default_start,
    end: Optional[str] = None,
    steps: Optional[int] = None,
    mc_paths: Optional[int] = None,
    mc_seed: Optional[int] = None,
    market_price: Optional[float] = None,
) -> OptionResult:
    """Price an option (three methods + Greeks) from given inputs or a ticker."""
    rate = SETTINGS.default_rate if rate is None else rate
    steps = steps or SETTINGS.binomial_steps
    mc_paths = mc_paths or SETTINGS.mc_paths
    mc_seed = SETTINGS.mc_seed if mc_seed is None else mc_seed

    spot_source, vol_source = "given", "given"
    if ticker is not None:
        src_spot, realized_vol = market_inputs(ticker, start, end, source)
        if spot is None:
            spot, spot_source = src_spot, f"{ticker} spot via fmde ({source})"
        if volatility is None:
            volatility, vol_source = realized_vol, f"{ticker} realized volatility via pae"
    if spot is None or volatility is None:
        raise ValueError(
            "provide spot and volatility, or a ticker to source them from Projects 1-2"
        )

    opt = Option(
        spot=spot,
        strike=strike,
        maturity=maturity,
        rate=rate,
        volatility=volatility,
        dividend=dividend,
        kind=kind,
        exercise=exercise,
    )
    logger.info(
        f"Option analysis: {maturity:g}y {exercise} {kind} K={strike} on S={spot:.2f} "
        f"(vol {volatility:.1%})"
    )

    bs_price = BS.price(opt)
    grk = BS.greeks(opt)
    euro = replace(opt, exercise="european")
    binomial_european = BN.binomial_price(euro, steps)
    binomial_price = BN.binomial_price(opt, steps)
    mc_price, mc_stderr = MC.monte_carlo_price(euro, mc_paths, mc_seed)
    early = binomial_price - binomial_european if exercise == "american" else 0.0
    implied_vol = BS.implied_volatility(opt, market_price) if market_price is not None else None
    methods_agree = abs(bs_price - binomial_european) < 0.05 and abs(bs_price - mc_price) < (
        3 * mc_stderr + 0.05
    )

    explanation = explain(
        opt,
        bs_price,
        grk,
        binomial_price,
        binomial_european,
        mc_price,
        mc_stderr,
        early,
        methods_agree,
        vol_source,
        source,
        used_market_data=ticker is not None,
        implied_vol=implied_vol,
    )
    row = {
        "spot": spot,
        "strike": strike,
        "maturity": maturity,
        "rate": rate,
        "volatility": volatility,
        "dividend": dividend,
        "kind": kind,
        "exercise": exercise,
        "bs_price": bs_price,
        "binomial_price": binomial_price,
        "binomial_european": binomial_european,
        "mc_price": mc_price,
        "mc_stderr": mc_stderr,
        "early_exercise_premium": early,
        **{f"greek_{k}": v for k, v in grk.to_dict().items()},
        "implied_vol": implied_vol,
    }
    storage_paths = save_all(
        row, opt, spot_source, vol_source, source, SETTINGS.processed_dir, SETTINGS.metadata_dir
    )
    report_path = generate_report(
        opt,
        bs_price,
        grk,
        binomial_price,
        binomial_european,
        mc_price,
        mc_stderr,
        early,
        implied_vol,
        SETTINGS.reports_dir,
        explanation,
    )

    logger.success(f"Option analysis complete -> {storage_paths['analytics_csv']}")
    return OptionResult(
        option=opt,
        spot_source=spot_source,
        vol_source=vol_source,
        source=source,
        bs_price=bs_price,
        greeks=grk,
        binomial_price=binomial_price,
        binomial_european=binomial_european,
        mc_price=mc_price,
        mc_stderr=mc_stderr,
        early_exercise_premium=early,
        implied_vol=implied_vol,
        methods_agree=methods_agree,
        storage_paths=storage_paths,
        report_path=report_path,
        explanation=explanation,
    )
