"""Option Pricing Engine (OPE) — AIFEL Project 6.

European and American option pricing by three methods — Black-Scholes (analytic),
a Cox-Ross-Rubinstein binomial tree, and Monte-Carlo — with the full set of
Greeks and implied volatility.

The pricing math is **standalone** (functions of spot, strike, volatility, rate,
time, dividend). An optional path prices options on a real ticker by sourcing
the spot price from Project 1 (``fmde``) and a realized-volatility estimate from
Project 2 (``pae``) — a genuine composition, since options are written on the
equities those projects already model.
"""

__version__ = "0.1.0"
