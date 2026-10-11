# Internal D1/W1 + owner iterative ATR5 audit — 2026-10-01

Status: EXECUTED, CAUSAL DIAGNOSTIC ONLY; not Gerchik level-quality or strategy validation.

## Provenance and execution
- Source: existing production read-only archive `/data/research/phase11g/historical_expansion_v1_20260905T144500Z/bundles`, previously continuity-preflight PASS 19/19. No archive mutation or duplication.
- Research source: PR #94 research branch exact commit `1f5c1f612394dad88a49e0dfa380bcd544d75ba1`. GitHub CI run 36916162653: success in Python 3.12, 3.14, Docker amd64/arm64, merge gate.
- Staged only five pinned research modules under existing writable `/data/research/isolated_results/atr5-audit-1f5c1f61/scripts/research` inside deployed container. No deployed production app code or trading config modified.
- Executed with deployed `/app/scripts/run_readonly_research.py` Landlock launcher, `--memory-mib 512 --cpu-seconds 120 --wall-seconds 180`, output in same separate isolated results tree. First attempt failed closed on an unstaged dependency; staged `structural_level_clusters_v1.py` and reran successfully in 7.67 seconds.
- Output: `/data/research/isolated_results/atr5-audit-1f5c1f61/report.json`; SHA-256 `f6ee46114b73d8315d572e9b76039d829163886f9be09fc4af274ae5be095767`.
- Audit code SHA-256 `b81220e11115fb9c118fc34cd10f2e12d50970ea38985376cba2f09a170cd90f`; iterative ATR5 code SHA-256 `723fa1c12ded150ffa183f73800246df00802098fbf5fecbd8b891e2307d02fe`.

## Aggregate findings
- 19 symbols processed; 19/19 `CAUSAL_DIAGNOSTIC_NOT_LEVEL_QUALITY_VALIDATION`; zero `INVALID_SOURCE`.
- 8,981 completed D1 bars; 1,257 fully completed UTC W1 bars.
- 8,902 historical D1 cutoffs yielded valid owner-iterative ATR5; 79 lacked sufficient five-normal-bar/replacement history (often the first four cutoffs).
- 1,526 **rejected-bar occurrences across rolling cutoffs**, NOT 1,526 unique abnormal candles.
- Exploratory pivot diagnostics: 1,774 D1 and 219 W1 confirmed pivots. These are NOT fully classified or validated Gerchik levels.

## Per-symbol follow-up
- AKEUSDT: 344 D1 bars, 338 valid ATR cutoffs, 6 insufficient, **309 rejected occurrences**. Disproportionately high: inspect time clusters and individual rolling cutoffs before interpreting as market anomaly or algorithm success.
- TRUMPUSDT: 500 D1, 495 valid, 5 insufficient, 122 rejected occurrences.
- XRPUSDT: 500 D1, 496 valid, 4 insufficient, 115 rejected occurrences.
- Other symbols mostly have 4 initial insufficient cutoffs.

## Limits and next gates
This audit validates that the staged research code can process all available native historical D1 archives and generate causal cutoff diagnostics. It does NOT independently prove W1 prefix stability, trading utility, Gerchik-level classification quality, or backtest profitability. Add deterministic W1 prefix-stability regression and investigate AKEUSDT's concentrated rejection count. Then proceed to approved strategy backtests (S1–S6, 1R then 3R) on at least six months where available, with transaction costs and separate holdout. Production trading remains unchanged.
