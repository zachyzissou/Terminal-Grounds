# Human Technology Master Material

This document defines the master material system for Human technology tier equipment and structures.

## Material Philosophy

Human technology materials emphasize **reliability**, **mass production**, and **military standards**. They should feel familiar, functional, and appropriately weathered based on service history.

## Master Material: M_Human_Base

### Input Parameters

#### Faction Colors
- **Faction_Color_Primary** (Vector3): Primary faction identification color
- **Faction_Color_Secondary** (Vector3): Secondary faction color for details
- **Faction_Color_Accent** (Vector3): Accent color for highlights and markings

#### Surface Properties  
- **Base_Albedo** (Vector3): Base material color before faction tinting
- **Metallic_Value** (Scalar): 0.0-1.0 metallic response
- **Roughness_Base** (Scalar): Base roughness value (0.0-1.0)
- **Normal_Intensity** (Scalar): Normal map strength multiplier

#### Weathering System
- **Weathering_Amount** (Scalar): Overall weathering intensity (0.0-1.0)
- **Rust_Amount** (Scalar): Rust/corrosion intensity (0.0-1.0)
- **Wear_Amount** (Scalar): Contact wear intensity (0.0-1.0)
- **Dirt_Amount** (Scalar): Dirt accumulation (0.0-1.0)

#### Environmental Response
- **Wet_Amount** (Scalar): Surface wetness (0.0-1.0)
- **Snow_Amount** (Scalar): Snow accumulation (0.0-1.0)
- **Dust_Amount** (Scalar): Dust coating (0.0-1.0)
- **Blood_Amount** (Scalar): Blood staining (0.0-1.0)

### Texture Inputs

#### Base Textures (512x512 minimum)
- **T_Human_Albedo**: Base color map with neutral tinting
- **T_Human_Normal**: Surface detail normal map
- **T_Human_Roughness**: Surface roughness variation
- **T_Human_Metallic**: Metallic mask (0=non-metal, 1=metal)
- **T_Human_AO**: Ambient occlusion for surface depth

#### Weathering Masks (512x512)
- **T_Human_Rust_Mask**: Rust accumulation areas
- **T_Human_Wear_Mask**: Contact wear locations
- **T_Human_Dirt_Mask**: Dirt accumulation patterns
- **T_Human_Detail_Mask**: Fine surface detail overlay

### Material Logic

#### Faction Color Application
```hlsl
// Apply faction colors to base albedo
FinalAlbedo = lerp(Base_Albedo, Faction_Color_Primary, FactionMask_R);
FinalAlbedo = lerp(FinalAlbedo, Faction_Color_Secondary, FactionMask_G);
FinalAlbedo = lerp(FinalAlbedo, Faction_Color_Accent, FactionMask_B);
```

#### Weathering System
```hlsl
// Rust application
RustColor = float3(0.4, 0.2, 0.1); // Brown rust color
RustMask = Rust_Mask * Rust_Amount * Weathering_Amount;
FinalAlbedo = lerp(FinalAlbedo, RustColor, RustMask);
FinalRoughness = lerp(Roughness_Base, 0.8, RustMask);

// Wear application  
WearMask = Wear_Mask * Wear_Amount * Weathering_Amount;
FinalRoughness = lerp(FinalRoughness, 0.3, WearMask);
FinalMetallic = lerp(Metallic_Value, 1.0, WearMask * 0.5);
```

#### Environmental Response
```hlsl
// Wet surface response
WetRoughness = FinalRoughness * (1.0 - Wet_Amount * 0.8);
WetReflection = lerp(0.04, 0.1, Wet_Amount);

// Snow accumulation
SnowMask = saturate(WorldNormal.z * 2.0 - 1.0) * Snow_Amount;
FinalAlbedo = lerp(FinalAlbedo, float3(0.9, 0.9, 0.95), SnowMask);
FinalRoughness = lerp(WetRoughness, 0.1, SnowMask);
```

## Material Instances

### Faction-Specific Instances

#### MI_Human_Directorate
- **Faction_Color_Primary**: (0.0, 0.12, 0.25) - Navy Blue
- **Faction_Color_Secondary**: (0.21, 0.27, 0.31) - Gunmetal Gray  
- **Faction_Color_Accent**: (1.0, 1.0, 1.0) - White
- **Weathering_Amount**: 0.2 - Minimal wear, good maintenance

#### MI_Human_VulturesUnion
- **Faction_Color_Primary**: (0.7, 0.13, 0.13) - Rust Red
- **Faction_Color_Secondary**: (0.41, 0.41, 0.41) - Scrap Gray
- **Faction_Color_Accent**: (1.0, 0.84, 0.0) - Warning Yellow
- **Weathering_Amount**: 0.8 - Heavy wear and corrosion

#### MI_Human_Free77
- **Faction_Color_Primary**: (0.82, 0.71, 0.55) - Desert Tan
- **Faction_Color_Secondary**: (0.33, 0.42, 0.18) - Olive Drab
- **Faction_Color_Accent**: (0.18, 0.18, 0.18) - Contractor Black
- **Weathering_Amount**: 0.4 - Professional maintenance

### Equipment-Specific Variants

#### MI_Human_Weapon
- Enhanced metallic response for barrel and action
- Wear patterns focused on grip and contact areas
- Faction color application limited to furniture and markings

#### MI_Human_Armor
- Balanced metallic/non-metallic for composite construction
- Impact damage patterns from ballistic testing
- Medical and rank markings in faction accent colors

#### MI_Human_Vehicle
- Heavy weathering on external surfaces
- Protective coatings with wear-through to bare metal
- Faction identification prominently displayed

## Performance Optimization

### LOD System
- **LOD0**: Full material complexity with all weathering layers
- **LOD1**: Simplified weathering, reduced texture sampling
- **LOD2**: Basic faction colors, minimal surface detail
- **LOD3**: Solid color approximation for distant objects

### Texture Streaming
- Base textures: High priority, always loaded
- Weathering details: Medium priority, distance-based loading
- Environmental overlays: Low priority, conditional loading

### Mobile Optimization
- Reduced texture resolution (256x256 on mobile)
- Simplified weathering logic (2 layers maximum)
- Static faction color variants instead of dynamic tinting

## Quality Validation

### Visual Standards
- Realistic material response under all lighting conditions
- Consistent faction identity across all variants
- Appropriate wear patterns for equipment age and usage
- Performance target: 90 FPS on recommended hardware

### Technical Requirements
- Maximum 32 texture samples per material
- Shader complexity under 200 instructions on PC
- Mobile compatibility with reduced feature set
- Memory footprint under 8MB per material variant

## Implementation Notes

### Asset Creation Pipeline
1. Create base textures with neutral colors
2. Set up master material with all parameter exposures
3. Create faction-specific material instances
4. Test across all lighting scenarios and quality settings
5. Profile performance on target hardware platforms

### Common Issues
- **Faction colors too saturated**: Reduce saturation in linear space
- **Weathering too uniform**: Add variation through masks and noise
- **Performance impact**: Use texture atlasing and reduce sampling
- **Mobile compatibility**: Create separate mobile material variants

This master material system provides the foundation for all Human technology tier assets while maintaining faction identity and visual consistency.