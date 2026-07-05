# Contributing to OPE

This repository follows the AIFEL portfolio engineering standards.

## Workflow
1. Fork/branch from `main`.
2. Install dev dependencies: `pip install -e ".[dev]"`.
3. Run tests: `pytest -v --cov=ope`.
4. Run linting/formatting: `ruff check src tests` and `black src tests`.
5. Update `docs/` if you change methodology or add a design decision.
6. Update `CHANGELOG.md`.
7. Open a pull request describing the problem, the change, and how it was validated.

## Code style
- Format with `black` (line length 100).
- Lint with `ruff`.
- Every public function needs a docstring explaining *why*, not just *what*.
- Every new design decision (pricing convention, parameter default) must be added to `docs/assumptions.md`.

## Option math
- Every formula must have its definition and convention in `docs/methodology.md`.
- Every pricer and Greek must be covered by a test validating it against a
  closed-form/textbook value or an independent oracle (the finite-difference
  Greeks check, put-call parity, or cross-method convergence) — not merely that
  the code runs.
- Pricing functions return **raw partial derivatives**; presentation-unit
  conversions (vega per 1%, theta per day) belong in the reporting layer.
- Every conclusion must ship with its assumptions and limitations (see `docs/explainability.md`).
