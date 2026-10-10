# S1 pretest integration — 2026-10-09

Implemented as draft PR #95, NOT deployed:
- `mt4_research.py` verified-source reader with explicitly synthetic MT4 wall-clock.
- `s1_setup.py` causal trend / BPU preliminary checks, fail-closed.
- `s1_atr5.py` filtered ATR5 candidate (not yet historical parity certified).
- `s1_intrabar.py` A/B intrabar replay for independently validated order candidates.
- `s1_research_runner.py`: executable cross-timeframe source reader + JSON readiness, with nonzero exit (2) on incomplete S1. Never reports readiness inspection as trading outcomes.
- `tests/test_s1_research_runner.py` fail-closed fixture.

Run in *test environment* where PR code is installed and verified MT4 corpus is mounted read-only:

```bash
python -m ktrader.s1_research_runner \
 --root /data/kif_research/external/kai_mt4_20261009 \
 --symbol ACHC.us --as-of 2026-10-07T00:00:00
```

Expected at current state: nonzero readiness gate with missing reviewed levels, broker Point/tick and non-integrated causal ATR5/BPU2 strategy engine. The script must not output a trade count of zero as an actual backtest outcome; trade and return fields are null.

To make an actual S1 backtest: implement complete level generation/strength proof, approved ATR5 v2, correct order lifecycle, symbol price metadata and accepted chronological A/B replay. Treat unknown session alignment as unevaluated under owner-approved artificial-clock scope. No trading or production changes.
