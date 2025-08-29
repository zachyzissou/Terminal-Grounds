---
title: "Territorial Warfare Workflow"
type: "reference"
domain: "process"
status: "draft"
last_reviewed: "2025-08-28"
maintainer: "Documentation Team"
tags: []
related_docs: []
---

# Territorial Warfare Development Workflow

**Status:** OPERATIONAL - Phase 2 Complete  
**Last Updated:** August 25, 2025  

## Development Environment Setup

### Terminal Grounds Territorial Warfare Stack

**Backend Systems:**
- **Database:** SQLite territorial database (0.04ms performance)
- **Real-Time Server:** Python WebSocket server (100+ concurrent players)
- **Asset Pipeline:** ComfyUI + FLUX1-dev-fp8 (92% success rate)

**Frontend Systems:**
- **Game Engine:** Unreal Engine 5.6
- **Gameplay Framework:** C++ classes with Blueprint integration
- **UI System:** UMG widgets with real-time WebSocket updates

**Development Tools:**
- **IDE:** Visual Studio 2022 (C++) + UE5 Editor (Blueprints)
- **Database Tools:** SQLite Browser, custom validation scripts
- **Testing:** Python multiplayer stress testing framework

## Daily Development Workflow

### 1. Environment Startup (5 minutes)

**Start Core Systems:**
```bash
# Terminal 1: Start WebSocket Server
cd "C:\Users\Zachg\Terminal-Grounds"
python Tools/TerritorialSystem/territorial_websocket_server.py

# Terminal 2: Start ComfyUI (for asset generation)
cd "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188

# Terminal 3: Validate System Health
python Tools/Testing/simple_websocket_test.py
python Database/cto_validation_minimal.py
```

**Launch UE5:**
```bash
# Open Terminal Grounds project
"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe" "C:\Users\Zachg\Terminal-Grounds\TerminalGrounds.uproject"
```

### 2. Feature Development Cycle

#### Territorial Gameplay Features

**1. Design Phase:**
- Define territorial objective requirements
- Specify database schema changes
- Plan UI/UX for territorial feedback
- Document asset generation needs

**2. Backend Implementation:**
```bash
# Modify database schema if needed
sqlite3 Database/territorial_system.db
> ALTER TABLE territories ADD COLUMN new_feature_data TEXT;

# Update WebSocket server for new message types  
# Edit: Tools/TerritorialSystem/territorial_websocket_server.py

# Test database changes
python Database/cto_validation_minimal.py
```

**3. UE5 C++ Implementation:**
```cpp
// Extend TerritorialExtractionObjective class
// Location: Source/TGCore/Public/TerritorialExtractionObjective.h

UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "New Feature")
FString NewFeatureProperty;

UFUNCTION(BlueprintCallable, Category = "New Feature")
void ProcessNewFeature();
```

**4. Blueprint Integration:**
- Create Blueprint derived from C++ class
- Implement custom logic in Blueprint Event Graph
- Add to level and configure parameters
- Test functionality in PIE (Play in Editor)

**5. UI Implementation:**
```cpp
// Extend TerritorialControlWidget
// Location: Source/TGUI/Public/TerritorialControlWidget.h

UFUNCTION(BlueprintImplementableEvent, Category = "New Feature")
void OnNewFeatureActivated(const FString& FeatureData);
```

**6. Asset Generation:**
```bash
# Generate new territorial assets if needed
python Tools/ArtGen/territorial_asset_integration.py

# Custom asset generation for new features
python Tools/ArtGen/terminal_grounds_generator.py
```

### 3. Testing and Validation

#### Automated Testing Pipeline

**System Validation:**
```bash
# Database performance test
python Database/cto_validation_minimal.py
# Expected: <0.1ms query performance

# WebSocket connectivity test  
python Tools/Testing/simple_websocket_test.py
# Expected: PASS - WebSocket operational

# Multiplayer stress test
python Tools/Testing/multiplayer_territorial_sync_test.py
# Expected: <500ms latency, <10% message loss, >80% consistency
```

**UE5 Integration Testing:**
```bash
# Compile C++ changes
"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" TerminalGroundsEditor Win64 Development -project="C:\Users\Zachg\Terminal-Grounds\TerminalGrounds.uproject" -rocket -progress

# In UE5 Editor:
# 1. Test Blueprint functionality
# 2. Validate WebSocket connections
# 3. Verify territorial objective completion
# 4. Check HUD updates in real-time
```

#### Manual Testing Checklist

**Territorial Objectives:**
- [ ] Objective activates correctly
- [ ] Database updates on completion
- [ ] WebSocket broadcasts to all clients  
- [ ] HUD displays updated territorial state
- [ ] Asset generation triggers appropriately

**Multiplayer Synchronization:**
- [ ] Multiple players see consistent territorial state
- [ ] Territorial changes propagate in <100ms
- [ ] No desynchronization under load
- [ ] Graceful handling of player disconnections

**UI/UX Validation:**
- [ ] Territorial control displays accurately
- [ ] Faction colors and themes correct
- [ ] Contested territories clearly marked
- [ ] Performance stable with UI updates

### 4. Asset Integration Workflow

#### Dynamic Territorial Assets

**Trigger Asset Generation:**
```python
# Territorial assets automatically generate when:
# 1. Territorial control changes
# 2. New contested zones created  
# 3. Faction dominance shifts

# Manual asset generation:
python Tools/ArtGen/territorial_asset_integration.py
```

