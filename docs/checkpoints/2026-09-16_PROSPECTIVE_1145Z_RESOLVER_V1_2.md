# K-Trader — Prospective 11:45Z / Resolver v1.2 Checkpoint

Date: 2026-09-16  
Status: **ACCEPTED DIAGNOSTIC CONTINUATION / NO RETUNING / HOLDOUT CLOSED**

## Governance

- Phase 11G: ACTIVE.
- Phase 12: FUTURE / NOT ACTIVE.
- Frozen strategy: `candidate_rule_set_v2_2` unchanged.
- Frozen harness SHA256: `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`.
- Protocol SHA256: `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`.
- Holdout opened: `false`.
- Production action: `false`.
- Evidence tier: `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`.

## Disk retention decision

The dry-run helper and systemd service are installed and validated on `k-trader-prod-vnic`.

Validation manifest:

- mode `DRY_RUN_ONLY`;
- status `FORCED_DRY_RUN_PLAN_READY`;
- filesystem use `19.000516%`;
- trigger `false`;
- eligible candidates `38`;
- would-delete candidates `20`;
- would-delete bytes `97,393,279`;
- deletion performed `false`;
- manifest SHA256 `d1ecdb98b8d4fc000098482126c3f9542a67562e44b5eddb73411187e3037d20`.

Systemd sandbox test:

- `Result=success`;
- `ExecMainStatus=0`;
- oneshot returns to `inactive/dead` as expected.

Decision: `ktrader-disk-retention.timer` remains **disabled by design**. At ~19% disk use an hourly dry-run adds little operational value and would only create recurring manifests. No destructive mode exists in v1.

## Prospective capture 2026-09-16T11:45:00Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T114500Z`

Capture state:

- status `VALID_SHADOW_CAPTURE`;
- provider `binance_usdm`;
- panel `19/19`;
- missing symbols `0`;
- signal bars evaluated `6574`;
- event count `295`;
- capture eligible observations `44`;
- capture unique eligible families `34`;
- holdout `false`;
- production action `false`.

Hashes:

- bundle set `971c4f62fd8d5a5341e8ae625e38558a3ae270be2222488636535619582aa2cf`;
- bundle export summary `ecfefa9a709682615c52daa7a33d55ff03cd9c1e0f3f5bcd5548b0a24f5b4a3a`;
- event file `ed1c6826bb63124a98081bd7998a0bde155c2d02654116146403aa46e767ff7e`;
- shadow summary `d4f52490488867d425a2eda1079b684f18322278c8e66b0272ba55071b574b3b`.

Ledger after capture:

- discovered snapshots `17`;
- valid snapshots `16`;
- rejected snapshots `1` known first infrastructure-invalid capture;
- deduplicated events `365`;
- eligible observations `56`;
- unique eligible families `43`;
- ledger event set SHA256 `3139b622956c90618222b864ef401ee179f99c18c4b60309822e724aa7288d36`.

No new independent family was added relative to the prior accepted catch-up.

## Funding snapshot

Persisted official Binance USD-M funding snapshot at `11:45Z`:

- symbol count `19`;
- records total `1849`;
- summary SHA256 `b1d94137e7cb4474d7ac0a35f1336c1fe337bf0b4deba10bd746db5e8daaa8d3`.

## Resolver v1.2

v1.1 failed closed at `11:45Z` on one stable-identity RAYSOLUSDT observation because stop representation drift `2.1062864785648117e-9` exceeded the existing `2e-9` absolute guard.

Across all `50` previously resolved observations:

- maximum entry-price delta `0.0`;
- maximum stop-price delta `2.1062864785648117e-9`;
- second-largest stop delta `1.7451648529065444e-9`;
- third-largest stop delta `1.620510220478634e-9`.

A separate versioned resolver entrypoint v1.2 was created. It changes only:

`PRIOR_PRICE_ABS_TOL: 2e-9 -> 3e-9`

Relative tolerance remains `1e-12`. Output schema and outcome semantics remain unchanged.

Canonical files:

- `research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_offline_v1_2.py`;
- `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_2.md`.

v1.2 result at `11:45Z`:

- eligible observations `56`;
- unique primary families `43`;
- resolved primary families `39`;
- unresolved primary families `4`;
- wins / losses `9 / 30`;
- win rate `23.076923%`;
- expectancy `-0.6482720085510278R`;
- prior terminal reuse `50`;
- prior terminal path revalidated `44`;
- prior source-window-expired `6`;
- newly resolved observations `0`;
- network used `false`;
- holdout `false`;
- production action `false`.

Temporary validation report SHA256:

`923d990bdd8d94b676ff0c79a92469ba78b65a469cba689e4d759da2914bd6d2`

Parity against the prior accepted 10:30Z state:

- previously resolved rows checked `50`;
- terminal/economic mismatches `0`.

## Four currently open primary families

At `11:45Z`:

- SUIUSDT SHORT/primary entry `08:00Z`: `15` bars observed; 8h boundary `16:00Z`;
- XRPUSDT entry `08:00Z`: `15` bars observed; 8h boundary `16:00Z`;
- ADAUSDT entry `08:15Z`: `14` bars observed; 8h boundary `16:15Z`;
- DOGEUSDT entry `08:15Z`: `14` bars observed; 8h boundary `16:15Z`.

No STOP/3R terminal occurred by `11:45Z`; therefore all four correctly remain unresolved. The resolver must not force TIME_EXIT before the causal 32-M15 boundary.

## Updated diagnostic-only analysis

Descriptive report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_post30_diagnostics/20260916T114500Z/descriptive.json/report.json`

SHA256:

`ff12665d0781b29a932e66923c88868c66e071e2c89559f49fbeb96c3c1e6717`

Statistical report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_post30_diagnostics/20260916T114500Z/statistical.json`

SHA256:

`e467c88533f1fd989180902b7745afe3f773830ec8dbdb5a8cc629b4c85c6483`

Accepted interpretation remains unchanged:

- SHORT vs LONG: no statistically supported separation;
- obstacle `<1R` / `<3R`: strongest current hypothesis-generating feature, but does not survive BH adjustment;
- raw VSA: no reliable separation;
- no subgroup diagnostic authorizes a frozen-v2.2 filter or retune.

## Next causal boundary

Continue prospective collection without retuning. The four open families may resolve by STOP/3R before max hold. If not, their causal TIME_EXIT boundaries are `16:00Z` and `16:15Z` on 2026-09-16.

No background task is assumed. A subsequent explicit continuation should perform a fresh capture/funding snapshot and resolver run at or after a suitable closed-bar cutoff.
