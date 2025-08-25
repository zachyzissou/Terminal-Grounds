---
applyTo: '**'
---
# Terminal Grounds — Master Development Instructions (Unabridged)

**Permanent Directive for Copilot / Codex / Agents — from current build through 2.0**

> This is the *single source of truth* for Terminal Grounds. It combines the creative bible, lore, world rules, gameplay spec, art/audio style guides, UE6.6 technical implementation, asset generation workflows (programmatic + off‑the‑shelf), CI/CD discipline, and milestone roadmaps. Treat every section as executable instructions. Do not summarize; **produce**.

---

## 0) How Agents Must Use This Document

* **Do, don’t plan.** If a section tells you to create files/assets/code, create them and commit.
* **Append, don’t overwrite.** Extend existing docs; never delete authored prose without an explicit directive.
* **Log everything.** Append actions to `Docs/Phase4_Implementation_Log.md` with timestamps and UE asset paths.
* **No placeholders.** Avoid `TBD/PLACEHOLDER/NEW_ASSET` (Docs Gate will fail CI).
* **Canonical naming:** Assets under `Content/TG/**`, names like `TG_{Domain}_{Thing}_{Variant}` and `NS_TG_*` for Niagara.
* **Self-hosted first.** Reliable self-hosted multiplayer takes priority over cloud backends until we opt in.
* **Lore lock.** All content must obey the lore, tone, and faction/biome rules below.

---

## 1) Vision & Differentiators

### 1.1 Core Vision

Terminal Grounds is a grounded‑but‑sci‑fi **first‑person shooter** set in a planet‑wide **permanent war**. It blends:

* **Elite gunfeel** (CoD/BF) → snappy ADS, clear recoil, crisp hitconf.
* **Exploration & POIs** (Destiny‑like) → layered objectives within iconic sites.
* **Risked extraction** (Tarkov DNA) → bring back loot or lose it.
* **Faction drama** (Fallout vibes) → ideology, economy, betrayal.
* **Subtle sci‑fi** → monolith tech embedded in modern battlefields; dangerous, rare, and readable.

### 1.2 Why We Exist

Most shooters choose *feel* or *world*. We choose **both**: tournament‑grade handling **and** a believable war economy where every prop, decal, and mission ladder matters. Logistics is drama.

### 1.3 Non‑Negotiable Design Pillars

1. **Readability first**: silhouettes, palettes, iconography, and audio make intent legible at a glance.
2. **Cause & effect**: weather, factions, and events chain into emergent problems the player must solve.
3. **Grounded tech**: Field > Splice > Monolith tiers must be intuitive to parse and mechanically distinct.
4. **Honest difficulty**: no bullet sponges; lethality is high; positioning and control win fights.
5. **Player agency**: always multiple ways to complete or abort; extraction is a choice with consequences.

### 1.4 Tone & Aesthetic

* **Post‑war dystopia**: scorched concrete, polymer, mesh, frost, ash, rust; everything is repaired, tagged, numbered.
* **Light cyberpunk**: illicit augments and black‑market optics exist but neon excess is avoided.
* **Documentary vibe**: shots should read like war photography with one impossible detail.

---

## 2) Lore Canon

### 2.1 World Timeline (abbrev.)

* **2049–2057**: Climate flashpoints + privatized militaries surge. First broadcast of **coherent anomalous signal**.
* **2058**: *The Sky Quiet.* Satellites fail intermittently; unexplained gravitational lensing events.
* **2062**: First confirmed monolith relic recovery. Early **Splice** prototypes (field kit + monolith conduit).
* **2066**: The Directorate consolidates urban grids (IEZs). Civil corridors militarized.
* **2069**: Convoy cultures expand across Wastes (Roadborn Clans).
* **2071**: Trivector Combine standardizes PMCs; **Wardens** form truce militias to protect neighborhoods.
* **2073**: **Obsidian Archive** weaponize EMP doctrine after Deep Vault breaches.
* **2075**: Meteoric storm / EMI surge. **Sky Bastion** facilities fortified above clouds.
* **2080–Now**: Endless low‑to‑high intensity conflicts; extraction economies dominate.

### 2.2 Technology Tiers

