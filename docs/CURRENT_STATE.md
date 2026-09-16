# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T13:45:00Z`, resolver v1.3 acceptance and prospective pipeline hardening.

Current checkpoint:

`docs/checkpoints/2026-09-16_PROSPECTIVE_1345Z_RESOLVER_V1_3.md`

Resolver specification:

`docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`

Hypothesis preregistration:

`docs/research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest verified state:

- host `k-trader-prod-vnic`;
- container `k-trader-ktrader-1` healthy;
- health `ok`;
- mode `read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition, not an outage;
- root filesystem remains approximately `19%` used;
- no production deploy, restart or trading action was performed by research continuation.

Extended soak remains accepted: `PASS`.

APT timers remain restored/enabled.

Disk-retention planner remains `DRY_RUN_ONLY`; destructive mode is absent and `ktrader-disk-retention.timer` remains disabled by design.

## Research isolation

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

No frozen rule, RR, 32-M15 max hold, risk gate, direction filter or production authorization changed.

Holdout remains:

`UNTOUCHED / NOT AUTHORIZED`

Phase 11G remains **ACTIVE**. Phase 12 remains **FUTURE / NOT ACTIVE**.

## External strategy-discovery boundary

Broad strategy-discovery / self-improving-strategy research has been delegated to the separate wider project `K_Investigation_Forecast`.

K-Trader must **not** reopen, redesign or optimize that research track until the user explicitly reports positive results from `K_Investigation_Forecast`.

Inside K-Trader, current v2.2 remains a benchmark/control and the project continues only its own accepted prospective validation, diagnostics, risk/evidence controls and infrastructure hardening.

## Latest accepted prospective state — 13:45Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T134500Z`

Capture:

- status `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- current capture eligible setups `48`;
- event count `299`;
- bundle set SHA256 `47253e3a2353f1a7b356c0ce5c275d60c183f59c8bdad15795d26876e5c483b3`;
- shadow summary SHA256 `901e935fa37f568da8f79e151e766a6ed95b83bbb96330fef456445e2b51b203`;
- holdout opened `false`;
- production action `false`.

Prospective ledger:

- eligible observations `60`;
- unique primary families `46`;
- valid snapshots `19`;
- one historical infrastructure-invalid first snapshot remains rejected.

Official Binance USD-M funding at 13:45Z:

- symbols `19`;
- records `1859`;
- summary SHA256 `c9f1a4c8a1f67d82a451243d0cc3c36c437ad1e8d4ae8f2dbee9bd66d2ff1e2a`.

## Resolver v1.3

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T134500Z`

State:

- eligible observations `60`;
- unique families `46`;
- resolved primary families `39`;
- unresolved primary families `7`;
- wins/losses `9/30`;
- win rate `23.0769230769%`;
- expectancy `-0.6482720085510278R`;
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- prior resolved observations reused `50`;
- current-path revalidated `44`;
- aged-out accepted terminal outcomes preserved `6`;
- network used `false`;
- holdout opened `false`;
- production action `false`.

Summary SHA256:

`9ecd26069c514fcafd1ce73fc06d5e05eb5aeffba549a99ef9487e18b9fc21af`

v1.3 acceptance parity:

- prior resolved observations checked `50/50`;
- terminal/economic mismatches `0`;
- prior entry max delta `0.0`;
- prior stop max delta `3.561768196352899e-9`.

v1.3 identity/revalidation rules:

- stable identity remains `(setup_family_id, symbol, side, entry_time)`;
- accepted prior entry price must match exactly;
- stop drift may pass existing `3e-9`/`1e-12` close or at most `1e-4` of accepted initial risk distance;
- terminal revalidation uses accepted prior entry/stop;
- larger drift fails closed.

v1.1 and v1.2 remain preserved for audit/history.

## Why v1.3 replaced v1.2 for continuation

At 13:45Z v1.2 correctly failed closed on a low-priced `VTHOUSDT` stop recomputation drift of `3.561768196352899e-9`.

Across the 50 prior resolved observations:

- entry drift remained exactly zero;
- maximum stop drift was only `4.9105198702635914e-05` of initial risk distance (~0.0049% of risk);
- drift was concentrated in VTHOUSDT.

