# Terminal Grounds

Terminal Grounds is an Unreal Engine 5.4 project: a session-based salvage/extraction game set after the Shattered Accord. Explore contested POIs, complete contracts, and extract what you can—alone or with a crew—while factions clash over technology from Human, Hybrid, and Alien origins.

"The siren on the evac corridor cuts through rust-wind. You shoulder a crate of Harvester cells; your radio crackles—Wardens closing the lane. Two turns to reach the rally point. You either drop the weight, or drop the dream of leaving this zone alive."

## Status

Work in progress. Active development across gameplay, art, and backend.

## Getting started
# Terminal Grounds

Modern warfare at the end of the world.

Terminal Grounds is a high-fidelity first-person shooter where disciplined gunplay collides with salvaged Hybrid (human + alien) tech in a planet-wide war that never ended. Raid volatile front lines, steal tech that shouldn’t exist, build your foothold—and extract alive.

> Tight CoD/BF-style shooting. Tarkov-grade risk. Fallout-level faction drama. Subtle, dangerous sci-fi.

Why this game?

Because modern shooters either feel great but say nothing, or have ambition without feel. Terminal Grounds aims for both: elite handling and a world with rules—where every weapon, decal, and mission has a place in the war economy.

Influences (vibes, not clones): Call of Duty, Battlefield, Escape from Tarkov, Fallout, Alien, Starship Troopers, Ender’s Game, The Lost Fleet, Warhammer (aesthetic clarity), a light touch of cyberpunk (illicit augments, not neon theme parks).

## What is Terminal Grounds?

- A grounded FPS with snappy ADS, predictable recoil, readable damage, and server-authoritative hitreg.
- A living warzone where factions fight, weather shifts, and procedural events (convoys, storms, alien vault windows) change your plan mid-mission.
- An extraction loop where you choose to push your luck or leave rich—and then reinvest in attachments, augments, vehicles, and base upgrades.
- Self-hosted multiplayer first, so squads can own their sessions; scalable backend later if the war goes global.

## Core Features

- Elite Gunfeel — CoD/BF-caliber handling: crisp ADS, clean flinch, clear hit feedback.
- Three Tech Tiers
  - Human: rugged, reliable ballistics.
  - Hybrid: experimental conduits and coils; powerful but overheats/overloads.
  - Alien: rare beam/grav/phase weapons—short supply, huge consequences.
- Faction Identity — Silhouette, palette, doctrine, and VO that read instantly in combat.
- Dynamic Missions & Events — Contracts composed of Verb × Target × Event (Escort/Defend/Raid × Grid/Convoy/Vault × Storm/Meteor/Swarm/Blackout).
- Extraction & Economy — Risk-weighted loot, reputation vendors, crafting at your base.
- Vehicles & Drones — APCs, scout helos, logistics trucks, recon/attack drones—and one terrifying alien skimmer.
- Weather as Drama — Ashfall, dust, electromagnetic interference; storms change visibility and tactics.
- Environmental Truth — Propaganda, serial-stamped crates, sandbag corridors; everything is scuffed, reused, repaired.

## Factions at a Glance

| Faction | Who they are | How they fight | Their look |
| --- | --- | --- | --- |
| Directorate (DIR) | The last disciplined command | Secure → exploit; bounding overwatch | Parkerized steel, chevrons, numbered crates |
| Vultures Union (VLT) | Salvage cartel | Smoke & flank; retreat rich | Layered scrap, hazard tape, spray tags |
| Free 77 (F77) | Metered mercenaries | Time-boxed ops; clean extracts | Practical kit, contract stencils |
| Corporate Combine (CCB) | PR-polished PMC | Precision strikes; legalese aftercare | Ceramic gloss, hex badges, spotless pads |
| Nomad Clans (NMD) | Convoy culture | Encircle and run you dry | Banners, axle icons, rusted plates |
| Vaulted Archivists (VAC) | Cult of meaning & EMP | Ambush, blind, vanish | Eye/coil symbols; violet warnings |
| Civic Wardens (CWD) | Neighborhood militias | Fortify, funnel, crossfire | Sandbags, mesh screens, plywood signage |

<!-- Faction emblem strip (images appear after generators/import run) -->
![DIR](Content/TG/Decals/Factions/Directorate_2K.png) ![VLT](Content/TG/Decals/Factions/VulturesUnion_2K.png) ![F77](Content/TG/Decals/Factions/Free77_2K.png) ![CCB](Content/TG/Decals/Factions/CorporateCombine_2K.png) ![NMD](Content/TG/Decals/Factions/NomadClans_2K.png) ![VAC](Content/TG/Decals/Factions/VaultedArchivists_2K.png) ![CWD](Content/TG/Decals/Factions/CivicWardens_2K.png)

## Where you’ll fight (Biomes & POIs)

