# Trust System — System Design (Bold)

## Core Loop

- Pledge to cooperate → Parley under pressure → Risk Breach when incentives flip → Reputation and access evolve.

## Player Fantasy

- Earn the right to be watched. Your name opens doors—or gets you shot on sight.

## Mechanics & Rules

- Actions: Pledge (assist, share, spare), Parley (dialog/gesture), Breach (betrayal).
- Trust Index: per-faction and per-player dyads with decay; global reputation gates.
- Consequences: Discounts, intel, back-up vs. bounties, ambushes, betrayal markers.

## Feedback

- HUD pips on allies; VO reactions; contract notes; simple meter in social menu.

## Failure & Recovery

- Breach wipes temporary buffs; decay and contrition missions can restore.

## Variants

- Safe: Hidden karma with reveal-at-vendor.
- Bold: Explicit Pledge/Parley/Breach records with visible outcomes (preferred).
- Experimental: Social contracts as on-chain IOUs with escrowed gear.

## Tech & Hooks

- Subsystem: GameInstance subsystem; events for UI; minimal persistence of records.
- Anti-abuse: Clamp deltas per session; cooldowns on betrayals; server audit trail.

### Engine wiring

- UTGTrustSubsystem receives Splice outcomes: ReputationDelta normalized to [-1..1]; >=0 uses RecordParley, <0 uses RecordBreach.
- Requires Context keys: PlayerA and PlayerB.

### Notes

- Clamp behavior: individual delta magnitudes capped per session; decay toward neutral between sessions.

## QA Notes

- No new lore names introduced; uses existing faction IDs.
