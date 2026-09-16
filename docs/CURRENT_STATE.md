# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T16:15:00Z`, parallel hardening completion and Plugin-migration preparation.

Current checkpoint:

`docs/checkpoints/2026-09-16_1615Z_HARDENING_PLUGIN_MIGRATION.md`

Core specifications:

- resolver: `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`;
- preregistration: `docs/research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`;
- max-hold evidence semantics: `docs/research/MAX_HOLD_CAUSAL_EVIDENCE_SEMANTICS.md`;
- portfolio-risk contract: `docs/research/PORTFOLIO_RISK_RESEARCH_CONTRACT_V1.md`;
- Phase 11G closure: `docs/research/PHASE_11G_CLOSURE_CRITERIA.md`;
- recovery: `docs/operations/RESEARCH_RECOVERY_RUNBOOK.md`;
- Plugin migration: `docs/plugin_migration/README.md`.

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest verified runtime:

- host `k-trader-prod-vnic`;
- health `ok`;
- mode `read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition, not an outage;
- container user `uid=1002(ktrader)`;
- Linux capabilities all zero;
- Docker socket absent inside the container;
- current public K-Trader API GET-only;
- no exchange-order credential names observed during the environment-name-only audit;
- no production deploy, restart or trading action performed by current research/hardening work.

Storage:

- filesystem exact byte utilization approximately `19.1%` (`df` rounded display 20%);
- inode use approximately `5%`;
- `/data/research` approximately `1.446 GB`;
- disk-retention remains `DRY_RUN_ONLY`, destructive mode absent;
- `ktrader-disk-retention.timer` remains disabled by design.

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

Broad strategy-discovery/self-improving-strategy research remains delegated to `K_Investigation_Forecast` and must not be reopened inside K-Trader until the user explicitly reports positive results.

## Latest accepted prospective state — 16:15Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T161500Z`

Capture:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- signal bars evaluated `6574`;
- current-capture eligible setups `49`;
- event count `299`;
- bundle set SHA256 `b929050728d0a07158f92775746c62ba861d6323fe751ff2e4ee59e7d6bca78a`;
- shadow summary SHA256 `a08597e26583516048e1c9e3596ded387e2d5a5bbd171f4795396055bbdc0abb`;
- holdout false;
- production false.

Ledger:

- eligible observations `61`;
- unique primary families `47`;
- valid snapshots `22`;
- one historical infrastructure-invalid first snapshot remains rejected;
- ledger event-set SHA256 `0fac0e8ed782b37090ca91b3388618724214bc2148c376e9ac580eecc0d8ba5c`.

Funding:

- symbols `19`;
- records `1878`;
- SHA256 `88882f4aa563438ea9723366d7f30c2b596174e8d4ac381960ffcbf1577f29a0`.

## Resolver v1.3

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T161500Z`

Summary SHA256:

`c579ac1684fa6d2f74d970601f69946559619341f9386e6747e3f829a9d0de75`

State:

- unique primary families `47`;
- resolved primary families `41`;
- unresolved primary families `6`;
- wins/losses `11/30`;
- win rate `26.8292682927%`;
- expectancy `-0.5902225135899566R`;
- evidence `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- holdout false;
- production false;
- network used false.

Newly resolved at this cutoff:

- SUIUSDT SHORT `08:00Z` -> `TIME_EXIT` at `16:00Z`, `+0.0991586118R`;
- XRPUSDT SHORT `08:00Z` -> `TIME_EXIT` at `16:00Z`, `+0.9843266645R`.

Both are discovery-context families.

## Max-hold / evidence-lag semantics

Frozen v2.2 processes 32 held M15 bars and TIME_EXIT executes at the next-bar open. The prospective resolver uses closed-bar-only evidence, so that open is confirmable one M15 evidence interval later.

Therefore:

- SUI/XRP strategy exit `16:00Z`, prospective confirmation `16:15Z`;
- ADA/DOGE discovery entries `08:15Z`: strategy TIME_EXIT `16:15Z`, prospective confirmation available at `16:30Z` if no earlier STOP/3R.

This is evidence lag, not a change to max hold.

## Preregistered confirmation sample

Boundary:

`entry_time >= 2026-09-16T13:00:00Z`

Evidence-tracker report SHA256:

`92378aaca9c3b60faf5a24cfb6371dcd66aa6f93ec648be1a9ebe019598373a3`

Counts:

- discovery primary families `44`;
- confirmation primary families `3`;
- confirmation resolved `0`;
- confirmation unresolved `3`;
- all current confirmation families are `SHORT / REST`;
- H1 LOW resolved `0`;
- obstacle <1R/<3R confirmation count `0`;
- chronology/governance invariants PASS.

Confirmation families:

- ADAUSDT SHORT `13:15Z`;
- DOGEUSDT SHORT `13:15Z`;
- ADAUSDT SHORT `15:00Z`.

No preregistered hypothesis can yet be evaluated.

## Current unresolved primary families

Discovery context:

- ADAUSDT SHORT `08:15Z` — strategy TIME_EXIT `16:15Z`, closed-bar confirmation available `16:30Z`;
- DOGEUSDT SHORT `08:15Z` — same evidence boundary;
- TRUMPUSDT SHORT `12:30Z`.

Confirmation:

- ADAUSDT SHORT `13:15Z`;
- DOGEUSDT SHORT `13:15Z`;
- ADAUSDT SHORT `15:00Z`.

Total unresolved: `6`.

## Diagnostics — 41 resolved

Descriptive SHA256:

