# Pull Request Checklist

Please confirm the following before requesting review. Check all that apply.

- [ ] Tests and linters pass locally
- [ ] Documentation updated (if applicable)
- [ ] ComfyUI pipelines validated (health on 8188 OK; sampler/scheduler/cfg as per presets)
- [ ] Deterministic seeds used for reproducible examples

## Lore QA (Required when lore changes)

If this PR adds/modifies lore (regions, factions, POIs, terminology), complete this section:

- [ ] Lore sources synced (docs/Lore/LORE_BIBLE.md → Tools/Comfy/ComfyUI-API/lore_prompts.json and any data tables)
- [ ] Prompts rebuilt via Build-LorePrompt.ps1; batch mappings verified with -UseLorePrompt(s)
- [ ] Smoke tests: ≥1 image per category per style fork; Lore Alignment ≥ 85 in audits
- [ ] overlay_meta/* labels updated if names/locations changed
- [ ] RUNBOOK and PR describe the Lore QA pass (what changed, tests run, results, follow-ups)

> PRs that affect lore must not be merged without a completed Lore QA section.
