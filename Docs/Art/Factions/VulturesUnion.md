# Vultures Union Faction Style Guide

Lore Reference: See canonical faction details in docs/Lore/LORE_BIBLE.md#factions

## Faction Identity

The Vultures Union are master scavengers and salvage operators who thrive in the post-Accord chaos. They excel at jury-rigging alien technology with human components, creating powerful but unpredictable hybrid systems.

## Visual Philosophy

**Salvaged Ingenuity** • **Industrial Grit** • **Pragmatic Function**

The Vultures aesthetic emphasizes improvisation, material reuse, and practical problem-solving. Their equipment should feel cobbled together but surprisingly effective.

## Color Palette

### Primary Colors

- **Rust Red**: `#B22222` - Oxidation, age, salvaged materials
- **Scrap Metal Gray**: `#696969` - Raw steel, industrial debris
- **Warning Yellow**: `#FFD700` - Hazard stripes, attention markers

### Secondary Colors

- **Oil Black**: `#0F0F0F` - Machinery lubricants, soot, deep shadows
- **Copper**: `#B87333` - Salvaged wiring, heat exchangers, patina

### Usage Guidelines

- Rust red for primary identification and structural elements (40% coverage)
- Scrap gray for base materials and armor plating (35% coverage)
- Warning yellow for hazard markings and important systems (15% coverage)
- Oil black for mechanical components and deep recesses (7% coverage)
- Copper for electrical and heat management systems (3% coverage)

## Material Motifs

### Salvaged Construction

- **Base Materials**: Reclaimed steel plate, aluminum sheet, salvaged polymers
- **Surface Treatments**: Natural oxidation, impact damage, field repairs
- **Wear Patterns**: Heavy corrosion, weld spatter, tool marks, impact dents
- **Detail Elements**: Riveted patches, visible welds, repurposed components

### Jury-Rigged Systems

- **Electrical**: Exposed conduits, improvised connections, heat-shrink repairs
- **Mechanical**: Mixed fastener types, replacement bushings, field modifications
- **Weathering**: Active rust, oil stains, thermal discoloration, chemical etching

## Insignia and Iconography

### Primary Emblem

- **Symbol**: Vulture head silhouette over crossed salvage tools
- **Colors**: Rust red vulture on scrap gray field with yellow warning border
- **Usage**: Painted on vehicles, welded to equipment, stamped into metal

### Secondary Symbols

- **Crew Tags**: Personal signatures welded or burned into equipment
- **Salvage Markers**: Claim stakes and territory indicators
- **Warning Symbols**: Improvised hazard signs, skull and crossbones variations

### Typography

- **Primary Font**: Hand-painted stencils, industrial block letters
- **Secondary Font**: Stamped metal lettering, engraved nameplates
- **Hierarchy**: Bold (warnings), Standard (identification), Small (specifications)

## Silhouette Design Language

### Character Silhouettes

- **Salvagers**: Heavy work gear with welding masks and tool belts
- **Engineers**: Multiple pouches and diagnostic equipment
- **Fighters**: Patchwork armor with jury-rigged weapon attachments

### Vehicle Silhouettes

- **Design Principles**: Boxy, reinforced, obviously modified from civilian origins
- **Proportions**: Oversized components, external modifications, visible repairs
- **Details**: Welded-on armor, jury-rigged weapons, improvised protection

### Weapon Silhouettes

- **Characteristics**: Modified civilian/military base with improvised attachments
- **Modifications**: Visible alterations, non-standard mounting systems
- **Condition**: Field-repaired, functional but rough, improvised improvements

## Environmental Control Points

### Salvage Yards

- **Layout**: Organized chaos with material sorting areas
- **Equipment**: Cranes, welding stations, parts bins, testing benches
- **Signage**: Hand-painted warnings, claim markers, directional indicators

### Workshop Facilities

- **Construction**: Converted industrial buildings with added modifications
- **Tools**: Heavy machinery, welding equipment, material processing
- **Organization**: Functional efficiency over aesthetic appearance

### Battlefield Markings

- **Territory Control**: Rust red paint applied with brushes or spray guns
- **Resource Claims**: Welded stake markers with crew identification
- **Hazard Warnings**: Improvised danger signs using available materials

## Technology Integration

### Human-Tier Base Equipment

- **Aesthetic**: Heavily modified civilian and military surplus
- **Reliability**: Constant maintenance required, frequent field repairs
- **Modification**: Extensive jury-rigging and performance modifications

### Hybrid Technology Mastery

- **Integration**: Alien components grafted onto human systems
- **Appearance**: Visible integration points, improvised cooling systems
- **Markings**: Hand-written specifications, warning labels, crew notes

### Alien Technology Salvage

- **Approach**: Careful extraction and integration into existing systems
- **Housing**: Improvised containment using available materials
- **Safety**: Ad-hoc radiation shielding and emergency shutdown systems

## Audio Identity

- **Communication Style**: Informal salvager slang, practical communication
- **Equipment Sounds**: Jury-rigged systems, improvised mechanical solutions
- **Voice Characteristics**: Working-class pragmatism, salvage expertise
- **Ambient Identity**: Scrap yard operations, metal salvage sounds

## Weathering and Damage Patterns

### Natural Weathering

- **Rust Development**: Active oxidation with bleeding patterns
- **Corrosion Types**: Galvanic corrosion at dissimilar metal joints
- **UV Damage**: Polymer degradation, paint fading, rubber cracking

### Usage Wear

- **Contact Points**: Polished wear from repeated handling
- **Stress Concentrations**: Crack initiation at weld points and fasteners
- **Tool Marks**: Grinder marks, cutting torch patterns, drill holes

### Battle Damage

- **Impact Marks**: Ballistic damage repaired with plate patches
- **Heat Damage**: Plasma burns welded over with new material
- **Explosive Damage**: Fragmentation holes filled with available materials

## Asset Implementation Notes

### UE5 Asset Paths

- **Materials**: `Content/TG/Materials/Factions/Vultures/`
- **Textures**: `Content/TG/Textures/Factions/Vultures/`
- **Meshes**: `Content/TG/Meshes/Factions/Vultures/`
- **Decals**: `Content/TG/Decals/Factions/Vultures/`

### Master Material Parameters

- **Faction_Color_Primary**: (0.7, 0.13, 0.13) - Rust Red
- **Faction_Color_Secondary**: (0.41, 0.41, 0.41) - Scrap Gray
- **Faction_Color_Accent**: (1.0, 0.84, 0.0) - Warning Yellow
- **Weathering_Amount**: 0.8 (heavy wear and corrosion)
- **Reflectance_Value**: 0.06 (varied surface conditions)

### Procedural Weathering Systems

- **Rust Gradients**: Procedural oxidation based on surface normals
- **Weld Seams**: Displaced geometry with thermal discoloration
- **Impact Damage**: Dented surfaces with stress pattern texturing
- **Oil Stains**: Fluid simulation-based contamination patterns

### Performance Considerations

- Heavy use of texture atlasing for salvaged component variety
- Modular attachment system for jury-rigged modifications
- LOD system maintains recognizable wear patterns at distance
- Rust and corrosion shaders optimized for mobile platforms
