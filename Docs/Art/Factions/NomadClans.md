# Nomad Clans Faction Style Guide

## Faction Identity
The Nomad Clans are mobile communities of traders and raiders who dominate the wasteland roads. They specialize in convoy operations, vehicle modification, and long-range logistics.

## Visual Philosophy
**Road Warrior** • **Mobile Community** • **Vehicular Culture**

The Nomad aesthetic emphasizes mobility, vehicle integration, and road-hardened functionality. Their equipment should feel designed for constant movement and harsh travel conditions.

## Color Palette

### Primary Colors
- **Road-Worn Brown**: `#8B4513` - Dust, earth, travel wear
- **Convoy Orange**: `#FF8C00` - Visibility, traffic safety, identification
- **Dust Tan**: `#D2B48C` - Desert travel, camouflage, weathering

### Secondary Colors
- **Engine Black**: `#1C1C1C` - Mechanical components, oil stains, rubber
- **Fuel Blue**: `#4682B4` - Fuel systems, coolant, technical fluids

### Usage Guidelines
- Road-worn brown for primary structural elements (40% coverage)
- Convoy orange for identification and safety systems (25% coverage)
- Dust tan for fabric and secondary surfaces (20% coverage)
- Engine black for mechanical and technical components (10% coverage)
- Fuel blue for fluid systems and technical indicators (5% coverage)

## Material Motifs

### Road-Hardened Construction
- **Base Materials**: Heavy steel plate, reinforced aluminum, impact polymers
- **Surface Treatments**: Powder coating, rust preventatives, impact protection
- **Wear Patterns**: Road wear, vibration damage, impact scarring, dust accumulation
- **Detail Elements**: Route markers, clan symbols, travel stickers

### Vehicle Integration
- **Mounting Systems**: Universal attachment points for equipment and weapons
- **Mobility Focus**: Lightweight, compact, easy to secure for travel
- **Modular Design**: Interchangeable components for different convoy roles

## Insignia and Iconography

### Primary Emblem
- **Symbol**: Stylized wheel with crossed axes representing movement and conflict
- **Colors**: Orange wheel on brown field with dust tan spokes
- **Usage**: Painted on vehicles, stamped into metal, sewn on clothing

### Secondary Symbols
- **Clan Markers**: Individual clan identification within the greater alliance
- **Route Signs**: Directional markers and navigation aids
- **Trade Symbols**: Commodity identification and exchange rates

### Typography
- **Primary Font**: Bold road sign lettering for maximum visibility
- **Secondary Font**: Stencil fonts for equipment marking
- **Hierarchy**: Large (clan ID), Medium (route info), Small (maintenance data)

## Silhouette Design Language

### Character Silhouettes
- **Drivers**: Vehicle-focused gear with communication and navigation equipment
- **Guards**: Mobile combat equipment optimized for convoy defense
- **Traders**: Cargo handling equipment and negotiation tools

### Vehicle Silhouettes
- **Design Principles**: Heavy, reinforced, obviously modified for long-distance travel
- **Proportions**: Extended fuel capacity, armor protection, cargo space
- **Details**: External equipment racks, communication arrays, defensive positions

### Weapon Silhouettes
- **Characteristics**: Vehicle-mounted or easily transportable systems
- **Mounting**: Universal vehicle mounts and quick-deployment systems
- **Condition**: Road-tested, vibration-resistant, weather-protected

## Environmental Control Points

### Mobile Camps
- **Layout**: Circular defensive arrangement with vehicles forming perimeter
- **Equipment**: Portable facilities, rapid deployment systems
- **Logistics**: Fuel storage, maintenance areas, communication centers

### Trading Posts
- **Construction**: Semi-permanent structures at crossroads and water sources
- **Commerce**: Exchange facilities, warehousing, fuel stations
- **Defense**: Fortified positions with clear sight lines

