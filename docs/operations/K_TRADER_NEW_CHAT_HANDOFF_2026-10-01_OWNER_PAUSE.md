# K-Trader authoritative new-chat handoff — 2026-10-01 — owner pause and approved development sequence

**Owner instruction:** Freeze current state and documentation for chat transition. DO NOT run further tests, experiments, deployments, CI triggers or server operations until explicit owner instruction. Existing automatic CI may run due to earlier commits; do not interpret pending as passed. This document is a documentation-only handoff, not approval to activate experimental research.

## Repository and operational separation
- Repository: `kolemasakar/K-Trader`; active research branch `research/dual-market-historical-levels-v0-1`; draft PR #94 remains **UNMERGED**.
- Last independently reported production deployment SHA `c1bb8b5e0fe314ab11e6eeb8a3f0dd601939cb91` with Landlock research launcher; do not infer live state without a fresh authorized check. No research commits were merged/deployed to production in this session.
- HP-OMEN prohibited for K-Trader until separately authorized. FREE_ONLY; no live orders from research; existing read-only archive and isolated results are distinct from production application.
- `docs/CURRENT_STATE.md` contains historical 2026-09-11 operational evidence below its newer research notices; do not confuse it with a current production inspection.

## Owner-approved development sequence to resume ONLY on command
1. Restore canonical documents, checkpoint, active branch, approved decisions and data provenance.
2. Formalize research and knowledge base: D1/W1 levels, Gerchik seven level types, cross-timeframe confirmation, ATR5 as energy/trade-parameter input (not level construction), S1–S6 and prerequisites.
3. Freeze historical backtest protocol in advance: entry, technical SL, TP, trading horizon, costs, data quality, causal cutoffs and independent holdout.
4. Prepare and validate initial >=6 months historical data, without lookahead.
5. Backtest approved S1–S6: first 1R then 3R; S3 stop beyond level. Do not introduce a mandatory 2R stage without owner approval.
6. Analyze results across assets, drawdown, execution costs, regimes and failure reasons.
7. Develop Level Strength v2: historical level reactions and weakening, then repeat testing.
8. Independently verify on a pre-reserved untouched holdout before considering adoption.

## ATR5 binding and experimental boundaries
- Approved **v2**: five newest completed bars, iterative current-five mean, abnormal LARGE if range >= 2x mean and SMALL if <= mean/3, replace one abnormal with next older unused completed bar, recompute and recheck all five. Newest-abnormal-first tie-break is current engineering implementation. Fail closed on insufficient older history. Do not reintroduce withdrawn 'no trading in transitional volatility' rule.
- Experimental **v3**: three consecutive new-regime D1 bars versus median preceding 10, provisional 2x expansion / 0.5x contraction; require five contiguous new-regime bars for new-regime ATR5. During 3–4-bar warmup returns no ATR5. This is NOT owner-approved for production; thresholds and treatment of anomalies within new regime require further work.
- Owner additionally specified future ATR5 v3 role in **trade evaluation** (movement energy, SL/TP suitability, entry context, regime and estimate reliability), not just volatility measurement. This is a planned research requirement, NOT an implemented integration.
- Research-only `atr5_quality_diagnostic` reports deep lookback; >20 inspected bars is a provisional reporting threshold, NOT a trade gate.

## Completed historical research and limitations
- Existing read-only D1 archive: 19 symbols, 8,981 D1 bars, 1,257 complete W1 bars. Earlier approved-v2 historical audit: 8,902 valid cutoffs, 79 insufficient; 1,526 rolling rejection occurrences, NOT unique bars. Exploratory pivots are NOT validated Gerchik levels.
- AKEUSDT 2026-07-18 v2 rejected 87 SMALL candidates, inspected 92 and used 2026-04-18 as fifth accepted bar. XRPUSDT 2026-08-22 rejected 47 SMALL candidates, inspected 52. Deep replacement is a mean-relative regime-change behavior; no approved algorithm changes resulted.
- First **experimental** v3 historical comparison: 19 symbols, 8,981 cutoffs; 8,530 V2_BASELINE, 164 NEW_REGIME_WARMUP, 59 NEW_REGIME_READY, 228 BASELINE_INSUFFICIENT. AKE 17–18 July and XRP 21–22 August warmup; next day ready. No strategy profitability, causal v3 holdout or trade-quality improvement established.
- Reproducible server artifacts under `/data/research/isolated_results/atr5-audit-1f5c1f61/`: `report.json` (v2 audit), `ake_diagnostic.json`, `deep_replacement_trace.json`, `v3_comparison.json` SHA256 `1dddd2b6de664acb6daf88a60fabb2d248af2798b36717bfbf1d57a84f19146a`. Do not assume server artifacts were copied to GitHub.
- Research code `scripts/research/gerchik_filtered_atr5_v1.py` (v2 and diagnostic), `scripts/research/gerchik_adaptive_atr5_v3_experiment.py` (v3 prototype); regression tests in `tests/test_gerchik_filtered_atr5_v1.py`, `tests/test_gerchik_adaptive_atr5_v3_experiment.py`, `tests/test_gerchik_causal_historical_audit_v0_1.py` (includes W1 prefix test).

## Verification discipline
- Previously confirmed green all-five CI run #272 for v2 research commit `1f5c1f612394dad88a49e0dfa380bcd544d75ba1`; later commits require separate final confirmation.
- W1 test commit `e35e3ad09c365a73e62a1fc42b80cff1068fd9d1` run #274 cancelled due to superseding commits. Later run #275 was in progress at last inspection. v3 test commit `c6bb1e76572ac43c7a84b6bc1f077c6006fc7bb8` run #280 in progress at last inspection. Never report pending as green.
- Draft PR #94 stays unmerged. Do not run new verification now: owner explicitly paused all checks.
- Reference checkpoints: `docs/checkpoints/2026-10-01_ITERATIVE_ATR5_19_SYMBOL_HISTORICAL_AUDIT.md`, `docs/checkpoints/2026-10-01_ATR5_AKE_OUTLIER_W1_PREFIX_FOLLOWUP.md`, `docs/checkpoints/2026-10-01_ATR5_DEEP_REPLACEMENT_TRACE_AND_QUALITY_FLAG.md`, `docs/checkpoints/2026-10-01_ADAPTIVE_ATR5_V3_FIRST_19_SYMBOL_EXPERIMENT.md`.

## First instruction in new chat
Read THIS handoff, `docs/CURRENT_STATE.md`, current branch HEAD and PR #94 status **read-only only when owner authorizes work**. Respect pause. On explicit resume, first reconcile approved development sequence and experimental ATR5 v3 trade-evaluation requirement; do not silently launch tests or deploy.
