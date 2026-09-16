#!/usr/bin/env python3
from __future__ import annotations

"""Versioned v1.2 entrypoint for the offline prospective v2.2 resolver.

v1.2 intentionally preserves the v1.1 output schema and all outcome semantics.
The only change is a narrowly widened absolute prior-price identity guard from
2e-9 to 3e-9, after a validated same-identity RAYSOLUSDT stop representation
drift of 2.1062864785648117e-9 was observed. Entry prices remained exact and
50/50 previously resolved observations retained identical terminal/economic
fields under the widened guard.
"""

import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE / "prospective_v2_2_outcome_resolver_offline_v1_1.py"


def load_base():
    spec = importlib.util.spec_from_file_location("prospective_v2_2_offline_v1_1_base", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load base resolver: {BASE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    base = load_base()
    base.PRIOR_PRICE_ABS_TOL = 3e-9
    base.main()


if __name__ == "__main__":
    main()
