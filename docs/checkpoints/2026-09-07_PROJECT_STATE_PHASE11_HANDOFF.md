# K-Trader Project State — Phase 11 Handoff

Date: 2026-09-07

Status: CHECKPOINT / READY FOR NEW-CHAT TRANSITION.

## Purpose

This checkpoint records the exact accepted project state after Phase 10 Custom GPT product closure and before continuing Phase 11 operational/research work in a new chat.

It is a recovery aid, not a change to Trading Engine behavior.

## Canonical repository state

- repository: `kolemasakar/K-Trader`;
- default branch: `main`;
- accepted repository HEAD before this checkpoint branch: `4df64eaa4d13def00f3d07c7c755936805a57bea`;
- PR #21 `Close Phase 10 product acceptance and synchronize documentation`: squash-merged;
- PR #21 merge SHA: `4df64eaa4d13def00f3d07c7c755936805a57bea`;
- post-merge CI run #112 / `34118896863`: SUCCESS;
- post-merge Tests run #41 / `34118896883`: SUCCESS;
- CI jobs on the accepted merge: pytest PASS, Docker amd64 PASS, Docker arm64 PASS.

## Branch protection

The `main` ruleset was restored after the Phase 10 closure merge:

- required approving reviews: `1`;
- stale approvals dismissed on push;
- squash is the only allowed merge method;
- required status check: `pytest`;
- deletion protection, non-fast-forward protection and linear history are active;
- no bypass actors; current user cannot bypass.

Do not lower the approval count except as an explicit temporary user-approved merge procedure, and restore it immediately afterward.

## Production runtime identity

The latest accepted runtime deployment remains the Phase 10 production build, because PR #21 was documentation-only and was not a runtime deployment:

- production origin: `https://ktrader-api.duckdns.org`;
- deployed runtime SHA: `470531500566b1dc7b6e5d7296caf57403aacaf4`;
- Deploy Production #6 run: `34111173939` — SUCCESS;
- production provider: `binance_usdm`;
- provider REST/WebSocket acceptance: PASS;
- scanner acceptance during final deployment: `DEGRADED`, `data_ready=true`, 17 ready / 3 failed;
- MTF API acceptance: PASS;
- Docker container: healthy;
- HTTPS/TLS: PASS;
- Action authentication: enabled;
- Phase 10 Action live acceptance: PASS.

Repository HEAD being newer than deployed runtime SHA is intentional at this checkpoint: the difference is documentation-only Phase 10 closure work.

## Phase 10 product acceptance

Phase 10 is COMPLETE for the current single-provider, read-only v1 product boundary.

Accepted GPT Builder state:

- existing GPT: `K_Trader`;
- active instructions: `custom_gpt/SYSTEM_K_TRADER_v1_2_COMPACT.md`;
- canonical description:
  `Професійний трейдер-аналітик. Відбір і ранжування торгових можливостей за підтвердженими ринковими даними та правилами K-Trader; без виконання угод.`
- canonical Action schema: `custom_gpt/openapi.yaml`;
- one-click schema URL: `https://ktrader-api.duckdns.org/action-openapi.yaml`;
- privacy URL: `https://ktrader-api.duckdns.org/privacy`;
- authentication: API key / Bearer;
- secret value is intentionally not recorded in repository documentation;
- selected distribution mode: link access (`Усі, хто має посилання`), updated after acceptance.

All eight Action operations passed Preview:

- `getHealth`;
- `getScannerStatus`;
- `listUniverse`;
- `getMarketSnapshot`;
- `getCandles`;
- `getAnalysis`;
- `listCandidates`;
- `listSignals`.

Behavioral acceptance passed:

