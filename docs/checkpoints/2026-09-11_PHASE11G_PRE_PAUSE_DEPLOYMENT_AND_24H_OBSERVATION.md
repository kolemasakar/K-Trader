# Phase 11G Pre-Pause Deployment and 24h Observation Checkpoint

Date: 2026-09-11

Status: DEPLOYED / ACCEPTED / PRE-PAUSE READY / PHASE 12 INACTIVE

## Purpose

Record the exact accepted K-Trader state before the planned 24-hour technical development pause and define the data-collection contract for the clean observation window.

Development freeze is planned for:

- Kyiv local start: `2026-09-12 09:00`;
- UTC start: `2026-09-12T06:00:00Z`;
- Kyiv local end: `2026-09-13 09:00`;
- UTC end: `2026-09-13T06:00:00Z`.

The freeze applies to code/config/deploy activity. Production read-only capture, health monitoring and research-data accumulation remain active.

## Canonical repository and deployment identity

PR #51 `Harden Phase 11G prospective-control single-writer execution` was squash-merged after full canonical CI.

- merge SHA: `b698f8744f631a1a704d40cc3b2b66cfd31a6199`;
- PR-head CI #182 / run `34621302939`: SUCCESS;
- post-merge CI #183 / run `34621739596`: SUCCESS;
- Python 3.12: PASS;
- Python 3.14: PASS;
- Docker amd64: PASS;
- Docker arm64: PASS;
- `canonical-merge-gate`: PASS.

Production deployment:

- deployment run: `34622156136`;
- exact approved checkout SHA: `b698f8744f631a1a704d40cc3b2b66cfd31a6199`;
- Oracle ARM64 architecture check: PASS;
- canonical `scripts/deploy.sh`: PASS;
- rollback-capable canonical deployment path was used;
- deployed runtime SHA: `b698f8744f631a1a704d40cc3b2b66cfd31a6199`.

Temporary branch-scoped deployment workflow was removed after the successful deployment so it cannot be retriggered accidentally.

## Runtime acceptance

Immediately after deployment:

- `/health`: `status=ok`;
- `mode=read_only`;
- `data_ready=true`;
- provider: `binance_usdm`;
- scanner status: `DEGRADED` due to expected young-contract D1 ineligibility, not a service-health failure;
- canonical live deployment acceptance: PASS.

The deployed single-writer lock was also smoke-tested inside the production container:

- concurrent second writer: `SECOND_WRITER_BLOCKED=PASS`;
- lock reuse after first owner exits: `LOCK_RELEASE=PASS`.

This closes the operational race observed when a transport timeout left a prior prospective-control process running while a second `--resume` was started.

## Capture continuity across deployment

Universe capture before/through/after deployment remained causal and did not create a `>300s` context gap.

Observed snapshots:

- `2026-09-11T16:20:51.106478272Z`;
- `2026-09-11T16:25:51.079741433Z`;
- `2026-09-11T16:28:44.840793668Z`;
- `2026-09-11T16:30:44.849220121Z`.

Therefore the deployment did not create a prospective-control stale/missing-context hole under the canonical `max_context_age_seconds=300` rule.

## Accepted Phase 11G evidence before pause

Latest incremental prospective-control window:

- interval: `2026-09-11T07:25:00Z` -> `2026-09-11T15:05:00Z`;
- logical cutoffs: `93`;
- selected context cutoffs: `93`;
- symbol slots: `1860`;
- history-pass/analyzed slots: `1581`;
- history-fail slots: `279`;
- analysis-error slots: `0`;
- decision records: `17946`;
- unique tradable signals: `0`;
- archive SHA: `5339a113092535cdf93b34714248bebecf10c97d0ad414e83aac98b068569902`;
- report SHA: `18bb6cb8a77c1a53a87807a9491f31b57fd25f986ab6114d16a6f177381f0ad7`;
- scanner-config SHA: `2ad4b4369f3276eb081b02fe44c9b05bec49bf05a7ae4f146dcbe66ff594bff0`.

Incremental sequential funnel:

