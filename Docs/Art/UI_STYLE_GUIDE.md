# Terminal Grounds UI Style Guide

## UI Philosophy

Terminal Grounds UI prioritizes **tactical clarity**, **diegetic integration**, and **accessibility**. The interface should feel like military-grade equipment integrated into the character's helmet and equipment systems.

## Design Principles

### 1. Diegetic Integration
- UI elements exist within the game world as helmet HUD overlays
- Interface components represent actual equipment systems
- No "floating" UI elements that break immersion

### 2. Tactical Clarity
- Critical information always visible and unambiguous
- Clear visual hierarchy for combat situations
- Rapid information processing under stress

### 3. Faction Consistency
- UI elements reflect faction technology and aesthetic
- Color schemes match faction identity
- Equipment interfaces show appropriate wear and technology level

### 4. Performance Scalability
- Clean rendering at all resolution scales
- Accessibility features for visual impairments
- Mobile platform compatibility

## Typography

### Primary Font: **Tactical Stencil**
- **Usage**: Alerts, warnings, critical information
- **Characteristics**: High contrast, stencil letterforms, military heritage
- **Size Range**: 14pt - 48pt
- **Weight**: Bold only
- **Color**: High contrast white/black or faction colors

### Secondary Font: **Technical Sans**
- **Usage**: Data displays, statistics, technical information
- **Characteristics**: Clean, monospace, high legibility
- **Size Range**: 8pt - 24pt
- **Weight**: Regular, Medium, Bold
- **Color**: Neutral grays with accent colors

### Accent Font: **Callsign Script**
- **Usage**: Player names, unit designations, signatures
- **Characteristics**: Hand-written military style, personal touch
- **Size Range**: 10pt - 16pt
- **Weight**: Regular only
- **Color**: Faction accent colors

## Color System

### Semantic Colors

#### Status Indicators
- **Safe/Good**: `#7ED321` - Bright green for positive status
- **Caution/Warning**: `#F5A623` - Amber for attention required
- **Danger/Critical**: `#D0021B` - Red for immediate action needed
- **Info/Neutral**: `#4A90E2` - Blue for informational content

#### System States
- **Active/Online**: `#50E3C2` - Cyan for active systems
- **Standby/Ready**: `#B8E986` - Light green for ready systems
- **Offline/Disabled**: `#9B9B9B` - Gray for inactive systems
- **Error/Malfunction**: `#BD10E0` - Purple for system errors

### Faction UI Variants

#### Directorate UI
- **Primary**: Navy blue backgrounds with white text
- **Accent**: Steel blue for interactive elements
- **Style**: Clean, institutional, high contrast

#### Vultures Union UI
- **Primary**: Dark gray/black backgrounds with amber text
- **Accent**: Warning yellow for critical elements
- **Style**: Improvised, weathered, functional

#### Free 77 UI
- **Primary**: Neutral tan backgrounds with black text
- **Accent**: Tactical brown for interactive elements
- **Style**: Professional, clean, efficient

#### Corporate Combine UI
- **Primary**: Corporate blue with white/silver text
- **Accent**: Energy purple for advanced systems
- **Style**: High-tech, sleek, experimental

#### Nomad Clans UI
- **Primary**: Road brown backgrounds with orange text
- **Accent**: Convoy orange for navigation elements
- **Style**: Vehicle-integrated, rugged, mobile

#### Vaulted Archivists UI
- **Primary**: Archive green with gold text
- **Accent**: Mystery purple for alien systems
- **Style**: Academic, reverent, mystical

#### Civic Wardens UI
- **Primary**: Emergency blue with white text
- **Accent**: Safety orange for alert systems
- **Style**: Medical, clean, safety-focused

## Iconography

### Icon Categories

#### Status Icons (24x24px baseline)
- **Health**: Medical cross, heart symbol
- **Armor**: Shield symbol, protection indicator
- **Ammunition**: Bullet symbols, magazine indicator
- **Energy**: Battery symbols, charge indicators

#### Weapon Icons (32x32px baseline)
- **Human Weapons**: Realistic firearm silhouettes
- **Hybrid Weapons**: Energy-enhanced weapon silhouettes
- **Alien Weapons**: Abstract energy construct symbols

