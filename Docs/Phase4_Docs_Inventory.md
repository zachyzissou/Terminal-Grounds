---
title: Phase4 Docs Inventory
type: reference
domain: process
status: draft
last_reviewed: '2025-08-28'
maintainer: Documentation Team
tags: []
related_docs: []
---


# Phase 4 — Docs Inventory (Present/Thin/Missing)

Scope: High-level classification of key documentation artifacts for the Phase 4 delta pass. Only classification; no content removed. Use this as a checklist for append-only expansions.

Date: 2025-08-11

## Present (meets baseline)

- README.md — Project overview, Quickstart (UE5), repo map, UE asset path index
- DESIGN_OVERVIEW.md — Pillars, loops, world foundation
- DECISIONS.md — Architecture and design choices
- PROGRESS.md — Phase milestones and status
- HOWTO-BUILD.md — Basic build steps (Editor, Server)
- HOWTO-HOST.md — Basic hosting steps (Docker, ports)
- Docs/Art/ART_BIBLE.md — Comprehensive art direction
- Docs/VFX/VFX_BIBLE.md — VFX direction and standards
- Docs/Audio/AUDIO_VISION.md — Audio/MetaSounds overview
- Docs/Lore/LORE_BIBLE.md (+ Factions/POIs flavor) — Narrative backbone
- Docs/Art/UI_STYLE_GUIDE.md — UI system and assets
- Tools/README.md — Tools overview
- Tools/TGModKit/README.md — Modding SDK

## Thin (needs append-only expansion)

- HOWTO-BUILD.md — Platform specifics (Windows toolchain details, Linux cross-build notes), first-run tips, common errors
- HOWTO-HOST.md — Docker compose env vars, save/config mount points, sample command-lines, cloud provider notes
- README.md — Badges and links to CI, server build artifacts; short “Troubleshooting” appendix
- PROGRESS.md — Align current tasks with Phase 4 delta specifics; add doc QA gate items

## Missing (recommended additions)

- CONTRIBUTING.md — PR workflow, branch naming, code style, review checklist
- CODE_OF_CONDUCT.md — Community standards
- SECURITY.md — Reporting vulnerabilities (even if N/A for now)
- TESTING.md — Minimal guidance for validating builds/assets, smoke tests
- BUILD-FAQ.md — Compilation errors and fixes (Unreal/VS toolchain, linker, plugins)

## Notes

- All changes must be append-only to preserve authored content. Use clear new sections and avoid renaming existing headings.
- Where screenshots are required, mark with "Screenshot TODO" only.
- Maintain markdown lint: no hard tabs, blank lines around headings/lists, and single trailing newline per file.