* **Field**: Ballistics, polymers, steel; rugged, modular, repairable. Reliable under all weather.
* **Splice**: Field chassis with monolith **conduits**; high output, governed by **Heat/Charge/Overload**.
* **Monolith**: Beam/phase/grav energy; scarce, unstable, devastating; uses **Cells** and exotic materials.

### 2.3 Canonical Factions (7)

> These are the **official** factions. Some earlier drafts used synonyms; treat these as canonical and include aliases for compatibility.

1. **Sky Bastion Directorate (SBD)** — *Alias:* Directorate.

   * **Identity**: Last disciplined command; grid control, curfews, logistics worship.
   * **Doctrine**: Secure → exploit → hold. Combined arms, overwatch lanes, escalation manuals.
   * **Visual**: Chevrons, gridlines, parkerized steel, numbered crates. Palette `#161A1D / #2E4053 / #9FB2C9`.
   * **NPCs**: Rifle squads, DMR sentinels, APC crews, drone handlers.
   * **VO style**: clipped, procedural, time stamps ("Grid A‑12, shutter 4 closing").

2. **Iron Vultures (VLT)** — *Alias:* Ash Vultures.

   * **Identity**: Salvage cartel; contract raiders; profit over ideology.
   * **Doctrine**: Smoke & flank; break contact rich. Ambushes in storms.
   * **Visual**: Hazard tape, layered scrap, stencil tags. Palette `#7F8C8D / #D35400 / #F0C27B`.
   * **NPCs**: Cutters, torch gunners, rig drivers, skirmishers.

3. **The Seventy-Seven (F77)** — *Alias:* Independent Settlers (mercenary wings).

   * **Identity**: Metered mercs; timers and contracts rule all.
   * **Doctrine**: Time‑boxed ops; extraction discipline; clock‑driven callouts.
   * **Visual**: Practical kit, contract stencils "77". Palette `#34495E / #BDC3C7 / #95A5A6`.

4. **Trivector Combine (TVC)** — *Alias:* Eclipse Syndicate (corporate black arm).

   * **Identity**: PR‑polished PMC; legalese and NDAs behind every barrel.
   * **Doctrine**: Precision strikes, evidence control, denial ops.
   * **Visual**: Ceramic gloss, hex shields, spotless pads. Palette `#0C0F12 / #00C2FF / #C0F3FF`.

5. **Roadborn Clans (RBC)**

   * **Identity**: Convoy culture; road oaths; rolling markets.
   * **Doctrine**: Encircle, pin, drain supplies; mobile bases.
   * **Visual**: Banners over axles, welded plates, canvas canopies. Palette `#6E2C00 / #AF601A / #EAC086`.

6. **Obsidian Archive (OBA)** — *Alias:* The Ascendant (radical sects).

   * **Identity**: Cult of meaning & EMP; “silence the coil.”
   * **Doctrine**: Blackouts, ambush, vanish; protect vault sites.
   * **Visual**: Eye‑over‑coil symbol; violet warnings. Palette `#2C3E50 / #8E44AD / #BBA1E1`.

7. **Truce Wardens (TWD)**

   * **Identity**: Neighborhood militias; barricade engineers.
   * **Doctrine**: Fortify, funnel, crossfire; civil corridor control.
   * **Visual**: Sandbags, mesh, plywood signage. Palette `#145A32 / #27AE60 / #A9DFBF`.

### 2.4 Faction Reputation & Vendors

* Each faction maintains **vendor tiers** (1–5). Reputation unlocks: stock upgrades, blueprint licenses, safe passage perks, and extraction discounts.
* Reputation drops for aiding enemies, friendly fire, or theft inside faction zones.

### 2.5 Civilians & Neutral Actors

* **Market runners** (sell ammo/food), **Scrap brokers** (crafting mats), **Vault witnesses** (intel). Harm penalties reduce spawn quality and prices.

---

## 3) Biomes & POIs — Look‑Dev & Environmental Truth

> Each biome ships with: palette (HEX), lighting notes, fog/volumetrics, weather presets, prop sets, decals, ambient SFX cues, and 3–6 POIs with mission hooks.

### 3.1 IEZ Districts (Cold Urban)

