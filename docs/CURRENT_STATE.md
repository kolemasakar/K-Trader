# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T14:15:00Z`.

Current checkpoint:

`docs/checkpoints/2026-09-16_PROSPECTIVE_1415Z_CONTINUITY.md`

Resolver specification:

`docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`

Hypothesis preregistration:

`docs/research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest verified runtime invariants:

- host `k-trader-prod-vnic`;
- health `ok`;
- mode `read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition, not an outage;
- no production deploy, restart or trading action was performed by research continuation;
- disk remains approximately 19% used;
- disk-retention planner remains `DRY_RUN_ONLY`, destructive mode absent, timer disabled by design.

Extended production soak remains accepted: `PASS`. APT timers remain restored/enabled.

## Research boundary

Research branch:

`research-strategy-benchmark-v1`

Canonical main baseline:

`4919fea4397d34898ddc7d4215ea898e6caea815`

Frozen candidate:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Protocol SHA256:

`ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

No frozen rule, RR, 32-M15 max hold, risk gate, side filter or production authorization changed.

Holdout remains `UNTOUCHED / NOT AUTHORIZED`.

Phase 11G remains **ACTIVE**. Phase 12 remains **FUTURE / NOT ACTIVE**.

Broad strategy-discovery/self-improving-strategy research is delegated to `K_Investigation_Forecast` and must not be reopened inside K-Trader until the user explicitly reports positive results.

## Latest accepted prospective state — 14:15Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T141500Z`

Capture:

- status `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- current-capture eligible setups `48`;
- current-capture unique eligible families `37`;
- event count `298`;
- signal bars evaluated `6574`;
- bundle set SHA256 `56e108731b61cfa1f5ef6d72cc3d5a14f95c5147e2a55a6c8dfd9ca50bc8b47d`;
- event file SHA256 `95f1256cb01c1ce720df4ef2f4974440df57678b2bc0653512f6e12c2bf27aa8`;
- shadow summary SHA256 `dbab78e36542e4471ca248d409f9dc0d2db2cb1aa89e65342b6018e5dcc27e90`;
- holdout opened `false`;
- production action `false`.

Ledger:

- discovered snapshots `21`;
- valid snapshots `20`;
- rejected snapshots `1` known historical infrastructure-invalid first attempt;
- eligible observations `60`;
- unique primary families `46`;
- ledger event-set SHA256 `06070917e913759c680b9a0e420742864ac7772e5796036b453be437223ac0a7`.

Official Binance USD-M funding:

- symbols `19`;
- records `1859`;
- summary SHA256 `19ecb0e27938375970e62f344439e9978511f23f24b15cca322e565fcab2f979`.

## Resolver v1.3

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T141500Z`

Summary SHA256:

`0f71d5c954d3176565c5380c134049f00d107a2404a82f5a03cb2af99dad15e2`

State:

- eligible observations `60`;
- unique primary families `46`;
- resolved primary families `39`;
- unresolved primary families `7`;
- wins/losses `9/30`;
- win rate `23.0769230769%`;
- expectancy `-0.6482720085510278R`;
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- prior resolved observations reused `50`;
- current-path revalidated `44`;
- aged-out accepted terminal outcomes preserved `6`;
- max prior entry delta `0.0`;
- max prior stop delta `3.495449963004417e-9`;
- network used `false`;
- holdout opened `false`;
- production action `false`.

Continuity parity against all previously accepted resolved observations: `50/50`, terminal/economic mismatches `0` — **PASS**.

v1.3 remains the canonical continuation. It requires exact accepted entry identity, bounds stop recomputation drift by the existing close guard or at most `1e-4` of accepted initial risk, and revalidates terminal paths using accepted prior entry/stop. v1.1 and v1.2 remain preserved for audit/history.

## Post-prereg confirmation sample

Preregistered confirmation boundary:

`entry_time >= 2026-09-16T13:00:00Z`

Current genuine post-prereg primary families:

- ADAUSDT SHORT, entry `13:15Z`, unresolved, `h1_ema_sep_atr≈1.7236`;
- DOGEUSDT SHORT, entry `13:15Z`, unresolved, `h1_ema_sep_atr≈1.6144`.

Both are H1 `REST`, not `LOW` (`LOW < 0.9033277894201235`).

TRUMPUSDT SHORT primary entry is `12:30Z`; a later 13:15Z observation belongs to that pre-prereg family and therefore does not count as post-prereg primary evidence.

Confirmation counts:

- total post-prereg primary families `2`;
- resolved `0`;
- H1 LOW resolved `0`;
- H1 REST resolved `0`.

No preregistered hypothesis can yet be evaluated.

## Unresolved primary families at 14:15Z

Pre-prereg/discovery context:

- SUIUSDT SHORT `08:00Z`: `25/32` bars;
- XRPUSDT SHORT `08:00Z`: `25/32` bars;
- ADAUSDT SHORT `08:15Z`: `24/32` bars;
- DOGEUSDT SHORT `08:15Z`: `24/32` bars;
- TRUMPUSDT SHORT `12:30Z`: `7/32` bars.

Post-prereg confirmation:

- ADAUSDT SHORT `13:15Z`: `4/32` bars;
- DOGEUSDT SHORT `13:15Z`: `4/32` bars.

The four early families retain max-hold boundaries `16:00Z` and `16:15Z` if STOP/3R does not occur first.

## Diagnostics

Resolved sample remains `39`; all findings remain diagnostic-only and non-authorizing.

14:15Z post-30 descriptive SHA256:

`29c636f0a4a8b01fb0fb4b24ee9588955b97700ca3bb698ac3b4fd66df485621`

14:15Z statistical SHA256:

`8d8ad6f472a61beb32afbc7f0927cb213282939ef5b02e29a36a2bf07216c306`

Resolved metrics remain unchanged:

- LONG expectancy `-0.585215R`;
- SHORT expectancy `-0.679800R`;
- no supported general LONG-only/SHORT-exclusion rule;
- obstacle <1R/<3R remains exploratory;
- raw VSA remains non-separating.

Portfolio state changed as more unresolved SHORT families coexist:

- max concurrent all `7`;
- max concurrent SHORT `7`;
- largest correlated cohort `4`;
- multi-family correlated cohort count `5`.

Previously accepted path-quality findings remain diagnostic only. No exit-management change is authorized.

## Prospective orchestration

Canonical runner:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v1.py`

It uses resolver v1.3 and remains fail-closed, plan-only by default, explicit `--execute`, dependency-preflighted, versioned-output aware and manifest-producing. Regression suite remains accepted.

## Governance

Prospective thresholds remain:

- `<30` resolved primary families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Historical trades never count toward thresholds.

Current resolved count remains `39`.

No evidence authorizes in-place retuning, direction filtering, exit-management modification, RR/max-hold/risk changes, holdout access, production mutation or Phase 12 activation.

## Next work order

1. Continue causal prospective collection using the hardened runner and resolver v1.3.
2. Resolve the seven current open primary families only after real STOP/3R or causal max hold.
3. Keep all pre-13:00Z primary families out of prereg confirmation counts.
4. Track post-prereg confirmation sample separately.
5. At/after the early-family causal boundaries `16:00Z` and `16:15Z`, run capture → funding → resolver → diagnostics and reassess the evidence tier.
6. Preserve frozen v2.2, holdout closure, production read-only boundary and disk-retention timer state.
7. Do not reopen the broad adaptive-strategy research delegated to `K_Investigation_Forecast` until the user explicitly reports positive results.
