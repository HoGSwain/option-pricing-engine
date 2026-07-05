"""Option instrument validation."""

import pytest

from ope.option.instrument import Option


def test_kind_must_be_call_or_put():
    with pytest.raises(ValueError):
        Option(100.0, 100.0, 1.0, kind="banana")


def test_exercise_must_be_european_or_american():
    with pytest.raises(ValueError):
        Option(100.0, 100.0, 1.0, exercise="bermudan")


def test_spot_and_strike_must_be_positive():
    with pytest.raises(ValueError):
        Option(0.0, 100.0, 1.0)
    with pytest.raises(ValueError):
        Option(100.0, -1.0, 1.0)


def test_is_call_property():
    assert Option(100.0, 100.0, 1.0, kind="call").is_call is True
    assert Option(100.0, 100.0, 1.0, kind="put").is_call is False
