# Phase 11G - Production TTL Rollout and Corrected Windows #1-#4

Date: 2026-09-09

Status: **PRODUCTION TTL ACCEPTED / CORRECTED WINDOWS #1-#4 REPLAY COMPLETE / ZERO TRADABLE SIGNALS**

## Purpose

Close the operational follow-up to the 60-minute setup-lifecycle gate by deploying the accepted canonical implementation to production and rerunning the four historical discovery windows under the explicit FAST profile lifecycle.

This checkpoint does not relax RR, ATR, structural-target, context freshness, probability, or catalogue integrity rules. It does not force reconstructed populations to match superseded runs.

## Canonical production rollout

Deployment source:

- repository: `kolemasakar/K-Trader`;
- branch: `main`;
- deployed canonical SHA: `9a257957e033f6265b9e746cb9f15e755ff87b72`;
- image: `k-trader:9a257957e033f6265b9e746cb9f15e755ff87b72`;
- GitHub workflow: `Deploy Production #10`;
- target: Oracle ARM64 production host `k-trader-prod-vnic`.

Deployment acceptance:

- workflow: SUCCESS;
- container: healthy;
- provider REST/WebSocket: PASS (`binance_usdm`);
- canonical MTF API: PASS;
- public HTTPS: PASS;
- Phase 10 Action live acceptance: PASS;
- immutable release identity / deployed SHA: exact match.

Immediate scanner acceptance was `DEGRADED` with usable data (`symbols_ready=3`, `symbols_failed=17`); this did not fail service health or release acceptance and is recorded as operational evidence rather than hidden.

## Live FAST lifecycle acceptance

Direct verification inside the accepted production container:

```text
setup_interval = 5m
setup_max_age_bars = 12
setup_max_age_seconds = 3600
AGE_60M_EXPIRED = False
AGE_60M_1S_EXPIRED = True
```

Therefore production implements the approved FAST lifecycle exactly:

- `setup_age <= 60m` -> valid with respect to lifecycle age;
- `setup_age > 60m` -> hard reject `SETUP_EXPIRED`.

The default production profile remains FAST/M5. Horizon-aware M15/H1 support is research-only unless separately activated and validated.

## Corrected historical window contract

All four replays used:

- provider: `binance_usdm`;
- setup interval: `5m`;
- setup TTL: `12 x M5 = 60m`;
- context selection: newest recorded universe snapshot at or before each cutoff;
- `max_context_age_seconds=300`;
- logical context cadence: M5;
- deep MTF target depths: `1d=300`, `4h=300`, `1h=300`, `15m=300`, `5m=400`;
- unchanged canonical `analyze_candle_snapshot()` engine;
- unchanged `RR >= 3`;
- unchanged ATR-used threshold;
- structural targets only;
- no fabricated rank/context/history/outcomes/probability.

Window boundaries and selected-context archive identities:

| Window | UTC range | Selected snapshots | Strict symbols | Selected archive SHA-256 |
|---|---|---:|---:|---|
| W1 | 2026-09-07 18:55 -> 20:10 | 16 | 44 | `03596e16842cde5cf704344316e5ff732959ac6d280e205486fa62826732cd20` |
| W2 | 2026-09-07 20:15 -> 21:30 | 16 | 46 | `621b3043ea6adbc8490ab02eab241060eb56e443ccd19d84718e4e04004eca37` |
| W3 | 2026-09-07 21:35 -> 22:50 | 16 | 45 | `b511599cce4116aa1cd93f07e1836ab5a4ce19e2750b07f27b372cf4c9b002ff` |
| W4 | 2026-09-07 22:55 -> 2026-09-08 00:10 | 16 | 45 | `bed603828a997570149f01d42e7a979d96eb6ff0247c68f045b7e65bbe2c0477` |

W3 and W4 archive identities exactly reproduce the recorded historical checkpoint identities, validating the reconstruction semantics for those windows.

## Replay results

