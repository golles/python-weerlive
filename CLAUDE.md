# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`weerlive-api` is an asynchronous Python client for the [Weerlive](https://weerlive.nl) weather API (Dutch weather service). It wraps a single upstream endpoint and deserializes the response into typed dataclasses. Targets Python 3.14 only.

## Commands

This project uses [uv](https://docs.astral.sh/uv) for dependency and environment management. Prefix Python tooling with `uv run`.

- Set up local environment: `./scripts/setup_env.sh` (creates `.venv`, installs deps + npm tools)
- Run tests: `uv run pytest`
- Run a single test: `uv run pytest tests/test_api.py::test_name`
- Run all CI checks locally: `./scripts/local_ci_checks.sh` (parses and runs the `checks` matrix from [.github/workflows/ci.yaml](.github/workflows/ci.yaml); requires `jq` and `yq`)

Individual checks (all run in CI):

- `uv run mypy .`
- `uv run pylint src tests`
- `uv run ruff check .` and `uv run ruff format --check .`
- `uv run yamllint .`
- `uv run shellcheck scripts/*.sh`
- `npm run prettier -- --check .`
- `uv lock --check`

Ruff runs with `select = ["ALL"]`; line length is 150. Test/script/example dirs have per-file ignores in [pyproject.toml](pyproject.toml).

## Architecture

The package lives in [src/weerlive/](src/weerlive/) and is small and layered:

- [api.py](src/weerlive/api.py) — `WeerliveApi`, the HTTP client. Two public methods (`city`, `latitude_longitude`) both build a URL from `API_ENDPOINT` and funnel through `_request`. Supports an injected `aiohttp` session or self-managed one, and works as an async context manager.
- [models.py](src/weerlive/models.py) — `mashumaro` dataclasses (`Response`, `LiveWeather`, `DailyForecast`, `HourlyForecast`, `ApiInfo`). These define the public typed surface and map terse Dutch API field names to readable English attributes via `field_options(alias=...)`.
- [helpers.py](src/weerlive/helpers.py) — date/time string parsing, timezone-aware (`Europe/Amsterdam`). Used as mashumaro `deserialize` hooks in models.
- [exceptions.py](src/weerlive/exceptions.py) — exception hierarchy rooted at `WeerliveAPIError`.
- [const.py](src/weerlive/const.py) — endpoint URL template, timeout, timezone.

### Key behaviors to know

- **Error handling quirk:** the Weerlive API returns HTTP 200 with a Dutch error message string (instead of a proper error status) for an invalid API key or exceeded daily limit. `_request` detects these by substring matching (`"Vraag eerst een API-key op"`, `"Dagelijkse limiet"`) and raises `WeerliveAPIKeyError` / `WeerliveAPIRateLimitError`. Preserve this when touching request logic.
- **Response shape normalization:** the API wraps `liveweer` and `api` as single-element lists. `Response.__pre_deserialize__` unwraps them to objects before deserialization.
- **Field naming:** model attributes intentionally use English names mapped from Dutch API keys via aliases. Ruff naming rules `N803`/`N815` are disabled to allow API-shaped names.

## Testing

- Tests use `pytest` with `aresponses` to mock HTTP, and `asyncio_mode = "auto"` (no `@pytest.mark.asyncio` needed).
- Sample API responses live in [tests/fixtures/](tests/fixtures/) (real-shaped JSON for cities, alarms, plus the plain-text error responses). Use these when adding model or API tests.
- Coverage is collected automatically (`addopts` in [pyproject.toml](pyproject.toml)) and reported to Codecov/SonarCloud in CI.

## Contributing notes

- A `pre-commit` hook is configured; install via the setup script.
- Automated-agent PRs are fast-tracked by appending `🤖🤖🤖` to the PR title (see [CONTRIBUTING.md](CONTRIBUTING.md)).
