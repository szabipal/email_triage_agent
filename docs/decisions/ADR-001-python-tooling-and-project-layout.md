# ADR-001: Python Tooling And Project Layout

## Status
Accepted

## Context
The system must be locally runnable, reproducible, maintainable, testable, and compatible with a Python-based AI application. This supports NFR-05, NFR-07, NFR-09, NFR-11, NFR-12, and the MVP setup requirements.

## Decision
Use Python 3.12, `uv` for dependency and virtual environment management, `pyproject.toml` for project configuration, a `src/email_agent/` source layout, Ruff for linting/formatting, Pyright for static type checking, and pytest for tests.

## Alternatives considered
Python 3.11, Python 3.13, pip/venv, Poetry, Black plus isort plus Flake8, mypy, and unittest.

## Consequences
Local setup is fast, modern, and reproducible. Tool configuration is centralized. Ruff reduces tool sprawl. Pyright gives useful type checking without requiring runtime framework changes. The main trade-off is choosing `uv`, which is newer than pip/venv.

## Reversal strategy
Move dependencies from `uv.lock`/`pyproject.toml` into another lock format such as Poetry or pip-tools, keep the `src/` layout, and replace tool commands in documentation and CI.