```text
HTF aligned                645
-> STRONG confirmed level  240
-> valid geometry           169
-> ATR <= 80%                40
-> TTL60 pass                10
-> RR >= 3                    0
-> grade A/A+                  0
-> tradable LONG/SHORT         0
```

Cumulative two-window non-overlap control evidence before pause:

- logical cutoffs: `419`;
- symbol slots: `8380`;
- history-pass slots: `7029`;
- history-fail slots: `1334`;
- analysis-error slots: `17` (all belong to the earlier pre-hardening UTC-midnight control boundary; latest incremental window has zero analysis errors);
- decision records: `85768`;
- tradable records: `0`.

Cumulative funnel:

```text
HTF aligned               2167
-> STRONG confirmed level  671
-> valid geometry           480
-> ATR <= 80%               229
-> TTL60 pass                20
-> RR >= 3                    0
-> grade A/A+                  0
-> tradable LONG/SHORT         0
```

No current evidence supports weakening RR, ATR, TTL, HTF, primary-level strength, structural-target, history or freshness gates.

## Dataset catalogue

Canonical catalogue remains unchanged:

- schema: `ktrader.dataset_catalogue.v1`;
- entries: `2`;
- symbols: `SUIUSDT`, `XRPUSDT`;
- catalogue semantic SHA: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- no new natural Phase 11G chain;
- no fabricated outcome;
- no probability estimate.

## 24-hour technical-pause observation contract

During `2026-09-12T06:00:00Z <= t < 2026-09-13T06:00:00Z`:

Allowed and required:

- keep the production service running read-only;
- keep Binance USD-M universe capture running continuously;
- preserve raw provider-recorded data and generated research artifacts;
- monitor health, freshness and continuity;
- record incidents without changing strategy semantics;
- notify on service failure, capture interruption or material data staleness.

Frozen unless required for emergency recovery:

- application code changes;
- merge/deploy activity;
- runtime configuration changes;
- schema migrations;
- heavy prospective replay on the 1-OCPU production VM;
- Phase 12 work;
- trading-rule changes.

Emergency recovery may restore the already accepted runtime/configuration only; it must not be used to introduce new strategy behavior during the clean observation window.

## Planned research dataset from the pause

For the exact 24-hour half-open observation interval, the canonical FAST/M5 prospective replay window is:

- first logical cutoff: `2026-09-12T06:00:00Z`;
- last logical cutoff: `2026-09-13T05:55:00Z`;
- expected logical M5 cutoffs: `288`;
- production `analysis_limit=20`;
- theoretical maximum selected symbol slots: `5760` before missing/stale-context and history-readiness accounting.

After the pause, build one immutable universe archive and coherent provider-recorded MTF bundle set, then run deterministic prospective control using the deployed single-writer contract, sequential low-priority shards, and canonical merge.

Primary post-pause measurements:

- snapshot continuity and context-age distribution;
- missing/stale cutoffs;
- history-pass/history-fail/analysis-error slots;
- decision count;
- sequential hard-gate funnel;
- especially `TTL_PASS -> RR_PASS` conversion;
- natural `RR>=3`, A/A+ or LONG/SHORT survivors;
- any new materializable chain only if every hard gate passes naturally;
- real subsequent-provider-bar outcomes only for already materialized chains.

## Invariants

Unchanged:

- FAST production research profile remains M5 / TTL60 (`12 x M5`);
- exact age `60m` is valid, strictly greater than `60m` is `SETUP_EXPIRED`;
- structural SL and nearest valid structural target only;
- no synthetic 3R target;
- `RR >= 3` hard gate;
- ATR-used `<=80%` hard gate;
- HTF directional alignment;
- STRONG/confirmed primary-level requirement;
- canonical history/freshness/provenance requirements;
- Setup Score/Grade semantics;
- `estimated_probability` remains null/N/A;
- outcomes require real subsequent provider bars;
- INTRADAY/M15 and MEDIUM/H1 remain research-only;
- Phase 12 remains FUTURE / NOT ACTIVE.

## Resume condition after pause

At or after `2026-09-13T06:00:00Z`, audit the full 24-hour observation window before resuming development. Development should resume only after confirming runtime health, capture continuity and artifact completeness, then selecting the next highest-value Phase 11G action from the new evidence.