#### Equipment Icons (28x28px baseline)
- **Attachments**: Scope, grip, muzzle device symbols
- **Deployables**: Drone, sensor, mine symbols
- **Medical**: Medkit, stim, bandage symbols

#### Navigation Icons (20x20px baseline)
- **Compass**: Directional indicators, bearing symbols
- **Waypoints**: Objective markers, navigation points
- **Hazards**: Warning symbols, danger indicators

### Icon Design Rules
- **2px minimum stroke width** for visibility
- **High contrast** against all background colors
- **Scalable vector format** (SVG) for all platforms
- **Faction variants** using appropriate color schemes

## HUD Layout

### Primary HUD Elements

#### Health/Armor Display (Bottom Left)
- **Position**: Bottom left corner, 20px margins
- **Layout**: Vertical bar with numerical display
- **Colors**: Health (red), Armor (blue), critical flash (white)
- **Animation**: Smooth transitions, damage flash effects

#### Ammo Counter (Bottom Right)
- **Position**: Bottom right corner, 20px margins
- **Layout**: Large current ammo, small reserve ammo
- **Colors**: Normal (white), low ammo (yellow), empty (red)
- **Animation**: Number flip animation, reload indicators

#### Compass/Minimap (Top Center)
- **Position**: Top center, 40px from edge
- **Layout**: Circular compass with bearing indicators
- **Colors**: Background (translucent black), markers (faction colors)
- **Animation**: Smooth rotation, objective pulsing

#### Heat/Charge Indicators (Weapon-Dependent)
- **Position**: Near crosshair, context-sensitive
- **Layout**: Horizontal bar with threshold markers
- **Colors**: Cold (blue) to Hot (red), overload (white flash)
- **Animation**: Progressive fill, overload warning pulse

### Secondary HUD Elements

#### Squad Status (Left Side)
- **Position**: Left edge, centered vertically
- **Layout**: Vertical list of squad member status
- **Colors**: Faction colors with status overlays
- **Animation**: Health changes, distance indicators

#### Objective Tracker (Top Right)
- **Position**: Top right corner, 40px margins
- **Layout**: Compact objective list with progress
- **Colors**: Incomplete (white), complete (green), failed (red)
- **Animation**: Progress bars, completion checkmarks

#### Equipment Selector (Bottom Center)
- **Position**: Bottom center, above crosshair area
- **Layout**: Horizontal equipment icons with selection indicator
- **Colors**: Available (white), selected (faction color), unavailable (gray)
- **Animation**: Selection slide, availability fade

## Menu System Design

### Main Menu
- **Background**: Faction-appropriate scene with subtle animation
- **Layout**: Vertical menu with large touch targets
- **Typography**: Tactical Stencil for headings, Technical Sans for options
- **Colors**: Faction primary colors with high contrast text

### In-Game Menus
- **Background**: Translucent overlay maintaining game visibility
- **Layout**: Grid-based layout with clear information hierarchy
- **Typography**: Technical Sans primary, Tactical Stencil for warnings
- **Colors**: Faction-appropriate with alpha transparency

### Inventory System
- **Layout**: Grid-based item display with drag-and-drop functionality
- **Item Cards**: Equipment images with stat overlays
- **Sorting**: Category tabs with search and filter options
- **Colors**: Rarity coding (Common/Rare/Epic/Legendary)

## Interactive Elements

### Buttons
- **Primary Buttons**: Faction color background, white text, 44px minimum height
- **Secondary Buttons**: Transparent background, faction color border and text
- **Icon Buttons**: 32px square minimum, faction color on interaction
- **Disabled State**: 50% opacity with gray overlay

### Input Fields
- **Text Input**: Dark background, faction color border, white text
- **Search Fields**: Magnifying glass icon, placeholder text in gray
- **Validation**: Green border for valid, red border for invalid

### Sliders
- **Track**: Dark gray background with faction color fill
- **Handle**: Faction color circle with white center
- **Labels**: Technical Sans font with min/max values

