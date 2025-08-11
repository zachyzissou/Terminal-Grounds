# Directorate Faction Style Guide

## Faction Identity
The Directorate represents the last remnant of unified human military command. Born from the collapse of the Global Reconstruction Accord, they maintain strict military discipline and hierarchical structure in a fractured world.

## Visual Philosophy
**Military Precision** • **Corporate Authority** • **Technological Superiority**

The Directorate aesthetic emphasizes clean lines, institutional authority, and technological advancement. Their equipment should feel mass-produced, standardized, and reliable.

## Color Palette

### Primary Colors
- **Navy Blue**: `#001F3F` - Authority, command, tradition
- **Gunmetal Gray**: `#36454F` - Industrial strength, durability
- **Crisp White**: `#FFFFFF` - Cleanliness, precision, medical/tech accents

### Secondary Colors
- **Steel Blue**: `#4682B4` - Technology interfaces, energy systems
- **Tactical Black**: `#2F2F2F` - Stealth operations, special forces

### Usage Guidelines
- Navy blue for primary faction identification (60% coverage)
- Gunmetal gray for structural elements (25% coverage)
- White for accents, medical symbols, technology displays (10% coverage)
- Steel blue for energy/interface elements (5% coverage)

## Material Motifs

### Armor and Equipment
- **Base Materials**: Mil-spec aluminum, composite ceramics, ballistic polymers
- **Surface Treatments**: Anodized navy finish, anti-reflective coatings
- **Wear Patterns**: Clean maintenance, minimal corrosion, contact wear at stress points
- **Detail Elements**: Military nomenclature, service numbers, rank insignia

### Fabric and Soft Goods
- **Uniform Base**: Navy blue ripstop fabric with subtle technical weave
- **Accent Materials**: White medical tape, steel blue utility straps
- **Weathering**: Clean laundering, minimal field wear, proper maintenance

## Insignia and Iconography

### Primary Emblem
- **Symbol**: Eagle head in profile within angular shield
- **Colors**: White eagle on navy field with steel blue border
- **Usage**: Primary identification on vehicles, facilities, uniforms

### Secondary Symbols
- **Rank Chevrons**: White on navy background, clean geometric lines
- **Unit Patches**: Standardized rectangular format, departmental colors
- **Warning Labels**: International military standards, trilingual text

### Typography
- **Primary Font**: Military stencil letterforms, high contrast
- **Secondary Font**: Technical sans-serif for data displays
- **Hierarchy**: Large (unit ID), Medium (personnel), Small (technical data)

## Silhouette Design Language

### Character Silhouettes
- **Officers**: Clean, pressed uniforms with minimal external gear
- **Infantry**: Standardized load-bearing equipment, recognizable military profile
- **Specialists**: Role-specific equipment while maintaining faction consistency

### Vehicle Silhouettes
- **Design Principles**: Angular, functional, recognizable military aesthetics
- **Proportions**: Conventional military vehicle ratios and dimensions
- **Details**: External equipment properly secured, official markings visible

### Weapon Silhouettes
- **Characteristics**: Familiar firearm profiles with military furniture
- **Attachments**: Standardized mounting systems, institutional procurement
- **Condition**: Well-maintained, properly zeroed, regulation appearance

## Environmental Control Points

### Fortifications
- **Bunker Style**: Reinforced concrete with navy blue identification bands
- **Barriers**: Standardized HESCO-style with Directorate markings
- **Signage**: Official warning signs in regulation format

### Equipment Staging
- **Supply Points**: Organized depot layout with proper labeling
- **Vehicle Parks**: Regulation spacing and maintenance areas
- **Command Posts**: Clean facility layout with proper communications

### Battlefield Markings
- **Territory Control**: Navy blue paint on key structures
- **Navigation**: Standard military map symbols and coordinates
- **Hazard Markers**: Regulation warning signs and barrier tape

## Technology Integration

### Human-Tier Equipment
- **Aesthetic**: Mass-produced military standard with quality control
- **Reliability**: Consistent performance, standardized maintenance
- **Modification**: Official upgrades only, no field modifications

### Hybrid Technology Adoption
- **Integration**: Careful testing and official procurement channels
- **Appearance**: Hybrid tech housed in regulation-compliant casings
- **Markings**: Official acceptance testing and certification labels

## Audio Identity
- **Communication Style**: Military radio protocols, clear command structure
- **Equipment Sounds**: Well-maintained gear, precise mechanical operation
- **Voice Characteristics**: Professional military bearing, disciplined communication
- **Ambient Identity**: Clean facility operation, organized equipment handling

## Asset Implementation Notes

### UE5 Asset Paths
- **Materials**: `Content/TG/Materials/Factions/Directorate/`
- **Textures**: `Content/TG/Textures/Factions/Directorate/`
- **Meshes**: `Content/TG/Meshes/Factions/Directorate/`
- **Decals**: `Content/TG/Decals/Factions/Directorate/`

### Master Material Parameters
- **Faction_Color_Primary**: (0.0, 0.12, 0.25) - Navy Blue
- **Faction_Color_Secondary**: (0.21, 0.27, 0.31) - Gunmetal Gray
- **Faction_Color_Accent**: (1.0, 1.0, 1.0) - White
- **Weathering_Amount**: 0.2 (minimal wear)
- **Reflectance_Value**: 0.04 (military non-reflective)

### Performance Considerations
- Standard military equipment should use shared base materials
- Faction-specific elements applied through material instances
- LOD system prioritizes recognizable silhouette features
- Decal atlas includes faction symbols for efficient rendering