- IEZ Districts — Frozen urban corridors; sodium vapor vs snow haze; the Blackline metro hum underfoot.
- Tech Wastes — Oxide dunes and crane skeletons; EMI micro-storms tick your radio.
- Sky Bastion — Corporate helipads above stormclouds; lightning arcs cut the fog.
- Black Vault — Buried alien doors; gravity anomalies; violet volumetrics.

<!-- Biome look-dev strip (images appear when available) -->
![IEZ palette](Docs/Concepts/Renders/IEZ_palette.png) ![Tech Wastes palette](Docs/Concepts/Renders/Wastes_palette.png)

![Sky Bastion storm](Docs/Concepts/Renders/SkyBastion_storm.png) ![Black Vault mood](Docs/Concepts/Renders/BlackVault_mood.png)

## How it plays (the loop)

- Brief — Pick a contract; check weather and faction activity.
- Insert — By truck, helo, or on foot; choose approach and time-of-day.
- Engage — Tight room-clears, smart overwatch, controlled bursts.
- React — Storms roll in, vault windows open, enemy convoys spawn. Decide: push or extract.
- Extract — Evade or smash through; the stash only matters if you make it out.
- Invest — Attachments, augments, vehicles, base upgrades, reputation unlocks.

Short, sharp raids. Or long, brutal grinds. Your risk, your reward.

## Weapons, Attachments, Augments

- Human — Blackline MK3 (AR), Watchman (DMR), Cyclops (LMG), Riot-10 (Shotgun). Predictable recoil, clear irons/holos, reliable mags.
- Hybrid — Longstrike H3 (rail DMR), Ion Pike H2 (rifle), Maul H2 (SMG): heat/charge/overload mechanics, vent hiss, bright coils.
- Alien — Phase Bow A2 (beam), Echo Lance A2 (pulse), Grav Harrow A1 (well). Small cells, big consequences.
- Attachments — Barrel/Muzzle/Optic/Underbarrel/Stock/Mag/Module. Alien modules require adapters and announce themselves visually.
- Augments — Reflex Splice (snappier ADS, stamina hit), Ocular Suite (thermal/IR; glare penalties), Subdermal Plating (DR vs speed), Neural Slicer (drone range vs blackout risk).

<!-- Weapon line art (auto-embeds as assets arrive) -->
![Blackline MK3](Docs/Concepts/AI/Weapons_Blackline_MK3.png) ![Longstrike H3](Docs/Concepts/AI/Weapons_Longstrike_H3.png) ![Phase Bow A2](Docs/Concepts/AI/Weapons_PhaseBow_A2.png)

## Vehicles & Drones

- APC 8×8 — Seats, turret, firing ports; tire damage states; engine-deck heat shimmer.
## Terminal Grounds

Modern warfare at the end of the world.

Terminal Grounds is a high-fidelity first-person shooter where disciplined gunplay collides with salvaged Hybrid (human + alien) tech in a planet-wide war that never ended. Raid volatile front lines, steal tech that shouldn’t exist, build your foothold—and extract alive.

    Tight CoD/BF-style shooting. Tarkov-grade risk. Fallout-level faction drama. Subtle, dangerous sci-fi.

<!-- ===== HERO IMAGES (auto-show once renders exist) ===== -->
<p align="center">
  <img src="Docs/Concepts/Renders/Hero.png" alt="Hero — Visual Kickstart" width="90%"/>
</p>

### Why this game?

Because modern shooters either feel great but say nothing, or have ambition without feel. Terminal Grounds aims for both: elite handling and a world with rules—where every weapon, decal, and mission has a place in the war economy.

Influences (vibes, not clones): Call of Duty, Battlefield, Escape from Tarkov, Fallout, Alien, Starship Troopers, Ender’s Game, The Lost Fleet, Warhammer (aesthetic clarity), a light touch of cyberpunk (illicit augments, not neon theme parks).

### What is Terminal Grounds?

- A grounded FPS with snappy ADS, predictable recoil, readable damage, and server-authoritative hitreg.
- A living warzone where factions fight, weather shifts, and procedural events (convoys, storms, alien vault windows) change your plan mid-mission.
- An extraction loop where you choose to push your luck or leave rich—and then reinvest in attachments, augments, vehicles, and base upgrades.
- Self-hosted multiplayer first, so squads can own their sessions; scalable backend later if the war goes global.

## Core Features

- Elite Gunfeel — CoD/BF-caliber handling: crisp ADS, clean flinch, clear hit feedback.
- Three Tech Tiers
  - Human: rugged, reliable ballistics.
  - Hybrid: experimental conduits and coils; powerful but overheats/overloads.
  - Alien: rare beam/grav/phase weapons—short supply, huge consequences.