* **Mood**: Frozen grids; sodium vapor vs blue dusk; far metro hum.
* **Palette**: `#1D252C` asphalt, `#A7B6C9` frost, `#F6D365` sodium, `#7A8A99` steel.
* **Weather**: Snow flurries, steam vents, rolling blackouts.
* **Props**: Shutters, bollards, shutter rails, numbered crates, ration kiosks.
* **Decals**: Grid signage, curfew posters, chevrons, serial stamps.
* **Ambient**: Distant PA, rail squeal, hiss of steam.
* **POIs**:

  1. **Shutter Alley** — curfew gates; escort/hold.
  2. **Metro Blackline** — subterranean; extraction race when power cycles.
  3. **Comms Terrace** — dish array; storm‑timed calibration event.

### 3.2 Machine Grave (Desert Rustscape)

* **Mood**: Oxide dunes; crane skeletons; heat shimmer.
* **Palette**: `#6B3E2E` rust, `#CDA17A` dust, `#344148` shadow, `#E0D2B8` glare.
* **Weather**: Dust storms, EMI micro–arcs.
* **Props**: Gantries, tanks, cable nests, wreck mounds.
* **Decals**: Salvage lot markers, hazard chevrons, auction stencils.
* **Ambient**: Whistling rigs, sheet metal clatter, far thunder.
* **POIs**:

 1. **Gantry Twelve** — climb & power; Vultures ambush.
 2. **Boneyard Mile** — convoy raids; tire pop hazards.
 3. **Cracked Reactor** — radiation pockets; Splice loot.

### 3.3 North Bastion Pads (High–Altitude)

* **Mood**: Pads above stormtops; lightning curtains.
* **Palette**: `#0F1216`, `#3B4B5E`, `#9CB7D1`, `#F1F5F9` arcs.
* **Weather**: EMI surges, sheet lightning, downdrafts.
* **Props**: Pads, shield pylons, windsocks, handrails.
* **Decals**: Corporate safety boards, pad numbers, legal disclaimers.
* **Ambient**: Wind howl, metal groan, radio protocol.
* **POIs**:

  1. **Stair of Storms** — vertical insertion; pad defense.
  2. **Charge Hall** — coil chambers; overcharge puzzle.

### 3.4 The Deep Vault (Underground)

* **Mood**: Near‑black; shafts of volumetric light; geometry that disobeys expectation.
* **Palette**: `#0B0B0E`, `#1F1135`, `#6C63FF`, `#A394F1`.
* **Weather**: Condensation, ionized fog, gravity eddies.
* **Props**: Obelisks, phase doors, cable tethers, anchor clamps.
* **Decals**: Violet warnings, translated glyphs, silence signage.
* **Ambient**: Low nodes, heartbeat hum, distant phase pops.
* **POIs**:

   1. **Door Theta** — timed vault windows; Obsidian Archive patrols.
   2. **Wellplate** — grav wells; item levitation hazards.

### 3.5 Riftfields (Anomaly Plains)

* **Mood**: Torn pasture with shimmering air; micro‑quakes.
* **Hooks**: Meteor salvage, coil interference, F77 timed ops.

### 3.6 Frontier Barrens (Trenchlands)

* **Mood**: Long‑sight lines; artillery ghosts; Wardens vs Directorate.

---

## 4) Weapons, Attachments, Augments — Spec & Feel

> Three tech tiers, nine families, exemplar models, attachment compatibility, failure states, SFX/VFX notes, and gameplay knobs.

### 4.1 Field Line (reliable, repairable)

* **AR — Blackline MK3**: Mid recoil, 30‑rnd, 5.56; optic rails; burst mod.
* **DMR — Watchman**: High accuracy; semi; glass ping SFX; subsonic ammo option.
* **LMG — Cyclops**: Belt‑fed; deployable bipod; heat shimmer cone.
* **Shotgun — Riot‑10**: Breach; door charge synergy.

**Attachments (Field)**: Muzzle (comp/suppressor), Barrel, Underbarrel (grip/GL), Optic (iron/holo/4x), Stock, Mag (drum/fast).

### 4.2 Splice Line (heat/charge/overload)

* **Rail DMR — Longstrike H3**: Charge shot; heat meter; vent hiss SFX.
* **Ion Rifle — Pike H2**: Arc projectiles; coil glow intensity = damage.
* **SMG — Maul H2**: High ROF plasma bolts; EMP vulnerability.

