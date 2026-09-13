# K-Trader Current State

Updated: 2026-09-13 post-pause resume  
Research checkpoint: `docs/checkpoints/2026-09-13_POST_PAUSE_RESUME.md`  
Bootstrap: `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Fresh verification at approximately `2026-09-13T06:12:54Z`:

- `/health`: `status=ok`;
- mode `read_only`;
- provider `binance_usdm`;
- `data_ready=true`;
- action authentication enabled;
- `scanner_status=DEGRADED` remains the known fail-closed/history-readiness condition;
- VM uptime ~`3 days 22:44`, therefore no reboot occurred during the technical pause.

The connected SentinelX identity cannot access the Docker socket directly, so direct container inspection requires an authorized Docker/root channel.

## Pause result

Planned pause:

`2026-09-12T06:00:00Z -> 2026-09-13T06:00:00Z`

Production is healthy after the pause and the deployed K-Trader SHA did not change.

However the pause was **not a strict no-host-change freeze**. `apt-daily-upgrade` ran inside the window at approximately `2026-09-12T06:04:35Z` and upgraded:

- Python 3.12 family `3.12.3-1ubuntu0.16 -> 3.12.3-1ubuntu0.17`;
- libc6 family `2.39-0ubuntu8.8 -> 2.39-0ubuntu8.9`.

No `2026-09-13` APT transaction was present at the resume audit. APT timers are back in normal active/waiting state.

This is host-environment drift, not a repository/deployment/strategy change. Before any production mutation, perform the post-pause host/runtime acceptance described in the current checkpoint.

## Monitoring limitation

The pause-watch automation does not provide a complete hourly evidence chain across the full 24h window. Current uptime and current health are positive runtime-continuity signals, but data/research continuity must be reconstructed from provider-recorded artifacts.

## Research isolation

Research branch:

`research-strategy-benchmark-v1`

Frozen candidate:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Prospective boundary:

`2026-09-11T20:00:00Z`

Holdout:

`UNTOUCHED / NOT AUTHORIZED`

No frozen rule, RR, 8h max-hold, risk gate, symbol/direction filter or holdout authorization changed during the pause.

## Latest accepted prospective evidence

A fully authorized post-pause catch-up has **not yet been executed**. Therefore the latest accepted immutable snapshot remains:

`2026-09-12T04:45:00Z`

Ledger at that boundary:

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

Accepted hashes:

- shadow summary: `4af1233c90464ab1d0e8cdf4b6e1ede062f66731558e6eb1eb947dc9377ca9df`;
- bundle set: `6e41b993477b47b179bc40e9f46a700d0aca9529797111562103920c124f355e`;
- bundle export summary: `8ce3bb969943ebe8814bd1c67952d8ef1215e56399134dd1430891097711e50d`;
- event file: `83b3f64813a803382048a9193a092e7423a3fef986213905603acdaa8b091073`;
- ledger event set: `cd25594d5e3f46a8894acf0bca050bf7b253c1618fe2f45184ed8a431287d166`;
- outcome summary: `f7e8314337166cdc4657f37b175c9744833a8356d2f0e3bc64702a5d0f4b19cb`;
- Level Context observation: `de61c71e7aef0c01b07eef03c01572f4dd618cd0def99f7bda2b0b1edc113b02`.

Primary outcomes at that boundary:

| Family | Symbol | Side | State | Realized R |
|---|---|---|---|---:|
| `15fc0a...` | RAYSOLUSDT | LONG | unresolved | — |
| `6aabd4...` | RAYSOLUSDT | LONG | STOP | `-1.0221R` |
| `293d11...` | RAYSOLUSDT | LONG | STOP | `-1.0350R` |
| `eecbdb...` | ENAUSDT | SHORT | unresolved | — |

The two resolved STOP families are the two current prospective Level Context disagreements: frozen v2.2 saw open-space, while the richer detector saw obstacles near `0.028R` and `0.214R`. This remains observation-only.

## Catch-up requirement

The prospective runner retains 400 M15 bars per symbol (~100h), so the 24h pause remains inside the causal recovery horizon.

First resumed research action must be:

- resolve the latest safe closed M15 cutoff;
- run one authorized provider-recorded frozen-v2.2 shadow cycle;
- rebuild the ledger;
- run deterministic family outcome resolution;
- refresh Level Context/VSA/execution observation diagnostics;
- audit pause-window continuity/gaps;
- write a post-catch-up checkpoint.

Do not substitute a noncanonical path if Docker/research-volume authorization is unavailable.

## Family evidence governance

Primary evidence unit = unique resolved setup family.

- `<30`: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Next hard milestone:

`>=30 unique resolved prospective frozen-v2.2 setup families`.

Do not tune frozen v2.2 from the current tiny prospective sample.

## Retained profile research

FAST v0 remains a negative baseline and is not promotable.

SWING v0 remains near breakeven under base assumptions but negative in validation/stress and is not promotable.

POSITION W1 remains prototype/data-architecture only; temporal integrity passed for 19/19 symbols with 47–70 W1 bars.

## Repository/governance

Canonical `main` after PR #57:

`4919fea4397d34898ddc7d4215ea898e6caea815`

PR #57 was squash-merged after CI success and canonized:

- approved `custom_gpt/SYSTEM_K_TRADER_v1_3_COMPACT.md`;
- active `custom_gpt/00_KNOWLEDGE_PRIORITY.md`;
- Builder/Action/catalogue references to v1.3.

Research branch accepted pre-resume head was:

`90debd3ed5c4284b4590b8e4ebe7f106d475a8d3`

At the resume audit the research branch was approximately `83 ahead / 1 behind` relative to the newly updated `main`. Preserve research history; do not rebase blindly. Synchronize ancestry after post-pause catch-up and content-parity verification.

Production remains deployed on `81b79...`; the new main commit is governance/documentation and does not require deployment.

## Resume order

1. P0 post-pause catch-up and continuity audit.
2. Post-host-drift runtime acceptance.
3. Post-catch-up checkpoint and repo ancestry sync.
4. Continue frozen-v2.2 prospective accumulation.
5. Continue observation-only Level Context/portfolio/execution diagnostics.
6. Consider only preregistered new strategy versions when evidence supports them.

Phase 11G remains **ACTIVE**.

Phase 12 remains **FUTURE / NOT ACTIVE**.
