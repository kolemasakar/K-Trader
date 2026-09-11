# Phase 11G Checkpoint — Prospective-Control Production Deployment

Date: 2026-09-11

Status: **DEPLOYED / ACCEPTED / CONTINUOUS DISCOVERY ACTIVE / PHASE 12 INACTIVE**

## Purpose

This checkpoint records production activation of the repository-owned Phase 11G prospective-control utility accepted in PR #48. The deployment changes operational tooling availability only; it does not change trading semantics.

## Canonical repository and runtime identity

- canonical repository: `kolemasakar/K-Trader`;
- deployed application/runtime SHA: `a73ba261a3ca97d2df3deac20b1459b7b4c38fff`;
- PR #48 merge commit verification: GitHub verified;
- deployed SHA: `a73ba261a3ca97d2df3deac20b1459b7b4c38fff`;
- deployed image: `k-trader:a73ba261a3ca97d2df3deac20b1459b7b4c38fff`;
- production host: Oracle Cloud ARM64 / Ubuntu 24.04;
- provider: `binance_usdm`;
- API mode: `read_only`.

Repository `main` may advance beyond the deployed application SHA through documentation-only synchronization commits. Such docs-only drift does not imply runtime drift and does not require redeployment.

## Deployment evidence

Approved GitHub Actions deployment run:

`34612617730`

The deployment path checked out the exact approved canonical SHA and executed the unchanged canonical `scripts/deploy.sh`. Accepted gates:

- exact SHA identity: PASS;
- ARM64 architecture: PASS;
- image build/start: PASS;
- localhost health: PASS;
- Phase 9 market/runtime acceptance: PASS;
- public HTTPS / Phase 10 Action acceptance: PASS;
- final container health: PASS;
- `/opt/k-trader/DEPLOYED_SHA`: exact approved SHA;
- deployed prospective-control CLI packaging check: PASS.

The temporary trigger workflow used only to initiate this approved deployment was removed immediately after success. Canonical `.github/workflows/deploy.yml` remains unchanged and `workflow_dispatch` only.

## Runtime observation after promotion

```text
status=ok
mode=read_only
data_ready=true
scanner_status=DEGRADED
provider_id=binance_usdm
container=healthy
```

`DEGRADED` retains the accepted semantics of partial young-contract ineligibility; it is not by itself a service-health failure.

## Prospective-control availability

The production image now contains:

- `src/ktrader/replay/prospective.py`;
- `scripts/run_prospective_control.py`;
- deterministic sharding/resume/merge;
- explicit UTC-midnight fail-closed accounting;
- self-contained flattened audit records including `canonical_symbol`.

## Trading invariants unchanged

No deployment change was made to:

- FAST setup interval `M5`;
- TTL `60m = 12 x M5`;
- exact `60m` valid / `>60m` expired;
- `RR >= 3`;
- ATR-used threshold;
- HTF alignment;
- STRONG/confirmed primary-level rule;
- structural stop/target geometry;
- Setup Score / Grade semantics;
- history/freshness rules;
- outcome or probability policy;
- dataset-catalogue materialization rules.

INTRADAY/M15 and MEDIUM/H1 remain research-only. Phase 12 remains inactive.

## Next work

1. keep provider-recorded Binance USD-M capture active;
2. use canonical prospective-control tooling for subsequent long-window controls;
3. continue natural FAST/M5 discovery under unchanged hard gates;
4. materialize a new Phase 11G chain only after a natural LONG/SHORT survives every hard gate with exact provenance;
5. evaluate any outcome only from subsequent real provider bars;
6. do not activate M15/H1 production profiles or Phase 12 without a separate explicit approval gate.