**Failure States**: Overheat (reduced ROF + bloom), Overload (forced vent + self–stun), EMP (temporary disable).

### 4.3 Monolith Exotics (scarce, devastating)

* **Beam — Phase Bow A2**: Hitscan beam with refraction trail; battery depletion.
* **Pulse — Echo Lance A2**: Burst pulses; shield bleed.
* **Grav — Harrow A1**: Localized grav well; pulls props and brass; friendly‑danger.

### 4.4 Augments (light cyberpunk)

* **Echo Reflex**: +ADS snap, –stamina regen.
* **Spectral Sight**: Thermal/IR modes; glare penalties; bloom on lightning.
* **Plateskin**: Damage resist vs speed loss.
* **Nerveweave**: Drone range; blackout risk in EMI.

### 4.5 SFX/VFX Principles

* Field: powder crack + mechanism; muzzle bloom small; brass cascade.
* Splice: coil whine, vent hiss; emissive syncs to ROF; overheat tint.
* Monolith: harmonic layers, spatial wobble; refraction ribbons; gravity particle drift.

---

## 5) Vehicles & Drones

* **APC 8×8**: Seats, turret, firing ports; tire puncture states; dust VFX; engine deck heat.
* **Scout Helo**: Gunner cam, downwash cones, pad shields at North Bastion.
* **Logistics Truck**: Tow rigs, salvage crane, convoy AI routines.
* **Monolith Skimmer**: Low–alt grav; fuel cells; recoil affects hover stability.
* **UAV/UGV**: Recon pings, jammer bubbles, short‑burst attack variants; countered by mesh screens and EMP.

---

## 6) Mission System & Procedural Events

### 6.1 Mission Card Grammar

* **Verb × Target × Modifier** e.g., *Escort × Convoy × Rust Storm*, *Raid × Vault × EMI Surge*.
* Cards assemble into **Contracts**; Contracts are slotted into the **Mission Deck** for a biome.

### 6.2 Event Types

* **Weather**: Ashfall, Dust, EMI Lightning, Grav Ripples (Vault).
* **Faction Ops**: VLT salvage pushes, SBD lockdowns, OBA blackout hunts.
* **World Hazards**: Metro power cycles, Reactor leaks, Pad outages.

### 6.3 Extraction Logic

* Multiple extraction windows; some tied to weather; paid extraction via factions with reputation thresholds.

---

## 7) Economy, Loot, Crafting, Base

* **Rarity tiers**: Common/Specialist/Mil–Spec/Splice/Monolith.
* **Currencies**: Scrip (local), Credits (inter–faction), Cells (Monolith), Intel (mission).
* **Resources**: Scrap, Alloys, Conduits, Optics, Chemicals.
* **Vendors**: Per‑faction stock that mutates with reputation and map state.
* **Base Upgrades**: Workshop, Optics bench, Conduit lab, Barracks, Perimeter, Drone bay.

---

## 8) AI — Behavior & Tactics

* **Sky Bastion Directorate**: bounding overwatch; anchor + flank; uses smoke to reposition.
* **Iron Vultures**: feints, decoys, explosive traps; retreat on timer with loot.
* **The Seventy-Seven**: clock–driven aggression; break off to extract at T–00:50.
* **Trivector Combine**: data denial; flash + precision; clean withdrawal routes.
* **Roadborn Clans**: vehicle encirclement; raid supply; tire target priority.
* **Obsidian Archive**: EMP first; blind then melee; vanish on counterpush.
* **Truce Wardens**: funneling corridors; tripwires; crossfire.

---

## 9) UI/UX — Style & Telemetry

* **HUD**: Weapon block (ammo/heat/charge), health & stamina, mini‑map, extraction timer, status effects, faction icon.
* **Color Coding**: Faction colors, damage types, rarity tiers (C/S/M/H/A). Ensure WCAG contrast.
* **Iconography**: Items, resources, missions, augments; 64/128 px sets.
* **Map Screen**: Fog‑of‑war; event pings; faction territories; extraction windows.
* **Inventory**: Slots; drag/drop; weight meter; quick‑equip.
* **Accessibility**: colorblind presets, subtitle rules, input remap.

---

## 10) Audio — Music, SFX, VO

