# ADR-003: REST bootstrap + WebSocket live model

Status: ACCEPTED
Date: 2026-08-23

## Decision

Use public REST for discovery, historical bootstrap and reconciliation; use public WebSocket for continuous live market updates.

Prefer a smallest canonical live interval (initially 5m where practical) and aggregate upward locally using UTC boundaries, while periodically reconciling against provider-native candles.

## Rationale

- avoids unnecessary duplicate subscriptions;
- centralizes bar sequencing;
- supports continuous live VSA inputs;
- REST provides deterministic recovery after disconnects.

## Caveat

Provider capabilities differ. The implementation may subscribe to additional native intervals when required for correctness. This is adapter/config behavior, not a change to engine contracts.
