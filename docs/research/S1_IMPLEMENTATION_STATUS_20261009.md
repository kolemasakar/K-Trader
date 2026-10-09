# S1 implementation status (2026-10-09)

**PARTIAL. No S1 backtest yet. No production changes.**

Staged in draft PR #95:
- Read-only MT4 adapter and synthetic tests: src/ktrader/mt4_research.py and tests/test_mt4_research.py.
- S1 research-only intrabar OHLC/OLHC path kernel: src/ktrader/s1_intrabar.py.
- Five synthetic S1 path tests: tests/test_s1_intrabar.py.
- Authoritative strategy and data gaps: docs/research/S1_BACKTEST_READINESS_AUDIT_20261009.md.

Important: latest CI must verify new commits; earlier CI #322 covers only earlier PR head.
Pending before ACHC.us backtest: validated level detector, strength evidence, ATR5 v2, trend, BPU1/BPU2, calendar and timestamp mapping, broker symbol Point/tick, position sizing, costs, full execution/cancellation events, complete data scan and independent chronological checks.

Do not claim success, trades, net profitability or release readiness until gates pass.
