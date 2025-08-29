---
title: "Faction Conflict Matrix — Season 1 Hooks"
type: "design"
domain: "narrative"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Narrative/Design"
tags: ["factions", "reputation", "betrayal", "auction", "gate"]
related_docs: ["Lore/LORE_BIBLE.md", "Design/Systems/TRUCE_GATE_GOVERNANCE.md", "Design/Systems/BLACK_AUCTION_SYSTEM.md", "Design/Systems/QUIETUS_MARKS_AND_FAILURES.md"]
---

## Conflict Matrix — Intent

- Formalize alliances, frictions, and hard enemies; wire to Gate and Auction behaviors.
- Provide betrayal triggers and reputation deltas that matter to extraction.

## Matrix (summary bullets)

- Sky Bastion Directorate (FCT_DIR)
  - Enemies: Trivector Combine (tech mandate overreach), Iron Vultures (black-market destabilization)
  - Frictions: The Seventy-Seven (contractors), Obsidian Archive (intel opacity)
  - Allies: Truce Wardens (public order), Nomads (humanitarian corridors)
  - Gate posture: high search, lawful neutral if rep ≥ 0
  - Auction posture: suppress illegal lots; seize provenance chips on sight

- Iron Vultures (FCT_VUL)
  - Enemies: Directorate (seizures), Wardens (tolls), Null Choir (stealth raids)
  - Frictions: Combine (IP claims), Archive (embargoes)
  - Allies: Nomads (trade routes), F77 (paid muscle)
  - Gate posture: test limits; bribery events; smuggler inspections
  - Auction posture: flood bids on refit kits; sabotage rivals via ghost bids

- The Seventy-Seven (FCT_F77)
  - Enemies: none persistent (contract-driven)
  - Frictions: everyone when contract flips
  - Allies: temporary per contract
  - Gate posture: compliant; leverage reputation to bypass searches
  - Auction posture: surgical snipes; escrow shivs to cut payments post-extraction

- Trivector Combine (FCT_CCB)
  - Enemies: Directorate (control), Wardens (oversight), Monolith Wardens (EMP backlash)
  - Frictions: Archive (data custody), Vultures (leaks)
  - Allies: F77 (demos), Blacksky Charter (events)
  - Gate posture: entitled; push tech through; trigger extra scans on rivals
  - Auction posture: prototype loss-leaders; panic when safety reports leak

- Roadborn Clans (FCT_NOM)
  - Enemies: pirates/raiders (unspecified)
  - Frictions: Wardens (toll creep), Directorate (corridor claims)
  - Allies: Vultures (market), Wardens (convoy rescue)
  - Gate posture: humanitarian pass; convoy priority if rep ≥ 1
  - Auction posture: logistics contracts; underbid with fleet speed

- Obsidian Archive (FCT_VAR)
  - Enemies: Null Choir (schism), Combine (reckless demos)
  - Frictions: Directorate (secrecy), Vultures (leaks)
  - Allies: Wardens (civilian protection)
  - Gate posture: stealth preference; immune to some searches by treaty
  - Auction posture: embargo classes; Silent Gavel events

- Truce Wardens (FCT_CWD)
  - Enemies: violators with Quietus ≥ Q2
  - Frictions: everyone during crackdowns
  - Allies: civilians, Nomads, Directorate
  - Gate posture: verdicts; patrol density scales with violations
  - Auction posture: observe; impound contraband on sight

## Betrayal & Reputation Hooks

- Gate Betrayal (fire inside zone) → Quietus +1, Warden rep −1, vendor access −1 tier.
- Auction Fraud (provenance forgery) → Heat +1, target-faction rep −2, Freeport lockdown chance.
- Handler Double-Cross (mission flip mid-run) → faction A +2, faction B −2; unlocks timed bounty events.

## Numbers (initial targets)

- Rep range: −3 to +3; neutral = 0; hard ban ≤ −2; VIP services ≥ +2.
- Quietus tiers Q0–Q4; redemption contracts reduce one tier per completion.
- Heat range 0–5; at ≥ 3, evac complications add 1–2 dynamic events.
