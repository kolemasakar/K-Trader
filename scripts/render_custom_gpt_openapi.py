#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from ktrader.action_package import render_action_schema, validate_action_schema_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or render the K-Trader Custom GPT Action OpenAPI schema.")
    parser.add_argument("--source", default="custom_gpt/openapi.yaml")
    parser.add_argument("--server", help="Deployed HTTPS origin, for example https://api.example.com")
    parser.add_argument("--output", help="Output file. Omit to print rendered schema to stdout.")
    args = parser.parse_args()

    text = Path(args.source).read_text(encoding="utf-8")
    if not args.server:
        operations = validate_action_schema_text(text, allow_placeholder=True)
        print(f"PASS read-only Action schema: {len(operations)} operations")
        return 0

    rendered = render_action_schema(text, args.server)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
