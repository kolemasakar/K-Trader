# Phase 11G — approved server-only monitoring activated

**Checkpoint:** 2026-09-25 approximately 13:20–13:22 UTC (16:20–16:22 Kyiv).  
**Status:** `ACTIVATED + READ_ONLY_BASELINE_PASS`; first **future scheduled hourly** report not yet due at this checkpoint.  
**Notifications and ChatGPT automations:** NONE.  
**HP-OMEN:** PROHIBITED (including all indirect K_AI/MT4 routes).

## Source and deployment

- Approved implementation: [PR #78](https://github.com/kolemasakar/K-Trader/pull/78), merged `d97f5b64c118e6091c83c1e6ee993901ba5db085`.
- Narrow CI test import correction: [PR #79](https://github.com/kolemasakar/K-Trader/pull/79), merged `d91c4ee4d0ec0eba0abf864a947a539530d5c21b`.
- The corrected exact-commit [Research Safety CI #36139933623](https://github.com/kolemasakar/K-Trader/actions/runs/36139933623) and [Research Guards #36139933771](https://github.com/kolemasakar/K-Trader/actions/runs/36139933771) both passed. Focused monitor compilation/tests passed.
- Reviewed one-shot [activation PR #80](https://github.com/kolemasakar/K-Trader/pull/80), merged `a2f1ea9c702f8d3a9056b5a7c249330fdd85cd7d`.
- [Activation workflow #36140194625](https://github.com/kolemasakar/K-Trader/actions/runs/36140194625) completed **SUCCESS**, including immutable preregistration, independent server/provider health, a single active collector, exact monitor source SHA, read-only self-test/baseline and confirmation of one detached monitor process.
- Exact installed monitor SHA-256: `8a6e4f5558aa7fd6e714e0ba280b037395d4600c458246a0c86676eeb2b7a4e9`. Original preregistration SHA-256 remains `b67a2d4c587995d4b58649ea136e99306dfe5927a178565cc176b82f36b7ef9e`.

## Server-verified activation result

Server-local path:

```text
/data/research/phase11g/prospective_epochs/epoch_20260925T114500Z_v1/checks/
```

Observed around 2026-09-25T13:19:59Z:

- exactly one independent data collector PID `119664` and exactly one epoch monitor PID `121255`;
- installed monitor SHA-256 matches the reviewed/approved source;
- immutable `checks/baseline.json`: **PASS**; 6/6 then-due cutoffs checked, 0 manifest/source errors, 380 first-seen raw-file SHA checks;
- all six frozen pins **PASS** (registration, recorder, accepted legacy state, legacy ledger, harness, protocol);
- production `health=ok`, `mode=read_only`, `provider=binance_usdm`, `data_ready=true`;
- `notifications_scheduled=false`, `prospective_families_admitted=0`;
- two hourly slots that passed before installation (12:06Z / 13:06Z) explicitly recorded as `MISSED_BEFORE_MONITOR_ACTIVATION`. Read-only retrospective baseline does not rewrite or backdate those missed events.

**Future schedule:** hourly at `:06` UTC/Kyiv until the registered epoch ends; five four-hourly deep checks beginning **2026-09-25T15:51Z / 18:51 Kyiv**; final full check **2026-09-26T11:36Z / 14:36 Kyiv**. First not-yet-elapsed scheduled hourly verification after activation is **2026-09-25T14:06Z / 17:06 Kyiv**. The workflow and baseline prove process activation, *not* completion of that future check.

## Fresh causal data-quality observation (separate from monitor integrity PASS)

The first six captured M15 cutoffs (11:45Z–13:00Z) passed source-file/manifest consistency under the first activation baseline. The subsequent **13:15Z** data-only cutoff was successfully recorded, but only **1/19** top-ranked instruments met the capture-time depth/closure/ingestion gates; **18/19** failed with `15m:MISSING_LAST_CLOSED_BAR` and `5m:MISSING_LAST_CLOSED_BAR`.

A later read-only SQLite diagnostic observed some of these bars appearing with ingestion timestamps around **13:20:48–13:20:50Z**, outside the original `cutoff+300s` first-seen deadline for 13:15Z. The old 13:15 manifest must **never** be revised to accept late data, and a successful capture-manifest integrity check must not be interpreted as 19/19 data readiness.

This is a separate **market-data timeliness/coverage follow-up**, not permission to alter epoch timing or the frozen strategy. Watch later hourly/deep reports for repeated low first-seen completeness and diagnose within approved independent K-Trader resources only.

## Safeguards and acceptance boundary

- No HP-OMEN or K_AI/MT4-backed data use.
- No reminders, push notifications, ChatGPT automations or automatic repair/restart.
- Missed schedule entries are explicit; no retroactive replay or false continuity claim.
- Accepted old cohort remains `54/100` resolved families; new epoch is **data-only**, no candidate outcomes or family promotion.
- Existing recorder and monitoring survive while their Docker container remains running; no automatic restart is configured on container/host restart.
- Mark the *first future hourly scheduled check* verified only after its durable report appears and its source hashes pass.
