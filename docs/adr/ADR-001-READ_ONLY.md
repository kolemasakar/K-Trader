# ADR-001: Read-only v1

Status: ACCEPTED
Date: 2026-08-23

## Decision

K-Trader v1 collects and analyzes public market data only. It has no exchange-account authentication and no order execution capability.

## Rationale

- minimizes implementation and security complexity;
- removes exchange credential custody;
- allows scanner/strategy validation before execution risk is introduced;
- matches the current project goal: live market screening and analysis.

## Consequences

- Position size/risk require separately supplied confirmed account parameters.
- Trading execution is explicitly deferred to a future separately approved phase.
