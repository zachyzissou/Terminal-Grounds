# Terminal Grounds - Quick Demo Setup Guide

## CREATE A PLAYABLE DEMO IN 5 MINUTES

Since the MCP plugins are having issues, here's how to quickly create a playable Terminal Grounds demo directly in the Unreal Editor:

---

## METHOD 1: Using Console Commands (Fastest)

Open the console in Unreal (press `~` key) and paste these commands:

### 1. Spawn Cover Objects
```
summon StaticMeshActor X=500 Y=300 Z=100
summon StaticMeshActor X=500 Y=-300 Z=100
summon StaticMeshActor X=500 Y=0 Z=100
summon StaticMeshActor X=0 Y=500 Z=100
summon StaticMeshActor X=0 Y=-500 Z=100
summon StaticMeshActor X=-500 Y=300 Z=100
summon StaticMeshActor X=-500 Y=-300 Z=100
summon StaticMeshActor X=-500 Y=0 Z=100
```

### 2. Spawn Lights
```
summon DirectionalLight X=0 Y=0 Z=5000
summon PointLight X=0 Y=0 Z=500
summon SpotLight X=0 Y=1000 Z=400
summon SpotLight X=0 Y=-1000 Z=400
```

### 3. Spawn AI Enemies (if TGEnemyGrunt exists)
```
summon TGEnemyGrunt X=300 Y=900 Z=100
summon TGEnemyGrunt X=-300 Y=900 Z=100
summon TGEnemyGrunt X=900 Y=300 Z=100
summon TGEnemyGrunt X=900 Y=-300 Z=100
summon TGEnemyGrunt X=300 Y=-900 Z=100
summon TGEnemyGrunt X=-300 Y=-900 Z=100
summon TGEnemyGrunt X=-900 Y=300 Z=100
summon TGEnemyGrunt X=-900 Y=-300 Z=100
```

### 4. Spawn Player Character
```
summon TGPlayPawn X=0 Y=0 Z=200
```

### 5. Spawn Weapons
```
summon TGWeapon X=100 Y=0 Z=100
summon TGWeapon X=-100 Y=0 Z=100
summon TGWeapon X=0 Y=100 Z=100
summon TGWeapon X=0 Y=-100 Z=100
```

---

## METHOD 2: Manual Placement (More Control)

### Step 1: Create Basic Level
1. **File → New Level → Basic**
2. This gives you a floor and basic lighting

### Step 2: Add Cover Objects
1. In **Place Actors** panel, search for "Cube"
2. Drag **Cube** into the level
3. Position at strategic locations:
   - Front line: X=500, Y=±300
   - Mid field: X=0, Y=±500
   - Back line: X=-500, Y=±300
4. Scale cubes to create cover (2x1x2 for walls, 1x3x2 for barriers)

### Step 3: Add Terminal Grounds Actors
1. In **Place Actors**, search for your Terminal Grounds classes:
   - `TGEnemyGrunt` - Place 8 around the arena
   - `TGPlayPawn` - Place at center
   - `TGWeapon` - Place several around map
   - `TGCaptureNode` - Place at objective points

### Step 4: Set Up Lighting
1. Add **Directional Light** for sun
2. Add **Sky Light** for ambient
3. Add **Exponential Height Fog** for atmosphere
4. Add **Point Lights** or **Spot Lights** for dramatic effect

### Step 5: Configure Game Mode
1. **World Settings** → **Game Mode Override**
2. Select your Terminal Grounds game mode
3. Set **Default Pawn Class** to `TGPlayPawn`

---

## METHOD 3: Using Existing Maps

### Open an Existing Terminal Grounds Map:
1. **File → Open Level**
2. Navigate to one of these:
   - `Content/TG/Maps/IEZ/IEZ_District_Alpha`
   - `Content/TG/Maps/IEZ/IEZ_District_Beta`
   - `Content/Maps/Demo_Combat_Zone`

These maps likely already have layout and just need enemies spawned.

---

## TO PLAY YOUR DEMO:

1. **Press Play** button or **Alt+P**
2. **Controls:**
   - WASD - Move
   - Mouse - Look/Aim
   - Left Click - Fire
   - Space - Jump
   - Shift - Sprint
   - Tab - Inventory (if implemented)
   - E - Interact

---

## QUICK TIPS:

- **Save your level**: File → Save Current Level As → "MyDemo"
- **Test AI**: Place Nav Mesh Bounds Volume for AI navigation
- **Add Spawners**: Use Target Points to mark spawn locations
- **Blueprint Logic**: Create a simple Blueprint to spawn waves of enemies

---

## TROUBLESHOOTING:

If actors don't spawn via console:
- The class names might be different
- Check Content Browser for actual Blueprint names
- Use full paths like: `/Game/TG/Blueprints/BP_EnemyGrunt.BP_EnemyGrunt_C`

If no Terminal Grounds content appears:
- Make sure the TG modules compiled successfully
- Check Output Log for errors
- Verify Content/TG folder exists

---

Your Terminal Grounds demo is ready to create! Use whichever method works best for your current setup.