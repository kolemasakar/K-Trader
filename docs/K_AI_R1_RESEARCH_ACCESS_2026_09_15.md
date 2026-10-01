# K_AI R1 Research Access

Date: 2026-09-15
Status: VERIFIED / ACTIVE

K_AI Trading System may use the existing bounded SentinelX sudo rule to execute read/research commands inside the single K-Trader application container:

```text
sudo docker exec k-trader-ktrader-1 <command...>
```

No Docker-group membership and no new sudo authority were added.

## R1 dataset

```text
/data/research/kai_trading_system/r1_180d_v1
```

Manifest:

```text
/data/research/kai_trading_system/r1_180d_v1/dataset_manifest.json
```

Verified live on 2026-09-15:

```text
KAI_R1_READ=PASS
symbol_count=15
research_start=2026-03-19T00:00:00Z
research_end_exclusive=2026-09-15T00:00:00Z
```

Timeframes per symbol: `5m`, `15m`, `1h`, `4h`, `1d`.

## Operational boundary

- Research/read-only use only unless a separate mutation is explicitly authorized.
- Do not add the K_AI execution identity to the Docker group.
- Do not broaden general sudo/root authority.
- Do not mutate production datasets through `docker exec`.
- Do not use generic `sudo docker`; the accepted command shape is the single-container `sudo docker exec k-trader-ktrader-1 ...` path above.

Sentinel Remote canonical access record:

```text
docs/K_AI_KTRADER_RESEARCH_INTERACTION_2026-09-15.md
```
