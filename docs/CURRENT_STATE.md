# K-Trader Current State

Updated: 2026-09-12 pre-freeze  
Research checkpoint: `docs/checkpoints/2026-09-12_PRE_FREEZE_FINAL_CHECK.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Fresh verification at approximately `2026-09-12T05:50:31Z`:

- localhost `/health`: HTTP 200;
- public HTTPS `/health`: HTTP 200;
- status `ok`;
- mode `read_only`;
- provider `binance_usdm`;
- `data_ready=true`;
- Action authentication enabled;
- `scanner_status=DEGRADED` remains the known fail-closed/history-readiness condition;
- `/opt/k-trader/current` resolves to release `81b79b281a4cc330b7c11058d202e0d74fb6d70e`.

No production code/config/deployment/risk/execution/trading semantics were changed by strategy research.

## Research isolation

Branch: `research-strategy-benchmark-v1`.

Frozen candidate: `candidate_rule_set_v2_2`.

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Prospective boundary: `2026-09-11T20:00:00Z`.

Holdout: `UNTOUCHED / NOT AUTHORIZED`.

Research does not imply production activation.

## Latest valid prospective evidence

A requested exact final `2026-09-12T05:45:00Z` capture was attempted before freeze but could not be executed because the connected SentinelX identity is `sentinelx` without Docker/root permission. The Docker socket and research-volume path correctly fail closed. No substitute result is asserted.

Therefore the latest **valid** immutable capture remains:

`2026-09-12T04:45:00Z`

Latest accepted ledger state:

- valid snapshots: 7;
- panel: 19/19;
- causally evaluable symbol-bars: 646;
- deduplicated frozen events: 31;
- eligible observations: 6;
- unique eligible families: 4;
- resolved primary families: 2;
- unresolved primary families: 2;
- resolved wins: 0;
- resolved losses: 2;
- resolved expectancy: `-1.0285267114R`;
- evidence status: `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`.

Latest artifact hashes:

- shadow summary: `4af1233c90464ab1d0e8cdf4b6e1ede062f66731558e6eb1eb947dc9377ca9df`;
- bundle set: `6e41b993477b47b179bc40e9f46a700d0aca9529797111562103920c124f355e`;
- bundle export summary: `8ce3bb969943ebe8814bd1c67952d8ef1215e56399134dd1430891097711e50d`;
- event file: `83b3f64813a803382048a9193a092e7423a3fef986213905603acdaa8b091073`;
- ledger event set: `cd25594d5e3f46a8894acf0bca050bf7b253c1618fe2f45184ed8a431287d166`;
- outcome summary: `f7e8314337166cdc4657f37b175c9744833a8356d2f0e3bc64702a5d0f4b19cb`;
- Level Context observation: `de61c71e7aef0c01b07eef03c01572f4dd618cd0def99f7bda2b0b1edc113b02`.

## Primary family outcomes at 04:45Z

| Family | Symbol | Side | Obs | State | Realized R |
|---|---|---|---:|---|---:|
| `15fc0a...` | RAYSOLUSDT | LONG | 2 | unresolved | — |
| `6aabd4...` | RAYSOLUSDT | LONG | 1 | STOP | `-1.0221R` |
| `293d11...` | RAYSOLUSDT | LONG | 2 | STOP | `-1.0350R` |
| `eecbdb...` | ENAUSDT | SHORT | 1 | unresolved | — |

The two resolved STOP families are exactly the two current families where frozen v2.2 classified open-space while Level Context v2 detected a richer obstacle inside 1R/3R (`~0.028R` and `~0.214R`). This remains observation-only and does not change frozen eligibility.

## Frozen strategy governance

Family accounting remains preregistered: earliest eligible observation is the immutable primary representative. Later observations are correlated diagnostics only.

Do not modify frozen v2.2 from current evidence:

- no Level Context/clean-break hard gate;
- no early-progress/profit-protection rule;
- no new minimum-risk threshold;
- no volume/VSA hard gate;
- no symbol/direction inclusion rule;
- no RR/8h retuning;
- no holdout opening.

Next hard evidence milestone:

`>=30 unique resolved prospective frozen-v2.2 setup families`.

## Profile research retained

FAST baseline v0 remains negative across development/validation/stress and is not promotable.

SWING baseline v0 remains near breakeven under base assumptions but negative in validation/stress and is not promotable.

POSITION W1 contract remains prototype/data-architecture only; temporal-integrity audit passed for 19/19 symbols with 47–70 W1 bars.

## Pre-freeze status

Planned technical freeze: `2026-09-12 09:00 Kyiv` -> `2026-09-13 09:00 Kyiv` (`06:00Z` -> `06:00Z`).

Production itself is healthy and read-only. Research evidence is internally consistent through `04:45Z`, but the requested exact `05:45Z` final capture is **NOT VERIFIED** because the automation identity lacks Docker/root access. The freeze must therefore be treated as **SAFE FOR PRODUCTION / NOT A FULL CLEAN RESEARCH FINALIZATION** unless an authorized operator performs the final capture before the boundary.

Phase 11G remains active. Phase 12 remains FUTURE / NOT ACTIVE.
