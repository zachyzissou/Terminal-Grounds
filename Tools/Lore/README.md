# Lore Builder

Use Build-LoreJSON.ps1 to compile LoreBook front-matter into:

- lore_index.json (full index for tools)
- Tools/Comfy/ComfyUI-API/lore_prompts.json (generator capsules)

Example (PowerShell):

pwsh -NoProfile -ExecutionPolicy Bypass -File Tools/Lore/Build-LoreJSON.ps1

Notes:

- The builder preserves existing lore_prompts entries if no LoreBook pages are present for a category.
- Front-matter keys expected: id, name, type, plus category-specific fields seen in the template files added.
