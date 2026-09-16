# Storage / Provenance Audit — 2026-09-16 16:30Z

Status: **PASS**

## Storage

Current root filesystem:

- size: ~45 GiB;
- used: ~8.5 GiB;
- displayed utilization: `20%`;
- available: ~36 GiB.

Research tree size measured inside the application container:

`/data/research = 1,471,489,881 bytes` (~1.47 GB decimal).

Disk-retention state:

- planner remains `DRY_RUN_ONLY`;
- destructive mode remains absent;
- `ktrader-disk-retention.timer` remains `disabled` by design;
- no retention activation was authorized by this audit.

The current capacity state does not justify enabling destructive retention.

## 16:30Z machine state provenance

State manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T163000Z.json`

Manifest SHA256:

`0608850f392f2f5beb5cf7be993b6c30effd67b615b9dc44c253e0f67c8aa8a5`

The manifest references five authoritative runtime artifacts:

- cycle summary;
- ledger summary;
- resolver summary;
- evidence tracker report;
- portfolio-risk report.

Independent recomputation result:

- source files checked: `5`;
- SHA mismatches: `0`;
- provenance result: **PASS**.

## Production boundary

Final runtime health during this audit:

- status `ok`;
- mode `read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness state;
- no production deploy/restart/order action performed.

## Conclusion

Storage and provenance are not current Phase 11G blockers.

Continue monitoring only. Do not enable destructive retention or broaden production privileges as a consequence of this audit.
