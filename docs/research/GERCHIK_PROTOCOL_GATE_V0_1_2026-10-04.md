# Gerchik protocol declaration gate v0.1 — 2026-10-04

## Result

A read-only machine-checkable preparation contract is implemented in `scripts/research/gerchik_protocol_gate_v0_1.py`. The populated candidate and deterministic report are `GERCHIK_PROTOCOL_CANDIDATE_V0_1_2026-10-04.json` and `GERCHIK_PROTOCOL_GATE_REPORT_2026-10-04.json`.

Candidate status: BLOCKED. Null fields are intentionally unresolved, not zero-cost or default assumptions. This is missing preparation information, not a permission request. Known cohort identities/boundaries/inventory hash and owner strategy families are populated. All six current executable specifications, parameter migration, level ledger/precision semantics, eligible study window, execution profile, cost provenance and bounded resource/output declarations still require concrete work before the run specification can be frozen. The input inventory hash identifies the exact repository JSON report bytes, not an invented replacement source-manifest hash.

## Guarantees and scope

- Exactly one each S1–S6 and their restored family mapping; S3 stop beyond level.
- Explicit no-ATR level geometry, canonical D1 ATR5 v2 diagnostics, completed UTC W1 policy and specification/ledger fingerprints.
- Study bounds within the declared cohort with an explicit warmup policy. No outcome-selected automatic split.
- Explicit execution interval/horizon, fees, adverse fill cost, signed funding estimate, cost-source category, overlap/calendar policies and read-only/free resource declaration.
- Target stages are 1R and 3R. A 3R declaration requires a completed 1R report hash and the identical comparison digest. Comparison digest excludes only target_r and prior_1r; code, inputs, specs, costs, policies and extensions remain included.
- Exploratory baseline is permitted without claiming untouched control. Independent-validation declarations require a reservation hash/provenance and previously_inspected=false. This records a declaration, not independent verification of a human claim.
- Status is DECLARATIONS_COMPLETE, never APPROVED or READY. The tool does not verify artifact existence/hash correspondence, executable semantics, historical cost adequacy, physical read-only isolation or control reservation truth. It does not run market simulations. Independent artifact checking remains necessary before scientific claims.

## Usage and evidence

`python scripts/research/gerchik_protocol_gate_v0_1.py docs/research/GERCHIK_PROTOCOL_CANDIDATE_V0_1_2026-10-04.json`

JSON is printed to stdout; exit 1 means incomplete declarations, exit 0 means declaration completeness only. CLI never edits the input/archive.

12 new meaningful cases cover wrong IDs, S3 stops, unresolved predicates, ATR geometry, partial-week policy, missing/nonfinite costs, boolean horizons, out-of-cohort windows, inspected control, 1R/3R linkage, and deterministic hashes. Combined local ATR5/cohort/execution/protocol suite: 47 passed on Python 3.12.

Execution simulator commit 629bda37 CI run 37199505349 completed SUCCESS. CI for this gate change is checked separately after publication. Research branch/PR #94 stays unmerged; no production change or market profitability evidence.
