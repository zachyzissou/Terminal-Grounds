# Terminal Grounds - Metro Underground Level Manual Implementation Guide

## Phase 1 Foundational Playability Level
**Level Name**: TG_MetroUnderground_Phase1  
**Target Performance**: 60+ FPS  
**Player Count**: 1-8 players  
**Setting**: Underground metro tunnel system with faction territorial control

---

## Quick Implementation Steps

### Step 1: Create New Level
1. Open Unreal Editor with Terminal Grounds project
2. **File > New Level > Empty Level**
3. Save as: `/Game/Maps/TG_MetroUnderground_Phase1`

### Step 2: Execute Python Implementation Script
```python
# In Unreal Editor Python Console:
exec(open(r'C:\Users\Zachg\Terminal-Grounds\Tools\MapCreation\TG_MetroUnderground_Implementation.py').read())
```

**OR Follow Manual Steps Below:**

---

## Manual Implementation Guide

### SPATIAL DESIGN: Basic Geometry Creation

#### Primary Corridors

**Main Transit Tunnel:**
- Location: Center of level (0, 0, -200)
- Dimensions: 3600 x 400 x 300 units
- Create using: Geometry > BSP > Box Brush
- Position: X=-1800 to X=1800, Y=-200 to Y=200, Z=-350 to Z=-50

**North Service Tunnel:**
- Location: (0, 1000, -150)
- Dimensions: 1600 x 200 x 250 units
- Position: X=-800 to X=800, Y=800 to Y=1200, Z=-275 to Z=-25

**South Maintenance Level:**
- Location: (0, -800, -300)
- Dimensions: 1200 x 400 x 200 units
- Position: X=-600 to X=600, Y=-1000 to Y=-600, Z=-400 to Z=-200

**Central Access Shaft:**
- Location: (0, 0, -100)
- Type: Cylinder brush
- Dimensions: Radius=75, Height=400
- Connects all three levels vertically

### LIGHTING SYSTEM: Atmospheric Underground Environment

#### Primary Lighting
1. **Directional Light** - "Ambient Surface Light"
   - Location: (0, 0, 500)
   - Rotation: Pitch=-45°
   - Intensity: 0.3
   - Color: Light Blue (0.8, 0.9, 1.0)

#### Emergency Lighting System
Create **18 Point Lights** along main tunnel:
```
Positions (every 400 units):
(-1600, -150, 50), (-1600, 150, 50)
(-1200, -150, 50), (-1200, 150, 50)
(-800, -150, 50), (-800, 150, 50)
(-400, -150, 50), (-400, 150, 50)
(0, -150, 50), (0, 150, 50)
(400, -150, 50), (400, 150, 50)
(800, -150, 50), (800, 150, 50)
(1200, -150, 50), (1200, 150, 50)
(1600, -150, 50), (1600, 150, 50)

Settings for each:
- Intensity: 800
- Color: Orange-Red (1.0, 0.4, 0.2)
- Attenuation Radius: 300
- Enable: Light Functions > Flicker (optional)
```

#### Work Lights (5 Spot Lights)
1. **West Work Area**: (-800, 0, -50) - Pitch=-60°, Yaw=45°
2. **Central Overhead**: (0, 0, 200) - Pitch=-90°, Yaw=0°
3. **East Work Area**: (800, 0, -50) - Pitch=-60°, Yaw=-45°
4. **North Service**: (0, 800, 50) - Pitch=-45°, Yaw=180°
5. **South Maintenance**: (0, -800, -150) - Pitch=-30°, Yaw=0°

**Settings for all Spot Lights:**
- Intensity: 1200
- Color: Warm White (0.9, 0.9, 0.8)
- Cone Angle: 45°
- Attenuation Radius: 500

### FACTION TERRITORIES: Environmental Storytelling

#### Faction Territorial Markers
Create Point Lights with faction colors:

1. **Directorate Territory** (-1200, -200, -100)
   - Color: Corporate Blue (0.0, 0.5, 1.0)
   - Add: Static Mesh Cube (Scale: 1.0, 1.0, 0.1)

2. **Free77 Territory** (-400, 200, -100)
   - Color: Military Yellow (0.8, 0.8, 0.0)
   - Add: Static Mesh Cube (Scale: 1.0, 1.0, 0.1)

3. **Iron Scavengers Territory** (400, -200, -100)
   - Color: Scrap Orange (1.0, 0.3, 0.0)
   - Add: Static Mesh Cube (Scale: 1.0, 1.0, 0.1)

4. **Nomad Clans Territory** (1200, 200, -100)
   - Color: Nature Green (0.5, 1.0, 0.3)
   - Add: Static Mesh Cube (Scale: 1.0, 1.0, 0.1)

5. **Neutral Zone** (0, 800, -50)
   - Color: Gray (0.7, 0.7, 0.7)

6. **Contested Zone** (0, -800, -200)
   - Color: Purple (1.0, 0.0, 1.0)

**Each Faction Light Settings:**
- Intensity: 600
- Attenuation Radius: 200

### COVER SYSTEM: Tactical Positioning

#### Support Columns (20 columns)
Create Static Mesh Actors using Basic Shapes > Cube:
```
Positions along main tunnel (every 200 units):
X-coordinates: -1600, -1400, -1200, -1000, -800, -600, -400, -200, 0, 200, 400, 600, 800, 1000, 1200, 1400, 1600

For each X position, create two columns:
- Column A: (X, -100, -200) - Scale: (0.5, 0.5, 2.8)
- Column B: (X, 100, -200) - Scale: (0.5, 0.5, 2.8)
```

