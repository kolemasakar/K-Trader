# Cross-timeframe luft matching — isolated test result (2026-09-28)

Status: **PASS, 12/12 pytest cases**, `python -m pytest -q tests/test_gerchik_cross_tf_luft_v0_2.py` (0.08 s).

An isolated local test directory was populated from the GitHub connector-returned content of `scripts/research/gerchik_cross_tf_luft_v0_2.py` and `tests/test_gerchik_cross_tf_luft_v0_2.py`. The dependency `gerchik_cross_tf_v0_1.py` was recreated with only the `_utc` helper required by the tested module; therefore this is a logic-equivalent isolated test, **not a byte-for-byte checkout of all repository sources**. No HP-OMEN or production server modifications.

Verified cases: symmetric inclusive luft (three parameter cases), outside-luft rejection (two cases), causal no-future confirmation, upstream qualification, ambiguous matches, invalid luft (two cases), missing luft, original price and primary-type preservation.

Limitations: the module trusts upstream `structurally_qualified`, external instrument-specific luft and exact symbol tick metadata; these require independent validation. It reports pair-level cross-timeframe confirmation but does not resolve global level identity, auto-promote the ledger, or enable live trading. No ATR used in level construction.
