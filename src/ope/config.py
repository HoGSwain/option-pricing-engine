"""
Central configuration for the Option Pricing Engine (OPE).

Mirrors the fmde/pae/poe/rae/bae settings pattern: one dataclass so every run
records exactly how it was parameterized. Conventions shared across the AIFEL
portfolio are reused (see ``docs/assumptions.md``).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PACKAGE_VERSION = "0.1.0"
OPTION_VERSION = "1.0.0"  # bump when a pricing/greek definition changes


@dataclass
class Settings:
    data_dir: Path = Path("data")
    reports_dir: Path = Path("reports")

    raw_dir: Path = field(init=False)
    cleaned_dir: Path = field(init=False)
    processed_dir: Path = field(init=False)
    sample_dir: Path = field(init=False)
    metadata_dir: Path = field(init=False)

    # Default risk-free rate (annual, continuously compounded for BS).
    default_rate: float = 0.05

    # Numerical-method resolution.
    binomial_steps: int = 500
    mc_paths: int = 100_000
    mc_seed: int = 42

    default_start: str = "2018-01-01"
    default_end: Optional[str] = None  # None => today

    def __post_init__(self) -> None:
        self.raw_dir = self.data_dir / "raw"
        self.cleaned_dir = self.data_dir / "cleaned"
        self.processed_dir = self.data_dir / "processed"
        self.sample_dir = self.data_dir / "sample"
        self.metadata_dir = self.data_dir / "metadata"
        for d in (
            self.raw_dir,
            self.cleaned_dir,
            self.processed_dir,
            self.sample_dir,
            self.metadata_dir,
            self.reports_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)


SETTINGS = Settings()
