# Materials Directory

This directory contains the master material library for Terminal Grounds, organized by technology tier and faction.

## Structure

### Master Materials
- `Human/` - Human technology base materials
- `Hybrid/` - Human-alien hybrid technology materials
- `Alien/` - Pure alien technology materials
- `Environment/` - Environmental and structural materials
- `Factions/` - Faction-specific material variants

### Technology Tier Materials

#### Human Technology (`Human/`)
- **Base Materials**: Mil-spec aluminum, carbon steel, polymer composites
- **Surface Treatments**: Anodization, parkerizing, cerakote coatings
- **Wear Characteristics**: Predictable weathering, contact wear, corrosion
- **Master Material**: `M_Human_Base` with faction color parameters

#### Hybrid Technology (`Hybrid/`)
- **Base Materials**: Alien alloys, energy-conducting ceramics, adaptive polymers
- **Surface Treatments**: Energy etching, thermal conditioning, field hardening
- **Wear Characteristics**: Heat stress patterns, energy burn marks, material fatigue
- **Master Material**: `M_Hybrid_Base` with energy effect parameters

#### Alien Technology (`Alien/`)
- **Base Materials**: Metamaterial composites, energy-matter constructs, living metal
- **Surface Treatments**: Quantum surface states, phase-locked structures
- **Wear Characteristics**: Reality distortions, phase shifts, temporal wear
- **Master Material**: `M_Alien_Base` with quantum effect parameters

### Procedural Weathering System

#### Surface Conditions
- **Wet**: Reflection enhancement, normal map variation
- **Dust**: Albedo darkening, roughness increase, particle accumulation
- **Snow**: Albedo lightening, displacement mapping
- **Blood**: Albedo staining, wet surface properties
- **Radiation Sheen**: Emissive enhancement, color shift

#### Damage Layers
- **Battle Damage**: Bullet impacts, explosion scorch, shrapnel damage
- **Energy Burns**: Plasma scars, EMP burns, phase damage
- **Environmental**: Rust streaks, UV degradation, thermal cycling

### Faction Material Variants

Each faction has material instances of the base materials with:
- **Faction_Color_Primary**: Primary faction identification color
- **Faction_Color_Secondary**: Secondary faction color
- **Faction_Color_Accent**: Accent color for details
- **Weathering_Amount**: Faction-appropriate wear level (0.0-1.0)
- **Reflectance_Value**: Surface reflectance based on faction standards

### Performance Optimization

#### LOD System
- **LOD0**: Full material complexity for close inspection
- **LOD1**: Reduced complexity for medium distance
- **LOD2**: Simplified materials for distant objects
- **LOD3**: Solid color approximation for far objects

#### Texture Atlasing
- **Material Atlas**: Combined textures for efficient GPU usage
- **Decal Atlas**: Damage and marking textures combined
- **Normal Atlas**: Surface detail normal maps combined

## Implementation Guidelines

### Material Instance Naming
- `MI_[TechTier]_[Faction]_[Material]` (e.g., `MI_Human_Directorate_Armor`)
- `M_[TechTier]_[Type]_Master` for master materials
- `T_[Atlas]_[Type]` for texture assets

### Parameter Exposure
All master materials expose:
- **Faction Colors** (Primary, Secondary, Accent)
- **Weathering Control** (Amount, Type, Distribution)
- **Surface Properties** (Roughness, Metallic, Normal Intensity)
- **Environmental Response** (Wet, Dust, Snow, Radiation)

### Quality Scaling
- **Ultra**: Full material complexity, 4K textures
- **High**: Standard complexity, 2K textures  
- **Medium**: Reduced complexity, 1K textures
- **Low**: Simplified materials, 512px textures

## Asset Paths
- **Master Materials**: `Content/TG/Materials/[TechTier]/`
- **Material Instances**: `Content/TG/Materials/Factions/[Faction]/`
- **Textures**: `Content/TG/Textures/Materials/`
- **Functions**: `Content/TG/Materials/Functions/`