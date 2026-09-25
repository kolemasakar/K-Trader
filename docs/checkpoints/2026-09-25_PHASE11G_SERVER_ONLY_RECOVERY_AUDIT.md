# K-Trader Phase 11G Server-Only Recovery Audit — 2026-09-25

**Status:** READ-ONLY DIAGNOSTIC CHECKPOINT / NO PROSPECTIVE ADVANCEMENT  
**Host access:** Oracle K-Trader production via policy-limited SentinelX, server-local reads only  
**Mandatory host exclusion:** [HP-OMEN is prohibited until separate explicit user authorization](../operations/K_TRADER_HP_OMEN_EXCLUSION_2026-09-25.md).

## Verified operational baseline

Observed on `k-trader-prod-vnic` on 2026-09-25, approximately 10:21–10:25 UTC:

- local production `/health`: `status=ok`, `mode=read_only`, `data_ready=true`;
- independent production scanner provider: `binance_usdm`, scanner status `DEGRADED`;
- `k-trader-ktrader-1`: Docker healthy;
- no Phase 11G prospective runner process observed;
- temporary staged runtime `/tmp/ktrader-runtime-v2` absent after prior container restart.

No HP-OMEN, K_AI/MT4-backed route, reverse tunnel or other external machine was queried. No production restart, deployment, strategy change, holdout access or order operation occurred.

## Last accepted prospective boundary — 2026-09-18T06:15:00Z

Authoritative persisted state:

```text
/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260918T061500Z.json
```

Read-only verification:

- state status `PASS`, cycle status `VALID_SHADOW_CAPTURE`;
- unique primary families `54`; resolved primary families `54`; unresolved `0`;
- evidence tier: `HYPOTHESIS_ONLY_50_99_RESOLVED_FAMILIES`;
- Path A: `54/100` resolved; shortfall `46`;
- `holdout_opened=false`; `production_action=false`;
- state-file SHA-256: `30d0510da10d3d8b40684f8bf97c9ae568a6b3b8a7b43289c6b8cd41543a997b`;
- matching pipeline manifest `pipeline_v2_20260918T061500Z_execute.json`: status `PASS`, eight stage results `PASS`;
- pipeline-file SHA-256: `cbfde4fc0d8da89c459bdc8aaba06f3d2b5906182da03ac733683b1f75031e57`;
- state source-hash verification: `5/5 PRESENT + MATCH`.

This is the latest **verified accepted state**, not a claim that the 2026-09-18→25 gap was prospectively observed.

## Incomplete 06:30Z cycle: preserve fail-closed

Path:

```text
/data/research/phase11g/v2_2_shadow_20260918T063000Z
```

- `cycle_status.json` reports `as_of=2026-09-18T06:30:00Z`, `status=EXPORTING`;
- five partially exported symbol bundle directories exist;
- no accepted 06:30 state manifest/pipeline manifest;
- runner log reports `PIPELINE_OUTPUT_EXISTS`;
- pause automation `status.json`: `FAIL_CLOSED`;
- pause runner is no longer active and the bounded pause ended at `2026-09-19T07:00Z`.

**Do not delete, overwrite, reuse or silently accept the 06:30 partial output.** The old pause runner must not be relaunched as though its expired `--until` window were current. Any recovery must be separately versioned and provenance-verified.

## Server-recorded archive since the interruption

Independent `binance_usdm` universe capture continues on K-Trader storage under `/data/research/universe/binance_usdm/`. File counts observed:

- 2026-09-19 through 2026-09-24: `288` snapshot files for each complete UTC day;
- 2026-09-25: capture continued through the read-only inspection.

File counts support an archive-availability preflight; they do **not** alone establish candle integrity, exact-cutoff causal suitability or a continuous Phase 11G prospective series. Do not use post-failure reconstruction to inflate preregistered prospective family counts. If studying the missing dates, isolate them as a distinct **retrospective recovery cohort** with explicit provenance and no promotion into the immutable prospective ledger.

## Frozen boundaries

Remain unchanged:

- candidate `candidate_rule_set_v2_2`;
- harness SHA-256 `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA-256 `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- resolver v1.3, ledger v1.2 first-seen event immutability;
- prereg boundary `2026-09-16T13:00:00Z`;
- holdout `UNTOUCHED / NOT AUTHORIZED`;
- no frozen RR, SL/TP, 32-M15 hold, filter, side or risk-gate change;
- Phase 11G `ACTIVE`; Phase 12 `NOT ACTIVE`; no trading authorization.

