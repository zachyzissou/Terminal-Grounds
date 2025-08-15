# Terminal Grounds Lore Bible (Canon)

Version: 1.0.0

Owners: Narrative (Primary), Design, Art

Last Updated: 2025-08-13

Scope: Canonical worldbuilding for Terminal Grounds across all disciplines.

Change Policy: Canon edits require “lore-change” PR label, narrative approval, and a changelog entry. Summaries must link here; duplication prohibited.

Index

- Themes & Tone (#themes)
- Canon Rules (#canon-rules)
- Timeline (#timeline)
- Cosmology & Harvesters (#cosmology)
- World & Regions (#world)
- Factions (#factions)
- Characters (#characters)
- Technology & Augments (#technology)
- Points of Interest (#pois)
- Culture & Language (#culture)
- Law, Conflict, Economy (#society)
- Glossary & Style Guide (#glossary)
- Cross-Discipline Notes (#cross-discipline)
- Changelog (#changelog)

## Themes & Tone {#themes}

Pillars

- Grounded military desperation: logistics, lines of supply, worn kit, triage choices.
- Salvage economy: scarcity breeds ingenuity; everything is modular, repurposed, re-soldered.
- Cosmic dread: alien tech functions but defies understanding; it changes people who use it.

No-go list

- Full cyberpunk replacement society (we are military/scavenger first, cyber as seasoning).
- Full alien presence (Harvesters are absent; their relics are the antagonist).
- Deus ex machina tech: alien devices must have costs, constraints, and failure modes.

## Canon Rules {#canon-rules}

- What is canon: this Lore Bible and any section it explicitly links as canon.
- What isn’t: summaries, art/style docs, marketing blurbs, and tool prompts (unless linked here).
- IDs: Stable IDs across docs, tools, and UE assets. Prefixes:
	- Factions FCT_*, Regions REG_*, POIs POI_*, Events EVT_*, Characters CHR_*, Tech TEC_*
- Retcons: Must include a changelog entry and a migration note for affected IDs.

## Timeline {#timeline}

- EVT_FIRST_CONTACT (2147–2149): Non-responsive alien craft observed in deep orbit. “Harvesters” enter inner system, leaving Lagrange artifacts and seeding micro-probes planet-wide. No direct contact.
- EVT_RECONSTRUCTION_ACCORD (2139–2159): After cascading climate/war disasters, the Global Reconstruction Accord unifies logistics and standards. The Accord is brittle but effective.
- EVT_WRECK_DISCOVERY (2156): First intact Skimmer-class wreck recovered off the Azores shelf. Power cells trigger localized EMP; early hybrids emerge.
- EVT_SALVAGE_ACTS (2158): Competing corporate charters (Vector Dynamics, Helix Industries, Sigma Collective) secure exclusive salvage zones. Black markets emerge around “blue ash” (Harvester alloy microdust).
- EVT_SHATTERED_ACCORD (2159–2161): Salvage disputes escalate into the War of Broken Chains. Accord fractures under corporate PMCs and rogue military formations.
- EVT_IEZ_CASCADE (2161-06): Monolith-class excavation triggers a six-week EMP cascade over a 200 km radius; clocks desync, drones go feral, city cores black out. The Interdiction Exclusion Zone (IEZ) is declared.
- Present Day (2161-12): Six months after the cascade. Factions encircle the IEZ. Whoever masters the wrecks decides the world’s next order.

## Cosmology & Harvesters {#cosmology}

- The Harvesters: Automated extractors. Purpose unknown. Wreck typology suggests reconnaissance (Skimmer), combat/logistics (Harrower), and deep infrastructure (Monolith).
- Linguistic artifacts: Emissions show prime harmonics and non-integer frequency lattices. Archivists’ “Cant” borrows terms from these patterns.
- Wreck Classification:
	- TEC_SKIMMER: 50–100m; basic energy systems, survey arrays; reliable hybridization source.
	- TEC_HARROWER: 200–500m; weaponized arrays, defensive drones; unstable but powerful yields.
	- TEC_MONOLITH: 1–5km; field manipulators (gravity, time-phase); catastrophic side effects.
- Field effects:
	- EMP lattices (Harrower): Decay in minutes but leave sensor ghosts for days.
	- Temporal jitter (Monolith): Misaligned oscillator drift, subjective time distortions in proximity.
	- Psychotropic resonance: Long exposure correlates with derealization, intrusive patterning.

## World & Regions {#world}

- REG_IEZ — Interdiction Exclusion Zone
	- The 200 km radius “dead-sky” where Monolith-caused cascade originated. Outer bands are salvageable; inner core remains jitter-locked. Terrain: tilted ferrocrete, melted rails, monolithic shadows.
	- Hazards: rolling EMP microbursts, phase shears, drone reactivation events.
	- Logistics: convoy cords and shielded relays, “breadcrumb” Faraday shelters.
- REG_TECH_WASTES — De-industrial belts
	- Semi-autonomous factories stutter to life with scavenged power. Corporate Combine and Archivists contest control.
- REG_METRO_A — Metro Maintenance A
	- Subterranean neutral ground enforced by Wardens’ tolls and truce rules.
- REG_CRIMSON_DOCKS — Salvage port
	- Vultures Union hub. The red-stained quays are both market and battleground.
- REG_SKY_BASTION — Directorate mountain stronghold
	- A high-altitude fortress with reinforced hangars and long-range comms arrays.
- REG_BLACK_VAULT — Subterranean complex of unknown origin
	- Claimed by Archivists; rumored pre-Harvester. Emits intermittent prime harmonics.

## Factions {#factions}

- FCT_DIR — Directorate
	- Philosophy: Order through discipline; legitimacy by continuity of command.
	- Territory: Sky Bastion, IEZ northern districts.
	- Tech Focus: Human-tier reliability; rigorously vetted hybrids.
	- Structure: Field Legions, Logistics Corps, Signals Authority.
	- Slogans: “Order from Chaos.”
	- Signature: Standardized kit, clean stenciling, disciplined comms.
- FCT_VUL — Vultures Union
	- Philosophy: Survival through salvage; markets as mediation.
	- Territory: Crimson Docks; roving scavenger flotillas.
	- Tech Focus: Jury-rigged hybrids; drone tethering.
	- Slogans: “From Scrap, Strength.”
	- Signature: Panel-patched armor, visible welds, colored tarps.
- FCT_F77 — Free 77
	- Philosophy: Contract pragmatism; competence as currency.
	- Territory: Itinerant; agency offices in neutral nodes.
	- Tech Focus: Balanced loadouts tailored to contracts.
	- Slogans: “Contract Complete.”
	- Signature: Mixed camo, modular kit, invoice tags on crates.
- FCT_CCB — Corporate Combine
	- Philosophy: Progress by supremacy of technology.
	- Territory: Tech Wastes, R&D pads, secured corridors.
	- Tech Focus: Prototype hybrids, dangerous edge cases.
	- Slogans: “Through Technology, Tomorrow.”
	- Signature: Polished composites, neon diagnostics, NDA stamps.
- FCT_NOM — Nomad Clans
	- Philosophy: Freedom through mobility; roads as lifelines.
	- Territory: Convoy-cities; seasonal routes.
	- Tech Focus: Vehicle mods; logistics systems; quick-deploy fortifications.
	- Slogans: “The Road Endures.”
- FCT_VAR — Vaulted Archivists
	- Philosophy: Knowledge as salvation; reality is a system to be studied.
	- Territory: Black Vault, hidden labs.
	- Tech Focus: EMP, stealth, sensor manipulation; pure artifact studies.
	- Slogans: “Knowledge Preserves.”
- FCT_CWD — Civic Wardens
	- Philosophy: Mutual aid through defense of civilians.
	- Territory: Metro Maintenance A; safe nodes; settlement belts.
	- Tech Focus: Hardening, shields, counter-drone networks.
	- Slogans: “We Stand Together.”

### Event-Only/Secret Aggressors

- FCT_BSK — Black Sky Charter
	- Modus: Off-books aerospace cell with legacy targeting stacks. Visible only during Skyfall. Laser-designation teams, decoy beacons, area denial.
- FCT_NCH — Null Choir
	- Modus: Archivist splinter; silent-cant ops; EMP/shadow kit; appears during Harmonic Windows and in Phase Pockets.
- FCT_MSN — Monolith Sentinels
	- Modus: Autonomous Harvester constructs; guard harmonics, punish energy spikes.

## Characters {#characters}

- CHR_ADELE_VARGAS (FCT_DIR) — Marshal of the Northern Districts
	- Background: Kept a corps intact through the Accord collapse by rationing reputation as carefully as munitions.
	- Motivation: Restore a chain of command the world can trust.
	- Conflict: Needs hybrid superiority she distrusts; leans on Archivist intel she resents.
- CHR_RIN_OKAFOR (FCT_VUL) — Union Broker of Crimson Docks
	- Background: Scrap dealer turned market architect; built arbitration rituals that keep the Docks from burning daily.
	- Motivation: Make salvage law stronger than faction law.
	- Conflict: Convoy raids keep the docks fed—but destabilize treaties.
- CHR_JAX_KORDER (FCT_F77) — Contract Captain
	- Background: Former signals NCO; now runs a debt-free, high-competence crew.
	- Motivation: Keep his crew alive and solvent; “no unwinnable contracts.”
	- Conflict: A mysterious client insists on Monolith artifacts with no paper trail.
- CHR_ELI_ZHOU (FCT_CCB) — Combine Program Director
	- Background: Skimmer-core prodigy; negotiates power as well as prototypes.
	- Motivation: Publish a breakthrough and secure Combine’s mandate.
	- Conflict: Suppresses a safety report on temporal jitter to hit a demo window.
- CHR_SABLE_KHAN (FCT_NOM) — Road Mother of the Ashway
	- Background: Third-generation convoy leader; carries the codex of routes.
	- Motivation: Keep the road sovereign; barter safety for the clans.
	- Conflict: IEZ detours add fatal risk; Wardens’ tolls creep upward.
- CHR_DOCTOR_IVEY (FCT_VAR) — Vault Lexicographer
	- Background: Compiles a grammar of Harvester harmonics.
	- Motivation: Understand the Monolith before the Monolith understands us.
	- Conflict: Quietly addicted to psychotropic resonance.
- CHR_LUPE_SANTOS (FCT_CWD) — Warden Captain
	- Background: Former firefighter; turned district guardian.
	- Motivation: Keep the tunnels safe and the truce sacred.
	- Conflict: Choose between guarding med caravans and escorting refugee trains.

## Technology & Augments {#technology}

Tiers

- TEC_HUMAN — Reliable, maintainable, well-documented. Countered by armor and alien shields.
- TEC_HYBRID — Powerful but heat/EMP/overdraw risks; requires cooldown disciplines and power budget planning.
- TEC_ALIEN — Rare, reality-bending effects; no repair; user psych cost.

Representative Systems

- Exergy Cells (hybrid power): Thermal derating curve; unsafe above 83°C junction.
- Coil-Plasma Rails: Muzzle bloom betrays position; ferrous debris ingestion risk.
- Phase Shields: Block high-velocity projectiles; leak to low-speed penetrators.
- Drone Tethers: Vulnerable to harmonic spiking; Wardens deploy “Chimes” (acoustic de-sync towers).

Augmentation Suite

- AUG_REFLEX_SPLICE — Reaction boost; nervous system cascade risk; incompatible with Neural Slicer.
- AUG_OCULAR_SUITE — Multi-spectrum targeting; hallucination side-effect.
- AUG_SUBDERMAL_PLATE — +DR; mobility reduction, chronic inflammation.
- AUG_NEURAL_SLICER — Tactical awareness, direct equipment interfacing; personality drift; blackout events.

Countermeasures

- EMP curtains (Wardens) vs hybrid drones.
- Faraday routing in vehicles (Nomads) vs phase bleed.
- Cooling lattice overlays (Combine) vs coil overrun.

## Points of Interest {#pois}

- POI_SKY_BASTION — Directorate High Fortress
	- Function: Command, long-range comms, artillery oversight.
	- Hooks: Sabotage uplink arrays; negotiate med-flight passage; intercept a Combine demo.
- POI_CRIMSON_DOCKS — Union Market Quays
	- Function: Salvage exchange, arbitration, refit yards.
	- Hooks: A rigged auction; drone hive under slipway twelve.
- POI_METRO_A — Warden Toll Tunnels
	- Function: Neutral passage, smuggling, truce.
	- Hooks: Escort a convoy; dismantle a black-ICE relay.
- POI_BLACK_VAULT — Archivist Depths
	- Function: Artifact study, containment.
	- Hooks: Rescue a lexicographer; silence a harmonic beacon.
- POI_IEZ_OUTER_RING — Salvage Fields
	- Function: Hybrid component harvest.
	- Hooks: Meteor salvage scramble; phase shear collapse; convoy standoff.

### IEZ Structure and Hardcore Play

- Rings: Outer (H1), Median (H2), Core (H3). Hazard and loot scale by ring.
- Phase Pockets: Temporary high-intensity zones that inherit base ring difficulty with event modifiers.
- Hardcore flags: H1/H2/H3 define AI comps, damage multipliers, respawn/extraction rules. H3 is one-life, extraction only at contested pads.

## Culture & Language {#culture}

Naming conventions

- Directorate: rank + surname; unit numerals (e.g., “Marshal Vargas, 3rd Signals”).
- Union: callsigns from trade (e.g., “Sawtooth,” “Blue Ash”).
- Combine: project-first (e.g., “PD-71 Zhou, Program Hyacinth”).
- Nomads: route lineage (e.g., “Sable Khan of the Ashway”).
- Wardens: post/location call (e.g., “Captain Santos, Gate 5”).

Idioms

- “Salvage before the storm” (act before the EMP cycle)
- “EMP’d and forgotten” (ruined beyond repair)
- “Harvester blessed” (luck, often ironic)
- “Pre-cascade thinking” (naïve)

Observances

- The Quiet Watch (Wardens): hour of radio silence for lost responders.
- Blue Ash Day (Union): alloy dust festival after the first big sale.
- Accordnight (Directorate): remembrance of fallen command.

## Law, Conflict, Economy {#society}

Law

- Docks Arbitration: Three-marker ritual; markers forfeited for breaking truce.
- Warden Tolls: flat rate plus tonnage; medical convoys discounted.

Economy

- Currencies: Credits (backed by verified salvage), barter, labor hours.
- Value Chain: Wreck → Strip → Grade → Refit → Certify → Auction.

Conflict Patterns

- Convoy Wars: Clans vs raiders; F77 hired by either side.
- Drone Swarms: Triggered by harmonic spikes; yield AI cores.
- Tech Vault Sieges: Multi-faction escalations; change map control.

## Glossary & Style Guide {#glossary}

- Interdiction Exclusion Zone (IEZ): Canon term. Not “Industrial Exclusion Zone.”
- Hybrid: human frames + alien components; never “mutant tech.”
- Harvester: automated alien system; never “visitors” or “angels.”

Style

- Tense: present for current play context, past for history.
- Units: metric; include local equivalents if spoken in-universe.
- Capitalization: Faction names capitalized; tech tiers capitalized.

## Cross-Discipline Notes {#cross-discipline}

- Art: Use faction signatures and palettes; link to Art/Factions guides. Don’t restate lore; reference this file.
- Design: Encounters reflect constraints (cooldown, EMP risk). POI hooks should map to mission types.
- Tools: Sidecars must include lore_id and workflow_hash; UE assets should carry lore tags.

### Signature Events {#events}

- EVT_SKYFALL_BARRAGE — Orbital debris strikes guided by dormant Harrower beacons; bombardments open salvage but draw predators. Black Sky Charter operatives mark targets; kinetic rods follow.
- EVT_HARMONIC_WINDOW — Monolith harmonic bloom opens Phase Pockets; stealth/EMP conditions favor Null Choir and awaken Monolith Sentinels.
- EVT_BLACKOUT_STORM — Rolling EMP microbursts collapse comms; Warden tolls suspend; drones desync and go feral.
- EVT_CONVOY_REDLINE — Trade routes go “hot”; Nomad long-hauls lock routes; mercenaries converge on LZs.
- EVT_VAULT_SIREN — Black Vault emits high-order primes; Archivists lock sectors; Combine pushes a demo; Directorate declares a no-fly.

---

## Changelog {#changelog}

- 1.0.0: Canonized timeline (2161, +6 months), standardized IEZ naming, set Sky Bastion to Directorate fortress, expanded factions (including event-only), characters, tech tiers, POIs, IEZ hardcore structure, culture, economy, glossary, and events.
