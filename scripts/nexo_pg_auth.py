#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx>=0.27",
#     "PyYAML>=6.0.1",
# ]
# ///
import argparse
import json
import pathlib
import signal
import sys
from typing import Any, Dict, Tuple

import httpx
import yaml

# Prevent BrokenPipeError when piping output (e.g., head, grep).
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

DEFAULT_CONFIG_PATH = pathlib.Path("nexo.config.yaml")


def load_config(config_path: pathlib.Path) -> Dict[str, Any]:
    """Load YAML config from disk."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    data = yaml.safe_load(config_path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError("Config file must contain a mapping at the top level")
    return data


def resolve_settings(
    args: argparse.Namespace, config: Dict[str, Any]
) -> Tuple[str, str, float]:
    base_url = args.base_url or config.get("base_url") or "https://pg.nexo.com"
    api_key = args.api_key or config.get("api_key")
    timeout = args.timeout or config.get("timeout_seconds") or 10

    if not api_key:
        raise ValueError(
            "Missing API key. Provide --api-key or set api_key in the config file."
        )

    try:
        timeout_value = float(timeout)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive parsing
        raise ValueError("timeout_seconds must be numeric") from exc

    return base_url, api_key, timeout_value


def build_client(base_url: str, api_key: str, timeout: float) -> httpx.Client:
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        timeout=timeout,
        headers={"x-api-key": api_key},
    )


def list_assets(client: httpx.Client) -> Dict[str, Any]:
    response = client.get("/api/v1/assets")
    response.raise_for_status()
    return response.json()


def create_deposit_address(
    client: httpx.Client, asset: str, reference_id: str
) -> Dict[str, Any]:
    payload = {"asset": asset, "referenceId": reference_id}
    response = client.post("/api/v1/deposit-addresses", json=payload)
    response.raise_for_status()
    return response.json()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Authenticate to Nexo Payment Gateway and run a simple call."
    )
    parser.add_argument(
        "--config",
        type=pathlib.Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to YAML config.",
    )
    parser.add_argument(
        "--api-key", help="Override API key (otherwise taken from config file)."
    )
    parser.add_argument(
        "--base-url", help="Override base URL (default: https://pg.nexo.com)."
    )
    parser.add_argument("--timeout", type=float, help="Request timeout in seconds.")
    parser.add_argument(
        "--operation",
        choices=["list-assets", "create-deposit"],
        default="list-assets",
        help="API call to execute.",
    )
    parser.add_argument("--asset", help="Asset symbol (required for create-deposit).")
    parser.add_argument(
        "--reference-id", help="Reference identifier (required for create-deposit)."
    )

    args = parser.parse_args()

    try:
        config = load_config(args.config)
        base_url, api_key, timeout = resolve_settings(args, config)
    except Exception as exc:  # pylint: disable=broad-except
        sys.stderr.write(f"Configuration error: {exc}\n")
        return 1

    try:
        with build_client(base_url, api_key, timeout) as client:
            if args.operation == "list-assets":
                result = list_assets(client)
            else:
                if not args.asset or not args.reference_id:
                    raise ValueError(
                        "--asset and --reference-id are required for create-deposit"
                    )
                result = create_deposit_address(client, args.asset, args.reference_id)
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        sys.stderr.write(f"API error ({exc.response.status_code}): {detail}\n")
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        sys.stderr.write(f"Request failed: {exc}\n")
        return 1

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
