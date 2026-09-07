# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md`

Current accepted state at the checkpoint:

- Phase 10 Custom GPT product acceptance: COMPLETE for the single-provider read-only v1 scope;
- repository HEAD before this docs-only checkpoint: `40cee9b17aa74ad45be1894d566ddb79f8a81ef4`;
- deployed production runtime SHA: `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`;
- Deploy Production #7 run `34139956047`: SUCCESS;
- post-PR-#30 main Tests `34144783877`: PASS;
- post-PR-#30 main CI `34144783943`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- Phase 11F production research capture remains active, immutable and provider-coherent;
- strict Phase 11G context policy remains `max_context_age_seconds=300`;
- first canonical production chain `binance_usdm` / `SUIUSDT`: COMPLETE / VERIFIED / CATALOGUED;
- second canonical production chain `binance_usdm` / `XRPUSDT`: COMPLETE / VERIFIED / CATALOGUED;
- current dataset catalogue entry count: `2`;
- current catalogue SHA: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- final catalogue reload with `verify_artifacts=True`: PASS;
- current work direction: read-only batch signal/outcome discovery across eligible symbols/windows, then selective canonical materialization and catalogue expansion.

Historical checkpoints:

- `2026-09-07_PHASE11G_FIRST_PRODUCTION_CHAIN.md` records the first SUI-only catalogue state and its historical one-entry catalogue SHA;
- `2026-09-07_PROJECT_STATE_PHASE11_HANDOFF.md` is an earlier transition snapshot and must not be used as the current repository/runtime/research identity.

## Related canonical documents

- Phase 11G checkpoint: `../PHASE_11G_CHECKPOINT.md`;
- dataset catalogue contract: `../DATASET_CATALOGUE_SPEC.md`;
- historical replay contract: `../HISTORICAL_REPLAY_SPEC.md`;
- current project state: `../CURRENT_STATE.md`;
- deployment state: `../DEPLOYMENT.md`;
- Phase 10 acceptance: `../PHASE_10_PRODUCT_ACCEPTANCE.md`;
- roadmap: `../../ROADMAP.md`;
- project overview: `../../README.md`;
- GPT Builder acceptance checklist: `../../custom_gpt/BUILDER_CHECKLIST.md`.

A checkpoint does not replace those specifications. It records which accepted versions/state should be used when work resumes.
