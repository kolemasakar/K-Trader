# Production Safety and Execution Compatibility Audit — 2026-09-16

Status: **PASS WITH FUTURE EXECUTION-CONTRACT GAP**

## Scope

Read-only audit of the current K-Trader production container and research boundary. No production mutation, deployment, restart, secret readout, permission expansion or order action was performed.

## Runtime safety facts

Verified on `k-trader-prod-vnic`:

- application health: `ok`;
- API mode: `read_only`;
- provider: `binance_usdm`;
- container process user: `uid=1002(ktrader) gid=1002(ktrader)`;
- effective/permitted/bounding Linux capabilities: all zero;
- `/var/run/docker.sock` inside the container: absent;
- current Action/OpenAPI surface exposes GET operations only;
- static research-tree scan found no create/place/cancel-order API calls or HTTP write-method calls;
- the only research subprocess orchestration observed calls other research scripts;
- no `production_action=True` research source assignment was found.

## Credential boundary

Environment variable names were inspected without reading values.

Present K-Trader-specific auth item:

- `KTRADER_ACTION_API_KEY` — protects the read-only `/v1/*` API.

No exchange order/trading credential variable names were observed in the production container environment during this audit.

The current API privacy text and application code explicitly state that the API does not accept exchange credentials and cannot place, modify or cancel orders.

## Filesystem boundary

Host bind mount:

`/opt/k-trader/data -> /data`

is mounted read/write for the `ktrader` container user.

This is intentional for scanner/research data persistence, but means safety cannot rely on a read-only filesystem claim. Safety therefore depends on:

1. no exchange execution credentials;
2. no order endpoints;
3. no Docker socket/capabilities;
4. bounded host-side SentinelX permissions;
5. fail-closed research governance and artifact separation.

## Current instrument model compatibility

`NormalizedInstrument` currently provides:

- provider_id;
- symbol;
- base_asset;
- quote_asset;
- market_type;
- contract_type;
- status;
- `price_tick`;
- `quantity_step`;
- provider_symbol;
- metadata.

This is sufficient for read-only market normalization, but **not sufficient for a future real-order execution adapter**.

## Required future execution specification contract

Before any strategy can progress from read-only/shadow validation to real execution, K-Trader needs a separate versioned broker/exchange execution-spec contract covering at minimum:

- minimum quantity;
- maximum quantity;
- quantity step;
- price tick/precision;
- minimum notional;
- maximum notional where applicable;
- leverage brackets / leverage limits;
- initial/maintenance margin rules;
- available margin checks;
- position mode (one-way/hedge);
- reduce-only semantics;
- supported order types;
- time-in-force constraints;
- trigger/stop-price constraints;
- market-order quantity/notional constraints;
- symbol trading status;
- provider error normalization;
- idempotency/execution identifiers.

The execution adapter must never infer missing exchange constraints from strategy output.

## Promotion-package compatibility

A future strategy promotion package should remain strategy-centric. K-Trader should translate it into an executable order only after applying:

`strategy intent -> instrument specification -> portfolio risk -> margin check -> normalized order -> authorization -> executor`

The promotion package must not embed provider secrets or assume provider-specific quantity/price formatting.

## Result

Current production remains safely read-only for the research phase.

The identified execution-spec gap is a **future prerequisite**, not a current blocker, because no production trading is authorized in Phase 11G.
