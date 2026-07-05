"""
Command-line interface for the Option Pricing Engine.

Usage:
    ope price 100 1 --spot 100 --vol 0.2                 # explicit inputs
    ope price 250 0.5 --ticker AAPL --source synthetic   # spot + realized vol from Projects 1-2
    ope price 100 1 --spot 100 --vol 0.2 --kind put --exercise american
    ope info
"""

import sys
from typing import Optional

import typer

# Windows consoles default to a legacy code page (cp1252) that cannot encode the
# ✔/✘ status glyphs printed below; force UTF-8 on the standard streams (fixed in
# Project 1). Guarded because a captured stream may lack reconfigure().
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001 - stream setup must never break import
        pass

from ope.config import PACKAGE_VERSION, SETTINGS  # noqa: E402
from ope.pipeline import run_option_analysis  # noqa: E402
from ope.utils.logging import logger  # noqa: E402

app = typer.Typer(help="Option Pricing Engine (OPE) — AIFEL Project 6")


@app.command()
def price(
    strike: float = typer.Argument(..., help="Strike price K"),
    maturity: float = typer.Argument(..., help="Years to expiry T"),
    spot: Optional[float] = typer.Option(None, help="Underlying spot price S"),
    vol: Optional[float] = typer.Option(None, help="Annualized volatility, e.g. 0.2"),
    ticker: Optional[str] = typer.Option(None, help="Source spot + realized vol for this ticker"),
    rate: float = typer.Option(SETTINGS.default_rate, help="Risk-free rate, e.g. 0.05"),
    dividend: float = typer.Option(0.0, help="Continuous dividend yield q"),
    kind: str = typer.Option("call", help="'call' or 'put'"),
    exercise: str = typer.Option("european", help="'european' or 'american'"),
    source: str = typer.Option(
        "synthetic", help="fmde source for --ticker: 'synthetic'|'yfinance'"
    ),
) -> None:
    """Price an option by Black-Scholes, binomial, and Monte-Carlo, with Greeks.
    Provide --spot and --vol, or --ticker to source them from Projects 1-2."""
    try:
        result = run_option_analysis(
            strike=strike,
            maturity=maturity,
            spot=spot,
            volatility=vol,
            rate=rate,
            dividend=dividend,
            kind=kind,
            exercise=exercise,
            ticker=ticker,
            source=source,
        )
    except Exception as exc:  # noqa: BLE001
        typer.secho(f"✘ option analysis failed: {exc}", fg=typer.colors.RED)
        logger.exception("run_option_analysis failed")
        raise typer.Exit(code=1)

    g = result.greeks
    typer.secho(
        f"✔ {result.option.kind} price: BS=${result.bs_price:.4f}  "
        f"binomial=${result.binomial_price:.4f}  MC=${result.mc_price:.4f}±{result.mc_stderr:.4f}",
        fg=typer.colors.GREEN,
    )
    typer.echo(
        f"  greeks: delta={g.delta:+.4f} gamma={g.gamma:.5f} vega={g.vega / 100:+.4f}/1% "
        f"theta={g.theta / 365:+.4f}/day rho={g.rho / 100:+.4f}/1%"
    )
    if result.option.exercise == "american":
        typer.echo(f"  early-exercise premium: ${result.early_exercise_premium:.4f}")
    typer.echo(f"analytics -> {result.storage_paths['analytics_csv']}")
    typer.echo(f"report    -> {result.report_path}")


@app.command()
def info() -> None:
    """Show package/version and configured pricing defaults."""
    typer.echo(f"Option Pricing Engine v{PACKAGE_VERSION}")
    typer.echo(f"  data_dir       = {SETTINGS.data_dir.resolve()}")
    typer.echo(f"  reports_dir    = {SETTINGS.reports_dir.resolve()}")
    typer.echo(f"  default_rate   = {SETTINGS.default_rate}")
    typer.echo(f"  binomial_steps = {SETTINGS.binomial_steps}")
    typer.echo(f"  mc_paths       = {SETTINGS.mc_paths} (seed {SETTINGS.mc_seed})")


if __name__ == "__main__":
    app()
