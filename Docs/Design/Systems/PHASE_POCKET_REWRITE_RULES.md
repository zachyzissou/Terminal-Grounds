---
title: "Phase Pocket Rewrite Rules"
type: "design"
domain: "design"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Design Team"
tags: ["events", "procedural", "experimental", "extraction"]
---

## Phase Pocket Rewrite Rules (Experimental)

Premise

- During Monolith Bloom windows, specific POIs enter “Phase Pocket” states: layouts, routes, and hazards temporarily rewrite.

Rules

- Trigger: EVT_HARMONIC_WINDOW active; local harmonics above threshold
- Scope: Tagged POIs only; evac windows become “coherence windows”
- Effects: Rewired doors, shifted cover, reversed signage, altered faction presence

Player Experience

- Maps that feel familiar but wrong; evac becomes a puzzle under time pressure
- Recon matters: squads that study patterns gain huge risk advantage

Implementation Notes

- Expose a PhasePocket tag to procgen; author 2–3 alternate micro-layouts per POI
- Hook to dynamic events to flip signage and route hints

Success Criteria

- 30–50% of players encounter at least one Phase Pocket per session
- Extraction decision phase tension reliably spikes without confusion
