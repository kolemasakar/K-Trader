# Research resumed — ATR5 trade evaluation foundation
Date: 2026-10-02. Base research HEAD: `9773833d4445f40e47169731ae7ad7f4f48eff54`.

## Authorization and verification
Owner instruction: «продовж реалізацію». Earlier OWNER_PAUSE applies to its dated snapshot; this explicit instruction resumes research implementation and relevant verification. It does not approve live orders, production deployment, experimental v3 adoption or merge.

Verified GitHub repository `kolemasakar/K-Trader`, default `main`; active branch `research/dual-market-historical-levels-v0-1`. PR #94 was open/draft/unmerged; base main `c1bb8b5e0fe314ab11e6eeb8a3f0dd601939cb91`. Read current state, 2026-10-01 handoff, canonical ATR decision, level-classification contract, research strategy catalogue, benchmark protocol, strategy knowledge summary and v2/v3 implementations. Runtime identity was not checked; work did not depend on runtime.

## Completed
- Added causal research-only trade-geometry diagnostic using canonical ATR5 v2, optional separately labelled v3 comparison, explicit source availability times and estimate provenance.
- Preserved canonical v2 in v3 early-history/warmup cases. No new trade gate.
- Corrected obsolete ATR wording and missing S6 coverage in the draft catalogue; S6 historical description remains a restoration reference, not an executable approved specification.
- Recorded implementation and constraints in `docs/research/ATR5_TRADE_EVALUATION_V0_1.md`.
- Local verification: 11/11 deterministic unittest cases passed; compilation passed.

## Limitations and next task
No real-market backtest, profitability conclusion, fresh production verification, merge or deployment. pytest is unavailable in this scratch Python environment; complete existing regression suite and remote CI status are unverified.

Before executing the six-month strategy program, exact entry conditions, timeframe choice, S3 technical stop beyond level, costs, intrabar ambiguity, horizons and holdout boundaries must be frozen. Default percentage tolerance needs explicit price/time anchor; Forex needs explicit point convention; tick rounding remains unresolved. Do not invent these approvals. Preserve the order 1R -> 3R -> analysis -> Level Strength v2 -> independent reserved holdout.
