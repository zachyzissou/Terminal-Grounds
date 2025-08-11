# LookDev Directory

This directory contains look development levels for establishing the visual identity of Terminal Grounds biomes and technology tiers.

## Structure

### Biome LookDev Levels
- `IEZ_Alpha/` - Industrial Exclusion Zone, Alpha District
- `IEZ_Beta/` - Industrial Exclusion Zone, Beta District  
- `TechWastes_Gamma/` - Technology Wastes, Gamma Band
- `SkyBastion/` - Aerial facility complex
- `BlackVault/` - Underground vault complex

### Technology Tier Showcases
- `Human_Tech/` - Human technology demonstration level
- `Hybrid_Tech/` - Human-alien hybrid technology showcase
- `Alien_Tech/` - Pure alien technology demonstration

### Weather and Lighting Variants
Each biome includes multiple lighting setups:
- `_Day` - Standard daylight conditions
- `_Dusk` - Twilight/golden hour lighting
- `_Night` - Night operations with artificial lighting
- `_Storm` - Weather effects and atmospheric conditions
- `_EMI` - Electromagnetic interference conditions

## Asset Paths
All LookDev levels should reference materials and assets from:
- `Content/TG/Materials/`
- `Content/TG/Textures/`
- `Content/TG/Meshes/`
- `Content/TG/VFX/`

## Implementation Notes
- Each level serves as a reference for lighting artists
- Levels include benchmark scenes for performance testing
- Cinematic camera paths for trailer and promotional content
- Performance profiling markers for optimization