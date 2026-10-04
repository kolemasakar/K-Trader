# Strategy restoration and year-cohort preflight — 2026-10-04
Status: DATA INTEGRITY VERIFIED / WEEKLY DERIVATION IMPLEMENTED / STRATEGY FREEZE BLOCKED.

## Completed evidence
- Verified current research HEAD fe5ec24fc1fcbe44e06ebfd13fdf71ad646a3906 and recovered server-local strategy approval, exploratory assumptions and S6 source.
- Identified and documented S2–S5 ID mismatch and superseded ATR-derived S6 levels; no silent strategy substitution.
- Implemented read-only streaming cohort audit with source checksums, count/chronology/OHLC and weekly-boundary checks. Added exact Decimal weekly aggregation, full-week causal availability and source lineage.
- Executed the exact prepared audit source through the existing bounded read-only Docker route on k-trader-prod-vnic: 42/42 hashes matched, 447489 bars, zero gaps/invalid OHLC, 7 partial final W1 bars. Derived 51 completed W1 bars per symbol in memory. No archive writes or outcome computation.
- Source report: docs/research/GERCHIK_COHORT_READINESS_2026-10-04.json.
- Defined common preparation requirements in GERCHIK_BACKTEST_PROTOCOL_V0_1_2026-10-04.md. This is not a fully frozen executable strategy protocol.
- 11 new audit/weekly cases plus 11 existing ATR geometry cases: 22/22 local unittest passed. ResourceWarning treated as an error. Remote full CI for this change requires separate confirmation.

## Limits
No new strategy backtest, level-strength validation or profitability claim. Production code/config, archived results, first-seen ledger and K_AI were not changed. Existing year archive is retrospective and inspected earlier; independent holdout provenance remains unverified. Original source W1 files remain unchanged and must not be used without excluding partial weeks.

## Next required gate
Restore one authoritative executable S1–S6 mapping and precise model parameters; replace obsolete level upstream with reviewed causal Gerchik ledger; freeze costs and untouched-control provenance. Continue through 1R -> 3R -> analysis -> Level Strength v2 -> independent validation. FREE_ONLY and no HP-OMEN persist.
