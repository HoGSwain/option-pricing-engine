"""Monte-Carlo pricing: statistical agreement with Black-Scholes and determinism."""

from ope.option import black_scholes as BS
from ope.option import monte_carlo as MC


def test_mc_within_three_stderr_of_bs(call_opt):
    price, stderr = MC.monte_carlo_price(call_opt, n_paths=100_000, seed=42)
    assert abs(price - BS.price(call_opt)) < 3 * stderr


def test_mc_put_within_three_stderr_of_bs(put_opt):
    price, stderr = MC.monte_carlo_price(put_opt, n_paths=100_000, seed=42)
    assert abs(price - BS.price(put_opt)) < 3 * stderr


def test_mc_is_deterministic_for_a_seed(call_opt):
    a, _ = MC.monte_carlo_price(call_opt, n_paths=50_000, seed=7)
    b, _ = MC.monte_carlo_price(call_opt, n_paths=50_000, seed=7)
    assert a == b


def test_mc_stderr_is_positive(call_opt):
    _, stderr = MC.monte_carlo_price(call_opt, n_paths=10_000, seed=1)
    assert stderr > 0.0