Therefore a fixed absolute stop tolerance was not scale-neutral. v1.3 replaces repeated absolute widening with a bounded risk-relative sanity guard while keeping accepted prices immutable for path revalidation.

## Post-prereg confirmation sample

Preregistered confirmation boundary remains:

`entry_time >= 2026-09-16T13:00:00Z`

At 13:45Z the confirmation sample contains exactly `2` primary families, both unresolved:

- ADAUSDT SHORT, entry `13:15Z`, `h1_ema_sep_atr=1.723638807428305`;
- DOGEUSDT SHORT, entry `13:15Z`, `h1_ema_sep_atr=1.614385470865619`.

Both are in the H1 **REST** group, not LOW (`LOW < 0.9033277894201235`).

Both have `level_v2_h1_next_level_R = null`, therefore neither is an obstacle-inside-1R/3R case.

Confirmation status:

- total post-prereg primary families `2`;
- resolved `0`;
- H1 LOW resolved `0`;
- H1 REST resolved `0`.

No preregistered hypothesis can yet be evaluated.

## Unresolved primary families at 13:45Z

Pre-prereg / discovery-context only:

- SUIUSDT SHORT `08:00Z`: `23/32` bars;
- XRPUSDT SHORT `08:00Z`: `23/32`;
- ADAUSDT SHORT `08:15Z`: `22/32`;
- DOGEUSDT SHORT `08:15Z`: `22/32`;
- TRUMPUSDT SHORT `12:30Z`: `5/32`.

Post-prereg confirmation:

- ADAUSDT SHORT `13:15Z`: `2/32`;
- DOGEUSDT SHORT `13:15Z`: `2/32`.

The four early families retain max-hold boundaries `16:00Z` and `16:15Z` if STOP/3R does not occur first.

## Diagnostics

Resolved sample remains `39`, so all diagnostic conclusions remain non-authorizing.

13:45Z post-30 descriptive SHA256:

`f1b2566593a0a0d2878b1db9c0b2e1894643fcfddea2c8a3d15536dbba1c745e`

13:45Z statistical SHA256:

`fd56096c5a5b37de3e64e5f49a364256d5ffbf3c6c2c7ae93ec9a163c55ab0b5`

Key state:

- LONG expectancy `-0.585215R`;
- SHORT expectancy `-0.679800R`;
- no supported general LONG-only / SHORT-exclusion rule;
- obstacle <1R/<3R remains exploratory only;
- raw VSA remains non-separating;
- max concurrent exposure increased to `7` because more unresolved SHORT families coexist;
- largest correlated cohort remains `4`.

Existing path-quality findings remain diagnostic only, including `7/26` STOP outcomes that had previously reached >=1R and positive TIME_EXIT expectancy. No exit-management change is authorized in frozen v2.2.

## Prospective orchestration

Canonical runner:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v1.py`

Current runner now uses resolver **v1.3** and has:

- plan-only default;
- explicit `--execute`;
- full capture dependency preflight (`10` required runtime files);
- explicit versioned outcomes root;
- existing run/outcome root guards;
- fail-closed stage execution;
- hashed manifests;
- no holdout or production action.

Regression suite: **6/6 PASS**.

Earlier 13:30Z failed orchestration manifests remain audit evidence. A resolver output accidentally written under a v1.1-labelled directory by the pre-fix runner is explicitly marked `INVALID_ORCHESTRATION_OUTPUT_DO_NOT_USE.json` and is non-canonical.

## Governance

Prospective thresholds remain:

- `<30` resolved families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Current resolved primary family count remains `39`.

Historical trades never count toward these thresholds.

No current evidence authorizes in-place retuning, direction filtering, exit-management modification, RR/max-hold/risk changes, holdout access, production mutation or Phase 12 activation.

## Next work order

1. continue causal prospective collection using the hardened runner and resolver v1.3;
2. resolve the seven current open primary families only after real STOP/3R or causal max-hold;
3. keep all pre-13:00Z families out of prereg H1-H4 confirmation counts;
4. track post-prereg confirmation sample separately;
5. preserve frozen v2.2, holdout closure, production read-only boundary and disk-retention timer state;
6. do not reopen the broad adaptive-strategy research delegated to `K_Investigation_Forecast` until the user explicitly reports positive results.
