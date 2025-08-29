---
title: "Black Auction System"
type: "design"
domain: "design"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Design Team"
tags: ["economy", "factions", "events", "extraction"]
related_docs: ["../../Lore/LORE_BIBLE.md", "../Season1_Arc.md", "MEMORY_ECONOMY_SPEC.md", "PHASE_POCKET_REWRITE_RULES.md"]
---

## Black Auction System

## Premise

- Timed, map-wide auction windows where artifact/intel demand spikes, compressing evac and altering faction behaviors.

## Contract

- Inputs: EVT_VAULT_SIREN, EVT_HARMONIC_WINDOW, market indices, faction reputation
- Outputs: price boards, AI posture, evac window shifts, mission seeds
- Failure: late extraction voids bids; hostile ambushes trigger; reputation loss with employer

## Mechanics

- Windows: 12–20 min intervals; sirens and signage flip; POI terminals broadcast bids
- Bids: faction-weighted; rare Monolith items create contested POIs
- Reactions: Directorate clamps corridors; Vultures flood the docks; Combine posts prototypes; Wardens raise tolls
- Player Choices: escort/ambush convoys; snipe bids by stealing rival artifacts; deliver on time for bonus reputation

## Extraction Stakes

- Auction items extracted before window close grant: credits x multiplier, faction rep, codex unlock chance (if tied to MEMORY_ECONOMY_SPEC)
- Failure creates “Blacklist” debuff: price penalties or temporary vendor lockouts

## Dynamic Events

- Jammers Online: shortens evac windows around auction hubs
- Silent Gavel: Obsidian embargo locks a POI; only stealth ingress counts
- Gate Toll Surge: Wardens randomize numbers; breaking truce doubles penalties

## UI/UX

- Price boards in Crimson Freeport; faction emblems indicate dominant bidders
- Map overlay highlights auction corridors; timers in world and HUD

## Implementation Notes

- Hook into Territorial Warfare influence deltas; auction wins shift local control
- Broadcast OnAuctionWindowStarted/Ended (TGEvents); expose to mission graph

## Success Criteria

- Uptake: 70% of mid-tier runs route through at least one auction POI
- Economy: 10–15% price oscillation during window; risk premium perceived as fair
- Narrative: distinct faction chatter per window (see VO seeds)
