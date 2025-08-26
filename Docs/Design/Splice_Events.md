# Splice Events — System Design (Bold)

## Core Loop

- Explore under unstable conditions → Trigger a Splice Event → Improvise (risk/reward) → Extract with unique loot/codex.

## Player Fantasy

- Ride the pulse. You sense the world shift and thread the needle to snatch forbidden opportunity.

## Mechanics & Rules

- Event Triggers: proximity, timer-window, loud action, low integrity, story beat.
- Eligibility: deck- and biome-gated; per-session weights; cooldown per card.
- Outcomes: grants (loot, access), threats (ambush, blackout), toggles (evac window, patrol mask).
- Limits: 1–3 events per run by tier; diminishing weights; never trigger while extracting.

## Feedback

- Telemetry: screen warp, haptics, bass hit; HUD tag; radio bark; brief UI card when safe.

## Failure & Recovery

- Overstay window or fumble inputs → event backfires; partial rollbacks on successful extract.

## Variants

- Safe: Weighted random encounters with clear tells and simple rewards.
- Bold: Deck-driven events with factional modulation and world toggles (preferred).
- Experimental: Player-authored decks (meta-crafting) and squad-synergy fusions.

## Tech & Hooks

- Subsystem: World subsystem that owns decks; data assets for cards; multicast event on trigger.
- Persistence: Per-session weights reset; cooldown saved only for chain beats.
- Save/Load: UTGGameInstance saves Trust/Codex and (optionally) Convoy to SaveGame.

## QA Notes

- No new lore names introduced. Uses existing regions (e.g., Black Vault) via display names.

## Context Keys (engine integration)

- PlayerA, PlayerB: string identifiers for trust dyads.
- RouteId: convoy route name for economy telemetry.
- JobType: contract/job type tag (Raid/Protect/Recon/Spoof).

## Outcome Effects (engine integration)

- ConvoyIntegrityDelta: forwarded to UTGConvoyEconomySubsystem.ApplyConvoyOutcome(abs(delta), RouteId, JobType, success=delta>=0).
- ReputationDelta: normalized to [-1..1] and applied via UTGTrustSubsystem.RecordParley (>=0) or RecordBreach (<0) using PlayerA/PlayerB.
- UnlockCodexIds: list of EntryIds sent to UTGCodexSubsystem.UnlockCodex.
