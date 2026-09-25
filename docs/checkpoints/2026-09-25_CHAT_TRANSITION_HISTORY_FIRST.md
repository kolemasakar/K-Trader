# K-Trader — chat transition control checkpoint: historical recovery first

**Recorded:** 2026-09-25, chat-transition preparation, after user requested project freeze/document synchronization and stated a separate transition generator would follow.  
**Scope:** K-Trader research branch `research-strategy-benchmark-v1` at pre-checkpoint verified Git SHA `b8b4609a9ef67f870f33dfc67a10f173fe2e3c59`. This checkpoint must not be read as a production deployment or new runtime acceptance.

## Owner priorities for the next chat (authoritative order)

1. **Historical recovery is the FIRST priority**: obtain the maximum genuinely available Binance USD-M history (initial goal up to 6 months, allowing for contract listing dates) to build, backtest, stress-test and independently validate candidate strategies. Inventory earlier bundles before redownloading. Historical requests need truthful `retrieved_at_utc` and separately declared requested historical `as_of`; a historical bar retrieved later must never be relabeled contemporaneously available.
2. **Current first-seen prospective data is a separate, parallel research stream**: use it to check fresh signals from frozen, historically researched candidates in later authorized *shadow/paper* prospective evaluations, including timely candle arrival, opportunity attrition, transaction costs, risk and realistic execution. **The existing running epoch is still DATA-ONLY**. Its presence does not grant approval to begin new strategy outcome resolution or live trades.
3. No automatic claims about positive expected trading returns: require temporally disjoint out-of-sample and walk-forward tests, cost/slippage/funding models, multi-symbol robustness, overfit controls, then an independently accepted fresh-data shadow phase. Only a later explicit owner decision can authorize actual execution.
4. **No HP-OMEN whatsoever**, directly or indirectly (including K_AI, MT4 relay, data, tunnels, backup, local runner or diagnostics), unless the owner explicitly reverses the restriction. Use independent K-Trader OCI infrastructure and owned Binance `binance_usdm` feeds only.
5. **GitHub Actions budget unavailable until 2026-10-01 per owner**: don't assume successful workflows can be launched; do not gate immediate research on Actions. GitHub API for documentation commits/PR/merge may still work independently. Where needed, perform server-local exact-SHA validation with durable, reproducible evidence, without privilege expansion, trading or production restart.
6. **No automatically scheduled ChatGPT reminders or alerts**. The separately approved, already launched bounded server-local monitor writes durable hourly/deep/final audit reports without notifications and never backfills missed scheduled checks.

## Implementation and source-state references (check exact current Git state in new chat)

