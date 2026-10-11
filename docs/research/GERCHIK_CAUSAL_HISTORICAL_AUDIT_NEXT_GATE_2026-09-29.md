# Historical Gerchik research gate: causal pivot visibility and ATR5

Added `scripts/research/gerchik_causal_historical_audit_v0_1.py` and `tests/test_gerchik_causal_historical_audit_v0_1.py`. The audit reads **only** native internal D1 research bundles and derives complete UTC W1 bars. It checks exploratory 3-left/3-right pivot visibility by actual confirmation close and computes filtered ATR5 separately at every D1 close using only the historical prefix. Output records input SHA256, counts, insufficient ATR history, rejected-bar occurrences and invalid sources. The runner **does not** call exploratory pivots verified Gerchik levels, does not generate signals, does not open trades, and does not use the reserved external holdout.

Command in an approved read-only research environment with access to the internal archive:

`python -m pytest -q tests/test_gerchik_causal_historical_audit_v0_1.py`

`python -m scripts.research.gerchik_causal_historical_audit_v0_1 --root <INTERNAL_NATIVE_D1_BUNDLE_ROOT> --output <ISOLATED_RESEARCH_OUTPUT>/gerchik_causal_audit.json`

**Status: pending execution**. At this session's start `kgm-e4-owner-pilot` was offline; do not use HP-OMEN or production K-Trader as an unapproved substitute. Earlier exact GitHub source SHA `1c10c8c...` passed 106 selected tests; that predates this runner and cannot validate it. Previously documented 8,981 D1 / 1,257 derived complete W1 source audit is not proof of level quality. Before claiming historical validation complete, rerun this exact code, audit native source hashes, then test independently reviewed level events, chronological revisits and predeclared baseline comparison. Candidate strategy catalogue is a draft and no live execution exists in this research model.