**Asset Types Generated:**
- **Environments** - Faction-controlled territorial zones
- **Markers** - Territory boundary indicators
- **Propaganda** - Faction messaging displays
- **Flags** - Territory ownership banners

**Integration Process:**
1. **Generation** - ComfyUI creates assets with faction theming
2. **Organization** - Assets sorted into production directory structure
3. **Import** - UE5 automatically imports new assets (if configured)
4. **Application** - Assets replace generic placeholders in territorial zones

#### Asset Quality Control

**Validation Pipeline:**
```bash
# Check asset generation success rate
grep "SUCCESS" Tools/Comfy/ComfyUI-API/logs/generation.log | wc -l

# Validate asset quality
python Tools/ArtGen/aaa_quality_pipeline.py

# Expected metrics:
# - Success Rate: >90%
# - Composition Score: >85
# - Detail Score: >85  
# - Technical Score: >85
# - Lore Alignment: >85
```

## Code Review and Quality Assurance

### C++ Code Standards

**Territorial System Guidelines:**
- **Performance** - All database queries <1ms
- **Memory Management** - Use UE5 smart pointers and garbage collection
- **Thread Safety** - WebSocket operations on game thread only
- **Error Handling** - Graceful degradation if database unavailable
- **Blueprint Integration** - All major functionality exposed to Blueprints

**Code Review Checklist:**
- [ ] Database operations properly error-handled
- [ ] WebSocket messages validated before processing
- [ ] Memory leaks prevented with proper cleanup
- [ ] Performance impact measured and acceptable
- [ ] Blueprint events properly implemented

### Documentation Standards

**Required Documentation:**
- **Technical Specs** - Database schema changes
- **API Documentation** - New C++ class interfaces  
- **Blueprint Guide** - Designer usage instructions
- **Performance Impact** - Benchmarks and optimization notes

## Deployment Pipeline

### Development → Testing → Production

**Development Branch:**
```bash
# Feature branch workflow
git checkout -b feature/territorial-enhancement
# Implement feature
git add -A
git commit -m "Add territorial enhancement feature"
git push origin feature/territorial-enhancement
```

**Testing Environment:**
```bash
# Deploy to testing server
python Tools/TerritorialSystem/territorial_websocket_server.py --port 8766
# Run full validation suite
python Tools/Testing/multiplayer_territorial_sync_test.py --server ws://127.0.0.1:8766
```

**Production Deployment:**
```bash
# Package UE5 project for distribution
# Deploy WebSocket server to production infrastructure
# Update database schema on production database
# Monitor performance and player feedback
```

## Performance Monitoring

### Key Metrics

**Database Performance:**
- Query response time: Target <1ms, Current 0.04ms ✓
- Connection pool health: Monitor connection count
- Database file size: Track growth and optimize as needed

**WebSocket Performance:**  
- Message latency: Target <500ms, Current <100ms ✓
- Concurrent connections: Target 100+, Validated 100+ ✓
- Message throughput: Monitor messages per second
- Connection stability: Track disconnection rates

**Asset Generation Performance:**
- Success rate: Target >85%, Current 92% ✓  
- Generation time: Monitor per-asset completion time
- Queue health: Ensure no stuck generations
- Quality metrics: Maintain AAA standards

### Performance Optimization

**Database Optimization:**
```sql
-- Add indexes for common queries
CREATE INDEX idx_territory_control ON territories(current_controller_faction_id);
CREATE INDEX idx_faction_influence ON faction_territorial_influence(territory_id, influence_level DESC);

-- Analyze query plans
EXPLAIN QUERY PLAN SELECT * FROM territorial_control_summary;
```

**WebSocket Optimization:**
```python
# Adjust server configuration
ping_interval=20,           # Reduce network chatter
max_size=256*1024,         # Optimize message size limits  
compression="deflate",      # Enable message compression
```

**UE5 Optimization:**
```cpp
// Cache territorial data to reduce database queries
UPROPERTY()
TMap<int32, FTerritorialDisplayData> CachedTerritorialData;

// Update interval configuration
UPROPERTY(EditAnywhere, Category = "Performance")
float TerritorialUpdateInterval = 2.0f; // Configurable update frequency
```

## Troubleshooting Guide

### Common Development Issues

**WebSocket Connection Drops:**
```bash
# Check server logs for connection issues
tail -f Tools/TerritorialSystem/logs/websocket.log

# Verify network connectivity  
python Tools/Testing/simple_websocket_test.py

# Kill and restart server if needed
taskkill /F /IM python.exe
python Tools/TerritorialSystem/territorial_websocket_server.py
```

**Database Lock Issues:**
```bash
# Check for database locks
lsof Database/territorial_system.db

# Force unlock if needed (backup first!)
cp Database/territorial_system.db Database/territorial_system.db.backup
sqlite3 Database/territorial_system.db "PRAGMA busy_timeout=30000;"
```

**UE5 Compilation Issues:**
```bash
# Clean and rebuild
rm -rf Intermediate/ Binaries/
"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe" -projectfiles -project="TerminalGrounds.uproject"
```

**Asset Generation Failures:**
```bash
# Check ComfyUI status
curl http://127.0.0.1:8188/system_stats

# Restart ComfyUI if needed
cd "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188
```

---

**Workflow Status:** OPERATIONAL - Ready for feature development and live testing  
**Development Efficiency:** Streamlined pipeline from concept to production  
**Quality Assurance:** Automated testing and validation at every stage  
**Performance:** All systems exceeding target specifications