#### Abandoned Metro Cars (4 cars)
Create Static Mesh Actors using Basic Shapes > Cube:
```
Positions:
1. (-1000, 0, -200) - Scale: (1.2, 3.0, 1.8)
2. (-200, 0, -200) - Scale: (1.2, 3.0, 1.8)
3. (600, 0, -200) - Scale: (1.2, 3.0, 1.8)
4. (1400, 0, -200) - Scale: (1.2, 3.0, 1.8)
```

### GAMEPLAY ELEMENTS: Spawn Points and Extraction Zones

#### Player Start Points

**Team Alpha Spawns (West Side):**
- Spawn 1: (-1600, -400, -180) - Rotation: Yaw=45°
- Spawn 2: (-1600, 400, -180) - Rotation: Yaw=-45°
- Spawn 3: (-1400, 0, -180) - Rotation: Yaw=0°

**Team Bravo Spawns (East Side):**
- Spawn 1: (1600, -400, -180) - Rotation: Yaw=135°
- Spawn 2: (1600, 400, -180) - Rotation: Yaw=-135°
- Spawn 3: (1400, 0, -180) - Rotation: Yaw=180°

**Solo/FFA Spawns:**
- Solo 1: (-800, 600, -130) - Rotation: Yaw=-90°
- Solo 2: (800, -600, -130) - Rotation: Yaw=90°
- Solo 3: (0, 0, 150) - Rotation: Yaw=0°
- Solo 4: (-200, 800, -130) - Rotation: Yaw=-135°
- Solo 5: (200, -800, -280) - Rotation: Yaw=45°

#### Extraction Zones
Create Static Mesh Actors using Basic Shapes > Cylinder + Point Lights:

**Primary Extraction - Central Shaft:**
- Location: (0, 0, 250)
- Cylinder Scale: (1.0, 1.0, 0.1)
- Light: Green (0.0, 1.0, 0.0), Intensity=1000, Radius=200

**Secondary Extraction - North Exit:**
- Location: (800, 800, 100)
- Cylinder Scale: (0.8, 0.8, 0.1)
- Light: Green (0.0, 1.0, 0.0), Intensity=1000, Radius=160

**Emergency Extraction - South Service:**
- Location: (-400, -800, -250)
- Cylinder Scale: (0.6, 0.6, 0.1)
- Light: Green (0.0, 1.0, 0.0), Intensity=1000, Radius=120

### NAVIGATION MESH: AI Pathfinding Setup

1. **Place Nav Mesh Bounds Volume:**
   - Location: (0, 0, 0)
   - Scale: (40, 40, 10) - Covers entire level
   
2. **Build Navigation:**
   - Window > Developer Tools > Navigation
   - Click "Build" to generate nav mesh
   - Verify green nav mesh appears on walkable surfaces

---

## PERFORMANCE OPTIMIZATION

### Level of Detail (LOD) Settings
- **High Detail Radius**: 500 units
- **Medium Detail Radius**: 1000 units
- **Low Detail Radius**: 2000 units
- **Culling Distance**: 3000 units

### Lighting Optimization
- **Max Dynamic Lights**: 8 simultaneous
- **Shadow Casting**: Primary lights only
- **Light Functions**: Emergency flicker only

### Texture Streaming
- **High Resolution**: 300 unit radius
- **Medium Resolution**: 800 unit radius
- **Low Resolution**: 1500 unit radius

---

## VALIDATION CHECKLIST

### Functional Testing
- [ ] All spawn points functional and properly oriented
- [ ] Navigation mesh covers all walkable areas
- [ ] Extraction zones properly placed and accessible
- [ ] Faction territories clearly marked
- [ ] Cover positions provide tactical advantage

### Performance Testing
- [ ] 60+ FPS maintained with 8 players
- [ ] Draw calls under 800
- [ ] Triangle count under 150,000
- [ ] Memory usage optimized

### Gameplay Balance
- [ ] No spawn camping positions
- [ ] Multiple routes between key areas
- [ ] Balanced sightlines (long, medium, short range)
- [ ] Fair faction territory distribution
- [ ] Risk/reward balanced extraction zones

### Visual Quality
- [ ] Atmospheric lighting achieved
- [ ] No light bleeding or dark spots
- [ ] Faction colors clearly distinguishable
- [ ] Environmental storytelling elements present

---

## LEVEL STATISTICS

**Total Actors**: ~120
- Support Columns: 20
- Emergency Lights: 18
- Faction Markers: 6
- Metro Cars: 4
- Work Lights: 5
- Extraction Zones: 3
- Spawn Points: 11
- Geometry Brushes: 4
- Navigation Bounds: 1

**Performance Targets**:
- **FPS**: 60+ (target hardware)
- **Frame Time**: <16.67ms
- **Draw Calls**: <800
- **Triangles**: <150,000

---

## POST-IMPLEMENTATION

### Testing Protocol
1. **Lighting Pass**: Verify atmospheric quality and performance
2. **Navigation Test**: AI pathfinding validation
3. **Spawn Testing**: All spawn points functional
4. **Performance Profiling**: Frame rate analysis
5. **Gameplay Testing**: Flow and balance validation

### Integration with AI Assets
- Replace basic cube meshes with AI-generated faction assets
- Integrate Terminal Grounds environmental textures
- Add atmospheric particle effects
- Implement faction-specific architectural details

---

**Implementation Complete**: Ready for Phase 1 gameplay testing
**Next Steps**: Asset integration and gameplay mechanics implementation