# K-Trader Current State

> **New server-only first-seen epoch preregistered (2026-09-25 11:11 UTC):** [bounded future data-only epoch checkpoint](checkpoints/2026-09-25_PHASE11G_NEW_EPOCH_1145Z_PREREG.md), first cutoff 11:45Z; old 54/100 accepted families and first-seen ledger remain immutable. New epoch selection uses independently recorded top-19 Binance ranks, with no strategy outcomes admitted until a separate isolation/compatibility acceptance gate. No HP-OMEN use.

> **Server-only retrospective audit completed (2026-09-25):** the 2026-09-18 06:30Z → 2026-09-25 10:15Z historical gap was assessed separately against an integrity-checked frozen K-Trader SQLite copy. Result: 688/688 universe-context cutoffs verified; 13,072 ranked slots; 9,717 structurally replayable with present historical data; 31 slots with compatible present-state ingest timestamps, **none admitted as prospective evidence**. The current Path A count remains **54/100**. See [auditor results and limitations](research/recovery_retrospective/2026-09-25T1015Z/README.md). New prospective epoch remains a separate unapproved gate. **HP-OMEN remains prohibited.**

> **Mandatory host restriction (2026-09-25):** HP-OMEN is **prohibited for all K-Trader use** (including indirect K_AI/MT4-backed data, diagnostics, CI, scripts, research and backups) until a separate explicit user instruction. Work only on verified independent K-Trader server/repository resources. If a step depends on HP-OMEN, mark it BLOCKED rather than substituting it. See [`docs/operations/K_TRADER_HP_OMEN_EXCLUSION_2026-09-25.md`](operations/K_TRADER_HP_OMEN_EXCLUSION_2026-09-25.md). This operational update does not change the historical Phase 11G evidence snapshot recorded below.

**Latest independent server-only audit:** 2026-09-25; [checkpoint](checkpoints/2026-09-25_PHASE11G_SERVER_ONLY_RECOVERY_AUDIT.md). Latest verified accepted prospective cutoff is **2026-09-18T06:15:00Z**, with **54/100 resolved primary families**, source-hash verification **5/5 PASS**, preserved recovery checksums **58/58 PASS** and accepted-bundle data quality **95/95 PASS**. The 06:30 cycle remains **FAIL_CLOSED/partial**; no active prospective runner was observed. On the separate 2026-09-25T10:15Z retrospective readiness check, recorded top-19 contained **14 ready / 5 fail-closed** symbols; this does not authorize continuation or additional prospective counting. The dated 2026-09-17 material below is historical and is not the latest runtime count. No HP-OMEN resource is permitted.

Updated: 2026-09-17 through accepted prospective cutoff `2026-09-17T02:30:00Z`.

Current checkpoint:
`docs/checkpoints/2026-09-17_0230Z_PRE_PAUSE_AUTOMATION.md`

Authoritative new-chat handoff remains:
`docs/operations/K_TRADER_NEW_CHAT_HANDOFF_2026-09-16_1930Z.md`

## Production invariant

- accepted/deployed SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`
- host `k-trader-prod-vnic`
- health `ok`
- mode `read_only`
- `data_ready=true`
- provider `binance_usdm`
- scanner `DEGRADED` remains known fail-closed/history-readiness condition
- public API remains GET-only
- no production deploy, restart, privilege expansion or trading action performed
- root filesystem usage approximately `20%`

## Research boundary

- branch `research-strategy-benchmark-v1`
- canonical main baseline `4919fea4397d34898ddc7d4215ea898e6caea815`
- frozen candidate `candidate_rule_set_v2_2`
- frozen harness SHA256 `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`
- protocol SHA256 `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`
- resolver v1.3
- ledger v1.2: first valid event-key payload immutable; later conflicting recomputations audit-only
- prereg boundary `2026-09-16T13:00:00Z`
- holdout `UNTOUCHED / NOT AUTHORIZED`
- Phase 11G **ACTIVE**
- Phase 12 **FUTURE / NOT ACTIVE**

No frozen rule, RR, 32-M15 max hold, risk gate, side filter or production authorization changed.

## Latest accepted prospective state — 02:30Z

Run root:
`/data/research/phase11g/v2_2_shadow_20260917T023000Z`

Pipeline manifest:
`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_pipeline_manifests/pipeline_v2_20260917T023000Z_execute.json`

Pipeline SHA256: `5669ef0b017bb1ccc07cd023975feefd197bb4fab7018e61ae7ccd7ac648c8a5`

State manifest:
`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260917T023000Z.json`

State SHA256: `576cc034a7bd1e87f7566848b69c8d9b0396082d3f3d65aca07752a8ded38d62`

State:

- status `PASS`
- panel `19/19`
- eligible observations `63`
- unique primary families `49`
- resolved primary families `48`
- unresolved primary families `1`
- current open families `1`
- wins/losses `13/35`
- win rate `27.08333333333333%`
- expectancy `-0.6088593884101355R`
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`
- confirmation families `5`
- confirmation resolved `4`
- confirmation unresolved `1`
- holdout false
- production action false

