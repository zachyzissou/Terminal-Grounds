# Terminal Grounds VFX Bible

## VFX Philosophy

Terminal Grounds VFX serves three core purposes:
1. **Gameplay Clarity**: Effects must clearly communicate damage, range, and faction identity
2. **Immersive Realism**: Grounded, believable effects that support the military aesthetic
3. **Performance Excellence**: Scalable systems that maintain 90+ FPS in combat scenarios

## Technology Tier VFX Systems

### Human Technology VFX

#### Muzzle Effects
- **Core System**: Traditional gunpowder combustion with realistic smoke and spark patterns
- **Smoke Behavior**: Dense initial burst, wind dispersion, 2-3 second dissipation
- **Flash Pattern**: Bright yellow-orange flash, rapid falloff, directional light influence
- **Spark Characteristics**: Metal fragment trajectories, gravity affected, 15-30 particles
- **Audio Sync**: Muzzle flash synchronized with gunshot impact for weapon feedback

#### Impact Effects
- **Material Response**: Sparks on metal, dust on concrete, wood splinters on organic materials
- **Penetration VFX**: Entry hole with radiating crack patterns, exit effect with debris spray
- **Ricochet System**: Spark trail with metallic ping sound, realistic deflection angles
- **Decal Application**: Bullet holes with burn marks, appropriate sizing for caliber
- **Debris Physics**: Small fragments with proper collision and settling behavior

#### Ballistic Tracers
- **Visibility Rules**: Every 5th round visible tracer for automatic weapons
- **Color Coding**: Green for NATO standard, red for enemy factions
- **Tracer Lifetime**: 0.8-1.2 seconds depending on range
- **Velocity Inheritance**: Full projectile velocity with drag simulation
- **Night Vision Compatibility**: Enhanced visibility with NVG systems

### Hybrid Technology VFX

#### Plasma/Ion Effects
- **Core System**: Energized particle streams with electromagnetic disturbance
- **Plasma Core**: Bright blue-white center with energy ripple effects
- **Heat Distortion**: Thermal shimmer trails following projectile path
- **Electromagnetic Pulse**: Brief screen distortion on near misses
- **Overload Warning**: Red heat buildup effects on weapon before overload
- **Cooldown Venting**: Steam and energy discharge effects during cooldown

#### Energy Impact Effects
- **Material Interaction**: Plasma burns through armor, energy scorch marks
- **Chain Lightning**: Electrical arcing between metal objects
- **EMP Burst**: Temporary HUD flicker and electronic interference
- **Heat Signature**: Thermal bloom visible on IR systems
- **Residual Energy**: Glowing impact sites that fade over 3-5 seconds

### Alien Technology VFX

#### Graviton/Phase Effects
- **Gravity Distortion**: Visible space warping around projectiles
- **Phase Shift**: Projectiles that flicker between dimensions
- **Reality Tears**: Brief dimensional rifts with otherworldly colors
- **Gravitational Lensing**: Light bending around high-energy weapons
- **Quantum Instability**: Unpredictable particle behavior and visual anomalies

#### Alien Impact Effects
- **Matter Displacement**: Targets appear to fold or warp on impact
- **Dimensional Scarring**: Temporary reality distortions at impact sites
- **Exotic Resonance**: Harmonic visual effects that affect nearby technology
- **Probability Flux**: Visual uncertainty in projectile trajectories
- **Temporal Echo**: Brief after-images suggesting time distortion

## Environmental VFX Systems

### Weather & Atmospheric Effects

#### Rust Storms
- **Particle Density**: 10,000-50,000 particles for visibility occlusion
- **Wind Patterns**: Directional gusts with debris interaction
- **Corrosion Effects**: Progressive equipment degradation visualization
- **Lightning Integration**: Electrical discharge through metallic particles
- **Visibility Impact**: Dynamic fog density affecting combat ranges

#### Electromagnetic Interference (EMI)
- **Screen Distortion**: HUD flicker and static overlay effects
- **Electrical Arcing**: Lightning between metal structures and vehicles
- **Communication Disruption**: Audio static and broken transmission effects
- **Equipment Malfunction**: Sparking electronics and system failures
- **Aurora Effects**: Ionospheric disturbance creating colored sky phenomena

#### Reactor Plumes
- **Heat Shimmer**: Thermal distortion columns rising from reactor sites
- **Radiation Visualization**: Geiger counter-style particle effects
- **Cooling Steam**: Massive vapor clouds with realistic condensation
- **Emergency Venting**: Pressurized gas releases with safety lighting
- **Containment Breach**: Catastrophic failure effects with shockwave propagation

### Combat Environment VFX

#### Vehicle Exhaust & Damage
- **Diesel Smoke**: Realistic combustion byproducts from military vehicles
- **Hydraulic Leaks**: Pressurized fluid spray from damaged systems
- **Engine Fire**: Progressive damage states with flame intensity scaling
- **Armor Spalling**: Metal fragments from penetrating hits
- **Crew Compartment**: Smoke and sparks from internal systems damage

