import pytest

from ope.option.instrument import Option


@pytest.fixture(autouse=True)
def isolate_output_dirs(tmp_path, monkeypatch):
    """Redirect every output directory — for ope AND its pae + fmde dependencies
    (the ticker path invokes the whole chain) — to a per-test temp dir."""
    import fmde.config as fmde_config
    import pae.config as pae_config

    import ope.config as ope_config

    dir_attrs = (
        "raw_dir",
        "cleaned_dir",
        "processed_dir",
        "sample_dir",
        "metadata_dir",
        "reports_dir",
    )
    for name, settings in (
        ("ope", ope_config.SETTINGS),
        ("pae", pae_config.SETTINGS),
        ("fmde", fmde_config.SETTINGS),
    ):
        for attr in dir_attrs:
            target = tmp_path / name / attr.replace("_dir", "")
            target.mkdir(parents=True, exist_ok=True)
            monkeypatch.setattr(settings, attr, target)


@pytest.fixture
def call_opt() -> Option:
    """The Black-Scholes reference option: S=K=100, T=1, r=5%, σ=20%, q=0."""
    return Option(100.0, 100.0, 1.0, 0.05, 0.20, 0.0, "call")


@pytest.fixture
def put_opt() -> Option:
    return Option(100.0, 100.0, 1.0, 0.05, 0.20, 0.0, "put")
