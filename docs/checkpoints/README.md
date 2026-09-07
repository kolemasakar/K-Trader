# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-07_PHASE11G_FIRST_PRODUCTION_CHAIN.md`

Current accepted state at the checkpoint:

- Phase 10 Custom GPT product acceptance: COMPLETE for the single-provider read-only v1 scope;
- repository/runtime code baseline used for the accepted Phase 11G production chain: `main` / deployed SHA `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`;
- Deploy Production #7 run `34139956047`: SUCCESS;
- main CI `34139445282`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- main Tests `34139445313`: PASS;
- Phase 11F production research capture verified healthy and provider-coherent;
- first real provider-recorded Phase 11G chain (`binance_usdm` / `SUIUSDT`) is COMPLETE / VERIFIED / CATALOGUED;
- catalogue SHA: `749c3aa20d02788b1c75b48e3325d854d7182f5b0729fea39dcf888af367b864`;
- final catalogue reload with `verify_artifacts=True`: PASS;
- current work direction: continue Phase 11 operational/research accumulation and expand the catalogue with additional coherent provider-recorded studies.

The older `2026-09-07_PROJECT_STATE_PHASE11_HANDOFF.md` remains a historical transition checkpoint and must not be used as the current repository/runtime identity after the accepted Phase 11G production materialization.

## Related canonical documents

- Phase 11G checkpoint: `../PHASE_11G_CHECKPOINT.md`;
- dataset catalogue contract: `../DATASET_CATALOGUE_SPEC.md`;
- historical replay contract: `../HISTORICAL_REPLAY_SPEC.md`;
- current project state: `../CURRENT_STATE.md`;
- Phase 10 acceptance: `../PHASE_10_PRODUCT_ACCEPTANCE.md`;
- roadmap: `../../ROADMAP.md`;
- project overview: `../../README.md`;
- GPT Builder acceptance checklist: `../../custom_gpt/BUILDER_CHECKLIST.md`.

A checkpoint does not replace those specifications. It records which accepted versions/state should be used when work resumes.