### Toggle Switches
- **Off State**: Dark gray background, white circle on left
- **On State**: Faction color background, white circle on right
- **Animation**: Smooth slide transition, 0.2 second duration

## Animation Standards

### Timing
- **Fast**: 0.1s - Immediate feedback (button presses, selections)
- **Standard**: 0.2s - UI transitions (menu slides, fades)
- **Slow**: 0.3s - Major state changes (screen transitions)

### Easing
- **Ease-Out**: For appearing elements (menus opening)
- **Ease-In**: For disappearing elements (menus closing)
- **Ease-In-Out**: For element movement (sliding panels)

### Effects
- **Fade**: Alpha transition for overlay elements
- **Slide**: Position transition for panel movements
- **Scale**: Size transition for focus states
- **Pulse**: Subtle scale animation for attention

## Accessibility Features

### Visual Accessibility
- **High Contrast Mode**: Increased contrast ratios for all UI elements
- **Color Blind Support**: Pattern and shape alternatives to color coding
- **Text Scaling**: 125%, 150%, 200% scaling options
- **Motion Sensitivity**: Reduced animation options for motion sensitivity

### Audio Accessibility
- **Screen Reader**: Full voice-over support for all UI elements
- **Audio Cues**: Sound feedback for UI interactions
- **Subtitle Options**: Comprehensive subtitle system with speaker identification

### Motor Accessibility
- **Large Touch Targets**: Minimum 44px for all interactive elements
- **Voice Commands**: Voice control for menu navigation
- **Controller Support**: Full gamepad support with custom binding
- **Hold/Toggle Options**: Alternatives to hold-based interactions

## Responsive Design

### Resolution Scaling
- **1080p (1920x1080)**: Baseline design resolution
- **1440p (2560x1440)**: 133% scaling with improved text clarity
- **4K (3840x2160)**: 200% scaling maintaining sharpness
- **Mobile (720p+)**: Adaptive layout with touch-optimized controls

### Aspect Ratio Support
- **16:9 (Standard)**: Default layout optimization
- **21:9 (Ultrawide)**: Extended HUD with additional information
- **4:3 (Legacy)**: Compact layout with essential information only

## Asset Implementation

### UE5 Asset Organization
- **UI Materials**: `Content/TG/UI/Materials/`
- **UI Textures**: `Content/TG/UI/Textures/`
- **Icon Assets**: `Content/TG/UI/Icons/`
- **Font Assets**: `Content/TG/UI/Fonts/`

### Widget Blueprint Structure
- **HUD Widgets**: `Content/TG/UI/HUD/`
- **Menu Widgets**: `Content/TG/UI/Menus/`
- **Faction Variants**: `Content/TG/UI/Factions/`

### Performance Guidelines
- **Texture Atlasing**: Combine small UI elements into atlas textures
- **Widget Pooling**: Reuse widgets to minimize garbage collection
- **LOD System**: Simplify UI elements at low resolutions
- **Batch Rendering**: Group similar UI elements for efficient rendering

## Development Standards

### Naming Conventions
- **Widgets**: WBP_[Category]_[Name] (e.g., WBP_HUD_AmmoCounter)
- **Materials**: MI_UI_[Element] (e.g., MI_UI_Button_Primary)
- **Textures**: T_UI_[Element] (e.g., T_UI_Icons_Weapons)

### Version Control
- **Widget Variants**: Separate blueprints for faction-specific variants
- **Shared Components**: Base widgets inherited by faction variants
- **Asset Dependencies**: Clear dependency chains for shared resources

### Testing Requirements
- **Resolution Testing**: Verify appearance at all supported resolutions
- **Accessibility Testing**: Validate with accessibility tools and users
- **Performance Testing**: Measure UI rendering performance impact
- **Localization Testing**: Verify layout with translated text

## UE asset path index (UI)

- HUD Widgets: `Content/TG/UI/HUD/`
- Menus: `Content/TG/UI/Menus/`
- Icons: `Content/TG/UI/Icons/`
- Fonts: `Content/TG/UI/Fonts/`
- Materials: `Content/TG/UI/Materials/`
