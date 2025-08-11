# Base Module Concepts

## Drone Bay
- **Function**: Craft, launch, and control UAV drones
- **Power Requirement**: High (150 units/hour)
- **Materials**: Reinforced concrete, launch rails, control systems
- **Palette**: #34495E (Gray), #F39C12 (Launch Lights), #2ECC71 (Ready Status)
- **Silhouette**:
```
    ╔═══════════════════════╗
    ║ 🚁 DRONE BAY ALPHA 🚁 ║
    ║ ╔═╗ ╔═╗ ╔═╗ ╔═╗     ║
    ║ ║1║ ║2║ ║3║ ║4║     ║
    ║ ╚═╝ ╚═╝ ╚═╝ ╚═╝     ║
    ║ [LAUNCH RAILS]        ║
    ║ [CONTROL STATION]     ║
    ╚═══════════════════════╝
    Dimensions: 15m x 10m x 4m
```

## Shield Generator
- **Function**: Area damage reduction field around base
- **Power Requirement**: Very High (200 units/hour)
- **Materials**: Alien-hybrid technology, energy emitters, control core
- **Palette**: #00C2FF (Shield Blue), #2C3E50 (Housing), #E74C3C (Warning)
- **Silhouette**:
```
    ⚡ SHIELD FIELD ACTIVE ⚡
    ╔═══════════════════════╗
    ║  ░░░░░ SHIELD ░░░░░   ║
    ║ ░ ◉ GENERATOR ◉ ░    ║
    ║  ░░░░░░░░░░░░░░░░░    ║
    ║ [POWER CORE] [FIELD] ║
    ║ [EMITTERS ] [CTRL ]  ║
    ╚═══════════════════════╝
    Dimensions: 8m x 8m x 6m
```

## Reactor
- **Function**: Convert fuel into electrical power for base systems
- **Power Output**: 300 units/hour (fuel dependent)
- **Materials**: Reinforced containment, cooling systems, control panels
- **Palette**: #F39C12 (Energy Core), #2C3E50 (Housing), #E74C3C (Danger)
- **Silhouette**:
```
    ☢️ REACTOR CORE ACTIVE ☢️
    ╔═══════════════════════╗
    ║ ≋≋≋≋≋ REACTOR ≋≋≋≋≋  ║
    ║ ≋ ⚡ POWER CORE ⚡ ≋  ║
    ║ ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋  ║
    ║ [COOLANT] [FUEL]     ║
    ║ [CONTROL] [OUTPUT]   ║
    ╚═══════════════════════╝
    Dimensions: 10m x 10m x 8m
```

## Vehicle Garage
- **Function**: Store, spawn, and repair vehicles
- **Power Requirement**: Medium (100 units/hour)
- **Materials**: Industrial garage structure, repair equipment, vehicle lifts
- **Palette**: #7F8C8D (Industrial Gray), #F39C12 (Work Lights), #2ECC71 (Ready)
- **Silhouette**:
```
    🚗 VEHICLE GARAGE 🚗
    ╔═══════════════════════╗
    ║ [📦] [📦] [📦] [📦]  ║
    ║  V1   V2   V3   V4   ║
    ║ ╔═════════════════╗   ║
    ║ ║ 🔧 REPAIR BAY 🔧║   ║
    ║ ╚═════════════════╝   ║
    ║ [LIFT] [CRANE] [FUEL]║
    ╚═══════════════════════╝
    Dimensions: 20m x 15m x 5m
```

## Power Graph System
- **Reactor** → **Main Grid** → **Modules**
- **Consumption Priority**: Shield > Drone Bay > Garage > Workbench
- **Overload Protection**: Auto-shutdown non-critical systems
- **Faction Bonuses**:
  - Archivists: Shield Generator +10% efficiency
  - Nomads: Vehicle Garage +15% spawn speed
  - Combine: Reactor +5% power output
  - Wardens: All modules +5% damage resistance