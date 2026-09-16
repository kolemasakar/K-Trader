# K-Trader New Chat Handoff — 2026-09-16 19:30Z

Status: **READY FOR CHAT TRANSITION**

## Read first

1. `docs/CURRENT_STATE.md`
2. `docs/checkpoints/2026-09-16_1930Z_PROJECT_SYNC.md`
3. this handoff
4. `docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1930Z.md`
5. deeper canonical specifications only as needed

## Repository

Research branch:

`research-strategy-benchmark-v1`

Canonical main baseline:

`4919fea4397d34898ddc7d4215ea898e6caea815`

## Production

Host:

`k-trader-prod-vnic`

Accepted deployed SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Invariant:

- health `ok`
- mode `read_only`
- `data_ready=true`
- provider `binance_usdm`
- scanner `DEGRADED` is the known fail-closed/history-readiness condition
- no trading action authorized

Sentinel Remote/SentinelX connectivity is operational after the recovered 2026-09-16 hub reconnect incident.

## Frozen research state

Candidate:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Protocol SHA256:

`ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

Do not change RR, 32-M15 max hold, filters, sides, risk gates or other frozen v2.2 parameters in place.

Holdout: `UNTOUCHED / NOT AUTHORIZED`.

Phase 11G: **ACTIVE**.

Phase 12: **NOT ACTIVE**.

## Latest accepted causal cutoff

`2026-09-16T19:30:00Z`

Pipeline v2 manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_pipeline_manifests/pipeline_v2_20260916T193000Z_execute.json`

SHA256:

`1ad3819eed6770c802a972b5c590cf7b3d2eff9426200c767738b89d027933ce`

State manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T193000Z.json`

SHA256:

`e3b97d383d8b23d9f1fdd5e6677c36325a6d414db1148f1d4eeb158a4ebeb801`

Accepted state:

- observations `61`
- unique primary families `47`
- resolved `47`
- unresolved `0`
- open `0`
- wins/losses `13/34`
- expectancy `-0.5989123384630131R`
- confirmation families `3`
- confirmation resolved `3`
- holdout false
- production action false
- provenance source verification `5/5 PASS`, `0` mismatches

## Ledger v1.2

Canonical ledger semantics:

`first valid event-key payload is immutable; later conflicting recomputations are audit-only.`

Current state at 19:30Z:

- schema `ktrader.candidate_v2_2.prospective_shadow.ledger.v1_2`
- first-seen immutable `true`
- deduplicated events `394`
- eligible observations `61`
- unique eligible primary families `47`
- raw duplicates `6587`
- conflicting duplicate occurrences `6587`
- conflicting event keys `393`
- event-set SHA256 `8d0801da0f03ca7d8f716782f57775c4cfa7993f2164efd94027734dda84e747`

Resolver v1.3 identity guards remain unchanged.

Do not use the obsolete standalone `/tmp/prospective_v2_2_outcome_resolver_offline_v1_3.py`. Use canonical staged runtime `/tmp/ktrader-runtime-v2/` and pipeline v2.

## Phase 11G closure

Path A:

- `47/100` resolved prospective primary families
- shortfall `53`

Path B has not been selected.

Therefore Phase 11G remains ACTIVE.

## Phase 10P Plugin migration

Preparation is active; cutover is not authorized.

Prepared artifacts include:

- `docs/plugin_migration/K_TRADER_SKILL_DRAFT.md`
- `docs/plugin_migration/INTEGRATION_CONTRACT_V1.md`
- `docs/plugin_migration/REGRESSION_SUITE.md`
- `docs/plugin_migration/PLUGIN_IMPLEMENTATION_BLUEPRINT_V1.md`
- `docs/plugin_migration/ACCOUNT_SURFACE_PRECHECK_2026-09-16.md`
- `docs/plugin_migration/MCP_TOOL_SURFACE_V1.md`

Target remains:

`K-Trader Plugin -> Skill + read-only App/Connector/MCP -> existing K-Trader backend`

Do not disable the current Custom GPT before replacement acceptance.

## External strategy discovery boundary

Broad strategy discovery/self-improving strategy research remains delegated to `K_Investigation_Forecast`.

Do not reopen it inside K-Trader until the user explicitly reports positive external results.

## Resume work order

1. Verify production health/read-only invariant and research branch/head.
2. Determine the latest fully closed M15 cutoff.
3. Resume causal pipeline v2 from the accepted prior outcomes below.
4. Preserve ledger v1.2 first-seen immutability and resolver v1.3 guards.
5. Preserve prereg boundary and discovery/confirmation separation.
6. Update diagnostics/checkpoint only on material sample/governance change or explicit project synchronization.
7. Do not open holdout, activate Phase 12, retune v2.2 or deploy production without explicit authorization.

Resume values immediately after this handoff:

```text
RESUME_FROM=2026-09-16T19:45:00Z
PRIOR_OUTCOMES=/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T193000Z
```