- canonical mode when `data_ready=true`;
- zero A/A+ signals are not converted into invented signals;
- canonical `NO_TRADE` is preserved;
- Entry/SL/TP are never invented;
- Setup Score remains deterministic and is not statistical probability;
- `estimated_probability` stays null/N/A until calibrated;
- fail-closed `WATCHLIST ONLY` fallback works when canonical analysis/OHLCV is unavailable;
- strict fallback source order checked direct Binance USD-M REST then Bybit Linear REST;
- stale/partial external responses were rejected as current trading evidence;
- provider series were not mixed;
- no aggregator was used when direct sources had been checked.

Provider ambiguity exception:

- live same-symbol multi-provider HTTP 409 was not reproducible in the current single-provider production runtime;
- backend 409 contract is regression-covered;
- GPT-side 409 retry is NOT counted as Preview PASS;
- live GPT-side 409 retry is a blocking acceptance gate before Phase 12 or any deployment enables simultaneous multi-provider exposure.

Formal Phase 10 evidence: `docs/PHASE_10_PRODUCT_ACCEPTANCE.md`.

## Current Phase 11 state

Repository-side implementation is already verified through Phase 11G:

- 11A — replay/regression hardening;
- 11B — provider history and signal outcomes;
- 11C — deep history / MTF replay bundles;
- 11D — full-engine historical replay / outcome studies;
- 11E — historical universe capture / cohorts;
- 11F — operations hardening / continuous research capture;
- 11G — deterministic dataset catalogue foundation.

Current Phase 11 work is operational/research accumulation rather than a new engine rewrite.

Next work:

- accumulate real provider-recorded production universe/research artifacts;
- populate and verify `ktrader.dataset_catalogue.v1` with real coherent chains;
- exercise target-host backup/restore, restart/recovery, disk-guard and stale-data watchdog behavior over longer periods;
- later define an explicitly approved statistical calibration methodology with time-separated out-of-sample validation;
- keep Setup Score non-probabilistic and `estimated_probability` null/N/A until that calibration work is formally accepted.

## Canonical safety/product rules to preserve

- read-only v1: no order placement, account access or exchange credentials;
- never mix OHLCV series across providers;
- stale, gapped, insufficient or ambiguous canonical context fails closed;
- `RR < 3` rejects;
- ATR usage `>80%` rejects; `40–80%` acceptable; `<40%` strong reserve;
- only A/A+ is tradable; B/C is `NO_TRADE`;
- Entry/SL/TP come only from canonical engine output;
- fallback mode is `WATCHLIST ONLY` and cannot invent canonical trading fields.

## Open governance / cleanup items

Issue #22 remains open and is not a Phase 10 blocker:

- repository description still contains `probability-based setup scoring`, which conflicts with the canonical deterministic/non-probabilistic Setup Score rule;
- two tests use `phase12_*` names even though Roadmap Phase 12 means multi-provider expansion.

The connected GitHub API currently reports repository visibility as public (`private=false`), while an earlier project baseline described the repository as private. This checkpoint records the discrepancy only. Do not change repository visibility without explicit user authorization.

## Recovery order in a new chat

When restoring work, use this authority order:

1. this checkpoint for the transition snapshot;
2. `docs/PHASE_10_PRODUCT_ACCEPTANCE.md` for Phase 10 product acceptance details;
3. `ROADMAP.md` for phase boundaries and next work;
4. `README.md` for current architecture/operational overview;
5. `custom_gpt/BUILDER_CHECKLIST.md` and `custom_gpt/SYSTEM_K_TRADER_v1_2_COMPACT.md` for GPT behavior;
6. `docs/DATASET_CATALOGUE_SPEC.md`, `docs/HISTORICAL_REPLAY_SPEC.md` and Phase 11 implementation for research operations.

Before making changes in the new chat:

- confirm `main` HEAD;
- confirm ruleset approval count is back to `1`;
- distinguish repository HEAD from deployed runtime SHA;
- do not request or expose the Action secret;
- do not reopen Phase 10 unless a regression is actually found;
- treat provider-ambiguity GPT Preview as deferred blocking work for multi-provider activation, not as an already-passed live gate.
