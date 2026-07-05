"""
Reproducible chart generation for the README / LinkedIn post.

Runs fully headless (matplotlib "Agg"). The option math is standalone, so the
charts need no network or data chain. Writes PNGs to ``screenshots/`` and a small
committed sample (an option chain across strikes) to ``data/sample/``.

Run from the repository root:  python notebooks/generate_charts.py
"""

from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ope.option import binomial as BN  # noqa: E402
from ope.option import black_scholes as BS  # noqa: E402
from ope.option.instrument import Option  # noqa: E402

screenshots = Path("screenshots")
screenshots.mkdir(exist_ok=True)
sample_dir = Path("data/sample")
sample_dir.mkdir(parents=True, exist_ok=True)

K, T, r, sigma = 100.0, 1.0, 0.05, 0.20
base_call = Option(100.0, K, T, r, sigma, 0.0, "call")
base_put = Option(100.0, K, T, r, sigma, 0.0, "put")

# 1) Option value vs spot — the gap above intrinsic payoff is time value
spots = np.linspace(50.0, 150.0, 200)
call_vals = np.array([BS.price(replace(base_call, spot=s)) for s in spots])
put_vals = np.array([BS.price(replace(base_put, spot=s)) for s in spots])
call_payoff = np.maximum(spots - K, 0.0)
put_payoff = np.maximum(K - spots, 0.0)

fig, ax = plt.subplots(1, 2, figsize=(12, 5.5))
ax[0].plot(spots, call_vals, color="navy", linewidth=2, label="BS value")
ax[0].plot(spots, call_payoff, color="firebrick", linestyle="--", label="Intrinsic payoff")
ax[0].axvline(K, color="grey", linewidth=0.8, alpha=0.6)
ax[0].fill_between(spots, call_payoff, call_vals, color="skyblue", alpha=0.3, label="Time value")
ax[0].set_title("Call — value vs spot")
ax[0].set_xlabel("Spot price")
ax[0].set_ylabel("Option value")
ax[0].legend()
ax[0].grid(alpha=0.3)

ax[1].plot(spots, put_vals, color="darkgreen", linewidth=2, label="BS value")
ax[1].plot(spots, put_payoff, color="firebrick", linestyle="--", label="Intrinsic payoff")
ax[1].axvline(K, color="grey", linewidth=0.8, alpha=0.6)
ax[1].fill_between(spots, put_payoff, put_vals, color="lightgreen", alpha=0.3, label="Time value")
ax[1].set_title("Put — value vs spot")
ax[1].set_xlabel("Spot price")
ax[1].set_ylabel("Option value")
ax[1].legend()
ax[1].grid(alpha=0.3)
fig.suptitle(
    f"1-year options, K={K:.0f}, r={r:.0%}, σ={sigma:.0%} — curve above payoff is time value"
)
plt.tight_layout()
plt.savefig(screenshots / "01_value_vs_spot.png", dpi=120)
plt.close()

# 2) Greeks vs spot — delta (call/put) and gamma
call_delta = np.array([BS.delta(replace(base_call, spot=s)) for s in spots])
put_delta = np.array([BS.delta(replace(base_put, spot=s)) for s in spots])
gamma = np.array([BS.gamma(replace(base_call, spot=s)) for s in spots])

fig, ax1 = plt.subplots(figsize=(9, 5.5))
ax1.plot(spots, call_delta, color="navy", linewidth=2, label="Call delta")
ax1.plot(spots, put_delta, color="darkgreen", linewidth=2, label="Put delta")
ax1.axvline(K, color="grey", linewidth=0.8, alpha=0.6)
ax1.set_xlabel("Spot price")
ax1.set_ylabel("Delta")
ax1.grid(alpha=0.3)
ax2 = ax1.twinx()
ax2.plot(spots, gamma, color="firebrick", linestyle=":", linewidth=2, label="Gamma")
ax2.set_ylabel("Gamma")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="center right")
plt.title("Greeks vs spot — delta sweeps 0→1 (call), gamma peaks at the money")
plt.tight_layout()
plt.savefig(screenshots / "02_greeks_vs_spot.png", dpi=120)
plt.close()

# 3) Binomial convergence to the Black-Scholes price
bs_price = BS.price(base_call)
steps = list(range(5, 205, 5))
bino = [BN.binomial_price(base_call, n) for n in steps]
plt.figure(figsize=(9, 5.5))
plt.plot(steps, bino, color="navy", marker="o", markersize=3, linewidth=1, label="Binomial (CRR)")
plt.axhline(bs_price, color="firebrick", linestyle="--", label=f"Black-Scholes = {bs_price:.4f}")
plt.title("Binomial price converges to Black-Scholes as steps increase")
plt.xlabel("Tree steps")
plt.ylabel("Call price")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(screenshots / "03_binomial_convergence.png", dpi=120)
plt.close()

# Committed sample: an option chain across strikes (moneyness ladder)
rows = []
for strike in [80, 90, 100, 110, 120]:
    c = Option(100.0, strike, T, r, sigma, 0.0, "call")
    g = BS.greeks(c)
    rows.append(
        {
            "strike": strike,
            "moneyness": "ITM" if strike < 100 else ("ATM" if strike == 100 else "OTM"),
            "call_price": BS.price(c),
            "put_price": BS.price(replace(c, kind="put")),
            "delta": g.delta,
            "gamma": g.gamma,
            "vega_per_1pct": g.vega / 100,
            "theta_per_day": g.theta / 365,
        }
    )
pd.DataFrame(rows).to_csv(sample_dir / "option_chain_sample.csv", index=False)

print("screenshots:", sorted(p.name for p in screenshots.glob("*.png")))
print("samples:", sorted(p.name for p in sample_dir.glob("*.csv")))