`b2ffefbe71352e737e699feeba9ecb50f4d0df716a389e7c6a9a0714eb59f275`

Statistical SHA256:

`b4fdd55d1db88ce33bfe5778d4dc2220b80e1cdb7495cdeb52fba1c16c94ebd7`

Key state:

- overall expectancy `-0.590223R`;
- LONG expectancy `-0.585215R`;
- SHORT expectancy `-0.592547R`;
- STOP: `26`, wins `0`, expectancy `-1.066884R`;
- TIME_EXIT: `15`, wins `11`, expectancy `+0.235991R`;
- no broad exploratory contrast currently authorizes a frozen-v2.2 retune;
- obstacle <1R/<3R remains exploratory;
- VSA remains non-authorizing.

Portfolio diagnostics:

- current open families `6`, all SHORT;
- current open symbols: ADA x3, DOGE x2, TRUMP x1;
- observed max concurrent all `8`;
- observed max concurrent SHORT `8`;
- largest correlated cohort `4`.

No production risk cap has been selected. `docs/research/PORTFOLIO_RISK_RESEARCH_CONTRACT_V1.md` defines the future parameter interface only.

## Prospective automation v2

New canonical hardening target:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v2.py`

Stages:

`capture -> funding -> resolver -> post30 -> statistics -> evidence -> portfolio_risk -> state_manifest`

Properties:

- plan-only default;
- explicit `--execute`;
- fail-closed sequencing;
- output collision protection;
- resolver v1.3;
- discovery/confirmation tracking;
- portfolio-risk artifact;
- machine-readable current-state artifact.

Tests:

- pipeline v1 regression `6/6 PASS`;
- pipeline v2 regression `2/2 PASS`;
- current research Python compile PASS.

16:15 machine-readable state:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T161500Z.json`

SHA256:

`348a31f0fbc7735660abab1203a4f25ed566def5ae17366386b9395883fc2d01`

## Storage planning

Read-only storage diagnostics are documented in:

`docs/operations/RESEARCH_STORAGE_GROWTH_2026-09-16.md`

Approximate additional growth to thresholds:

- 70% review point: `24.09 GB`;
- 80% retention-planning threshold: `28.82 GB`.

Timer remains disabled and destructive cleanup unauthorized.

## Production safety / future execution compatibility

Audit:

`docs/operations/PRODUCTION_SAFETY_EXECUTION_COMPATIBILITY_AUDIT_2026-09-16.md`

Current read-only phase safety: PASS.

Before any future real execution, a separate versioned exchange/broker execution-spec contract is required for minimum/maximum quantity, notional, leverage/margin, position mode, order constraints and idempotency. This is a future prerequisite, not a Phase 11G blocker.

## Recovery and Phase 11G closure

Recovery runbook:

`docs/operations/RESEARCH_RECOVERY_RUNBOOK.md`

Closure contract:

`docs/research/PHASE_11G_CLOSURE_CRITERIA.md`

Closure paths:

- Path A: evidence-complete v2.2 benchmark at `>=100` resolved primary prospective families plus final reproducible report;
- Path B: explicit user decision to terminate v2.2 collection earlier and archive it as negative/inconclusive benchmark.

Closure does not itself open holdout, activate Phase 12 or authorize production trading.

## OpenAI product migration — Phase 10P

OpenAI's announced Custom GPT retirement changes the ChatGPT-facing product layer, not the canonical backend.

Current decision:

- keep the working Custom GPT until replacement acceptance;
- classify `custom_gpt/` as legacy compatibility assets;
- treat Custom Actions/OpenAPI as legacy transport, not the strategic future interface;
- preserve the existing read-only HTTPS backend;
- migrate durable behavior to a reusable K-Trader skill;
- use a Plugin app/connector integration, or thin MCP adapter if required by the supported platform path;
- re-test auth, permissions and sharing independently.

Prepared package:

- `docs/plugin_migration/README.md`;
- `docs/plugin_migration/K_TRADER_SKILL_DRAFT.md`;
- `docs/plugin_migration/INTEGRATION_CONTRACT_V1.md`;
- `docs/plugin_migration/REGRESSION_SUITE.md`;
- `docs/plugin_migration/SOURCE_ASSESSMENT_2026-09-16.md`;
- `custom_gpt/LEGACY_MIGRATION_NOTICE_2026-09-16.md`;
- `docs/ROADMAP_ADDENDUM_PLUGIN_MIGRATION_2026-09-16.md`.

New workstream: **Phase 10P — Plugin Migration**, preparation active; activation depends on the account/workspace migration/plugin creation capability becoming available.

Phase 10P and Phase 11G are independent.

## Governance

Prospective thresholds remain:

- `<30`: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Current resolved count: `41`.

No evidence authorizes in-place retuning, side filtering, exit-management modification, RR/max-hold/risk changes, holdout access, production mutation or Phase 12 activation.

## Next work order

1. At the next causally available closed-bar cutoff `>=16:30Z`, confirm the ADA/DOGE discovery-family TIME_EXIT paths if no STOP/3R occurs first.
2. Continue prospective collection with resolver v1.3 and the evidence-aware pipeline v2.
3. Keep discovery and post-prereg confirmation evidence separated.
4. Keep portfolio-risk diagnostics current; do not choose production caps inside Phase 11G.
5. Preserve production read-only state, holdout closure and disk-retention timer state.
6. Prepare Phase 10P only; do not disable the current Custom GPT until replacement Plugin acceptance.
7. Do not reopen `K_Investigation_Forecast` strategy discovery until the user explicitly returns positive results.
