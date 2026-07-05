# API Reference

## `ope.option.instrument`

```python
Option(spot, strike, maturity, rate=0.05, volatility=0.20,
       dividend=0.0, kind="call", exercise="european")
```
Frozen, validated dataclass. `kind ∈ {"call","put"}`, `exercise ∈
{"european","american"}`; spot/strike must be positive, maturity/volatility/
dividend non-negative. Property `is_call`.

## `ope.option.black_scholes`

```python
price(opt) -> float
delta(opt) -> float ; gamma(opt) -> float ; vega(opt) -> float
theta(opt) -> float ; rho(opt) -> float
greeks(opt) -> Greeks                       # dataclass; .to_dict()
implied_volatility(opt, market_price) -> float
```
Greeks are **raw partials** (per unit of the underlying variable). Vega is per
1.0 of volatility, theta per year, rho per 1.0 of rate — convert for display.

## `ope.option.binomial`

```python
binomial_price(opt, steps=500) -> float
```
Cox-Ross-Rubinstein tree. Prices European or American exercise per `opt.exercise`.

## `ope.option.monte_carlo`

```python
monte_carlo_price(opt, n_paths=100_000, seed=42) -> tuple[float, float]
```
Returns `(price, standard_error)`. European exercise only; seeded for reproducibility.

## `ope.source.market`

```python
market_inputs(ticker, start, end=None, source="synthetic") -> tuple[float, float]
```
Returns `(spot, realized_volatility)` — the latest fmde adjusted close and pae's
annualized volatility of the returns. `source ∈ {"synthetic","yfinance"}`.

## `ope.pipeline`

```python
run_option_analysis(strike, maturity, spot=None, volatility=None, rate=None,
                    dividend=0.0, kind="call", exercise="european",
                    ticker=None, source="synthetic", start=..., end=None,
                    steps=None, mc_paths=None, mc_seed=None,
                    market_price=None) -> OptionResult
```
Prices by all three methods, computes Greeks, optionally backs out implied vol,
writes CSV + metadata + report. Provide `spot` and `volatility`, **or** a
`ticker` to source them. `OptionResult` fields: `option`, `spot_source`,
`vol_source`, `source`, `bs_price`, `greeks`, `binomial_price`,
`binomial_european`, `mc_price`, `mc_stderr`, `early_exercise_premium`,
`implied_vol`, `methods_agree`, `storage_paths`, `report_path`, `explanation`.

## `ope.explain`

```python
explain(...) -> Explanation      # .findings, .limitations, .to_markdown()
```

## CLI

```bash
ope price STRIKE MATURITY [--spot S --vol σ | --ticker SYM]
         [--rate 0.05] [--dividend 0.0] [--kind call|put]
         [--exercise european|american] [--source synthetic|yfinance]
ope info
```
