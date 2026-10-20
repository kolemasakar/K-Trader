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

## 2026-10-09 actual ACHC.us preflight

Read-only M5 inspection: 2,198 rows, open_time strictly increasing, zero invalid OHLC geometries. Adjacent raw broker-wall-clock open timestamps: 2,153 gaps of 5m, 14 gaps of 10m, two gaps of 20m; numerous longer overnight/weekend session gaps. This does not establish missing-market-data defects until broker/exchange session calendar is grounded.

**Critical source fact**: real MT4 JSONL header states `timestamp_semantics=BROKER_SERVER_WALL_CLOCK_OPAQUE`; no timezone, Point or tick-size provided in the inspected header. Treating naive MT4 timestamp as UTC is invalid. Updated adapter to reject read/replay until a verified broker timezone is explicitly provided; synthetic tests use explicit UTC only for fabricated fixtures. A verified timezone mapping also requires DST and session-boundary audit before release.

No real S1 orders generated. Broker metadata and independently qualified D1/W1 strong levels not available for an honest ACHC.us S1 backtest. Status remains G2 partial; G3-G7 pending.

## Owner clarification: conditional clock coordinates

User explicitly confirmed that the goal is **testing strategy algorithms**, for which MT4 broker-wall-clock chronology is sufficient. The missing UTC timezone is **not an algorithmic backtest blocker**. Use explicit `wall_clock_mode=True` in the MT4 adapter and treat naive `as_of` as the same broker clock. Do not claim real exchange-session or first-hour filters were evaluated; label these gates as unavailable in the algorithmic-only report. Actual `ACHC.us` M5 source preflight: 2,198 closed bars, strictly increasing close times (2026-08-26T16:50:00 through 2026-10-06T22:55:00). Full S1 signal generator and end-to-end run still pending.
