# Phase 11G independent forward-only epoch — activation checkpoint

**Recorded:** 2026-09-25 approximately 11:19 UTC  
**State:** `ACTIVATED / WAITING_FOR_FIRST_FUTURE_CUTOFF`  
**Classification:** `FORWARD_FIRST_SEEN_DATA_ONLY`  
**HP-OMEN:** STRICTLY PROHIBITED.

## Authorized future epoch

The owner approved starting the separate future Phase 11G epoch (`go`). The actual server-side immutable preregistration occurred **2026-09-25T11:11:07.910185Z**, before the first future cutoff:

- epoch ID: `epoch_20260925T114500Z_v1`;
- first cutoff: **2026-09-25T11:45:00Z**;
- last inclusive cutoff of the bounded pilot: **2026-09-26T11:30:00Z**;
- first-seen capture time: cutoff + 180 seconds; capture expires at cutoff + 300 seconds;
- first 19 contemporaneous recorded Binance USD-M liquidity ranks, with no substitution;
- strictly closed `1d:20 / 4h:80 / 1h:300 / 15m:400 / 5m:20` history;
- no candidate strategy execution, no family outcome counting, no historical/retrospective bridge.

Canonical preregistration and immutable source hashes: [2026-09-25 11:45Z preregistration](2026-09-25_PHASE11G_NEW_EPOCH_1145Z_PREREG.md).

## Approved operational activation

SentinelX's restricted sudo context explicitly denied a direct detached `docker exec -d` request. No unreviewed workaround, extra SentinelX privilege or unrelated host was used.

Instead, the existing approved K-Trader **GitHub self-hosted production runner** executed the narrowly scoped one-shot job after a reviewed PR:

- source PR: [#76](https://github.com/kolemasakar/K-Trader/pull/76);
- activation squash SHA: `2e2dced610534bb2c3864bd243659db6c2e46fc6`;
- GitHub Actions: [isolated epoch activation #36128619406](https://github.com/kolemasakar/K-Trader/actions/runs/36128619406) — `SUCCESS`;
- [Research Guards #36128619390](https://github.com/kolemasakar/K-Trader/actions/runs/36128619390) — `SUCCESS`;
- [Research Safety CI #36128619317](https://github.com/kolemasakar/K-Trader/actions/runs/36128619317) — `SUCCESS`.

The workflow first re-verified `read_only` health, the original accepted state and script/registration SHA pins. It then activated **only** the approved isolated Python capture, not any trading/replay command.

## Observed server state at 11:18:59Z

```text
host=k-trader-prod-vnic
service_health=ok
service_mode=read_only
provider=binance_usdm
isolated_runner_lock=PRESENT
runner_log=WAITING 2026-09-25T11:45:00Z
legacy_anchor_sha256_match=true
legacy_ledger_sha256_match=true
completed_new_cutoff_manifests=0
```

The bounded runner is started and waiting. **This checkpoint is not evidence that the first 11:45Z data capture has succeeded**; that can only be verified after the 180-second close-settlement interval and immutable output/hash audit.

The runner does not survive a production-container restart automatically; interruption must be explicitly reported, never backfilled or hidden. Completed cutoff directories are immutable and any partial/collision stops the runner fail-closed.

## Governance and next gate

- old accepted Path A `54/100` resolved families remains unchanged;
- original candidate `candidate_rule_set_v2_2`, harness/protocol hashes, resolver v1.3 and ledger v1.2 are unchanged;
- old 2026-09-18 06:30Z partial cycle remains untouched;
- no new prospective families are admitted by this data-only recorder;
- first verification gate: after **2026-09-25T11:48:00Z**, inspect first cutoff manifest, SHA-256 of its raw history files, source universe digest, slot failures/ready counts and actual first-seen timestamps;
- then perform isolated full frozen-v2.2 strategy/resolver compatibility validation as a distinct step; do **not** merge the two first-seen cohorts automatically;
- HP-OMEN/K_AI-backed sources, holdout, Phase 12 and trade execution remain prohibited.
