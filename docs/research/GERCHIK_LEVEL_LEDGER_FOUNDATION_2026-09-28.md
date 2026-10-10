# Gerchik level event ledger v0.1 — research-only foundation

Implementation: `scripts/research/gerchik_level_event_ledger_v0_1.py`; test specification: `tests/test_gerchik_level_event_ledger_v0_1.py`.

Seven type labels are supported as metadata. The ledger enforces exact tick-price identity, D1/W1 HIGH/LOW input restrictions, immutable primary type per price/timeframe, as-of formation visibility, event provenance and duplicate event rejection. **It does not detect, confirm, score or trade levels.** Every formation remains `CANDIDATE` pending separately validated detector and confirmation gates. No ATR used in level formation. Archived pivots are not ingested.

Test status: test file committed, but execution has **not been verified** in this turn. The isolated container could not resolve `raw.githubusercontent.com` to retrieve GitHub files; no claim of passing tests. Next: execute the checked-in test suite on an authorized non-production runner and inspect any failures before detector implementation. Preserve HP-OMEN exclusion and production isolation.

Important research caveat: current ledger identity is scoped to `(symbol, timeframe, tick_size, tick-price)`; cross-timeframe D1/W1 deduplication is not yet implemented. `formed_at` and evidence times are ISO timestamps passed by upstream; require a strict timestamp parser and independent detector evidence verification before promotion. Tick precision and symbol metadata must be sourced from the actual instrument, not inferred.