- Faction Identity — Silhouette, palette, doctrine, and VO that read instantly in combat.
- Dynamic Missions & Events — Contracts composed of Verb × Target × Event (Escort/Defend/Raid × Grid/Convoy/Vault × Storm/Meteor/Swarm/Blackout).
- Extraction & Economy — Risk-weighted loot, reputation vendors, crafting at your base.
- Vehicles & Drones — APCs, scout helos, logistics trucks, recon/attack drones—and one terrifying alien skimmer.
- Weather as Drama — Ashfall, dust, electromagnetic interference; storms change visibility and tactics.
- Environmental Truth — Propaganda, serial-stamped crates, sandbag corridors; everything is scuffed, reused, repaired.

## Factions at a Glance

| Faction | Who they are | How they fight | Their look |
|---|---|---|---|
| Directorate (DIR) | The last disciplined command | Secure → exploit; bounding overwatch | Parkerized steel, chevrons, numbered crates |
| Vultures Union (VLT) | Salvage cartel | Smoke & flank; retreat rich | Layered scrap, hazard tape, spray tags |
| Free 77 (F77) | Metered mercenaries | Time-boxed ops; clean extracts | Practical kit, contract stencils |
| Corporate Combine (CCB) | PR-polished PMC | Precision strikes; legalese aftercare | Ceramic gloss, hex badges, spotless pads |
| Nomad Clans (NMD) | Convoy culture | Encircle and run you dry | Banners, axle icons, rusted plates |
| Vaulted Archivists (VAC) | Cult of meaning & EMP | Ambush, blind, vanish | Eye/coil symbols; violet warnings |
| Civic Wardens (CWD) | Neighborhood militias | Fortify, funnel, crossfire | Sandbags, mesh screens, plywood signage |

<!-- ===== FACTION EMBLEM STRIP (uses ArtGen outputs after import) ===== -->
<p align="center">
  <img src="Content/TG/Decals/Factions/Directorate_2K.png" alt="DIR" height="90"/>
  <img src="Content/TG/Decals/Factions/VulturesUnion_2K.png" alt="VLT" height="90"/>
  <img src="Content/TG/Decals/Factions/Free77_2K.png" alt="F77" height="90"/>
  <img src="Content/TG/Decals/Factions/CorporateCombine_2K.png" alt="CCB" height="90"/>
  <img src="Content/TG/Decals/Factions/NomadClans_2K.png" alt="NMD" height="90"/>
  <img src="Content/TG/Decals/Factions/VaultedArchivists_2K.png" alt="VAC" height="90"/>
  <img src="Content/TG/Decals/Factions/CivicWardens_2K.png" alt="CWD" height="90"/>
</p>

## Where you’ll fight (Biomes & POIs)

- IEZ Districts — Frozen urban corridors; sodium vapor vs snow haze; the Blackline metro hum underfoot.
- Tech Wastes — Oxide dunes and crane skeletons; EMI micro-storms tick your radio.
- Sky Bastion — Corporate helipads above stormclouds; lightning arcs cut the fog.
- Black Vault — Buried alien doors; gravity anomalies; violet volumetrics.

<!-- ===== BIOME LOOK-DEV STRIP ===== -->
<p align="center">
  <img src="Docs/Concepts/Renders/IEZ_Day.png" alt="IEZ Day" width="45%"/>
  <img src="Docs/Concepts/Renders/IEZ_Night.png" alt="IEZ Night" width="45%"/>
</p>
<p align="center">
  <img src="Docs/Concepts/Renders/SkyBastion_Day.png" alt="Sky Bastion Day" width="45%"/>
  <img src="Docs/Concepts/Renders/BlackVault_Night.png" alt="Black Vault Night" width="45%"/>
</p>

## How it plays (the loop)

- Brief — Pick a contract; check weather and faction activity.
- Insert — By truck, helo, or on foot; choose approach and time-of-day.
- Engage — Tight room-clears, smart overwatch, controlled bursts.
- React — Storms roll in, vault windows open, enemy convoys spawn. Decide: push or extract.
- Extract — Evade or smash through; the stash only matters if you make it out.
- Invest — Attachments, augments, vehicles, base upgrades, reputation unlocks.

Short, sharp raids. Or long, brutal grinds. Your risk, your reward.

## Weapons, Attachments, Augments

- Human — Blackline MK3 (AR), Watchman (DMR), Cyclops (LMG), Riot-10 (Shotgun). Predictable recoil, clear irons/holos, reliable mags.
- Hybrid — Longstrike H3 (rail DMR), Ion Pike H2 (rifle), Maul H2 (SMG): heat/charge/overload mechanics, vent hiss, bright coils.
- Alien — Phase Bow A2 (beam), Echo Lance A2 (pulse), Grav Harrow A1 (well). Small cells, big consequences.
- Attachments — Barrel/Muzzle/Optic/Underbarrel/Stock/Mag/Module. Alien modules require adapters and announce themselves visually.
- Augments — Reflex Splice (snappier ADS, stamina hit), Ocular Suite (thermal/IR; glare penalties), Subdermal Plating (DR vs speed), Neural Slicer (drone range vs blackout risk).

