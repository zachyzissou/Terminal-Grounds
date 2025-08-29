---
title: "Retcon Notes — 2025-08-28"
type: "change-log"
domain: "lore"
status: "approved"
last_reviewed: "2025-08-28"
maintainer: "Narrative Team"
tags: ["retcon", "naming", "aliases", "governance"]
---

## Retcon Notes — August 28, 2025

## Summary

Align public display names with Bold+ canon while preserving stable IDs. All changes use aliasing in `lorebook.yml`; no IDs change.

## Changes

1. Vault Lexicon → Obsidian Archive

- Affected: public copy, headings, flavor packs
- Rationale: stronger identity and market clarity
- Migration: Update displays to "Obsidian Archive"; keep `FCT_VAR`; add alias in glossary

1. Deep Vault ↔ Black Vault

- Affected: regions
- Policy: `REG_BLACK_VAULT` is canonical ID; primary display "Black Vault"; alias "Deep Vault"
- Migration: Use display mapping in UI/data tables; update glossary entries

1. IEZ naming

- Affected: regions/events
- Policy: Primary display "Dead Sky (IEZ)"; in tech notes "IEZ" acceptable; avoid "Industrial Exclusion Zone"
- Migration: Glossary enforcement; docs gate rule for term usage

1. Corporate Combine → Trivector Combine

- Affected: design docs
- Migration: Replace textual occurrences; confirm slogans and signatures match Lore Bible

## Enforcement

- Glossary terms locked in `LORE_BIBLE.md#glossary`; Docs Gate lints for mismatches
- All PRs with `lore-change` label must update this file and link diffs

## Verification

- Lore QA: Rebuild prompts, smoke-test 1–2 per category per style; target ≥85 alignment
- Runbook: Document pass in Tools/Comfy/ComfyUI-API/RUNBOOK.md with checklist

## Changelog

- 2025-08-28: Initial retcon set approved and applied.
- 2025-08-28 (Addendum): Clarified REG_BLACK_VAULT display as "Black Vault" with alias "Deep Vault"; added glossary candidates: Quietus Mark, Ghost Bid, Provenance Forgery, Mnemonic Debt, Coherence Band. No ID changes. Lore QA sync required if terms are promoted to canon.
