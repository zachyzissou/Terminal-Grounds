# UI/HUD Concept Documentation

## Heat/Charge Indicators

- **Location**: Lower right HUD, near ammo counter
- **Field Weapons**: No indicator (conventional ammo only)
- **Splice Weapons**: Heat bar (blue→yellow→red), overheat warning
- **Monolith Weapons**: Charge indicator (violet glow), phase ready state

### Heat Bar Design
 
```text
HEAT: ████████░░ 80%
      BLUE  RED   DANGER
```


### Charge Indicator Design  

```text
CHARGE: ◉◉◉◉◉ READY
  VIOLET GLOW
```

## Jamming Status

- **Location**: Upper left, near minimap
- **States**: Clear, Interference, Jammed
- **Visual**: Signal strength bars with interference effects

```text
SIGNAL: ████░ CLEAR
SIGNAL: ≋≋≋≋░ JAMMING
SIGNAL: ░░░░░ BLOCKED
```

## Drone Control Widget

- **Location**: Center screen overlay when controlling drones
- **Elements**:
  - Camera feed (bandwidth-limited snapshots)
  - Range indicator
  - Battery level
  - Signal strength
  - Control mode (Direct/Waypoint/Auto)

```text
╔═══════════════════════════╗
║ 🚁 DRONE CONTROL ACTIVE   ║
║ ╔═════════════════╗       ║
║ ║ CAMERA FEED     ║ 📡 85%║
║ ║ [▓▓▓▓▓▓▓▓░░]   ║ 🔋 67%║
║ ║ RANGE: 250m    ║ SIGNAL║
║ ╚═════════════════╝       ║
║ [DIRECT] [WAYPOINT] [AUTO]║
╚═══════════════════════════╝
```

## Exosuit Frame Indicator

- **Location**: Bottom left, character status area
- **Shows**: Frame type, armor integrity, movement modifiers

```text
EXOSUIT: [ASSAULT] ████████░░ 80%
MODS: +ADS -SPEED +ARMOR
```

## Event Notification System

- **Location**: Top center, temporary overlay
- **Events**: Convoy War, Blacksky Barrage, Monolith Bloom, Vault Clarion, Drone Swarm
- **Duration**: 10 seconds, fades to minimap icon

```text
⚡ EVENT DETECTED ⚡
CONVOY WAR - SECTOR 7
DISTANCE: 1.2km NE
[INVESTIGATE] [IGNORE]
```
