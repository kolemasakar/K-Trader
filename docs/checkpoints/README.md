# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-07_PROJECT_STATE_PHASE11_HANDOFF.md`

Current accepted state at the checkpoint:

- Phase 10 Custom GPT product acceptance: COMPLETE for the single-provider read-only v1 scope;
- canonical repository baseline before the handoff checkpoint: `main` SHA `4df64eaa4d13def00f3d07c7c755936805a57bea`;
- deployed production runtime remains SHA `470531500566b1dc7b6e5d7296caf57403aacaf4` because the Phase 10 closure merge was documentation-only;
- post-merge CI #112 and Tests #41: SUCCESS;
- branch protection restored to one required approval;
- current work direction: Phase 11 operational/research accumulation through the already-implemented 11A–11G foundations.

## Related canonical documents

- Phase 10 acceptance: `../PHASE_10_PRODUCT_ACCEPTANCE.md`;
- roadmap: `../../ROADMAP.md`;
- project overview: `../../README.md`;
- GPT Builder acceptance checklist: `../../custom_gpt/BUILDER_CHECKLIST.md`;
- dataset catalogue contract: `../DATASET_CATALOGUE_SPEC.md`;
- historical replay contract: `../HISTORICAL_REPLAY_SPEC.md`.

A checkpoint does not replace those specifications. It records which accepted versions/state should be used when work resumes.