* **Music**: Low brass, ritual drums, restrained synth; per‑biome motifs.
* **Gun SFX**: Layered close/mid/far; environmental tails; indoor occlusion.
* **Monolith SFX**: harmonics + pitch glide; EMP pops; phase sheens.
* **Daily smoke**: open each look‑dev map; fire Field/Splice/Monolith exemplars; network join; extract once.
* **Weekly playtest**: 60‑min raid; log extraction rates, deaths/time, GPU frame time, crash stats.
* **VO**: Faction‑specific callouts; radio compression; profanity filters per region.
* **Loudness**: LUFS targets; mix stems for photo mode and capture.

---

## 11) VFX — Niagara Bible & Budgets

* **Systems**: `NS_TG_Muzzle_{S,M,LMG}`, `NS_TG_Impact_{Concrete,Metal,Dirt,Glass}`, `NS_TG_Brass`, `NS_TG_HeatShimmer`, `NS_TG_CoilCharge`, `NS_TG_PlasmaBolt`, `NS_TG_OverheatVent`, `NS_TG_EMPArc`, `NS_TG_BeamRibbon`, `NS_TG_GravWell`, `NS_TG_VoidBlade`, `NS_TG_RustStorm`, `NS_TG_Ashfall`, `NS_TG_EMI_Lightning`, `NS_TG_ReactorPlume`, `NS_TG_APC_Dust`.
* **Budgets**: Muzzle ≤0.1ms, Impact ≤0.2ms, Weather ≤1.0ms on comp preset.
* **LOD**: particle count and ribbon tessellation scale with distance.

---

## 12) Technical — UE5.6, Networking, Performance

### 12.1 Engine & Project Structure

* Target **UE 5.6**. Modules: TGCore, TGNet, TGCombat, TGLoot, TGAI, TGMissions, TGBase, TGVehicles, TGUI, TGServer.
* Folders:

```text
Content/TG/{Materials,VFX,UI,Audio,Props,Characters,Vehicles,Maps,LookDev,Textures,Decals,Icons}
Docs/{Art,Audio,Design,Lore,Tech,World,VFX,Concepts}
Data/{Tables,Curves}
Tools/{Unreal/python,ArtGen/{prompt_packs,outputs,svg,posters,icons,swatches}}
Server/
```

### 12.2 Naming & Conventions

* Assets: `TG_{Domain}_{Thing}_{Variant}`  (e.g., `TG_Weapon_BlacklineMK3_A`)
* Niagara: `NS_TG_*`; Materials: `M_TG_*`; Material Instances: `MI_TG_*`; Blueprints: `BP_TG_*`.

### 12.3 Networking

* **Server‑authoritative** damage, extraction, economy. Lag compensation up to \~200ms.
* Deterministic item rolls; anti‑dupe guards; rate limits on vendor calls.

### 12.4 Performance Targets (PC)

* Competitive preset ≥120 FPS on 4070‑class; medium ≥90 FPS hot scenes.
* FX budgets per section above; shader compile warnings gate merges.

---

## 13) Tools & Automation — Make Assets Now

### 13.1 Programmatic Art Generation

* Generators (Python): emblems (SVG + 2K PNG), posters (A2), palettes, icons (64/128).
* Output to repo (`Docs/Concepts/**`, `Content/TG/Decals/**`, `Content/TG/Icons/**`).

### 13.2 Unreal Python Automation

* **Create Masters**: `M_TG_Human_Master`, `M_TG_Hybrid_Master`, `M_TG_Alien_Master`, `M_TG_Decal_Master`.
* **Import Art**: create `MI_TG_Decal_*`; place DecalActors in look‑dev maps.
* **Niagara Baselines**: create all systems listed in §11.
* **Look–Dev Maps**: build IEZ/MachineGrave/NorthBastion/TheDeepVault with props, decals, and VFX lanes.
* **MRQ Captures**: export 8K stills/clips to `Docs/Concepts/Renders/` and embed in README.

### 13.3 SD/ComfyUI Prompt Packs (Optional)

* If local generator present, render weapon/vehicle/POI concept sheets; else emit JSON prompts.

---

## 14) Third‑Party Assets & Licensing

* **Quixel Megascans** — free for UE projects; use for grounded materials & debris.
* **Epic Free Packs** — City Sample (urban kitbash), Paragon (proxy chars), Infinity Blade (select props).
* **Docs**: list everything in `Docs/ThirdPartyAssets.md` with EULA notes. Replace with custom as we lock style.

