# Phase 1 Setup and Testing Guide

## Quick Setup Checklist

### 1. Project Configuration
- [ ] Compile project with new C++ classes
- [ ] Ensure Enhanced Input plugin is enabled
- [ ] Verify Navigation System is enabled for AI movement

### 2. Level Setup
- [ ] Create or use existing map (recommend starting with existing Content/Maps/Demo_Combat_Zone.umap)
- [ ] Place NavMeshBoundsVolume covering entire playable area
- [ ] Add ATGDemoSetup actor to level
- [ ] Add ATGPlaytestExtractionZone actor to level
- [ ] Set GameMode to ATGPlaytestGameMode

### 3. Input Configuration
Create Enhanced Input assets in Content/Input/:

**Input Mapping Context: IMC_PlaytestControls**
- Move: IA_Move (2D Vector, WASD keys)
- Look: IA_Look (2D Vector, Mouse X/Y) 
- Jump: IA_Jump (Digital, Space)
- Sprint: IA_Sprint (Digital, Left Shift)
- Fire: IA_Fire (Digital, Left Mouse Button)
- Aim: IA_Aim (Digital, Right Mouse Button)
- Restart: IA_Restart (Digital, R key)

**Assign to ATGPlayPawn Blueprint**:
- Set DefaultMappingContext to IMC_PlaytestControls
- Assign each Input Action to corresponding property

### 4. HUD Setup
- [ ] Create Blueprint Widget based on UTGPlaytestCombatHUD (WBP_PlaytestCombatHUD)
- [ ] Design UI layout with health bar, ammo counter, enemy counter, objectives
- [ ] Implement Blueprint events (OnHealthUpdated, OnMissionStateUpdated, etc.)
- [ ] Add HUD to viewport in ATGPlaytestGameMode or PlayerController

### 5. Demo Setup Configuration
Configure ATGDemoSetup actor:
- [ ] Set bAutoSetupOnBeginPlay = true
- [ ] Set NumberOfEnemies (recommend 5-8 for testing)
- [ ] Set EnemyClass to ATGEnemyGrunt
- [ ] Set WeaponClass to ATGWeapon (or TGDemoWeapon)
- [ ] Set PlayerClass to ATGPlayPawn
- [ ] Enable bCreateCoverObjects and bCreatePatrolPoints for better gameplay

### 6. Extraction Zone Configuration
Configure ATGPlaytestExtractionZone:
- [ ] Position in appropriate location (helipad, marked area)
- [ ] Set collision box size (default 400x400x250)
- [ ] Enable bRequiresAllEnemiesDead = true
- [ ] Create Blueprint events for visual feedback

## Testing Procedure

### Basic Functionality Test
1. **Start Level**: Level should load with player spawned
2. **Mission Initialize**: After 2 seconds, enemies should spawn and mission begins
3. **HUD Display**: Health, ammo, and enemy count should be visible
4. **Movement**: WASD movement, mouse look, Space jump, Shift sprint should work
5. **Combat**: Left click should fire weapon, bullets should hit enemies
6. **AI Behavior**: Enemies should patrol, then chase and attack player when detected
7. **Enemy Elimination**: Shot enemies should take damage and die, count should decrease
8. **Extraction**: When all enemies dead, extraction zone should become active
9. **Mission Complete**: Standing in extraction zone should complete mission
10. **Restart**: Pressing R should restart the mission

### Advanced Testing
1. **Player Death**: Take enough damage to die, mission should fail
2. **Extraction Conditions**: Entering extraction zone before killing all enemies should show message
3. **AI Navigation**: Enemies should navigate around obstacles using NavMesh
4. **HUD Updates**: All HUD elements should update in real-time
5. **Visual Feedback**: Blueprint events should trigger visual/audio effects

## Common Issues and Solutions

### Compilation Issues
- **Missing includes**: Ensure all new headers include necessary dependencies
- **Module dependencies**: Add required modules to Build.cs files:
  - TGCore: "EnhancedInput", "NavigationSystem"
  - TGAI: "AIModule", "NavigationSystem"
  - TGUI: "UMG", "Slate", "SlateCore"

### Runtime Issues
- **Input not responding**: Check Enhanced Input Mapping Context assignment
- **Enemies not spawning**: Verify ATGDemoSetup configuration and EnemyClass assignment
- **AI not moving**: Ensure NavMeshBoundsVolume covers area and is built
- **HUD not updating**: Check HUD widget is added to viewport and events are bound
- **Weapon not firing**: Verify weapon class assignment in ATGDemoSetup

### Blueprint Integration Issues
- **Events not firing**: Ensure Blueprint implements all required events
- **Visual updates not working**: Check Blueprint bindings to C++ properties
- **State synchronization**: Verify HUD updates are bound to game mode events

## Performance Optimization

### Recommended Settings
- **AI Update Frequency**: 0.5 second timer for AI logic updates
- **HUD Refresh Rate**: Use event-driven updates rather than tick-based
- **Line Trace Optimization**: Use simple collision for AI sight checks
- **Enemy Count**: Start with 5-8 enemies for testing, optimize before scaling

### Monitoring
- **Frame Rate**: Should maintain 60+ FPS with 8 enemies
- **Memory Usage**: Monitor for memory leaks during mission restart
- **AI Performance**: Check AI responsiveness and pathfinding efficiency

## Blueprint Customization

### Essential Blueprint Events to Implement

**WBP_PlaytestCombatHUD**:
```
OnHealthUpdated() - Update health bar visual
OnAmmoUpdated() - Update ammo counter visual  
OnMissionStateUpdated(State) - Change mission status display
OnEnemyCountUpdated(Remaining, Total) - Update kill counter
OnMissionComplete() - Victory screen/effects
OnMissionFailed() - Failure screen/effects
```

**BP_PlaytestExtractionZone**:
```
OnPlayerEntered(Player) - Entry visual effects
OnPlayerExited(Player) - Exit visual effects
OnZoneActivated() - Available extraction visuals
OnZoneDeactivated() - Locked extraction visuals
```

### Material and Effect Integration
- Use Blueprint events to trigger particle effects
- Implement dynamic materials for health bars and UI elements
- Add sound effects for combat, mission events, and state changes
- Create visual feedback for damage, kills, and objectives

## Success Criteria

Phase 1 is successfully implemented when:

- [ ] Complete gameplay loop: spawn → combat → extraction → completion
- [ ] All systems integrate cleanly (no crashes or critical bugs)
- [ ] HUD provides clear mission feedback
- [ ] AI behavior is engaging and functional
- [ ] Mission restart works reliably
- [ ] Performance is stable with target enemy count
- [ ] Blueprint integration points are functional
- [ ] Code is well-documented and maintainable

## Next Steps

Once Phase 1 testing is complete:

1. **Gather Feedback**: Document gameplay balance and UX issues
2. **Performance Profiling**: Identify optimization opportunities  
3. **Polish Pass**: Visual effects, audio, UI improvements
4. **Phase 2 Planning**: Procedural generation system integration
5. **Asset Integration**: Connect with existing Terminal Grounds art pipeline

This setup guide ensures consistent implementation and testing of the Phase 1 vertical slice across different development environments.