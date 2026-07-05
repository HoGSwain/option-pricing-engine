"""
Storage layer.

Persists the option analysis (one-row CSV) and a JSON run-metadata file (option
spec, sources, timestamp, checksum, versions) for reproducibility — mirroring
the portfolio pattern. Directory arguments resolve ``SETTINGS`` at call time.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from ope.config import OPTION_VERSION, PACKAGE_VERSION, SETTINGS
from ope.option.instrument import Option


def _checksum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def save_analysis_csv(
    row: dict, directory: Optional[Path] = None, filename: str = "option_analytics.csv"
) -> Path:
    directory = directory if directory is not None else SETTINGS.processed_dir
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    pd.DataFrame([row]).to_csv(path, index=False)
    return path


def save_run_metadata(
    option: Option,
    spot_source: str,
    vol_source: str,
    source: str,
    analytics_csv: Optional[Path],
    directory: Optional[Path] = None,
    filename: str = "option_metadata.json",
) -> Path:
    directory = directory if directory is not None else SETTINGS.metadata_dir
    directory.mkdir(parents=True, exist_ok=True)
    meta = {
        "option": {
            "spot": option.spot,
            "strike": option.strike,
            "maturity": option.maturity,
            "rate": option.rate,
            "volatility": option.volatility,
            "dividend": option.dividend,
            "kind": option.kind,
            "exercise": option.exercise,
        },
        "spot_source": spot_source,
        "vol_source": vol_source,
        "source": source,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "analytics_checksum_md5": _checksum(analytics_csv) if analytics_csv else None,
        "package_version": PACKAGE_VERSION,
        "option_version": OPTION_VERSION,
    }
    path = directory / filename
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)
    return path


def save_all(
    row: dict,
    option: Option,
    spot_source: str,
    vol_source: str,
    source: str,
    processed_dir: Optional[Path] = None,
    metadata_dir: Optional[Path] = None,
) -> dict:
    """Write the analysis CSV + run metadata."""
    csv_path = save_analysis_csv(row, processed_dir)
    meta_path = save_run_metadata(option, spot_source, vol_source, source, csv_path, metadata_dir)
    return {"analytics_csv": csv_path, "metadata": meta_path}