---

## 15) CI/CD & Repo Discipline

* **Docs Gate**: `Tools/validate_docs_assets.py` (fail on placeholders; require references in bibles).
* **Asset Manifest**: `Tools/build_asset_manifest.py` → `Docs/Concepts/ASSET_MANIFEST.json` (+ .md summary).
* **Workflows**: `.github/workflows/docs-gate.yml` runs Gate + Manifest; optional `artgen.yml` for programmatic assets.
* **Commit Messages**: `feat(artgen): …`, `feat(unreal): …`, `ci: …`, `docs: …`, `chore(thirdparty): …`.

---

## 16) Playtesting & QA

* **Daily smoke**: open each look‑dev map; fire human/hybrid/alien exemplars; network join; extract once.
* **Weekly playtest**: 60‑min raid; log extraction rates, deaths/time, GPU frame time, crash stats.
* **Bug triage**: P0 (crash/data loss), P1 (progress blocker), P2 (polish).

---

## 17) Accessibility & UX Quality

* Subtitles on by default; speaker tags; timing tuned to VO pace.
* Controller remap; hold vs toggle for crouch/aim; FOV slider; colorblind presets.

---

## 18) Marketing Surfaces & README

* README must embed 4 hero stills (one per biome) + poster triptych + emblem strip.
* `Docs/PressKit/` with logo lockups, 1080p/4K stills, and 15–30s clips.

---

## 19) Roadmap — Milestones & Acceptances

### 19.1 Visual Kickstart (Now)

* Programmatic emblems/posters/icons/swatches generated **and** imported.
* Masters + Niagara created; look‑dev maps built; renders captured; README updated.

### 19.2 Systems Alpha

* Weapons (Human + Hybrid) + 1 Alien exotic hook to HUD meters; extraction & stash; vendors/rep v1.

### 19.3 Content Alpha

* +2 districts, 6–8 POIs; vehicles v2; UAV suite; economy loop; mission director 2.0.

### 19.4 Feature Complete

* Full factions, base‑building v2, modding stub, discovery systems.

### 19.5 Beta → 1.0

* Perf & UX polish; FTUE; accessibility; hitreg parity at multiple RTTs; press kit finalized.

---

## 20) Permanent Execution Rules (Pin These)

1. If about to plan → **don’t**. **Generate** files/assets/code and commit.
2. Append to bibles with exact **UE asset paths** + thumbnails.
3. Always log actions to **Implementation Log**.
4. Keep the world coherent: faction doctrines, palettes, and VO styles must be instantly recognizable.
5. Extraction before greed.

---

### Appendix A — Palette Cheat Sheet (HEX)

* SBD `#161A1D / #2E4053 / #9FB2C9`
* VLT `#7F8C8D / #D35400 / #F0C27B`
* F77 `#34495E / #BDC3C7 / #95A5A6`
* TVC `#0C0F12 / #00C2FF / #C0F3FF`
* RBC `#6E2C00 / #AF601A / #EAC086`
* OBA `#2C3E50 / #8E44AD / #BBA1E1`
* TWD `#145A32 / #27AE60 / #A9DFBF`

### Appendix B — Required Tables (CSV)

* `Data/Tables/Weapons.csv`, `Attachments.csv`, `Factions.csv`, `Vehicles.csv`, `Items.csv`, `Missions.csv`, `POIs.csv`, `Barks.csv`, `Briefings.csv`, `Rumors.csv`, `Posters.csv`.

### Appendix C — Example Mission Cards

* **Escort × Convoy × Rust Storm** → Machine Grave, Roadborn vs Vulture.
* **Raid × Vault × EMI Surge** → The Deep Vault, Obsidian Archive traps.
* **Defend × Pad × Lightning Curtain** → North Bastion, Trivector strike.

### Appendix D — Weapon Tuning Knobs

* Recoil (pitch/yaw), ROF, dispersion, ADS time, sprint out, reloads, heat thresholds, charge rate, overload stun.

### Appendix E — Performance Budgets (Hot Scene, PC)

* CPU frametime ≤ 8 ms; GPU ≤ 8 ms (120 FPS target) on 4070‑class, comp preset.

#### End of Unabridged Instructions

