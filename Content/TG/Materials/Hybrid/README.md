# Hybrid Technology Master Material

This document defines the master material system for Hybrid technology tier equipment, combining human engineering with alien technology integration.

## Material Philosophy

Hybrid technology materials emphasize **innovation**, **energy integration**, and **controlled instability**. They should feel like advanced human technology enhanced with carefully integrated alien components.

## Master Material: M_Hybrid_Base

### Input Parameters

#### Faction Colors
- **Faction_Color_Primary** (Vector3): Primary faction identification color
- **Faction_Color_Secondary** (Vector3): Secondary faction color for details
- **Faction_Color_Accent** (Vector3): Accent color for highlights and markings
- **Energy_Color** (Vector3): Alien energy signature color

#### Surface Properties
- **Base_Albedo** (Vector3): Base material color before faction tinting
- **Metallic_Value** (Scalar): 0.0-1.0 metallic response
- **Roughness_Base** (Scalar): Base roughness value (0.0-1.0)
- **Normal_Intensity** (Scalar): Normal map strength multiplier

#### Energy System
- **Energy_Intensity** (Scalar): Overall energy activity level (0.0-1.0)
- **Heat_Amount** (Scalar): Thermal stress from energy systems (0.0-1.0)
- **Charge_Level** (Scalar): Current energy charge state (0.0-1.0)
- **Overload_Warning** (Scalar): Overload warning intensity (0.0-1.0)

#### Hybrid Integration
- **Alien_Blend** (Scalar): Amount of alien technology integration (0.0-1.0)
- **Energy_Flow_Speed** (Scalar): Animation speed for energy effects
- **Cooling_Efficiency** (Scalar): Heat dissipation effectiveness (0.0-1.0)
- **System_Stability** (Scalar): Technology stability (0.0-1.0, affects flicker)

#### Weathering System
- **Weathering_Amount** (Scalar): Overall weathering intensity (0.0-1.0)
- **Heat_Damage** (Scalar): Thermal damage from overheating (0.0-1.0)
- **Energy_Burn** (Scalar): Energy discharge damage (0.0-1.0)
- **Integration_Wear** (Scalar): Wear at human-alien interfaces (0.0-1.0)

### Texture Inputs

#### Base Textures (512x512 minimum)
- **T_Hybrid_Albedo**: Base color with human and alien regions
- **T_Hybrid_Normal**: Combined human and alien surface details
- **T_Hybrid_Roughness**: Surface roughness with thermal variation
- **T_Hybrid_Metallic**: Metallic mask including alien materials
- **T_Hybrid_AO**: Ambient occlusion for complex geometry

#### Energy System Textures (512x512)
- **T_Hybrid_Energy_Mask**: Energy conduit and component locations
- **T_Hybrid_Heat_Mask**: Heat generation and dissipation areas
- **T_Hybrid_Flow_Pattern**: Energy flow direction and animation
- **T_Hybrid_Integration_Mask**: Human-alien interface boundaries

#### Weathering Masks (256x256)
- **T_Hybrid_Thermal_Damage**: Heat stress and thermal cycling damage
- **T_Hybrid_Energy_Burn**: Energy discharge damage patterns
- **T_Hybrid_Interface_Wear**: Wear at technology integration points

### Material Logic

#### Energy System Implementation
```hlsl
// Energy flow animation
float2 FlowUV = UV + (Energy_Flow_Speed * Time) * FlowDirection;
float3 EnergyMask = tex2D(T_Hybrid_Energy_Mask, FlowUV).rgb;

// Charge level visualization
float ChargeGlow = saturate(Charge_Level * 2.0 - 1.0);
float3 EnergyGlow = Energy_Color * ChargeGlow * EnergyMask.r;

// Heat visualization
float3 HeatColor = lerp(float3(0.1, 0.3, 1.0), float3(1.0, 0.3, 0.1), Heat_Amount);
float HeatGlow = Heat_Amount * EnergyMask.g;
```

#### Overload Warning System
```hlsl
// Overload warning flicker
float WarningFlicker = sin(Time * 10.0) * 0.5 + 0.5;
WarningFlicker = smoothstep(0.3, 0.7, WarningFlicker);
float3 WarningGlow = float3(1.0, 0.1, 0.1) * Overload_Warning * WarningFlicker;

// System instability
float Instability = 1.0 - System_Stability;
float InstabilityNoise = noise(UV * 50.0 + Time * 5.0) * Instability;
EnergyGlow *= (1.0 + InstabilityNoise * 0.5);
```

#### Hybrid Material Blending
```hlsl
// Human-alien material transition
float AlienMask = tex2D(T_Hybrid_Integration_Mask, UV).r * Alien_Blend;
float3 HumanAlbedo = Base_Albedo;
float3 AlienAlbedo = Base_Albedo * float3(0.8, 0.9, 1.1); // Slight alien tint

FinalAlbedo = lerp(HumanAlbedo, AlienAlbedo, AlienMask);
FinalMetallic = lerp(Metallic_Value, 0.9, AlienMask); // Alien materials more metallic
FinalRoughness = lerp(Roughness_Base, 0.2, AlienMask * Energy_Intensity);
```

