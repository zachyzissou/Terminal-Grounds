---
title: "Ui Style Guide"
type: "reference"
domain: "process"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Documentation Team"
tags: []
related_docs: []
---

# Terminal Grounds - UI Style Guide

## Core Principles

### Design Philosophy
- **Military Functional**: Every UI element serves a tactical purpose
- **High Readability**: Clear contrast and legibility in all conditions
- **Minimal Chrome**: Reduce decorative elements, maximize information density
- **Contextual Adaptation**: UI responds to faction affiliation and biome

## Typography

### Font Hierarchy
1. **Headers**: Industrial sans-serif, condensed weight
2. **Body**: Military stencil-inspired, high legibility
3. **Numbers**: Monospaced tactical display font
4. **Warnings**: Bold condensed, high contrast

### Size Standards
- **Large Headers**: 32pt
- **Section Headers**: 24pt
- **Body Text**: 16pt
- **Small Text**: 12pt
- **Minimum Size**: 10pt (tooltips only)

## Color System

### Universal Palette
- **Background**: `#0A0A0A` (90% opacity)
- **Primary Text**: `#E8E8E8`
- **Secondary Text**: `#A0A0A0`
- **Dividers**: `#2A2A2A`
- **Interactive**: `#00C2FF`
- **Warning**: `#D35400`
- **Critical**: `#C0392B`
- **Success**: `#27AE60`

### Faction Tints
UI elements adopt subtle faction color hints:
- **DIR**: Blue-gray tint
- **VLT**: Orange-rust tint
- **F77**: Neutral gray
- **CCB**: Cyan accent
- **NMD**: Brown-amber
- **VAC**: Purple accent
- **CWD**: Green tint

## Icon Design

### Icon Grid
- **Base Size**: 64x64 grid
- **Safe Zone**: 8px padding
- **Stroke Weight**: 4px consistent
- **Corner Radius**: 0px (sharp military aesthetic)

### Icon Categories

#### Damage Types
- **Kinetic**: Bullet silhouette
- **Energy**: Lightning bolt
- **Plasma**: Circular burst
- **Chemical**: Droplet symbol
- **Explosive**: Blast radius

#### Status Effects
- **Bleeding**: Blood drop
- **Stunned**: Dizzy spiral
- **Suppressed**: Downward arrows
- **Burning**: Flame icon
- **Poisoned**: Skull symbol
- **Shielded**: Hexagon outline

#### Mission Objectives
- **Attack**: Crosshair
- **Defend**: Shield
- **Extract**: Exit arrow
- **Escort**: Double chevron
- **Hack**: Terminal icon
- **Survive**: Clock symbol

#### Rarity Tiers
- **Common**: No border
- **Uncommon**: Single line border
- **Rare**: Double line border
- **Epic**: Triple line with corner accents
- **Legendary**: Full frame with energy effect

## HUD Layout

### Screen Zones
```
┌─────────────────────────────────┐
│ [Mission] [Timer]    [Squad]    │  Top Bar
├─────────────────────────────────┤
│                                 │
│          Main View              │  Game World
│                                 │
├─────┬───────────────────┬───────┤
│Health│               │ Minimap  │  Bottom HUD
│Ammo  │   Actions     │ Tactical │
└─────┴───────────────────┴───────┘
```

### Element Specifications

#### Health/Shield Display
- Segmented bars (not smooth)
- Faction-colored accents
- Numeric overlay
- Damage direction indicators

#### Ammo Counter
- Large primary count
- Magazine visualization
- Ammo type icon
- Reserve display

#### Minimap
- 200x200px default
- Faction-colored friendlies
- Objective markers
- Threat indicators
- Extraction zones

## Menu Design

### Main Menu
- Full-screen background (biome concept art)
- Left-aligned navigation
- Faction emblem watermark
- Version info bottom-right

### Inventory Grid
- 64x64 item cells
- Rarity border system
- Stack count overlay
- Hover tooltip expansion
- Drag-and-drop indicators

### Loadout Screen
- 3D character preview
- Equipment slots
- Stat comparisons
- Mod attachment tree

## Interactive States

### Button States
1. **Default**: Base color, 1px border
2. **Hover**: 20% brightness increase, glow
3. **Active**: Inset shadow, color shift
4. **Disabled**: 50% opacity, no border
5. **Selected**: Faction color highlight

### Feedback Systems
- **Click**: Sharp mechanical sound
- **Hover**: Subtle highlight animation
- **Error**: Red flash + shake
- **Success**: Green pulse
- **Critical**: Red strobe warning

## Animation Guidelines

### Timing
- **Instant**: 0ms (critical actions)
- **Fast**: 150ms (menu transitions)
- **Normal**: 300ms (standard animations)
- **Slow**: 500ms (dramatic reveals)

### Easing
- **Menu**: Cubic-bezier(0.4, 0, 0.2, 1)
- **HUD Updates**: Linear
- **Alerts**: Elastic for attention

## Accessibility

### Requirements
- **Colorblind Modes**: Protanopia, Deuteranopia, Tritanopia
- **UI Scale**: 80% - 150% range
- **Subtitles**: With speaker tags
- **Input Hints**: Platform-appropriate icons
- **Screen Reader**: Compatibility tags

### Contrast Ratios
- **Normal Text**: 7:1 minimum
- **Large Text**: 4.5:1 minimum
- **Icons**: 3:1 minimum
- **Decorative**: No requirement

## Platform Adaptations

### PC
- Mouse-optimized hover states
- Keyboard shortcuts visible
- Higher information density
- Tooltips on hover

### Console
- D-pad navigation optimized
- Larger touch targets
- Simplified menus
- Button prompts

### Steam Deck
- Touch-friendly sizing
- Readable at 7" screen
- Modified layout for 16:10

## Technical Specifications

### Asset Requirements
- **Format**: PNG with alpha
- **Compression**: BC7 for quality, BC1 for performance
- **Mipmaps**: Disabled for UI
- **sRGB**: Enabled
- **Power of 2**: Required for atlases

### Performance Targets
- **Draw Calls**: <50 for full HUD
- **Texture Memory**: <128MB UI atlas
- **Update Rate**: 60fps minimum
- **Response Time**: <100ms input latency

## Implementation Notes

### Unreal Engine 5.6
- Use UMG for all UI
- Implement view models for data binding
- Utilize UI materials for effects
- Optimize with widget pooling
- Use invalidation boxes

### Scalability
- Support 720p to 4K
- Dynamic resolution scaling
- LOD system for complex widgets
- Async loading for menus

---

*Version 1.0 - Phase 4 Implementation*
*Engine: Unreal Engine 5.6*
*Target Platforms: PC, Console, Steam Deck*
