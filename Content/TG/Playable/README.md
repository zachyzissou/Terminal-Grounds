# Playable Slice Directory

This directory contains the small-scale playable slice implementation for Terminal Grounds, serving as a functional demonstration of core gameplay systems and visual identity.

## Purpose

The playable slice validates:
- **Gameplay Mechanics**: Core combat and movement systems
- **Visual Coherence**: Art style and faction identity implementation
- **Performance Targets**: 90+ FPS optimization goals
- **System Integration**: How all game systems work together

## Map Structure

### Test Environment: `TG_TestCombat`
A focused combat scenario in a single biome for concentrated testing.

#### Environment Selection
- **Biome**: IEZ Alpha District (Industrial Exclusion Zone)
- **Size**: 200m x 200m combat arena
- **Verticality**: Multi-level structures with tactical positioning
- **Cover System**: Varied cover types for tactical gameplay

#### Objective Types
- **Elimination**: Clear all enemy forces
- **Capture Point**: Control strategic locations
- **Extraction**: Reach evacuation point under fire
- **Survival**: Defend against waves of enemies

### Level Layout

#### Combat Zones
- **Central Courtyard**: Open area with scattered cover
- **Industrial Complex**: Multi-story building with interior combat
- **Perimeter**: Defensive positions and approach routes
- **Extraction Zone**: Helicopter landing pad for mission completion

#### Tactical Elements
- **High Ground**: Sniper positions and overwatch points
- **Chokepoints**: Corridors and doorways for CQB combat
- **Flanking Routes**: Alternative paths for tactical maneuvering
- **Destructible Cover**: Environmental elements that can be destroyed

## AI Implementation

### Enemy Forces
- **Faction**: Vultures Union (opposing force)
- **Count**: 8-12 AI enemies with varied roles
- **Behavior**: Basic combat AI with cover usage and flanking
- **Equipment**: Human-tier weapons with faction-appropriate appearance

### AI Roles
- **Riflemen**: Standard infantry with assault rifles
- **Heavies**: Armored units with machine guns
- **Scouts**: Fast-moving units with submachine guns
- **Snipers**: Long-range threats from elevated positions

## Player Systems

### Character Setup
- **Exosuit**: Light Frame for mobility testing
- **Primary Weapon**: Human-tier assault rifle
- **Sidearm**: Standard military pistol
- **Equipment**: Basic ammunition and medical supplies

### Core Mechanics
- **Movement**: Running, crouching, leaning, climbing
- **Combat**: ADS (Aim Down Sights), recoil, reload, weapon switching
- **Survival**: Health system, healing, respawn mechanics
- **Interaction**: Door opening, switch activation, item pickup

## HUD Implementation

### Essential Elements
- **Health/Armor**: Bottom left corner with visual feedback
- **Ammo Counter**: Bottom right with reload indicators
- **Compass**: Top center with objective markers
- **Crosshair**: Center screen with weapon-specific variants

### Status Indicators
- **Weapon Status**: Heat/charge for hybrid weapons
- **Equipment**: Grenades, medical supplies, deployables
- **Objectives**: Current mission status and waypoints
- **Squad**: Team member status and positioning

## Performance Targets

### Frame Rate Goals
- **Ultra Settings**: 90 FPS @ 1440p
- **High Settings**: 120 FPS @ 1080p
- **Medium Settings**: 90 FPS @ 1080p on mid-range hardware
- **Low Settings**: 60 FPS on minimum spec hardware

### Optimization Features
- **LOD System**: Distance-based detail reduction
- **Culling**: Frustum and occlusion culling for off-screen objects
- **Texture Streaming**: Dynamic texture resolution based on distance
- **Effect Scaling**: VFX complexity reduction for performance

## Audio Integration

### Weapon Audio
- **Gunfire**: Layered weapon discharge with distance falloff
- **Impacts**: Material-specific hit sounds
- **Reloads**: Mechanical weapon handling sounds
- **Environment**: Footsteps, movement, ambient sound

### Faction Audio
- **Vultures Union**: Improvised equipment sounds, salvager communications
- **Player Faction**: Professional military audio aesthetic
- **Environmental**: Industrial ambience, machinery, wind

## Visual Validation

### Art Style Testing
- **Faction Identity**: Clear visual distinction between player and enemy
- **Technology Tier**: Consistent Human-tier aesthetic
- **Environmental Storytelling**: Lore-appropriate details and atmosphere
- **Lighting**: Time-of-day and weather effect demonstration

### Material Implementation
- **Surface Variety**: Multiple material types with appropriate wear
- **Faction Colors**: Correct color palette application
- **Weathering System**: Procedural wear and damage demonstration
- **Performance**: Efficient material usage and rendering

## Testing Scenarios

### Combat Validation
- **Weapon Feel**: Recoil, accuracy, damage feedback
- **AI Behavior**: Enemy tactics, cover usage, difficulty
- **Player Movement**: Responsive controls, tactical positioning
- **Objective Clarity**: Clear mission goals and progress indication

### Performance Validation
- **Frame Rate**: Consistent performance across hardware ranges
- **Memory Usage**: Efficient resource utilization
- **Loading Times**: Rapid level loading and asset streaming
- **Stability**: Crash-free operation over extended play sessions

### Accessibility Validation
- **Visual**: High contrast modes, colorblind support
- **Audio**: Subtitle system, audio cue alternatives
- **Controls**: Button remapping, hold/toggle options
- **Difficulty**: Scalable challenge for different skill levels

## Implementation Notes

### Asset Requirements
- **Level Geometry**: Modular building blocks for rapid iteration
- **Props**: Industrial equipment, cover objects, decorative elements
- **Lighting**: Dynamic time-of-day system with weather effects
- **Effects**: Muzzle flashes, impacts, atmospheric particles

### Code Systems
- **Game Mode**: Basic team deathmatch with objective variants
- **Player Controller**: FPS controls with tactical movement
- **AI Controller**: Basic combat AI with state machine
- **HUD**: Essential information display with faction theming

### Content Pipeline
- **Asset Integration**: Streamlined import process for art assets
- **Iteration Speed**: Rapid testing and modification capability
- **Performance Monitoring**: Built-in profiling and optimization tools
- **Quality Assurance**: Automated testing for regression detection

## Success Metrics

### Gameplay Validation
- **Fun Factor**: Engaging combat with tactical depth
- **Visual Coherence**: Consistent art style and faction identity
- **Performance**: Stable frame rates on target hardware
- **Accessibility**: Inclusive design for diverse players

### Technical Validation
- **System Integration**: All game systems working together
- **Scalability**: Performance scaling across hardware ranges
- **Stability**: Reliable operation without crashes or bugs
- **Optimization**: Efficient resource usage and rendering

This playable slice serves as the foundation for expanded gameplay development and visual identity validation.