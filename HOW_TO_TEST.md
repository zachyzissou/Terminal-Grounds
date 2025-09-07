# How to Test Terminal Grounds Complete System

## Quick Start (3 Steps)

### 1. Compile the Project
- Open Terminal Grounds in Unreal Engine
- Compile the C++ code (Ctrl+Alt+F11 or Build → Compile)

### 2. Open a Test Level
**Option A: Use existing IEZ map**
- Open `Content/TG/Maps/IEZ/IEZ_District_Alpha` (or any IEZ map)

**Option B: Use any existing map**
- Open `Content/Maps/Demo_Combat_Zone` or any map with a floor

**Option C: Create new empty level**
- File → New Level → Empty Level
- Add a floor (cube scaled to 100,100,1)

### 3. Run the Test

#### Method 1: Place Test Actor (Easiest)
1. In Content Browser, navigate to `C++ Classes/TGCore`
2. Find `TGCompleteTestActor`
3. Drag it into the level
4. Hit Play (Alt+P)
5. Watch as it generates faction buildings and spawns enemies!

#### Method 2: Console Commands (Most Control)
1. Hit Play (Alt+P)
2. Press ` (tilde) to open console
3. Type: `TG_SpawnCompleteTest`
4. The system will:
   - Generate procedural faction buildings
   - Spawn 8 enemies
   - Create extraction zone
   - Start the mission

## Console Commands Available

```
TG_SpawnCompleteTest           # Spawn everything at once
TG_GenerateTerritory 1 2       # Generate Free77 territory  
TG_TestDirectorateVsFree77     # Spawn faction vs faction battle
TG_TestMultiFaction            # Spawn 5-faction warzone
TG_SpawnEnemies 10             # Spawn 10 enemies
TG_ShowStatus                  # Show mission progress
TG_RestartMission              # Restart current mission
TG_Help                        # Show all commands
```

## Testing Different Scenarios

### Directorate Outpost
```
1. Place TGCompleteTestActor in level
2. Set ScenarioType to "Directorate Outpost"
3. Play - creates blue corporate structures
```

### Free77 Stronghold  
```
1. Place TGCompleteTestActor in level
2. Set ScenarioType to "Free77 Stronghold"
3. Play - creates red resistance base
```

### Contested Territory
```
1. Place TGCompleteTestActor in level
2. Set ScenarioType to "Contested Territory"
3. Play - creates two opposing faction bases
```

### Multi-Faction Battle
```
1. Place TGCompleteTestActor in level
2. Set ScenarioType to "Multi-Factional Battle"
3. Play - creates 5 different faction territories in a circle
```

## What You'll See

When the test runs successfully:

1. **Console Output**:
```
========================================
TERMINAL GROUNDS COMPLETE TEST STARTING
========================================
Generated Directorate territory (ID: 1001) at (0,0,0) with radius 10000
Generated 8 buildings for territory 1001
Generated 15 detail objects for territory 1001
Generated 10 vegetation objects for territory 1001
Combat scenario setup complete: 8 enemies spawned
Extraction zone created at (0,5000,0)
========================================
TERMINAL GROUNDS TEST SETUP COMPLETE
Mission: Eliminate all enemies and reach extraction
========================================
```

2. **In-Game**:
- Faction-colored buildings spawn around you
- Crates and props scattered as cover
- 8 AI enemies patrolling
- Health/ammo displayed (if HUD configured)
- Extraction zone marker north of spawn

3. **Gameplay**:
- Enemies attack on sight
- Kill all enemies to unlock extraction
- Reach extraction zone to win
- Press R to restart mission

## Troubleshooting

### Nothing Spawns
- Check console (`) for error messages
- Ensure project compiled successfully
- Set Game Mode to `ATGPlaytestGameMode` in World Settings

### No Buildings Appear
- Buildings use fallback to Engine basic shapes if assets missing
- Check console for "Selected mesh" messages
- At minimum, you'll see cubes/cylinders as buildings

### Enemies Don't Move
- Add NavMeshBoundsVolume to level
- Press P to show navigation mesh
- Build navigation (Build → Build Paths)

### Can't Extract
- Kill all enemies first (check remaining count)
- Extraction zone turns green when available
- Stand in extraction zone for 5 seconds

### Performance Issues
- Reduce NumberOfEnemies (default 8)
- Reduce ProceduralGenerationRadius (default 10000)
- Disable vegetation generation

## Advanced Testing

### Custom Parameters
Edit TGCompleteTestActor properties:
- `NumberOfEnemies`: 1-50 enemies
- `ProceduralGenerationRadius`: Size of generated area
- `NumberOfTerritories`: How many faction zones
- `ScenarioType`: Different battle configurations

### Blueprint Customization
Create Blueprint from TGCompleteTestActor:
1. Right-click TGCompleteTestActor in Content Browser
2. Create Blueprint Class
3. Override events for visual effects:
   - OnTestSetupComplete
   - OnCombatSetupComplete
   - OnProceduralGenerationComplete
   - OnExtractionZoneCreated

## Expected Results

✅ **Success Indicators**:
- Buildings spawn (even if just primitive shapes)
- Enemies spawn and patrol
- Console shows generation messages
- Can kill enemies and extract
- Mission complete message appears

❌ **Known Limitations**:
- Buildings may be basic shapes if construction assets not available
- Materials may be default if TG materials not found
- Vegetation uses placeholders without foliage assets

## Summary

The system is designed to work with ANY level:
1. It generates its own buildings and cover
2. It spawns its own enemies
3. It creates its own objectives
4. It manages the entire mission flow

Just drop `TGCompleteTestActor` in any level and hit Play!