## Next approved-safe work order

1. Preserve the 06:15 accepted immutable manifests and the failed 06:30 partial directory; do not mutate either.
2. Verify available recovery-bundle checksums and determine whether all required source data and historical closed bars exist on independently approved server storage.
3. Produce a read-only gap/data-quality and causality report for 06:30Z onward. Distinguish *recorded snapshots* from *eligible prospective evidence*.
4. Design a separate versioned recovery or new prospective-start plan that will not cross-contaminate the immutable prior ledger or the touched/untouched data boundaries.
5. Do not execute a catch-up pipeline, promote hypotheses, open holdout, change production or use HP-OMEN before the relevant validation/authorization gates are met.

This checkpoint is documentation of an observed fail-closed state, **not** acceptance of additional prospective outcomes.

## Follow-up reproducibility and readiness gate — 2026-09-25, 10:15Z

This follow-up was performed entirely on independently operated K-Trader server-local storage, in **read-only** mode. No HP-OMEN or HP-OMEN-backed route was accessed.

### Integrity and existing accepted evidence

- recovery bundle `predeploy_20260917T1925Z`: manifest SHA-256 checks **58/58 match**, zero missing or mismatched;
- the archived `2026-09-18T06:15:00Z` bundles passed the pinned Phase 11G data-quality watchdog: **95 interval files checked, 0 errors, PASS**;
- source-hash checks of the accepted state remain **5/5 MATCH**;
- no new prospective family was accepted, no immutable event was rewritten, and the partial `06:30Z` output remains untouched.

### Point-in-time server-only readiness — not prospective evidence

The independent K-Trader `binance_usdm` recorded universe snapshot at `2026-09-25T10:10:39.123329Z` is the newest inspected source snapshot before logical cutoff `2026-09-25T10:15:00Z`. Its age is approximately **261 seconds**, inside the existing `<=300s` context-age boundary. The selection consists of the **first 19 members in recorded liquidity order**, without replacing any failed member with a lower-ranked symbol.

A read-only SQLite query against `/data/ktrader.db` checked the required historical depth, sequence contiguity and latest closed-bar availability at that cutoff:

- `1d=20`;
- `4h=80`;
- `1h=300`;
- `15m=400`;
- `5m=20`.

Result: **14/19 PASS**, **5/19 fail closed**.

PASS in original recorded rank order:

```text
1  XRPUSDT
2  ONDOUSDT
3  DOGEUSDT
4  SUIUSDT
5  LSKUSDT
6  1000PEPEUSDT
7  ENAUSDT
10 NILUSDT
11 WLDUSDT
12 ADAUSDT
13 XLMUSDT
14 AKEUSDT
15 ARBUSDT
18 ONEUSDT
```

Failed, with observed reasons:

- rank 8, `SAGAUSDT`: one gap in the latest 400 `15m` bars;
- rank 9, `XPLUSDT`: one gap each in the latest 300 `1h` and 400 `15m` bars;
- rank 16, `龙虾USDT`: insufficient `1d/4h/1h` depth and multiple gaps, including `15m`;
- rank 17, `BROCCOLI714USDT`: insufficient `1h` (267/300) and `15m` (316/400) depth;
- rank 19, `BTWUSDT`: insufficient depth, multiple gaps and stale `4h` close.

The earlier accepted panel from `2026-09-18T06:15Z` is a different set from this recorded top-19. Nine symbols from that historical panel met all five current point-in-time bar checks; this **does not** establish readiness for the frozen old panel, nor authorize a changed prospectively counted sample.

### Operational outcome and next gate

- **Recovery bundle integrity:** PASS.
- **Last accepted archive quality:** PASS.
- **Fresh point-in-time full-panel readiness:** **FAIL_CLOSED (14/19)** under the no-substitution rule.
- **Prospective continuation from 06:15Z through the 7-day interruption:** NOT AUTHORIZED / NOT ESTABLISHED.
- **Holdout, Phase 12, trade execution, strategy modification, risk-policy promotion and HP-OMEN use:** NOT AUTHORIZED.

Next bounded work: prepare a *versioned, server-only restart/recovery protocol* separating (a) any retrospective investigation of the downtime from (b) a newly preregistered prospective epoch using future fully closed M15 boundaries. Maintain first-seen ledger v1.2 semantics and do not silently bridge the interruption or count retrospectively recovered data toward the frozen prospective `54/100` total. Resolve or explicitly fail-closed the five recorded current top-19 history deficits; do not change rank selection to manufacture a full panel.
