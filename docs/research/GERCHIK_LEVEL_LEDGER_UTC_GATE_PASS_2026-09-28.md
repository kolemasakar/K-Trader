# Gerchik event ledger UTC hardening gate — 2026-09-28

Research branch `research/dual-market-historical-levels-v0-1`. Added strict UTC timestamp parser and parsed datetime comparison for formation, strengthening evidence and as-of queries. UTC Z and +00:00 accepted; naive, nonzero offsets and invalid timestamp text rejected. Added two persistent tests for timestamp guards and equivalent UTC forms.

Isolated assistant container (no HP-OMEN or production changes): `python -m pytest -q` with recreated current module and 16 parameterized test cases: **16 passed in 0.09s**. Module update commit `1d38f167f598ebbf7ea9de1950ae8b69b5f11b71`; test update commit `b77480bc7ecb61e84b017c17f3984e0d8e768e6a`.

Remaining gates: real symbol tick/session metadata; cross-timeframe D1/W1 price identity policy; independent formation detectors with causal evidence; labelled historical review. This ledger never promotes CANDIDATE to confirmed and does not trade or consume ATR.
