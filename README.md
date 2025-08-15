# Terminal Grounds

A grounded, session-based salvage/extraction FPS built in Unreal Engine 5.6. Tight gunfeel, faction-driven conflict, and a salvage economy where Human → Hybrid → Alien tech escalates both power and risk.

“Logistics is drama. Alien tech is dangerous. Extract, or it never happened.”

## Status

Active development on Windows. Self-hosting and packaging supported. See docs for canon and design.

## Quick start (Windows + VS Code tasks)

Prereqs

- Unreal Engine 5.6 installed locally
- Visual Studio 2022 with C++ workload
- Git LFS enabled for large assets

One-time setup

1) In VS Code Settings, set "ue.engineRoot" to your UE path (e.g., `C:\\Program Files\\Epic Games\\UE_5.6`).
2) Clone with LFS and open the folder in VS Code.

Build and run

- UE5.6: Generate Project Files (VSCode)
- UE5.6: Build Editor (Dev Win64)
- UE5.6: Launch Editor

Optional checks/tools

- UE5.6: Sanity Pass (Headless Python)
- UE: Validate Required Plugins
- Docs: Run Docs Gate

## Dedicated server

Windows (PowerShell)

```powershell
Server\run_server.ps1
```

Linux/macOS

```bash
bash Server/run_server.sh
```

## Package a dev build

Use the task: UE5.6: Package Game (Win64 Dev)

Artifacts are written to `.packages/Win64/Development`.

## Canon and design docs

- Lore Bible (single source of truth): docs/Lore/LORE_BIBLE.md
- Machine-readable lore index: docs/Lore/lorebook.yml
- World scale & expansion: docs/Design/World_Scale_And_Expansion.md
- Faction art guides: docs/Art/Factions/

## Contributing

Read CONTRIBUTING.md and CODE_OF_CONDUCT.md.

- Keep lore canonical: link to the Lore Bible; don’t duplicate canon in feature docs
- Use stable IDs from lorebook.yml (REG_*, EVT_*, FCT_*, POI_*) in assets and docs
- Run the Docs Gate before PRs (task: "Docs: Run Docs Gate")
- Follow UE asset paths/naming (e.g., `Content/TG/...`)

## Repo map (short)

- Config/ — Engine/project settings
- Content/ — UE assets (Maps, Materials, VFX, UI, etc.)
- Data/ — Source tables for DataTables
- docs/ — Canon, art guides, concepts, tech notes
- Plugins/ — Project plugins (TGAttachments, TGModKit)
- Server/ + Docker/ — Dedicated server + containerization
- Source/ — C++ modules (TGCore, TGNet, TGCombat, …)

## Troubleshooting

- Tasks can't find the engine? Verify the VS Code setting: "ue.engineRoot".
- Missing images in docs? Run ArtGen/UE import pipelines under Tools/.
- Build failures? Re-run Generate Project Files and ensure VS 2022 C++ components are installed.
- Wishlist: (link soon) • Discord: (invite soon)
- See `Docs/Phase4_Implementation_Log.md` for what landed each week.

Terminal Grounds — Logistics is drama. Alien tech is dangerous. Every screenshot should look like a news photo with one impossible detail.

## Notes on the image paths

- If you haven't run the generators yet, the image tags will 404 on GitHub—that's fine. After you run the ArtGen + Unreal Python tools, the paths above will exist and render.
- If your repo uses different import paths, update the `src=` values accordingly.

---

## Quickstart (UE5)

- Open `TerminalGrounds.uproject` in UE 5.4+
- Build targets: Game, Editor, and `TerminalGroundsServer`
- Startup Map: Set in `Config/DefaultGame.ini`
- Tools: See `Tools/Unreal/python/` and `Tools/ArtGen/` for generators and importers

## Repository map

- `Config/` — Engine, Game, and project DeveloperSettings
- `Content/` — UE assets (Maps, Materials, VFX, UI, ConceptArt, etc.)
- `Data/` — Source-of-truth CSVs for datatables (mirrors subset under Content/DataTables)
- `Docs/` — Bibles and guides (Art, VFX, Audio, Lore, Concepts)
- `Plugins/` — Project plugins (TGAttachments, TGModKit)
- `Source/` — C++ modules (TGCore, TGNet, TGCombat, …)
- `Server/` + `Docker/` — Dedicated server packaging and container runtime

## UE asset path index

- Maps
  - Content/TG/Maps/IEZ/ — District lookdev and gameplay maps
  - Content/TG/Maps/TechWastes/ — Wasteland bands and POIs
  - Content/TG/LookDev/ — Auto-generated lookdev grid
- DataTables
  - Content/DataTables/*.csv — In-project datatables (built from `Data/Tables`)
- Materials
  - Content/TG/Materials/
- VFX
  - Content/TG/VFX/
- Audio
  - Content/TG/Audio/
- UI
  - Content/TG/UI/
- Concept Art (references)
  - Content/TG/ConceptArt/
