# K-Trader Current State

Updated: 2026-09-13 through prospective capture `2026-09-13T12:00:00Z` and accepted corrected causal rolling historical replay.  
Current research checkpoint: `docs/checkpoints/2026-09-13_V2_2_PROSPECTIVE_1200Z.md`  
Historical methodology checkpoint: `docs/checkpoints/2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md`  
Bootstrap: `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest runtime health at `2026-09-13T12:09:45Z`:

- `status=ok`;
- `mode=read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness state;
- container image remains `k-trader:81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- no production deploy or restart occurred during current research work.

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

No frozen rule, RR, 8h max-hold, risk gate, symbol/direction filter or holdout authorization changed.

## Track A — prospective evidence

Only unique resolved prospective `setup_family_id` values count toward the preregistered family thresholds.

Latest accepted capture/ledger cutoff:

`2026-09-13T12:00:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260913T120000Z`

Capture state:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- signal bars evaluated `3021`;
- deduplicated events `124`;
- eligible observations `17`;
- unique eligible families `12`;
- valid snapshots `12`;
- holdout unopened.

New 12th independent family:

- id `f7c6c40048ccd80d3a0ffeac266f4227e71b511a327ba43e9f7d6ddafc3dfebf`;
- `VTHOUSDT LONG`;
- primary entry `2026-09-13T09:00:00Z`;
- two correlated observations by 12:00Z.

Capture hashes:

- bundle set: `6b3f9762be7e1704d9db6dc9490b25f44e99cd79903c8511dc26b192b44843dc`;
- bundle export summary: `a1f62a6e5930d663bcd708af37ab7e9b25832de7968cdfde0907331c04e4c60c`;
- shadow summary: `fac14d51f33958adb2e8aab98320477a02910687a2c60b383ab329c6e80541c0`;
- event file: `43dededa0e76386c518d81a2861fb88c3e9a7c52a4688d29561ad1fe990fbebe`;
- ledger event set: `39477107acb99b0a5a8b4443bbe27d10f8828c809fd5dcc29c4adfa05fcc0d78`.

Deterministic outcome resolution has not yet been refreshed for the 12:00Z ledger because the execution channel blocked the resolver invocation before server execution. No substitute resolver semantics were used.

Last accepted resolver state therefore remains the 08:30Z result:

- unique families at that resolver state: `11`;
- resolved primary families: `9`;
- unresolved primary families: `2`;
- resolved wins/losses: `1 / 8`;
- resolved WR: `11.11%`;
- resolved expectancy: `-0.8807054663R`;
- evidence status: `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`.

The 12th family is accepted as ledger evidence but must not be counted as resolved until the canonical resolver succeeds.

### Observation-only Level Context

Refreshed on the 12-family ledger:

- eligible observations `17`;
- unique families `12`;
- clean-break/no-revisit `4`;
- frozen-v2.2 vs richer-context disagreements `2`;
- richer obstacle inside `3R`: `5`;
- richer obstacle inside `1R`: `4`;
- report SHA256 `8d5fc7c3c69f84fb90c194ba7e01a1644bc8159c8939de3e6785da54c5790f32`.

All Level Context fields remain diagnostic only and do not change frozen eligibility.

Next prospective hard milestone:

`>=30 unique resolved prospective frozen-v2.2 setup families`.

## Track B — corrected causal historical replay

The earlier Historical Expansion v1 and first long-window results are superseded for inference because they exposed the structural-space detector to more H1 history than the canonical prospective path.

Supersession:

`docs/research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_SUPERSESSION.md`

Corrected protocol:

`docs/research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`

Accepted replay semantics:

- rolling M15 context exactly `400` closed bars after warm-up;
- rolling H1 context exactly `300` closed bars after warm-up;
- original frozen `signal_at()` and `level_features()`;
- original 3R / 32-M15 max hold / STOP-first / costs and funding;
- no holdout access;
- no production action.

Global audit:

- `630240` historical decision bars;
- 19 symbols;
- M15 context `400/400` min/max;
- H1 context `300/300` min/max;
- `21964` raw frozen signal cases.

Prospective parity gate against the canonical 08:30Z snapshot:

- symbols `19/19`;
- decision bars `1824`;
- signal cases `70`;
- structural cases `69`;
- mismatches `0`;
- PASS.

Accepted corrected historical results:

| Window | Cohort | Trades | WR | Expectancy R | PF_R | Stress expectancy R | Stress PF_R |
|---|---:|---:|---:|---:|---:|---:|---:|
| P25 | 19 | 214 | 44.86% | +0.259415 | 1.5193 | +0.224861 | 1.4459 |
| R90 | 19 | 531 | 39.36% | +0.031637 | 1.0574 | -0.009676 | 0.9829 |
| R180 | 19 | 1073 | 39.14% | -0.013131 | 0.9761 | -0.042896 | 0.9232 |
| R365 | 17 | 2099 | 37.54% | -0.051000 | 0.9096 | -0.074531 | 0.8704 |

Direction diagnostics, base:

- P25 LONG `+0.457787R`, SHORT `-0.408573R`;
- R90 LONG `+0.209006R`, SHORT `-0.213339R`;
- R180 LONG `+0.084231R`, SHORT `-0.112140R`;
- R365 LONG `-0.011860R`, SHORT `-0.074765R`.

Interpretation:

- the corrected historical edge decays materially with horizon;
- P25 is positive and robust to frozen stress;
- R90 is marginally positive under base costs and slightly negative under stress;
- R180 and R365 are negative;
- v2.2 is therefore a recent/regime-dependent candidate, not a long-horizon historically robust strategy;
- SHORT weakness is a future-version hypothesis only; no in-place LONG-only filter is authorized.

Corrected hashes:

- result index `5db748737535254ac9983fa55f6c971e7198d9a6ffe80899e08f2d3ac23ea528`;
- parity `47b03d3c7280d8cc2c7f3f73af529fb2fa89e9ccf47c8b2132d289438396effe`;
- context audit `4e7ee32542c0ec15d6e166a285fcc1252529cf73420d70d869b1c73625ec82f9`.

Reproducibility:

- base evaluator `research/strategy_benchmark_v1/historical_causal_rolling_replay_v1_1.py`;
- base evaluator commit `196df4948f292505ffdb8c7b5966781843c5c878`;
- persisted equivalent optimization patch `research/strategy_benchmark_v1/patches/historical_causal_rolling_replay_v1_1_lossless_short_circuit.patch`;
- patch commit `a90585ca4ac5068fe434b8f52767ae3f4b426b4c`;
- accepted runtime evaluator SHA256 `c0dead4957622515a7d432d8142ac7ae8915f46e36905a5cc0e483c93e78b7e7`.

## Governance

Prospective thresholds remain unchanged:

- `<30` resolved primary families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Historical trades never count toward these family thresholds. Neither corrected historical results nor the current prospective sample authorize in-place retuning of frozen v2.2.

## Planned 24h data-collection pause

Planned window:

`2026-09-14 10:00 Europe/Kyiv -> 2026-09-15 10:00 Europe/Kyiv`.

Pre-pause host fact retained:

- `apt-daily.timer` enabled/active;
- `apt-daily-upgrade.timer` enabled/active;
- observed next `apt-daily-upgrade` schedule approximately `2026-09-14 09:01 Europe/Kyiv`;
- SentinelX `sudo systemctl` requires a password, so manual owner action is expected if that state remains unchanged.

Per user instruction, exact manual actions are to be supplied at `2026-09-14 07:00 Europe/Kyiv`. No automatic reminder or automation is configured.

## Repository

Canonical `main`:

`4919fea4397d34898ddc7d4215ea898e6caea815`

Research remains a descendant of canonical main with no rebase or force update. Production remains deployed on `81b79...`; research/documentation updates do not require redeployment.

## Next work order

1. Refresh the deterministic prospective resolver as soon as the execution channel permits it and resolve the 12-family ledger causally.
2. Continue exact frozen-v2.2 prospective captures only on materially newer safe closed-M15 cutoffs.
3. Keep corrected historical replay results immutable as accepted Track B evidence; do not tune historical windows based on P&L.
4. Continue Level Context / VSA / execution / correlation diagnostics as observation-only features.
5. Prepare the pre-pause baseline and exact owner manual host actions for `2026-09-14 07:00 Europe/Kyiv`.
6. Do not open holdout and do not retune frozen v2.2 in place.

Phase 11G remains **ACTIVE**.  
Phase 12 remains **FUTURE / NOT ACTIVE**.
