---
title: "Quietus Marks & Failure Consequences"
type: "design"
domain: "design"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Design/Narrative"
tags: ["truce", "penalties", "failure", "memory", "extraction"]
related_docs: ["Design/Systems/TRUCE_GATE_GOVERNANCE.md", "Design/Systems/MEMORY_ECONOMY_SPEC.md", "Design/Faction_Conflict_Matrix.md"]
---

## Quietus Marks — Law of Numbers (Experimental Enforcement)

Tiers

- Q0 — Clean: normal services.
- Q1 — Noted: extra scans at Gates; minor toll increase; handlers warn you.
- Q2 — Marked: vendor tier −1; Warden patrol density +1; bounty pings within 300m.
- Q3 — Hunted: neutral services locked; convoy reroutes cost +20%; bounty squads spawn once per run.
- Q4 — Exiled: Gates deny passage except during Mercy windows; only black vendors trade; global broadcast of your callsign.

Duration & Decay

- Marks persist across sessions; decay by one tier per redemption contract or per 48h real-time without violations.
- Public verdicts are broadcast at Gate boards and on Freeport signage.

Redemption Paths

- Reparations: deliver aid crates to settlements (Wardens +1, Quietus −1).
- Escort: guard a med or evac convoy (Wardens +1, faction-neutral goodwill).
- Arbitration: pay fines at a Gate (credits sink; partial reduction).

## Failure & Memory — Coherence, Debt, Persona

Coherence Bands (C)

- C3 — Intact: codex unlocks persist; map variance toggles allowed.
- C2 — Frayed: partial unlocks; reduced vendor trust for intel sales.
- C1 — Shattered: no persistence; mnemonic debt +1.
- C0 — Lost: negative flag; next run starts with interference (glitch UI, comms hiss).

Mnemonic Debt (D)

- Earned on death-before-evac or EMP redaction at C1 or lower.
- Effects: handler availability −1 slot; VO changes; auction bid caps −10%.
- Reduce D by extracting with a “memory core” (squad carry) or completing Archive stabilization tasks.

Persona Shedding (P)

- Voluntary memory trade at Gates: swap a trait (minor perk) for access to Choir keys or black channels.
- P has social consequences: some handlers refuse, others unlock.

## Integration Notes

- Gate verdicts increment Quietus; Auction fraud increments Heat; Memory failures adjust C/D.
- Evac complications scale with max(Heat, Quietus).
- All values are season-tunable; surface timers and clarity in UI.
