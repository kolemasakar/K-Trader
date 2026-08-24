# K-Trader Scope Definition

Status: UPDATED 2026-08-24

## Purpose

K-Trader is an AI market intelligence and trading opportunity analysis system.

The system provides market screening, analysis and setup evaluation through its own specialized AI agents.

K-Trader is not an execution system and does not perform autonomous trading.

## Responsibilities

K-Trader:

- receives public market data from exchanges and other sources;
- normalizes and validates market information;
- analyzes markets through K-Trader AI agents;
- identifies and ranks trading opportunities;
- evaluates setups using deterministic rules and analytical scoring;
- provides reports for user decision making.

## Out of Scope

The following functions belong to K_AI Trading System or future separate projects:

- order execution;
- broker API trading;
- MT4/MT5 execution bridges;
- position lifecycle management;
- account management;
- autonomous trading;
- transition to production trading.

## Primary User Scenario

Example request:

"Select the most promising assets for trading, price below $5, with an expected execution horizon around 4 hours."

Processing flow:

```
Exchange public APIs
        ↓
Market Data Layer
        ↓
Universe Selection
        ↓
Liquidity / Volatility Filters
        ↓
AI Agent Analysis
        ↓
Setup Evaluation
        ↓
Ranking
        ↓
Analytical Report
```

## Exchange Architecture

K-Trader uses an exchange-agnostic adapter model:

```
MarketDataProvider
        |
        +-- Binance
        +-- Bybit
        +-- OKX
        +-- KuCoin
        +-- future providers
```

Exchange adapters provide data only. Trading logic remains provider independent.

## Separation from K_AI Trading System

```
K-Trader
---------
Market intelligence
Screening
Analysis
Signals
Reports


K_AI Trading System
------------------
Execution
Broker integration
Orders
Positions
Capital management
```

## Core Principle

K-Trader generates analysis and recommendations. The final trading decision remains with the user.