#### Thermal Effects
```hlsl
// Heat stress damage
float3 HeatDamageColor = float3(0.3, 0.2, 0.1); // Heat-stressed metal
float HeatDamageMask = tex2D(T_Hybrid_Thermal_Damage, UV).r * Heat_Damage;
FinalAlbedo = lerp(FinalAlbedo, HeatDamageColor, HeatDamageMask);
FinalRoughness = lerp(FinalRoughness, 0.8, HeatDamageMask);

// Energy burn patterns
float3 EnergyBurnColor = Energy_Color * 0.3;
float EnergyBurnMask = tex2D(T_Hybrid_Energy_Burn, UV).r * Energy_Burn;
FinalAlbedo = lerp(FinalAlbedo, EnergyBurnColor, EnergyBurnMask);
```

#### Emissive Combination
```hlsl
// Combine all emissive sources
FinalEmissive = EnergyGlow + (HeatColor * HeatGlow) + WarningGlow;
FinalEmissive *= Energy_Intensity;

// Modulate by cooling efficiency
FinalEmissive *= lerp(1.5, 0.5, Cooling_Efficiency);
```

## Material Instances

### Faction-Specific Instances

#### MI_Hybrid_Directorate
- **Energy_Color**: (0.28, 0.56, 0.88) - Steel Blue
- **System_Stability**: 0.8 - High engineering standards
- **Cooling_Efficiency**: 0.7 - Good thermal management
- **Weathering_Amount**: 0.3 - Regular maintenance protocols

#### MI_Hybrid_VulturesUnion
- **Energy_Color**: (1.0, 0.65, 0.0) - Warning Orange
- **System_Stability**: 0.4 - Jury-rigged integration
- **Cooling_Efficiency**: 0.3 - Improvised cooling
- **Weathering_Amount**: 0.8 - Heavy field modifications

#### MI_Hybrid_CorporateCombine
- **Energy_Color**: (0.58, 0.44, 0.86) - Energy Purple
- **System_Stability**: 0.6 - Experimental prototype
- **Cooling_Efficiency**: 0.9 - Advanced thermal systems
- **Weathering_Amount**: 0.1 - Laboratory conditions

### Equipment-Specific Variants

#### MI_Hybrid_Weapon
- Enhanced energy flow patterns along barrel and action
- Heat buildup visualization during sustained fire
- Cooling vent emissive effects

#### MI_Hybrid_Armor
- Energy distribution network across armor plates
- Heat stress patterns at high-load areas
- Integration points with additional alien material blend

#### MI_Hybrid_Vehicle
- Large-scale energy routing and heat management
- Visible alien technology integration points
- Overload warning systems for critical components

## Advanced Features

### Dynamic Energy States
```hlsl
// Energy ramp-up during activation
float ActivationCurve = smoothstep(0.0, 1.0, Charge_Level);
float SpinUp = sin(ActivationCurve * PI * 0.5);
EnergyGlow *= SpinUp;

// Cooldown cycling
float CooldownCycle = sin(Time * 2.0) * 0.5 + 0.5;
HeatGlow *= lerp(CooldownCycle, 1.0, 1.0 - Cooling_Efficiency);
```

### Alien Technology Integration
```hlsl
// Quantum fluctuation simulation
float QuantumNoise = noise(UV * 100.0 + Time * 0.1) * Alien_Blend;
AlienAlbedo += QuantumNoise * float3(0.1, 0.3, 0.2) * Energy_Intensity;

// Phase coherence effects
float PhaseCoherence = sin(dot(UV, float2(10.0, 7.0)) + Time * 3.0) * 0.1;
FinalEmissive += Energy_Color * PhaseCoherence * Alien_Blend * Energy_Intensity;
```

## Performance Optimization

### LOD System
- **LOD0**: Full energy effects, heat simulation, quantum fluctuations
- **LOD1**: Simplified energy animation, static heat patterns
- **LOD2**: Basic emissive glow, no animation
- **LOD3**: Solid color with faction tinting only

### Energy Effect Scaling
- High settings: Full animation, all energy layers active
- Medium settings: Reduced animation frequency, simplified heat effects
- Low settings: Static energy glow, no heat simulation
- Mobile: Pre-baked energy patterns, minimal emissive

### Texture Optimization
- Energy masks combined into single RGB texture
- Flow patterns use simple UV animation instead of flow maps
- Heat effects use gradient textures instead of full color maps

## Quality Validation

### Visual Standards
- Energy effects clearly indicate system state and faction
- Heat buildup provides tactical information for gameplay
- Alien integration feels otherworldly but not overwhelming
- Performance target: 85 FPS on recommended hardware (5% reduction for energy effects)

### Technical Requirements
- Maximum 48 texture samples per material (50% increase from Human tier)
- Shader complexity under 300 instructions on PC
- Emissive range 0.0-2.0 to maintain HDR pipeline compatibility
- Energy animation optimized for 30 FPS temporal coherence

## Implementation Notes

### Energy System Integration
- Charge_Level parameter driven by gameplay systems
- Heat_Amount responds to weapon usage and environmental factors
- Overload_Warning triggered by gameplay events
- Energy_Intensity scales with technology tier progression

### Common Issues
- **Energy effects too bright**: Limit emissive range, use HDR tonemapping
- **Performance impact**: Reduce animation frequency, combine texture channels
- **Heat effects unclear**: Increase contrast between cool and hot states
- **Alien integration unconvincing**: Add subtle animation and color variation

This hybrid material system bridges human and alien technology while maintaining gameplay clarity and visual spectacle.