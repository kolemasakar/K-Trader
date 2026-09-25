# K-Trader Checkpoints

This directory contains accepted snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint (2026-09-25, pre-transition-generator)

`2026-09-25_CHAT_TRANSITION_HISTORY_FIRST.md`

History-first research priority, independent OCI-only prospective collector + non-notifying monitor, final verified runtime at approximately 2026-09-25T15:23Z, post-activation hourly PASS reports at 14:06Z and 15:06Z, Actions quota/HP-OMEN restrictions, and next H0/H1 gates are recorded here. The owner will supply a separate generator for the new-chat bootstrap. Use the newly generated handoff only after it is actually created; do not imply one exists yet.

## Historical 2026-09-17 checkpoint (superseded as current)

`2026-09-17_0230Z_PRE_PAUSE_AUTOMATION.md`

Current accepted state:

- Phase 11G **ACTIVE**; Phase 12 **FUTURE / NOT ACTIVE**;
- production SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`, mode `read_only`; no trading action authorized;
- frozen candidate `candidate_rule_set_v2_2`, harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- resolver v1.3; ledger v1.2 with immutable first-seen event payload;
- holdout untouched/unauthorized;
- latest accepted cutoff `2026-09-17T02:30:00Z`;
- prospective state `63` eligible observations / `49` primary families / `48` resolved / `1` unresolved;
- wins/losses `13/35`, expectancy `-0.6088593884101355R`;
- confirmation sample `5`, of which `4` resolved and `1` unresolved;
- current open primary families `1` (`NEARUSDT LONG`);
- Phase 11G Path A `48/100`, shortfall `52`;
- bounded data-only pause runner staged and waiting for `2026-09-17T06:00:00Z`;
- pause-window end `2026-09-19T07:00:00Z`.

## Latest accepted research checkpoints

- `2026-09-17_0230Z_PRE_PAUSE_AUTOMATION.md` — pre-pause automation/hardening acceptance and accepted 02:30Z state;
- `2026-09-16_2015Z_PROSPECTIVE_MATERIAL_UPDATE.md` — material confirmation-family resolution and accepted 20:15Z state;
- `2026-09-16_1930Z_PROJECT_SYNC.md` — prior authoritative project synchronization;
- `2026-09-16_1900Z_LEDGER_V1_2_RECOVERY.md` — ledger-v1.2 causality recovery.

## Related documents

- current state: `../CURRENT_STATE.md`;
- data-only pause runbook: `../operations/PHASE_11G_DATA_ONLY_PAUSE_2026-09-17_TO_2026-09-19.md`;
- current new-chat handoff: `../operations/K_TRADER_NEW_CHAT_HANDOFF_2026-09-16_1930Z.md`;
- current Phase 11G closure audit: `../research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1930Z.md`;
- ledger v1.2 acceptance: `../research/PROSPECTIVE_LEDGER_V1_2_ACCEPTANCE_2026-09-16.md`;
- resolver v1.3: `../research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`;
- preregistration: `../research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`;
- pipeline v2 acceptance: `../research/PROSPECTIVE_PIPELINE_V2_ACCEPTANCE.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
