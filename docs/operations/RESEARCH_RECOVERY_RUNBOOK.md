# K-Trader Research Recovery Runbook

Status: **ACTIVE OPERATIONS RUNBOOK**

## Goal

Recover the exact accepted research state after a chat/session/operator transition without guessing, replaying mutable assumptions or accidentally opening holdout/production paths.

## Canonical recovery order

1. **Repository identity**
   - repository: `kolemasakar/K-Trader`;
   - research branch: `research-strategy-benchmark-v1`;
   - verify branch is descendant of the recorded canonical main baseline;
   - require `behind_by=0` relative to the accepted research history unless a documented merge occurred;
   - never rebase or force-update accepted research history.

2. **Human-readable state**
   - read `docs/CURRENT_STATE.md`;
   - read `docs/checkpoints/README.md`;
   - open the current checkpoint referenced there.

3. **Machine-readable state**
   - load the latest accepted file under:
     `/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/`;
   - verify its source hashes before trusting counters.

4. **Production health**
   - query local `/health`;
   - require `mode=read_only` during Phase 11G;
   - verify `data_ready=true` or treat the runtime as degraded/blocking as documented;
   - do not convert scanner `DEGRADED` into an outage unless its known history-readiness meaning changed.

5. **Research invariants**
   - frozen harness hash must match the current checkpoint;
   - protocol hash must match;
   - `holdout_opened=false`;
   - `production_action=false`;
   - current resolver version must match the checkpoint;
   - accepted prior terminal outcomes must remain immutable.

6. **Evidence boundary**
   - load the latest `prospective_evidence_tracker` report;
   - preserve discovery/confirmation split;
   - confirmation boundary remains immutable unless a new preregistration version explicitly supersedes it;
   - pre-boundary families must never be counted as confirmatory evidence.

7. **Open-family state**
   - load latest `families.jsonl` from accepted resolver output;
   - identify unresolved primary families;
   - compute/verify causal max-hold boundaries;
   - never synthesize TIME_EXIT before required closed bars exist.

8. **Portfolio diagnostics**
   - load latest `prospective_portfolio_risk` report;
   - retain current open-family/same-side/correlation state as diagnostic context only;
   - no production cap is implied unless separately versioned and approved.

9. **Storage/operations**
   - verify root filesystem utilization;
   - disk-retention timer remains disabled unless an accepted policy change says otherwise;
   - destructive retention mode remains unauthorized.

10. **Next action**
    - only after all above checks pass, resume from the next causal closed-bar cutoff using the accepted prospective pipeline/resolver.

## Fail-closed conditions

Stop recovery and classify the session as `RECOVERY_CONSISTENCY_BLOCKER` if any of the following occur:

- repository checkpoint and runtime accepted state disagree materially;
- source hash mismatch for accepted state artifacts;
- harness/protocol hash mismatch;
- holdout unexpectedly opened;
- production action flag true;
- future/equal entry contaminates an as-of dataset;
- accepted terminal outcome changes without a versioned resolver acceptance;
- resolver output directory is ambiguous or marked invalid;
- an output path already exists where the pipeline expects an immutable new run.

## Recovery output

A successful recovery should state at minimum:

- branch HEAD and canonical merge-base;
- deployed production SHA;
- latest accepted cutoff;
- resolver version;
- unique/resolved/unresolved family counts;
- expectancy/wins/losses;
- confirmation sample counts;
- unresolved families and next causal boundaries;
- holdout/production invariants;
- current health and storage state;
- exact next work order.

## External strategy-discovery boundary

Broad adaptive strategy discovery belongs to `K_Investigation_Forecast`. Do not reopen or redesign that track from this runbook until the user explicitly reports positive results and requests reintegration.
