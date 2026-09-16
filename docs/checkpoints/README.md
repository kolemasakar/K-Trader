# K-Trader Checkpoints

This directory contains accepted snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-16_2015Z_PROSPECTIVE_MATERIAL_UPDATE.md`

Current accepted state:

- Phase 11G **ACTIVE**; Phase 12 **FUTURE / NOT ACTIVE**;
- production SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`, mode `read_only`; no trading action authorized;
- frozen candidate `candidate_rule_set_v2_2`, harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- resolver v1.3; ledger v1.2 with immutable first-seen event payload;
- holdout untouched/unauthorized;
- latest accepted cutoff `2026-09-16T20:15:00Z`;
- prospective state `62` eligible observations / `48` primary families / `48` resolved / `0` unresolved;
- wins/losses `13/35`, expectancy `-0.6088593884101355R`;
- confirmation sample `4/4 resolved`, still underpowered;
- current open primary families `0`;
- Phase 11G Path A `48/100`, shortfall `52`; Path B not selected.

## Latest accepted research checkpoints

- `2026-09-16_2015Z_PROSPECTIVE_MATERIAL_UPDATE.md` — material confirmation-family resolution and accepted 20:15Z state;
- `2026-09-16_1930Z_PROJECT_SYNC.md` — prior authoritative project synchronization;
- `2026-09-16_1900Z_LEDGER_V1_2_RECOVERY.md` — ledger-v1.2 causality recovery;
- `2026-09-16_1830Z_PROSPECTIVE_MATERIAL_UPDATE.md` — prior material prospective update.

## Related documents

- current state: `../CURRENT_STATE.md`;
- current new-chat handoff: `../operations/K_TRADER_NEW_CHAT_HANDOFF_2026-09-16_1930Z.md`;
- current Phase 11G closure audit: `../research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1930Z.md`;
- ledger v1.2 acceptance: `../research/PROSPECTIVE_LEDGER_V1_2_ACCEPTANCE_2026-09-16.md`;
- resolver v1.3: `../research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`;
- preregistration: `../research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`;
- pipeline v2 acceptance: `../research/PROSPECTIVE_PIPELINE_V2_ACCEPTANCE.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
