"""Storage layer: CSV + run metadata."""

import json

from ope.option.instrument import Option
from ope.storage.manager import save_all


def test_save_all_writes_csv_and_metadata():
    opt = Option(100.0, 100.0, 1.0, 0.05, 0.20, 0.0, "call")
    row = {"spot": 100.0, "strike": 100.0, "bs_price": 10.4506}
    paths = save_all(row, opt, "given", "given", "synthetic")

    assert paths["analytics_csv"].exists()
    assert paths["metadata"].exists()

    meta = json.loads(paths["metadata"].read_text())
    assert meta["option"]["strike"] == 100.0
    assert meta["option"]["kind"] == "call"
    assert meta["analytics_checksum_md5"]
    assert meta["option_version"]
    assert meta["package_version"]
