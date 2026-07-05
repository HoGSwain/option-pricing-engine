"""
Option instrument definition.

A vanilla European or American call/put on a single underlying, with a
continuous dividend yield ``q``. All prices/Greeks are functions of
(spot, strike, maturity, rate, volatility, dividend, kind).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Option:
    spot: float  # S — underlying price
    strike: float  # K
    maturity: float  # T — years to expiry
    rate: float = 0.05  # r — risk-free rate (continuously compounded)
    volatility: float = 0.20  # σ — annualized
    dividend: float = 0.0  # q — continuous dividend yield
    kind: str = "call"  # "call" | "put"
    exercise: str = "european"  # "european" | "american"

    def __post_init__(self) -> None:
        if self.kind not in ("call", "put"):
            raise ValueError(f"kind must be 'call' or 'put', got {self.kind!r}")
        if self.exercise not in ("european", "american"):
            raise ValueError(f"exercise must be 'european' or 'american', got {self.exercise!r}")
        if self.spot <= 0 or self.strike <= 0:
            raise ValueError("spot and strike must be positive")
        if self.maturity < 0 or self.volatility < 0:
            raise ValueError("maturity and volatility must be non-negative")

    @property
    def is_call(self) -> bool:
        return self.kind == "call"