#### Destruction Effects
- **Building Collapse**: Debris physics with dust cloud generation
- **Explosive Fragmentation**: Realistic shrapnel patterns and ricochets
- **Secondary Explosions**: Fuel and ammunition cookoff effects
- **Structural Failure**: Progressive damage with material stress visualization
- **Debris Settling**: Realistic particle physics for post-destruction cleanup

## Performance Guidelines

### LOD System Implementation
- **Distance Scaling**: Effect complexity reduces linearly with range
- **Particle Count Limits**: 
  - Close (0-50m): Full detail, no particle limit
  - Medium (50-150m): 75% particles, reduced simulation steps
  - Far (150m+): 25% particles, billboard-only effects
- **Update Frequency**: Near effects at 60Hz, distant at 30Hz

### Scalability Presets
- **Ultra**: All effects enabled, maximum particle counts
- **High**: 85% particle density, full shader effects
- **Medium**: 65% particles, simplified shaders
- **Low**: 40% particles, minimal effects only
- **Performance**: Essential effects only, maximum optimization

### Memory Management
- **Texture Atlasing**: All effect textures combined into 2048x2048 atlases
- **Particle Pooling**: Reuse effect instances to minimize allocation
- **Culling System**: Frustum and occlusion culling for all particle systems
- **Streaming**: Large effects loaded on-demand for specific scenarios
- **Trajectory**: Slightly visible trail with appropriate ballistic drop
- **Distance Falloff**: Fade over range, invisible beyond weapon max range

### Hybrid Technology VFX

#### Coil Effects
- **Charging Sequence**: Energy buildup visible in weapon barrel, 0.5-1.5 second charge time
- **Magnetic Field**: Subtle air distortion around coil systems during operation
- **Energy Discharge**: Blue-white energy pulse along magnetic field lines
- **Heat Venting**: Steam and energy dissipation from cooling systems
- **Overload Warning**: Red energy buildup with electrical arcing before system shutdown

#### Plasma Effects
- **Plasma Formation**: Contained energy sphere with internal turbulence
- **Launch Trail**: Superheated air distortion wake behind plasma projectiles
- **Impact Behavior**: Explosive energy dissipation with electrical branching
- **Heat Signature**: Infrared glow visible through thermal optics
- **Containment Failure**: Chaotic energy dispersion when systems malfunction

#### Heat Management VFX
- **Thermal Buildup**: Progressive heat distortion around weapon systems
- **Cooling Cycles**: Steam venting with pressure release sounds
- **Warning States**: Color progression from blue (cool) to red (danger) to white (critical)
- **Automatic Shutdown**: Visible system power-down with energy dissipation
- **Emergency Venting**: Dramatic steam release with temporary weapon inoperability

### Alien Technology VFX

#### Beam Effects
- **Phase Coherence**: Stable energy beam with minimal distortion
- **Reality Interaction**: Slight space-time distortion around beam path
- **Charging Buildup**: Reality "tearing" effect as dimensional energy accumulates
- **Sustained Fire**: Continuous beam with particle stream and heat mirage
- **Beam Termination**: Energy dissipation with spatial "healing" effect

#### Graviton Effects
- **Gravity Wells**: Visible space distortion with debris attraction
- **Projectile Behavior**: Mass-less projectiles unaffected by gravity or wind
- **Impact Deformation**: Target compression and spatial warping on contact
- **Area Effects**: Gravitational field visualization affecting loose objects
- **Field Collapse**: Explosive release when gravitational systems fail

#### Distortion Effects
- **Phase Shifting**: Reality "ripple" effects around alien energy sources
- **Temporal Echoes**: Brief afterimages showing previous states of affected objects
- **Spatial Warping**: Visible bending of light and space around high-energy systems
- **Quantum Fluctuation**: Random particle generation and annihilation
- **Dimensional Tears**: Rare visual glitches showing "underneath" reality

## Environmental VFX

### Weather Systems

#### Rust Storms
- **Formation**: Dust cloud buildup with metallic particle visibility
- **Wind Effects**: Debris patterns showing wind direction and intensity
- **Visibility Impact**: Progressive opacity reduction, orange-brown atmospheric tinting
- **Equipment Effects**: Metal corrosion acceleration, electrical system interference
- **Duration**: 5-15 minute storm cycles with gradual buildup and dissipation

#### EMI Lightning
- **Electrical Arcing**: Blue-white electrical branches between conductive surfaces
- **Field Visualization**: Electromagnetic field lines visible through specialized optics
- **System Interference**: HUD static, weapon system glitches, communication disruption
- **Cascade Events**: Chain lightning between electronic systems
- **EMP Aftermath**: Electrical system restart sequences, smoke from overloaded components

### Industrial Effects

