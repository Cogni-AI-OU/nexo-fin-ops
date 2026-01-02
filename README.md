# Nexo Payment Gateway Ops

This repository provides helper assets for the Nexo Payment Gateway API
(pg.nexo.com), including the OpenAPI definition and a small Python helper for
authenticated calls.

## What you get

- Nexo Payment Gateway OpenAPI spec
  ([docs/API/Nexo-PG-OpenAPI.json](docs/API/Nexo-PG-OpenAPI.json)).
- Starter Python script to authenticate and make simple calls
  ([scripts/nexo_pg_auth.py](scripts/nexo_pg_auth.py)).
- Config example for storing your API key
  ([docs/nexo-config.example.yaml](docs/nexo-config.example.yaml)).

## SDK options (research summary)

- No official or maintained Python SDK exists for the Nexo Payment Gateway. The
  only PyPI package named "nexo" is an empty placeholder (0.0.0) and is not
  suitable for production use.
- The provided OpenAPI file is the authoritative source for endpoints; the
  gateway uses an `x-api-key` header for all requests and has no sandbox
  environment.

## API keys and access

- Nexo does not provide public API key creation instructions in the available
  documentation we can access.
- To set up or request API access, contact Nexo Support / Client Care from your
  account interface and ask about API access or API keys. They will confirm
  whether API keys are available for your account type and guide you through the
  steps in your dashboard.

## Quick start

1. Copy and edit the config example:

  ```bash
  cp docs/nexo-config.example.yaml nexo.config.yaml
  $EDITOR nexo.config.yaml
  ```

1. Run an authenticated call (requires Python 3.11+ and `uv`):

  ```bash
  ./scripts/nexo_pg_auth.py --config nexo.config.yaml --operation list-assets
  ```

1. Create a deposit address (requires your asset code and a reference ID):

  ```bash
    ./scripts/nexo_pg_auth.py --config nexo.config.yaml \
      --operation create-deposit --asset BTC --reference-id my-order-123
  ```

The script installs its dependencies on the fly via `uv run --script`. Errors
from the API are printed to stderr with the response body for easier debugging.