<!-- ===== WEAPON LINE ART (prompted renders as they land) ===== -->
<p align="center">
  <img src="Docs/Concepts/AI/Weapons_Blackline_MK3.png" alt="Blackline MK3 concept" width="31%"/>
  <img src="Docs/Concepts/AI/Weapons_Longstrike_H3.png" alt="Longstrike H3 concept" width="31%"/>
  <img src="Docs/Concepts/AI/Weapons_PhaseBow_A2.png" alt="Phase Bow A2 concept" width="31%"/>
</p>

## Vehicles & Drones

- APC 8×8 — Seats, turret, firing ports; tire damage states; engine-deck heat shimmer.
- Scout Helo — Stabilized gunner, downwash cones, storm-shielded pads.
- Logistics Truck — Rig salvage, tow stranded assets, anchor convoys.
- Alien Skimmer (rare) — Low-alt grav hover; unforgiving fuel cells; punishing recoil on beam fire.
- UAV/UGV — Recon snapshots, jammer bubbles, short-burst attack drones (countered by mesh screens).

## Screenshots & Concept (auto-generated as we build)

- Faction emblems & propaganda posters → `Content/TG/Decals/**` + `Docs/Concepts/Posters/`
- Look-dev renders → `Docs/Art/LookDevRenders/` (README pulls images from here when available)
- UI icon sets → `Content/TG/Icons/`
- Asset manifest → `Docs/Tech/asset_manifest.json`

Our pipeline programmatically generates and imports decals/posters/icons, then wires them to masters and look-dev maps. Renders get auto-embedded here as they land.

<!-- ===== POSTER WALL (once ArtGen runs) ===== -->
<p align="center">
  <img src="Docs/Concepts/Posters/DIR_HOLD_THE_LINE.png" alt="DIR Poster" width="30%"/>
  <img src="Docs/Concepts/Posters/VLT_SALVAGE_FEEDS_THE_WAR.png" alt="VLT Poster" width="30%"/>
  <img src="Docs/Concepts/Posters/CCB_PUBLIC_SAFETY_EVENT.png" alt="CCB Poster" width="30%"/>
</p>

## Roadmap (high level)

0.4 Visual Kickstart — Materials, Niagara baselines, look-dev scenes, posters/emblems in-engine, first renders.

0.5 Systems Alpha — Weapons (Human+Hybrid), one Alien exotic, extraction + stash, vendors/rep v1, Mission Director 2.0.

0.6 Content Alpha — +2 districts, 6–8 POIs, vehicles v2, UAV suite, attachments pass, economy loop.

0.7 Feature Complete — Full faction set, base building v2, modding sample, discovery stub.

0.8 Beta — Perf/UX polish, FTUE, accessibility, hitreg parity at 60/120/180ms RTT.

1.0 Launch — Stable builds, docs + SDK, live presets, day-one patch.

Full details in ROADMAP.md.

## Play the current slice

Self-hosted (listen or dedicated)

Windows (PowerShell)

```
Server\run_server.ps1
```

Linux/macOS

```
bash Server/run_server.sh
```

In-editor: open a look-dev map:

- `Content/TG/LookDev/L_TG_LookDev.umap` (generated by tools_build_lookdev_level)

## Contributing

We’re welcoming focused contributions while we lock core feel and identity.

- Read `Docs/TERMINAL_GROUNDS_MASTER_REFERENCE_AND_BUILD_BRIEF.md`.
- Follow naming & paths: `Content/TG/...`, `TG_{Domain}_{Thing}_{Variant}`.
- No “temp/placeholder” strings; our Docs Gate CI will fail PRs that include them.
- Add UE asset paths in bibles when you land content.
- Attach 1–3 in-engine screenshots to your PR.

## System Targets (WIP)

- Engine: Unreal Engine 5 (Lumen + Nanite).
- Perf: Competitive preset ≥120 FPS (FX ≤3 ms), Medium ≥90 FPS in hot scenes.
- PC: 8C/16T CPU, 16–32 GB RAM, RTX 3070/4070-class GPU or equivalent.

## Press & Community

- Wishlist: (link soon) • Discord: (invite soon)
- See `Docs/Phase4_Implementation_Log.md` for what landed each week.

Terminal Grounds — Logistics is drama. Alien tech is dangerous. Every screenshot should look like a news photo with one impossible detail.

## Notes on the image paths

- If you haven’t run the generators yet, the image tags will 404 on GitHub—that’s fine. After you run the ArtGen + Unreal Python tools, the paths above will exist and render.
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
- `docs/` — Bibles and guides (Art, VFX, Audio, Lore, Concepts)
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
