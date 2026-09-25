# Phase 11G new isolated forward-only epoch preregistration — 2026-09-25

**Status:** PREREGISTERED / SERVER PREFLIGHT PASS; bounded data-only collection activation is separately observed in live runtime.  
**Explicit user approval:** `go` after the separate future-epoch proposal, 2026-09-25.  
**Classification:** `FORWARD_FIRST_SEEN_DATA_ONLY` — **not** an extension of the interrupted immutable ledger.

## Exact future window and isolation

- epoch ID: `epoch_20260925T114500Z_v1`;
- actual server registration: **2026-09-25T11:11:07.910185Z**;
- first prospective cutoff: **2026-09-25T11:45:00Z** (strictly after the registration time by more than 15 minutes);
- bounded last inclusive cutoff: **2026-09-26T11:30:00Z**;
- first-seen capture target: cutoff + 180 seconds, mandatory completion no later than cutoff + 300 seconds;
- server-only root: `/data/research/phase11g/prospective_epochs/epoch_20260925T114500Z_v1`;
- operation restricted to independently owned K-Trader Oracle host and existing production read-only Binance USD-M archive/SQLite, **never HP-OMEN, K_AI/MT4 or a remote relay**;
- do not backdate, catch up, overwrite a cutoff, substitute lower-ranked symbols, or automatically restart after missed first-seen windows.

## Read-only frozen identity pins

| Component | SHA-256 |
| --- | --- |
| Original accepted 2026-09-18T06:15Z state | `30d0510da10d3d8b40684f8bf97c9ae568a6b3b8a7b43289c6b8cd41543a997b` |
| Original immutable prospective event ledger | `c0c1b261a6684d1f9381e820736f9dd702319947e3e7f78fb38b607508dcfade` |
| Original frozen v2.2 harness | `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08` |
| Original frozen protocol | `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3` |
| Installed independent new epoch recorder | `3ff7d5ff85f315e785fb5eca8b28ef04fc6fa150374c85edfd0db10b67465213` |
| Server registration JSON | `b67a2d4c587995d4b58649ea136e99306dfe5927a178565cc176b82f36b7ef9e` |

Accepted recorder repository merge: `7493b9843ec6889cc1da1e646968698a7b7cd6ea`; Git blob `beb2f5182b9803c45189a854b7d63eb863b97385`. Both Research Safety CI and Research Guards passed; server recorder self-tests `6/6` and independent offline regression cases `11/11` passed.

## Registered panel policy and data contract

- provider `binance_usdm`, archive config `max_candidates=50`, `max_price="3"`, `price_limit_enabled=true`, `quote_asset="USDT"`;
- first **19** ranks in each canonical source snapshot, no substitution for insufficient history;
- source snapshot must be canonical-digest verified, timestamp `<= cutoff`, age `<=300 seconds`;
- strictly closed history depth `1d:20`, `4h:80`, `1h:300`, `15m:400`, `5m:20`;
- one read-only SQLite transaction for all ranked slots in each cutoff;
- record every slot's data/failed reasons, ingestion timestamps, source-file hashes, actual first-seen clock time, archive digest and final immutable cutoff manifest;
- fail-closed on source drift, corrupt latest archive, health-boundary failure, time-budget breach or output collision;
- historical recorded top-19 policy is **new epoch selection context**. It does not rewrite the frozen old 19-symbol fixed panel/protocol or establish cross-epoch sample comparability.

## Server preflight before the first future cutoff

At **2026-09-25T11:11:33Z**, local verification returned:

```text
SELF_TEST=PASS (6 gates)
status=PASS
epoch_id=epoch_20260925T114500Z_v1
start=2026-09-25T11:45:00Z
until=2026-09-26T11:30:00Z
health.mode=read_only
health.status=ok
health.provider_id=binance_usdm
recording_only=true
admitted_new_prospective_families=0
```

**Governance:** `candidate_rule_set_v2_2`, its original harness/protocol pins, resolver v1.3, ledger v1.2 and first 54/100 resolved prospective families remain unchanged. No new strategy evaluation, resolved family counting, holdout opening, Phase 12 activation, trading or HP-OMEN access is authorized. This preregistration only authorizes the bounded **new first-seen market-context/data capture**. Isolated candidate/resolver/evidence compatibility is a later gate.

Operational code and capture contract: [PHASE11G_FUTURE_FIRST_SEEN_EPOCH_CAPTURE_V1.md](../research/PHASE11G_FUTURE_FIRST_SEEN_EPOCH_CAPTURE_V1.md).
