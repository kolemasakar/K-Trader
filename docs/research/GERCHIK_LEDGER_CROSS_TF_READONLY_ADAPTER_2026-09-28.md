# Read-only ledger to cross-TF luft evidence adapter

Implemented `scripts/research/gerchik_ledger_cross_tf_evidence_v0_1.py` and five regression cases in `tests/test_gerchik_ledger_cross_tf_evidence_v0_1.py`.

The adapter reads visible canonical `LevelLedger` levels, joins source review metadata by `formation_event_id`, requires symbol/timeframe/event identity and causal review timestamp, and passes immutable views to `confirm_pairs`. Overlapping D1/W1 candles are accepted as reinforcing level evidence within symmetric inclusive upstream luft. Cross-TF confirmation is an evidence view only: it does not change either level's primary type, state, or evidence ledger. Confirmation time is the later of formation/review availability; source prices/types are preserved.

**Security/semantic limitation:** `reviewed_sources` is caller-supplied; the adapter validates its shape and chronology but does not independently authenticate approval. Wire it only to verified review records from the existing structural review gate before promoting any trust. The adapter does not yet persist cross-TF evidence in canonical ledger because cross-price identity, repeated evidence deduplication and global primary-type policy require an explicit integration contract. No live trading.

**Verification pending:** new regression tests have been committed but not executed against the exact GitHub checkout; the isolated environment cannot resolve github.com. Previous isolated 25/25 result predates this adapter and is not evidence of its correctness.