### Convoy Formations
- **Organization**: Standard convoy arrangements for different mission types
- **Communication**: Vehicle-to-vehicle coordination systems
- **Defense**: Escort positions and defensive fire patterns

## Technology Integration

### Vehicle-Centric Systems
- **Aesthetic**: Everything designed for vehicle integration and mobility
- **Reliability**: Proven systems that can survive constant vibration and impacts
- **Modification**: Extensive vehicle modification and performance enhancement

### Mobile Workshops
- **Integration**: Repair facilities that can be rapidly deployed and relocated
- **Capability**: Field maintenance, modification, and fabrication systems
- **Efficiency**: Maximum capability with minimum setup time

### Navigation Technology
- **Approach**: Advanced navigation and communication systems for convoy coordination
- **Equipment**: GPS, radio, satellite communication for route planning
- **Redundancy**: Multiple backup systems for critical navigation functions

## Audio Identity
- **Communication Style**: Road-focused terminology, convoy coordination
- **Equipment Sounds**: Vehicle-mounted systems, mobile equipment operation
- **Voice Characteristics**: Road wisdom, convoy leadership
- **Ambient Identity**: Engine operation, convoy movement, mobile camp sounds

## Mobile Culture Elements

### Clan Hierarchy
- **Road Captains**: Convoy leadership with navigation and tactical responsibility
- **Specialists**: Mechanics, traders, and scouts with specific convoy roles
- **Community**: Extended family groups traveling together for mutual protection

### Trade Networks
- **Route Knowledge**: Detailed information about safe passages and trading opportunities
- **Commodity Exchange**: Mobile trading systems and currency management
- **Information Brokerage**: Intelligence gathering and dissemination services

### Survival Systems
- **Resource Management**: Fuel, water, and food conservation strategies
- **Maintenance Protocols**: Preventive maintenance and field repair procedures
- **Security Measures**: Convoy defense and threat assessment systems

## Weathering and Travel Wear

### Road Conditions
- **Dust Accumulation**: Heavy dust loading from constant travel
- **Vibration Damage**: Fatigue cracking and fastener loosening
- **Impact Damage**: Stone chips, debris impacts, collision damage

### Environmental Exposure
- **Solar Degradation**: UV damage to polymers and painted surfaces
- **Temperature Cycling**: Thermal stress from desert day/night cycles
- **Sandblasting**: Abrasive wear from wind-blown particulates

### Maintenance Patterns
- **Field Repairs**: Visible patch work and improvised fixes
- **Component Replacement**: Mixed-age components from various sources
- **Upgrade Integration**: Progressive improvement over time

## Asset Implementation Notes

### UE5 Asset Paths
- **Materials**: `Content/TG/Materials/Factions/Nomads/`
- **Textures**: `Content/TG/Textures/Factions/Nomads/`
- **Meshes**: `Content/TG/Meshes/Factions/Nomads/`
- **Decals**: `Content/TG/Decals/Factions/Nomads/`

### Master Material Parameters
- **Faction_Color_Primary**: (0.55, 0.27, 0.07) - Road-Worn Brown
- **Faction_Color_Secondary**: (1.0, 0.55, 0.0) - Convoy Orange
- **Faction_Color_Accent**: (0.82, 0.71, 0.55) - Dust Tan
- **Weathering_Amount**: 0.7 (heavy travel wear)
- **Reflectance_Value**: 0.05 (dust-covered surfaces)

### Travel Wear Systems
- **Dust Simulation**: Procedural dust accumulation based on surface angle
- **Vibration Wear**: Fatigue patterns around mounting points and stress areas
- **Impact Damage**: Random impact scarring from road debris
- **Route Marking**: Decal system for travel stickers and route markers

### Performance Considerations
- Vehicle-based LOD system optimized for convoy scenarios
- Dust effect systems designed for multiple simultaneous vehicles
- Modular attachment system for convoy role specialization
- Audio occlusion system for convoy formation communication