- Research branch: `research-strategy-benchmark-v1`, pre-checkpoint Git SHA `b8b4609a9ef67f870f33dfc67a10f173fe2e3c59`; after merging this checkpoint the canonical branch SHA changes. Do not use the pre-checkpoint SHA as the new HEAD.
- Historical-first master plan accepted and merged: [PR #82](https://github.com/kolemasakar/K-Trader/pull/82), commit `b8b4609a9ef67f870f33dfc67a10f173fe2e3c59`; `docs/research/PHASE11G_HISTORICAL_RECOVERY_AND_PROSPECTIVE_STRATEGY_PLAN_20260925.md`.
- Approved monitor implementation [PR #78](https://github.com/kolemasakar/K-Trader/pull/78), narrow test import fix [PR #79](https://github.com/kolemasakar/K-Trader/pull/79), one-shot server-only activation [PR #80](https://github.com/kolemasakar/K-Trader/pull/80). Previously observed Research Safety CI, Research Guards and activation all PASS when they ran; do not interpret them as current Actions quota availability. [Activation checkpoint](2026-09-25_PHASE11G_MONITOR_ACTIVE_BASELINE.md), docs synchronized via [PR #81](https://github.com/kolemasakar/K-Trader/pull/81), commit `f5cf2c1870792f6bcedcae8158512bb4e675f9f8`.
- Existing reusable research code: `src/ktrader/history/collector.py` (`collect_deep_provider_history`), `src/ktrader/history/dataset.py` (strict, hash-verified provider datasets), `src/ktrader/providers/binance_usdm.py` (public historic klines), `research/strategy_benchmark_v1/historical_robustness_dataset_export_v1.py` (existing deep exporter and candidate for correction), `historical_causal_rolling_replay_v1_1.py` (research causal replay), `audit_retrospective_gap_v1.py` (retrospective-only provenance inventory).
- Existing historical server datasets reported in prior audits: `/data/research/phase11g/historical_robustness_v1_20260905T144500Z` and `historical_expansion_v1_20260905T144500Z` (folders confirmed in a later basic directory listing; *their current content/completeness has NOT yet been inventoried*). Proposed new isolated recovery root `/data/research/phase11g/historical_recovery_v1/` must remain distinct from prospective and frozen roots.
- Phase 11G original frozen `candidate_rule_set_v2_2`, harness SHA256 `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`, protocol SHA256 `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`, offline resolver v1.3, ledger v1.2, original accepted cohort **54/100 resolved** at **2026-09-18T06:15:00Z**; original 06:30Z partial recovery remains immutable. **No new eligible prospective family outcomes admitted** from the newer raw epoch, holdout unopened, no trade execution.
- Original accepted state SHA256 `30d0510da10d3d8b40684f8bf97c9ae568a6b3b8a7b43289c6b8cd41543a997b`; original immutable ledger SHA256 `c0c1b261a6684d1f9381e820736f9dd702319947e3e7f78fb38b607508dcfade`. Independently reverify before any future work.

## Runtime status — final verified snapshot before transition

Final independent read-only host check completed at approximately **2026-09-25T15:23Z** on `k-trader-prod-vnic`; Docker container `k-trader-ktrader-1`.

Verified facts:
- HTTP health `status=ok`, `mode=read_only`, `provider_id=binance_usdm`, `data_ready=true`; scanner remains `DEGRADED` because of known first-seen readiness variability rather than a production write authorization.
- Exactly one first-seen collector process, PID `119664`, and one non-notifying monitor process, PID `121255`.
- **15 completed M15 first-seen cutoff directories**, first `2026-09-25T11:45Z`, latest `2026-09-25T15:15Z`.
- Latest collector state: `PASS`, `admitted_new_prospective_families=0`, `full_depth_ready_slots=5`, `failed_slots=14`.
- Monitor durable reports: pre-activation `12:06Z` and `13:06Z` correctly recorded `MISSED_BEFORE_MONITOR_ACTIVATION`; post-activation `14:06Z` **PASS** and `15:06Z` **PASS**; baseline remains **PASS**.
- Original accepted state SHA256 `30d0510da10d3d8b40684f8bf97c9ae568a6b3b8a7b43289c6b8cd41543a997b` and original ledger SHA256 `c0c1b261a6684d1f9381e820736f9dd702319947e3e7f78fb38b607508dcfade` were reverified unchanged.
- Approx. **31.78 GiB** remained available in the research filesystem during the final check.
- Historical recovery root `/data/research/phase11g/historical_recovery_v1/` has **not** yet been created or populated; next work remains H0 inventory before H1 collection.

Registered prospective epoch boundaries remain first cutoff `2026-09-25T11:45Z` through final inclusive cutoff **2026-09-26T11:30Z**. Deep monitor reports remain scheduled at 15:51Z, 19:51Z, 23:51Z, 03:51Z and 07:51Z; final audit at 11:36Z. **Do not restart or retrofit data if later checks fail; diagnose and preserve immutable first-seen evidence.**

The earlier transient SentinelX internal-tool errors were not host failures: subsequent independent host calls succeeded and produced the final snapshot above.

**Known separate data-quality anomaly**: fixed-rank cutoff `2026-09-25T13:15Z` had only 1/19 timely-complete instruments (18/19 flagged missing latest M15/M5 closed candles). At a later read-only SQLite probe, some bars showed actual ingest times around 13:20:48–13:20:50Z, past the 13:20:00Z cutoff+300s hard deadline. Later Binance retrieval can support retrospective gap analysis, **never change those immutable first-seen failure outcomes**.

## Immediate continuation order

1. On fresh tools/host access, perform **read-only H0 existing historical bundle inventory**, available range/coverage, checksums, storage and measured gaps by symbol/timeframe; check live collector and monitor status without restart.
2. Develop/validate a new isolated recovery manifest with truthful retrieval timestamps and `RETROSPECTIVE_RECOVERY` tagging. Do not silently modify old frozen exporter artifacts or use retrospective data to modify causal first-seen records.
3. Execute a bounded, non-invasive **H1 5 symbols × 5 timeframes historical pilot**, 7–30 days for detailed gap recovery where supported; control requests, 25 streams, provider rate limits and disk budget. Preserve source identities and provenance. Evaluate H1 independently before growing toward six months.
4. Parallel: continue existing current-data collection and accepted monitoring *without notifications*. Progress to historical out-of-sample strategy experiments, then propose a separately approved paper/shadow real-time validation gate. Do not start new strategy prospective outcomes or trading automatically.

## New-chat transition workflow

The owner explicitly said a **separate transition generator will be supplied next**. This checkpoint synchronizes the facts and next-step gate but is not a bootstrap generator output. When the owner provides the generator, execute it according to its supplied contract against this updated checkpoint and current `docs/CURRENT_STATE.md`, and use the newly generated handoff as the authoritative restart pointer. Avoid presenting the old 2026-09-16 and 2026-09-14 handoffs as up-to-date.
