# IMMEDIATE TESTING STEPS

## What You Should Do Right NOW:

1. **In Unreal Editor** (which is already open):
   - Open: `Content/TG/Maps/IEZ/IEZ_District_Alpha`
   - OR create a new Empty Level with a floor

2. **Press Play** (Alt+P or click Play button)

3. **Open Console** (press ` backtick key)

4. **Type this exact command**:
   ```
   TG_SpawnCompleteTest
   ```

5. **Press Enter**

## What Should Happen:

```
========================================
TERMINAL GROUNDS COMPLETE TEST STARTING
========================================
Generated Directorate territory (ID: 1001) at (0,0,0) with radius 10000
Generated 8 buildings for territory 1001
Generated 15 detail objects for territory 1001
Combat scenario setup complete: 8 enemies spawned
Extraction zone created at (0,5000,0)
========================================
TERMINAL GROUNDS TEST SETUP COMPLETE
Mission: Eliminate all enemies and reach extraction
========================================
```

## What You'll See in Game:
- Blue faction buildings spawn around you (or basic cube shapes)
- Crates and props scattered for cover
- 8 AI enemies patrolling the area
- Extraction zone marker to the north
- Console messages showing generation progress

## If Nothing Happens:
Try these backup commands:
- `TG_GenerateTerritory 1 1` (Generate Directorate territory)
- `TG_TestDirectorateVsFree77` (Create faction battle)
- `TG_Help` (Show all available commands)

**THE SYSTEM IS READY - JUST RUN THE COMMAND!**