Outcomes summary SHA256: `024db2439bc6985e5f7d2a44aa7a549200a15f131287fc6ac60f13c017b00ac9`
Evidence tracker SHA256: `0b3aa0afd409937ff6d35a7b5edb3757d74e6793c8def46e05099e4c2a3efc5c`
Portfolio-risk report SHA256: `85b3fee793a997b93198d527577ca144075b39286c0aa5834182cc25f7b1f81e`

## Confirmation sample

- discovery primary families `44`
- confirmation primary families `5`
- confirmation resolved `4`
- confirmation unresolved `1`
- current unresolved confirmation family: `NEARUSDT LONG`, entry `2026-09-17T00:15:00Z`
- previous four confirmation families remain resolved STOP outcomes
- chronology/governance invariants PASS

## Path quality / failure-mode diagnostics

Accepted descriptive baseline at 48 resolved families:

- STOP `31`
- TIME_EXIT `17`
- median MFE approximately `0.698R`
- families reaching `>=1R` MFE: `13/48`
- families reaching `>=2R` MFE: `2/48`
- families reaching `>=3R` MFE: `0/48`
- STOP before reaching `1R` MFE: `24`

These are diagnostic only and do not mutate frozen v2.2.

## Portfolio risk

- current open families `1` (`NEARUSDT LONG`)
- observed max concurrent all `8`
- observed max concurrent SHORT `8`
- largest correlated cohort `4`
- diagnostic only; no production cap selected or enforced

## Phase 11G closure state

Path A:

- resolved primary families `48/100`
- shortfall `52`
- evidence tier remains `30-49`: diagnostics only

At `50-99`, only hypotheses/ablation proposals become allowed. Frozen v2.2 remains unchanged.
Path B has not been selected. Phase 11G remains **ACTIVE**.

## Development pause / data-only automation

Approved development pause window:

- start `2026-09-17 09:00 Europe/Kyiv` = `2026-09-17T06:00:00Z`
- end `2026-09-19 10:00 Europe/Kyiv` = `2026-09-19T07:00:00Z`

Canonical bounded runner `scripts/phase11g_pause_runner.py` has been staged in the research container with pinned runtime/tool manifests.

Automation root:
`/data/research/phase11g/automation/pause_20260917_20260919`

Current runner state: `WAITING_FOR_NOT_BEFORE`.

Pause preflight against accepted `02:30Z` artifacts: **PASS**.

During the pause only causal M15 collection/resolution/evidence/diagnostics are allowed. No strategy development, holdout, Phase 12, production risk selection, Plugin cutover or trading action is authorized.

## Hardening / automation implemented before pause

- fail-closed Phase 11G guardrails and evidence-tier monitor;
- MFE/MAE and failure-mode diagnostics;
- data-quality watchdog;
- immutable outcome replay verifier;
- pause preflight verifier;
- strict causal runner utility;
- evidence-tier-gated hypothesis proposal generator;
- Plugin GET-only/OpenAPI surface guard;
- focused regression tests;
- lightweight research safety CI.

Research Safety CI and existing Research Guards both passed for the implementation package.

## Core specifications

- current checkpoint: `docs/checkpoints/2026-09-17_0230Z_PRE_PAUSE_AUTOMATION.md`
- data-only pause runbook: `docs/operations/PHASE_11G_DATA_ONLY_PAUSE_2026-09-17_TO_2026-09-19.md`
- resolver: `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`
- preregistration: `docs/research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`
- max-hold semantics: `docs/research/MAX_HOLD_CAUSAL_EVIDENCE_SEMANTICS.md`
- portfolio-risk contract: `docs/research/PORTFOLIO_RISK_RESEARCH_CONTRACT_V1.md`
- pipeline-v2 acceptance: `docs/research/PROSPECTIVE_PIPELINE_V2_ACCEPTANCE.md`
- Phase 11G closure criteria: `docs/research/PHASE_11G_CLOSURE_CRITERIA.md`
- recovery: `docs/operations/RESEARCH_RECOVERY_RUNBOOK.md`
- Plugin migration: `docs/plugin_migration/README.md`

## Next work order

1. Before `06:00Z`, continue only already-approved safe work and causal collection as needed.
2. At `06:00Z`, development enters DATA-ONLY pause; bounded pause runner begins causal collection automatically.
3. Any invariant failure stops advancement fail-closed.
4. At `50` resolved families, allow hypotheses/ablation proposals only; do not retune frozen v2.2.
5. At or after `2026-09-19T07:00:00Z`, produce the final pause-window control slice and resume-development work order.
