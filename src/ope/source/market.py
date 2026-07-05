"""
Market-input adapter — the point where OPE composes with Projects 1-2.

Option pricing math is standalone, but pricing an option *on a real ticker*
needs a spot price and a volatility. This module sources both from the earlier
projects: the latest price from Project 1 (``fmde``) and a **realized**
annualized-volatility estimate by reusing Project 2's
``pae.metrics.annualized_volatility``. This is a genuine composition — options
are written on the equities those projects already model.
"""

from typing import Optional, Tuple

from fmde.pipeline import run_pipeline
from pae.metrics.analytics import annualized_volatility

from ope.utils.logging import logger


def market_inputs(
    ticker: str,
    start: str,
    end: Optional[str] = None,
    source: str = "synthetic",
) -> Tuple[float, float]:
    """Return ``(spot, realized_volatility)`` for a ticker: the latest
    fmde-cleaned adjusted close, and pae's annualized volatility of its returns."""
    logger.info(f"Sourcing spot + realized volatility for {ticker} via fmde/pae (source={source})")
    result = run_pipeline(ticker=ticker, start=start, end=end, source=source)
    spot = float(result.features["adj_close"].iloc[-1])
    vol = float(annualized_volatility(result.features["arithmetic_return"].dropna()))
    return spot, vol
