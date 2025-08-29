---
title: "Tg Audit Gameplaytags"
type: "reference"
domain: "process"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Documentation Team"
tags: []
related_docs: []
---

# Gameplay Tags Audit

- Verified `Config/DefaultGameplayTags.ini` exists and added canonical roots:
  - `TG.Faction`
  - `TG.Weapon`
  - `TG.Damage`
  - `TG.Mission`
  - `TG.Event.Weather`
- Confirmed `Config/DefaultEngine.ini` enables `ImportTagsFromConfig`.
- Added automation test `TGGameplayTagsSanityTest` to assert the `TG.Faction.Corporate` tag loads correctly.