#### Reactor Plumes
- **Energy Emission**: Stable energy pillar with internal particle circulation
- **Heat Distortion**: Massive heat mirage effects around reactor cores
- **Containment Fields**: Visible energy barriers with surface tension effects
- **Safety Systems**: Warning light patterns, automated vent sequences
- **Failure States**: Containment breach with expanding energy waves

#### APC Dust Systems
- **Engine Exhaust**: Diesel particulate with heat distortion
- **Track/Wheel Dust**: Surface-specific dust clouds (sand, dirt, concrete powder)
- **Scale Appropriate**: Dust cloud size proportional to vehicle mass and speed
- **Wind Interaction**: Dust dispersion patterns affected by environmental wind
- **Visibility Impact**: Temporary concealment effects for tactical gameplay

### Combat Environment Effects

#### Explosion Systems
- **Blast Sphere**: Expanding pressure wave with debris acceleration
- **Fireball Formation**: Combustion gases with realistic expansion and cooling
- **Shockwave Propagation**: Ground ripple effects and structural stress indicators
- **Debris Field**: Fragment trajectories with appropriate mass and wind resistance
- **Audio Integration**: Synchronized blast wave arrival based on distance

#### Structural Damage
- **Progressive Destruction**: Building damage states with appropriate debris
- **Dust and Smoke**: Structural collapse generates realistic particulate clouds
- **Sparking Systems**: Electrical damage creates dangerous arcing hazards
- **Fire Propagation**: Realistic fire spread based on material properties
- **Stability Warning**: Visual indicators for structural integrity loss

## Performance Budgets

### Particle Count Limits
- **Per-Weapon System**: Maximum 500 particles for muzzle flash and projectile effects
- **Environmental Systems**: 2000 particles total for weather and ambient effects
- **Explosion Events**: 1500 particles for major destructive events
- **Background Ambience**: 300 particles for continuous atmospheric effects
- **Emergency Override**: Systems automatically cull particles to maintain framerate

### LOD Systems
- **Distance-Based**: Particle density reduction beyond 50 meters
- **Quality Scaling**: Performance presets reduce effect complexity
- **Visibility Culling**: Effects outside player view frustum immediately disabled
- **Priority System**: Gameplay-critical effects maintain quality over aesthetic effects
- **Dynamic Adjustment**: Real-time particle count adjustment based on current framerate

### Scalability Settings

#### Ultra Preset
- Full particle density, maximum draw distance
- All secondary effects enabled (sparks, debris, atmospheric)
- Real-time lighting on all particle systems
- 4K texture resolution for effect assets

#### High Preset  
- 75% particle density, reduced draw distance
- Primary effects at full quality, secondary effects simplified
- Mixed real-time and baked lighting
- 2K texture resolution for effect assets

#### Medium Preset (Target: 90 FPS @ 1440p)
- 50% particle density, moderate draw distance
- Simplified effect systems with reduced complexity
- Primarily baked lighting with key real-time effects
- 1K texture resolution for effect assets

#### Competitive Preset (Target: 120 FPS @ 1080p)
- 25% particle density, minimal draw distance
- Only gameplay-critical effects enabled
- Baked lighting only, no real-time particle illumination
- 512px texture resolution for effect assets

## Niagara System Architecture

### Modular System Design
- **Base Emitters**: Core particle generation systems shared across weapons
- **Modifier Modules**: Faction-specific visual modifications applied to base systems
- **Environmental Adapters**: Dynamic systems that respond to weather and lighting
- **Performance Monitors**: Automatic system scaling based on current performance metrics

### Parameter Exposure
- **Designer Controls**: Easily adjustable intensity, color, and timing parameters
- **Faction Customization**: Color palette and style modifications per faction
- **Weapon Integration**: Automatic parameter binding to weapon statistics
- **Environmental Response**: Dynamic adjustment based on weather and lighting conditions

### Performance Optimization
- **Instanced Rendering**: Shared geometry for similar particle types
- **Texture Atlasing**: Combined textures to reduce draw calls
- **GPU Simulation**: Physics calculations performed on graphics hardware
- **Temporal Reprojection**: Frame interpolation to maintain visual quality at lower update rates

## Audio-Visual Synchronization

### Timing Requirements
- **Weapon Feedback**: Visual effects synchronized within 16ms of audio cues
- **Environmental Sync**: Thunder and lightning coordination for weather systems
- **Impact Timing**: Visual and audio impact effects precisely aligned
- **System Warnings**: Visual status indicators match audio alert timing

### Cross-System Integration
- **MetaSounds Integration**: VFX parameters driven by audio system data
- **Gameplay Feedback**: Visual effects respond to player action timing
- **Network Synchronization**: Multiplayer effect timing maintained across clients
- **Performance Scaling**: Audio and visual quality scale together in performance presets

This VFX bible provides the foundation for all visual effects development in Terminal Grounds Phase 3, ensuring consistency, performance, and gameplay clarity across all effect systems.