# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md`

Current accepted state at the checkpoint:

- Phase 10 Custom GPT product acceptance: COMPLETE for the single-provider read-only v1 scope;
- canonical code/runtime SHA before this docs-only checkpoint: `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- PR #33 side-to-regime contract fix: merged and historical-replay validated;
- post-merge Tests `34177001398`: PASS;
- post-merge CI `34177001482`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- Deploy Production #9 run `34177978988`: SUCCESS;
- production image: `k-trader:7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- production container healthy; provider REST/WS, MTF API and Phase 10 Action acceptance PASS;
- Phase 11F production research capture remains active, immutable and provider-coherent;
- strict Phase 11G context policy remains `max_context_age_seconds=300` using newest snapshot at/before each cutoff;
- canonical SUIUSDT and XRPUSDT chains remain COMPLETE / VERIFIED / CATALOGUED;
- dataset catalogue entry count remains `2`;
- catalogue SHA remains `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- corrected Window #4 replay: 7596 candidate decisions, 7161 HTF rejects, 435 HTF-aligned candidates, zero tradable decisions;
- conditional aligned audit: all 435 were `LONG -> BULLISH`;
- sequential downstream funnel: `435 -> 202 -> 168 -> 142 -> 0` at HTF -> level -> geometry -> ATR -> RR;
- all 142 final survivors were blocked only by `RR_BELOW_3`;
- current work direction: read-only RR-geometry audit before any threshold change, materialization or catalogue expansion.

Historical checkpoints:

- `2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md` records the accepted two-chain catalogue state before corrected historical discovery;
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
