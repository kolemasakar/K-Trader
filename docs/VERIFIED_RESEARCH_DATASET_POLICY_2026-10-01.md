# Verified research dataset: Phase 11G source and reuse authorization

Owner directive: amendment #33, 2026-10-01.
Status of observed source: **SOURCE VERIFIED / DIRECT READ ACCEPTED** (2026-10-01).
Policy status: **VERIFIED RESEARCH DATASET** applies to a specifically recorded, SHA-256-verified version after appropriate research-reader acceptance; direct source reuse needs no duplicated copy.

## Standing authorization
K-Trader may read and reuse the accepted, version-pinned, internal historical dataset in its current and future research without seeking per-task reapproval. Authorized research includes D1/W1 and Gerchik levels, ATR/ATR5, strategy and prerequisite research, offline historical backtesting, and statistical analysis. This is authorization to use data, NOT authorization to change live trading/deployment parameters, relax research quality gates or execute trades.

A single K-Trader-owned canonical archive is preferable. Do not generate permanent duplicate archives purely to provide K-Trader research access. KGM access is separate and deferred.

## Canonical observed source
- Host: `k-trader-prod-vnic`.
- Host path: `/opt/k-trader/data/research/phase11g/historical_expansion_v1_20260905T144500Z`.
- Existing container path: `/data/research/phase11g/historical_expansion_v1_20260905T144500Z`.
- Provenance: `binance_usdm`, source summary `as_of=2026-09-05T14:45:00Z`; immutable captured history identified by this archival path and registered digest.
- 2026-10-01 observed: 138 files, 84,503,013 file-content bytes, 19 bundles, D1 8,981; H4 19,000; H1 38,000; M15 57,000; M5 57,000 closed candles; 179,981 total. JSONL manifest rows must be excluded when counting candle rows.
- Source version tree SHA-256: `b7c030bdd71a93a8733574e285b05a8093f23f5efcecd9a4edc5fdde8f914aa6`. Algorithm: sorted relative file paths; concatenate UTF-8 lines `<path> <sha256(file_bytes)>\\n`; SHA-256 the concatenation. Recompute against a stable input before each *new version* acceptance; a later changed archive is not the same verified version.
- Reader verification: existing `ktrader` process UID 1002 read the source and inspected D1; structural count and full-file tree-digest checks passed. This confirms direct reading, **not** a separate read-only mounted container.

## Data status and lifecycle
1. `SOURCE_VERIFIED`: capture provider ID, retrieval/as-of timestamp, symbol list, timeframe coverage, source manifest, path, per-file SHA-256 and archive-tree digest; verify all source files and closed-bar flags.
2. `DIRECT_READER_ACCEPTED`: verify K-Trader's actual research reader can open the same verified source without modifying it. This state is accepted for the existing container research reads. A new standalone research container/process must be tested independently before claiming its access or enforced `READ-ONLY` mount.
3. `VERIFIED RESEARCH DATASET`: grant the standing research-use authorization for the **specific SHA-256-identified version** once integrity and actual reader access are both accepted. If a separate copy is required in future, verify *its* per-file content against source before promoting that transferred copy; transfer is not a prerequisite for in-place research.
4. On source change, rebuild integrity evidence and register a new version. Do not relabel a changed source using the previous version's status.
5. Preserve original data. Save reports, extracted features, W1 aggregation, levels, ATR5 series, model outputs, backtest trade simulations and statistical tables **outside** the archived source tree, linking each output to the dataset digest and exact research code/configuration.

## Scientific and operational limits
- `VERIFIED RESEARCH DATASET` means data integrity, recorded provenance and demonstrated accessibility. It does not establish historical suitability for every hypothesis or prove a strategy.
- This archive is an **internal development/research dataset**, not automatically an independent out-of-sample holdout for final model validation. Treat earlier exploration/tuning on overlapping dates/assets as leakage risk and select an independent control period separately.
- Enforce time-order validation, no future candles or future knowledge at each simulated cutoff, coherent providers/UTC and the existing strict Phase 11G research gates.
- Do not confuse this 19-symbol expanded research archive with the *two-entry canonical Phase 11G replay-study catalogue*; catalogue registration, cohort/context validation and outcome-sample constraints remain independently governed by `docs/DATASET_CATALOGUE_SPEC.md`.
- No production config change, service restart, credential copying, extra paid infrastructure or HP-OMEN use is required by this authorization.

## Responsibilities
- K_Sentinel / Sentinel-Remote: source/destination access facts, integrity checks, version handoff, narrowly scoped private paths and infrastructure report; no trading-model assessment.
- K-Trader: research reader, version-pinned data references, derivation and result storage, look-ahead safeguards and independent final model evaluation.
- Owner: grants standing dataset research use here; separately approves exceptional infrastructure privileges and other owner-gated runtime changes.

Related Sentinel-Remote access record: `kolemasakar/Sentinel-Remote/docs/K_TRADER_RESEARCH_DATASET_ACCESS_2026-10-01.md`.
