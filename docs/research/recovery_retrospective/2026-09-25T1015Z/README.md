# Phase 11G isolated retrospective gap audit — 2026-09-25T10:15Z

**Classification:** `RECOVERY_RETROSPECTIVE` — NOT prospective evidence  
**State:** COVERAGE AUDIT COMPLETE / PROSPECTIVE CONTINUATION NOT AUTHORIZED  
**Host:** independent K-Trader Oracle Cloud server only; HP-OMEN and all HP-OMEN-backed routes prohibited.

## Reproducibility

- **Historical interval:** 2026-09-18 06:30 UTC through 2026-09-25 10:15 UTC inclusive, every closed M15 boundary.
- **Panel:** first 19 instruments in the canonical archived Binance USD-M liquidity order at each cutoff. Never substitute lower-ranked instruments.
- **Universe selection:** latest canonical verified recorded snapshot captured at or before the cutoff; at most 300 seconds old.
- **Candle requirements:** 1d:20, 4h:80, 1h:300, 15m:400, 5m:20; exact close, full historical depth, sequence continuity and no future/equal-bar contamination.
- **Ingestion-timing check:** all required rows' *current database* `ingested_at_ms` values no later than cutoff plus the original 180-second settlement delay. This is a separate diagnostic, **not proof** that history was immutable or operationally available at the past cutoff.
- **Auditor:** `research/strategy_benchmark_v1/audit_retrospective_gap_v1.py`. Offline built-in self-tests: 11 checks PASS; causal last-closed-bar logic explicitly handles in-progress H1/4H/D1 bars. Separate regression tests live beside the auditor.
- **Frozen server-only SQLite copy:** `/data/research/phase11g/recovery_retrospective/20260925T1015Z_sourcefreeze_v1/source_sqlite_snapshot.db`; SQLite online backup created 2026-09-25 10:48:40 UTC, integrity `ok`, delete journal, read-only file.
- **SQLite backup SHA-256:** `d456f2e0cd9aeb7284f69ae9ca5fe740f54f38fdeb9a3e0521e9f6fc235a583d`.
- **Frozen source manifest SHA-256:** `603aa8ef91cce69edb1c66632cc50467580dffbb3acbe561af1a763c05e3f04f`.
- **Canonical universe source manifest SHA-256:** `64da70e62fc1c29ce58539aa274a2894eb8e274eaa13296cbd898c05c69184a2`.
- **Selected current-state frozen DB candle rows digest SHA-256:** `0bbd510e7f2311a32c9278bbc0a510e49e8135091df116b19181750c8dac8106`.
- **Replay stability:** two full runs against the same frozen source and fixed input archive produced byte-identical reports; a further run was used to preserve the final authoritative artifact.

The live production SQLite was observed changing historical-row hashes between earlier runs, despite identical counters. Therefore `report.json` in this folder is an **unfrozen preliminary diagnostic**; **the authoritative frozen-input report is `report_frozen_source.json`**. Do not substitute one for the other.

## Final results

| Metric | Result |
|---|---:|
| Closed M15 cutoffs examined | 688 |
| Cutoffs with verified universe within 300s | 688 |
| Canonically validated archived universe files | 2,065 |
| Invalid/corrupt universe archives | 0 |
| Distinct selected top-19 symbols over the interval | 55 |
| Ranked slots examined | 13,072 |
| Structurally eligible slots using today's frozen historical DB | 9,717 |
| Fail-closed slots (history/depth/gaps/last close) | 3,355 |
| Structurally eligible but NOT supported by timely current ingest metadata | 9,686 |
| Structurally eligible with cutoff-compatible current ingest metadata | 31 |
| New prospective families admitted | **0** |

Note: the 31 metadata-compatible slots are **not verified first-seen prospective observations**. The frozen SQLite copy was created AFTER the historical period, so its current `ingested_at_ms` cannot replace contemporaneously immutable market-candle archives.

### Daily breakdown

| UTC date | Closed M15 cutoffs | Ranked slots | Structurally eligible | Failed | Current-ingest-compatible |
|---|---:|---:|---:|---:|---:|
| Sep 18 | 70 | 1,330 | 823 | 507 | 0 |
| Sep 19 | 96 | 1,824 | 1,321 | 503 | 0 |
| Sep 20 | 96 | 1,824 | 1,420 | 404 | 0 |
| Sep 21 | 96 | 1,824 | 1,445 | 379 | 0 |
| Sep 22 | 96 | 1,824 | 1,370 | 454 | 0 |
| Sep 23 | 96 | 1,824 | 1,304 | 520 | 0 |
| Sep 24 | 96 | 1,824 | 1,441 | 383 | 0 |
| Sep 25 through 10:15Z | 42 | 798 | 593 | 205 | 31 |
| **Total** | **688** | **13,072** | **9,717** | **3,355** | **31** |

Failure reasons are counted per *timeframe* and may overlap for the same ranked slot. Most frequent individual depth failures were 1h (2,927) and 15m (2,423); these must not be summed as unique failed slots.

## Causal and governance interpretation

- The recorded **universe context** has complete 688/688 selection coverage under the frozen 300-second rule.
- Current hindsight **historical candle coverage** is incomplete for 3,355 top-ranked slots and lacks timely-ingestion metadata support for most other slots.
- Coverage does **not** mean prospective continuity across the outage. Do not use 9,717 hindsight-ready or 31 metadata-compatible slots as proof of past first-seen decisions.
- Phase 11G Path A stays **54/100 verified resolved primary families**, no new outcomes.
- The partial 2026-09-18T06:30Z output remains untouched; no historical output collision was bypassed.
- Candidate `candidate_rule_set_v2_2`, frozen harness/protocol SHA-256, resolver v1.3 and ledger v1.2 remain unchanged.
- `holdout_opened=false`, `production_action=false`, Phase 12 inactive, no trading authorization.

**Next separate gate:** review the previously prepared server-only future prospective epoch protocol. A future-only preregistration, versioned namespace, strict data readiness and explicit owner authorization are required before restarting counted prospective evidence. This completed retrospective audit does not itself authorize a new epoch.

## Artifacts

- [Authoritative frozen-input coverage report](report_frozen_source.json)
- [Frozen SQLite source manifest](source_manifest.json) (the SQLite data copy stays on the K-Trader server, not in Git)
- [Pre-freeze exploratory output — not authoritative](report.json)
- [Mandatory host restriction](../../../operations/K_TRADER_HP_OMEN_EXCLUSION_2026-09-25.md)
- [Separate proposed future-epoch protocol](../../PHASE11G_SERVER_ONLY_GAP_RECOVERY_PROPOSAL_2026-09-25.md)
