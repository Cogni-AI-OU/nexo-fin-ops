# Copilot Instructions for Nexo Ops

````instructions
# Copilot Instructions for Nexo Ops

## Project Overview

- Helpers for the Nexo Payment Gateway (pg.nexo.com) based on the supplied
  OpenAPI specs and a lightweight Python CLI for authenticated calls.

## Coding Standards

### Python

- Use **Python 3.11+**.
- Use `uv` script headers for dependency management:

  ```python
  #!/usr/bin/env -S uv run --script
  # /// script
  # requires-python = ">=3.11"
  # dependencies = [
  #     "httpx>=0.27",
  #     "PyYAML>=6.0.1",
  # ]
  # ///
  ```

- Follow **PEP 8** style guidelines.
- Use `argparse` for CLI argument parsing.
- Handle `BrokenPipeError` for CLI tools that might be piped to `head` or
  `grep`:

  ```python
  import signal
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  ```

- Prefer `httpx` clients with explicit timeouts and base URLs.

### Nexo Payment Gateway (PG)

- Base URL: `https://pg.nexo.com`.
- Authenticate every request with the `x-api-key` header; there is no sandbox,
  so assume production traffic.
- Webhook signature validation uses SHA256 over the JSON payload plus the
  shared secret (see docs/API/Nexo-PG-OpenAPI.json for details).
- Do not commit secrets; use local config files (see
  docs/nexo-config.example.yaml).

## Project Structure

- OpenAPI specs: docs/API/Nexo-PG-OpenAPI.json and
  docs/API/Nexo-Pro-OpenAPI.json.
- Config example: docs/nexo-config.example.yaml (copy to nexo.config.yaml
  locally).
- CLI helper: scripts/nexo_pg_auth.py for basic authenticated calls.

## Common Tasks

- Copy the config example, set `api_key`, and run scripts/nexo_pg_auth.py with
  `uv run --script` (built into the shebang).
- Use `--operation list-assets` for a lightweight authentication check, or
  `--operation create-deposit` with `--asset` and `--reference-id` to create
  addresses.
- When adding new tools, keep dependencies pinned in the `uv` header and avoid
  adding unused libraries.

````
