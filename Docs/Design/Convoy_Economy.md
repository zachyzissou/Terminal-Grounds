---
title: "Convoy Economy"
type: "reference"
domain: "process"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Documentation Team"
tags: []
related_docs: []
---

# Convoy Economy — System Design (Bold)

## Core Loop

- Scout routes → Intercept or escort convoys → Affect Integrity Index → See prices and contracts shift → Re-engage.

## Player Fantasy

- Tip the market with a single clean hit. Every bullet leaves a dent in someone’s balance sheet.

## Mechanics & Rules

- Integrity Index (0–1): shared-season metric; decays toward equilibrium; clamped per bracket.
- Routes: rotating lanes; threat levels modulated by index and beat.
- Jobs: Raid, Protect, Recon, Spoof; outcomes push/pull the index with caps per window.
- Rewards: Dynamic payouts; vendor stock and crafting costs tied to index bands.

## Feedback

- World ticker on HUD; vendors call out price bands; contract board color-codes risk.

## Failure & Recovery

- If wiped, partial payout on intel; index shift reduced by half-life.

## Variants

- Safe: Linear slider economy with static bands.
- Bold: Elastic index with caps, hysteresis, and factional hedging (preferred).
- Experimental: Player-owned futures with delivery slippage and sabotage insurance.

## Tech & Hooks

- Subsystem: World subsystem with index, routes; events for UI and contracts.
- Persistence: index saved per season; route masks rotate daily.
	- Implementation: stored via SaveGame (UTGGameInstance) or server authority in future phase.

### Engine wiring

- UTGConvoyEconomySubsystem exposed as WorldSubsystem; Splice outcomes call ApplyConvoyOutcome(|delta|, RouteId, JobType, success=(delta>=0)).
- OnIntegrityIndexChanged(NewIndex, Delta) raises UI updates and vendor price band shifts.

### Math

- Decay: exponential toward Equilibrium with half-life (default 3600s): I(t)=E+(I0−E)·e^(−λt), λ=ln(2)/halfLife.

## QA Notes

- No new lore names introduced; aligns with Black Vault display alias policy.