| Window | History pass | History fail | Analyzed cutoffs | Candidate decisions | HTF aligned | Strong level | `SETUP_EXPIRED` | Tradable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| W1 | 40 | 4 | 600 | 6,951 | 489 | 240 | 5,601 | 0 |
| W2 | 42 | 4 | 630 | 7,392 | 540 | 262 | 6,258 | 0 |
| W3 | 41 | 4 | 615 | 7,569 | 523 | 240 | 6,576 | 0 |
| W4 | 40 | 5 | 600 | 7,596 | 435 | 202 | 5,517 | 0 |
| **TOTAL** | **163** | **17** | **2,445** | **29,508** | **1,987** | **944** | **23,952** | **0** |

`SETUP_EXPIRED` is a reason-code occurrence count and can overlap with other hard rejects; it must not be interpreted as a disjoint funnel stage.

No replay cutoff was skipped for missing/stale selected context after the strict selection gate, and no cutoff was skipped for insufficient replay history after symbol-level deep-history qualification.

## Deep-history failures

The symbol-level deep-history gate failed closed. Representative failures remained newly listed/short-history symbols, including `MARSCOINUSDT`, `PONSUSDT`, `牛来USDT`, `龙虾USDT`, `PIEVERSEUSDT`, and `CFGUSDT` depending on the window. No missing history was synthesized.

## Window #4 population reproduction

The current replay reproduced the canonical historical W4 population exactly at the high-level contract stages:

```text
strict symbols = 45
history pass = 40
analyzed cutoffs = 600
candidate decisions = 7596
HTF aligned = 435
strong primary level = 202
```

The public `TradingDecision` intentionally masks `entry`, `stop`, and `target` when `side=NO_TRADE`; `rr` and `atr_used_pct` remain audit-visible when geometry exists. Therefore geometry-stage auditing must use canonical geometry/reason semantics rather than masked entry/stop/target presence.

## Aggregate conclusion

The production rollout and corrected discovery answer the lifecycle question without changing trading standards:

- the 60-minute FAST TTL is live and boundary-correct in production;
- all four corrected historical windows were replayed under that lifecycle;
- `23,952 / 29,508` candidate decisions carried `SETUP_EXPIRED` as one of their rejection reasons;
- no natural tradable signal survived all unchanged hard gates;
- no new dataset chain is justified by these four windows;
- the canonical catalogue therefore remains SUIUSDT + XRPUSDT only;
- zero tradable signals is an accepted research outcome and is not grounds to lower `RR >= 3`, widen freshness, synthesize targets, or manufacture probability/outcomes.

## Conditional Window #4 geometry/lifecycle audit

A corrected helper audit avoided the public-decision masking trap by treating geometry as available when canonical geometry outputs (`rr`, `atr_used_pct`) exist and no geometry hard-reject code is present. It did not require public `entry/stop/target`, because those fields are intentionally masked for `NO_TRADE`.

The exact W4 conditional funnel is:

```text
HTF aligned           435
-> strong level       202
-> valid geometry     168
-> ATR <= 80%         142
-> setup age <= 60m     0
-> RR >= 3              0
```

This reproduces the historical pre-TTL conditional population exactly through the ATR stage (`435 -> 202 -> 168 -> 142`). The explicit 60-minute lifecycle then removes all `142` candidates in this exact historical W4 population before RR eligibility.

This is consistent with, but population-distinct from, the later V2 control replay where three post-expiry RR-only candidates survived lifecycle and all still failed `RR >= 3`. No contradiction is implied because the historical W4 and V2 input populations were already documented as non-byte-identical.

## Next Phase 11G work

1. preserve this production/replay checkpoint as the canonical closure of the FAST 60m rollout + historical Windows #1-#4 rerun;
2. keep continuous provider-recorded research capture active;
3. materialize/register a new chain only when a naturally useful deterministic setup survives every unchanged hard gate;
4. continue the separately defined INTRADAY (M15) and MEDIUM (H1) lifecycle research as research profiles, without activating them in production until replay evidence and an explicit activation gate exist;
5. keep probability calibration inactive until real binary outcome sample size and an approved out-of-sample methodology justify it.