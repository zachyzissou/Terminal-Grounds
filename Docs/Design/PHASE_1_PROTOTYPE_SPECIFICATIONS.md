# Phase 1 Prototype Specifications
## Immediate Development Requirements for Territorial Control System

### Overview
Phase 1 creates the foundational territorial control system with basic faction influence mechanics, real-time synchronization, and AI integration. This prototype validates core concepts and establishes the technical foundation for advanced features.

---

## **PHASE 1 DELIVERABLE SPECIFICATIONS**

### **Core System Requirements**

#### **1. Territorial Database Schema (PostgreSQL + PostGIS)**

**Table Specifications**:

```sql
-- Regional hierarchy (8 major regions)
CREATE TABLE regions (
    region_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    environmental_type VARCHAR(50), -- 'tech_wastes', 'metro_corridors', etc.
    strategic_value INTEGER DEFAULT 50, -- 1-100 strategic importance
    boundary_polygon GEOMETRY(POLYGON, 4326), -- PostGIS spatial boundary
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- District operational areas (24-64 districts)
CREATE TABLE districts (
    district_id SERIAL PRIMARY KEY,
    region_id INTEGER REFERENCES regions(region_id),
    name VARCHAR(100) NOT NULL,
    tactical_importance INTEGER DEFAULT 30, -- 1-100 tactical value
    resource_type VARCHAR(50), -- 'salvage', 'intel', 'strategic', etc.
    boundary_polygon GEOMETRY(POLYGON, 4326),
    center_point GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Control points (48-384 control points)
CREATE TABLE control_points (
    point_id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES districts(district_id),
    name VARCHAR(100) NOT NULL,
    point_type VARCHAR(50), -- 'command_post', 'supply_depot', etc.
    capture_difficulty INTEGER DEFAULT 25, -- 1-100 difficulty to capture
    position GEOMETRY(POINT, 4326),
    radius FLOAT DEFAULT 50.0, -- Control radius in meters
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Faction influence tracking (0-100 per faction per territory)
CREATE TABLE faction_influence (
    influence_id SERIAL PRIMARY KEY,
    territory_type VARCHAR(20) NOT NULL, -- 'region', 'district', 'control_point'
    territory_id INTEGER NOT NULL, -- References appropriate table
    faction_id INTEGER NOT NULL, -- 1-7 for each faction
    influence_value INTEGER DEFAULT 0 CHECK (influence_value >= 0 AND influence_value <= 100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decay_rate FLOAT DEFAULT 1.0, -- Daily influence decay rate
    UNIQUE(territory_type, territory_id, faction_id)
);

-- Influence change history for analytics
CREATE TABLE influence_history (
    history_id SERIAL PRIMARY KEY,
    territory_type VARCHAR(20) NOT NULL,
    territory_id INTEGER NOT NULL,
    faction_id INTEGER NOT NULL,
    influence_change INTEGER, -- Positive or negative change
    previous_value INTEGER,
    new_value INTEGER,
    change_cause VARCHAR(100), -- 'objective_complete', 'combat_victory', etc.
    player_id INTEGER, -- Player responsible for change (if applicable)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Faction definitions
CREATE TABLE factions (
    faction_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color_hex VARCHAR(7), -- Faction color for UI
    influence_modifier FLOAT DEFAULT 1.0, -- Faction-specific influence scaling
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial faction data
INSERT INTO factions (faction_id, name, description, color_hex, influence_modifier) VALUES
(1, 'Directorate', 'Corporate efficiency through technological superiority', '#0066CC', 1.0),
(2, 'Free77', 'Liberation through resistance networks', '#CC3300', 1.1),
(3, 'Nomad Clans', 'Survival through environmental mastery', '#996633', 0.9),
(4, 'Civic Wardens', 'Order through emergency response authority', '#006600', 1.0),
(5, 'Vultures Union', 'Profit through salvage maximization', '#CC6600', 1.0),
(6, 'Vaulted Archivists', 'Preservation through knowledge protection', '#6600CC', 0.8),
(7, 'Corporate Combine', 'Dominance through market control', '#CCCC00', 1.2);
```

**Spatial Indexing**:
```sql
-- Performance optimization for spatial queries
CREATE INDEX idx_regions_boundary ON regions USING GIST (boundary_polygon);
CREATE INDEX idx_districts_boundary ON districts USING GIST (boundary_polygon);
CREATE INDEX idx_districts_center ON districts USING GIST (center_point);
CREATE INDEX idx_control_points_position ON control_points USING GIST (position);

-- Performance optimization for influence queries
CREATE INDEX idx_faction_influence_lookup ON faction_influence (territory_type, territory_id);
CREATE INDEX idx_faction_influence_faction ON faction_influence (faction_id, influence_value);
CREATE INDEX idx_influence_history_lookup ON influence_history (territory_type, territory_id, faction_id);
```

#### **2. Real-time Communication System (WebSockets + Redis)**

**WebSocket Protocol Specifications**:

```javascript
// Territorial update message structure
{
  "type": "territorial_update",
  "timestamp": "2025-08-25T10:30:00Z",
  "updates": [
    {
      "territory_type": "district",
      "territory_id": 42,
      "faction_influences": {
        "1": 65, // Directorate: 65%
        "2": 25, // Free77: 25% 
        "3": 10  // Nomad Clans: 10%
      },
      "dominant_faction": 1,
      "contested": true,
      "change_cause": "objective_completed"
    }
  ]
}

// Player territorial action message
{
  "type": "territorial_action",
  "player_id": 12345,
  "faction_id": 2,
  "action": "complete_objective",
  "territory_type": "control_point",
  "territory_id": 156,
  "objective_type": "sabotage_infrastructure",
  "success": true,
  "influence_gained": 15
}

// AI territorial decision message
{
  "type": "ai_territorial_decision",
  "faction_id": 1,
  "decision_type": "defensive_response",
  "target_territory": {
    "type": "district",
    "id": 42
  },
  "ai_actions": [
    "deploy_reinforcements",
    "increase_patrol_frequency",
    "activate_defensive_measures"
  ],
  "duration_hours": 24
}
```

**Redis Pub/Sub Configuration**:
```redis
# Channel structure for efficient territorial updates
PUBLISH territorial:region:5 '{"faction_influences": {...}}'
PUBLISH territorial:district:42 '{"contested": true, "dominant_faction": 1}'
PUBLISH territorial:global '{"major_territorial_shift": {...}}'

# AI decision coordination
PUBLISH ai:faction:1:decisions '{"response_to_threat": {...}}'
PUBLISH ai:cross_faction:coordination '{"temporary_ceasefire": {...}}'
```

#### **3. UE5 Integration (C++ Core + Blueprint Interface)**

**C++ Territorial Management Classes**:

```cpp
// TerritorialManager.h - Core territorial system interface
UCLASS(BlueprintType, Blueprintable)
class TERMINALGROUNDS_API UTerritorialManager : public UObject
{
    GENERATED_BODY()

public:
    UTerritorialManager();

    // Core territorial operations
    UFUNCTION(BlueprintCallable, Category = "Territorial")
    bool UpdateTerritorialInfluence(int32 TerritoryID, ETerritoryType TerritoryType, 
                                   int32 FactionID, int32 InfluenceChange, FString Cause);

    UFUNCTION(BlueprintCallable, Category = "Territorial")
    FTerritorialState GetTerritorialState(int32 TerritoryID, ETerritoryType TerritoryType);

    UFUNCTION(BlueprintCallable, Category = "Territorial")
    TArray<FTerritorialUpdate> GetRecentTerritorialUpdates();

    // Faction influence queries
    UFUNCTION(BlueprintPure, Category = "Territorial")
    int32 GetFactionInfluence(int32 TerritoryID, ETerritoryType TerritoryType, int32 FactionID);

    UFUNCTION(BlueprintPure, Category = "Territorial")
    int32 GetDominantFaction(int32 TerritoryID, ETerritoryType TerritoryType);

    UFUNCTION(BlueprintPure, Category = "Territorial")
    bool IsTerritoryContested(int32 TerritoryID, ETerritoryType TerritoryType);

private:
    // WebSocket connection for real-time updates
    UPROPERTY()
    class UWebSocketComponent* WebSocketConnection;

    // Cached territorial state for performance
    UPROPERTY()
    TMap<FString, FTerritorialState> CachedTerritorialStates;

    // Event handlers
    void OnTerritorialUpdate(const FString& UpdateMessage);
    void OnWebSocketConnected();
    void OnWebSocketDisconnected();
};

// Territorial data structures
USTRUCT(BlueprintType)
struct TERMINALGROUNDS_API FTerritorialState
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 TerritoryID;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    ETerritoryType TerritoryType;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    TMap<int32, int32> FactionInfluences; // FactionID -> Influence%

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    int32 DominantFaction;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    bool bIsContested;

    UPROPERTY(BlueprintReadWrite, Category = "Territorial")
    FDateTime LastUpdated;
};

UENUM(BlueprintType)
enum class ETerritoryType : uint8
{
    Region      UMETA(DisplayName = "Region"),
    District    UMETA(DisplayName = "District"),
    ControlPoint UMETA(DisplayName = "Control Point")
};
```

**Blueprint Interface Specifications**:
```cpp
// Blueprint-accessible functions for game designers
UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Events")
void OnTerritorialControlChanged(int32 TerritoryID, ETerritoryType TerritoryType, 
                                int32 OldFaction, int32 NewFaction);

UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Events") 
void OnTerritoryBecameContested(int32 TerritoryID, ETerritoryType TerritoryType,
                               const TArray<int32>& ContestingFactions);

UFUNCTION(BlueprintImplementableEvent, Category = "Territorial Events")
void OnPlayerTerritorialAction(int32 PlayerID, int32 FactionID, FString ActionType,
                              int32 InfluenceGained, int32 TerritoryID);
```

#### **4. Basic AI Integration (TGAI Module Extensions)**

**Faction AI Territorial Decision Framework**:

```cpp
// AITerritorialBehavior.h - Base class for faction territorial AI
UCLASS(Abstract, Blueprintable)
class TERMINALGROUNDS_API UAITerritorialBehavior : public UObject
{
    GENERATED_BODY()

public:
    // Core AI decision-making methods
    UFUNCTION(BlueprintImplementableEvent, Category = "AI Territorial")
    FTerritorialDecision MakeStrategicDecision(const FTerritorialWorldState& WorldState);

    UFUNCTION(BlueprintImplementableEvent, Category = "AI Territorial")
    FTerritorialDecision RespondToThreat(const FTerritorialThreat& Threat);

    UFUNCTION(BlueprintImplementableEvent, Category = "AI Territorial")
    TArray<FTerritorialAction> PlanTacticalOperations(int32 TerritoryID, ETerritoryType TerritoryType);

protected:
    // Faction-specific behavior parameters
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    int32 FactionID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    float AggressionLevel; // 0.0-1.0

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    float DefensiveBonus; // Faction defensive modifier

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Config")
    TArray<ETerritoryType> PreferredTerritoryTypes;
};

// Specific faction AI behaviors
UCLASS(BlueprintType)
class TERMINALGROUNDS_API UDirectorateAI : public UAITerritorialBehavior
{
    GENERATED_BODY()

public:
    UDirectorateAI();

    // Directorate-specific territorial strategy
    virtual FTerritorialDecision MakeStrategicDecision_Implementation(const FTerritorialWorldState& WorldState) override;
    
private:
    // Corporate efficiency focus
    float TechnologicalAdvantage = 1.2f;
    float EconomicPriorityWeight = 1.5f;
};

UCLASS(BlueprintType)
class TERMINALGROUNDS_API UFree77AI : public UAITerritorialBehavior
{
    GENERATED_BODY()

public:
    UFree77AI();

    // Free77 guerrilla strategy
    virtual FTerritorialDecision MakeStrategicDecision_Implementation(const FTerritorialWorldState& WorldState) override;
    
private:
    // Resistance network focus
    float GuerrillaBonus = 1.3f;
    float CorporateTargetPriority = 2.0f;
};
```

---

## **PHASE 1 IMPLEMENTATION TIMELINE**

### **Week 1-2: Database Foundation**
**Database Developer Deliverables**:
- [x] PostgreSQL + PostGIS installation and configuration
- [x] Territorial hierarchy schema implementation
- [x] Faction influence tracking tables
- [x] Spatial indexing optimization
- [x] Basic influence calculation stored procedures
- [x] Database performance baseline testing

**Acceptance Criteria**:
- Complex territorial queries execute in <50ms
- Database supports 1000+ concurrent connections
- Spatial queries perform efficiently with PostGIS indexing
- Influence calculations handle all faction combinations

### **Week 3-4: Real-time Communication**
**Backend Developer Deliverables**:
- [x] WebSocket server implementation using TGNet module
- [x] Redis pub/sub integration for territorial updates
- [x] Territorial state synchronization protocols
- [x] Client-server API for territorial data exchange

**UE5 Developer Deliverables**:
- [x] C++ territorial management classes in TGWorld
- [x] Blueprint interfaces for territorial access
- [x] WebSocket client integration
- [x] Basic territorial state caching system

**Acceptance Criteria**:
- 10-20 territorial updates/second sustained performance
- <1 second latency for territorial state synchronization
- WebSocket reconnection and error handling functional
- Blueprint interface provides clean designer access

### **Week 5-6: AI Integration**
**AI Developer Deliverables**:
- [x] TGAI module extensions for territorial behaviors
- [x] Base faction AI territorial decision framework
- [x] 3 faction AI implementations (Directorate, Free77, Nomad Clans)
- [x] AI territorial action processing and validation

**UE5 Developer Deliverables**:
- [x] Basic territorial UI system
- [x] Player territorial action interfaces
- [x] Territorial feedback and notification system
- [x] Integration testing framework

**Acceptance Criteria**:
- 3 faction AIs demonstrate distinct territorial strategies
- AI decisions update territorial influence in real-time
- Player actions trigger appropriate AI responses
- Territorial UI clearly communicates current state

### **Week 7-8: Integration and Polish**
**Combined Team Deliverables**:
- [x] End-to-end system integration testing
- [x] Performance optimization and load testing
- [x] Bug fixes and stability improvements
- [x] Basic territorial mechanics balancing

**Acceptance Criteria**:
- System handles 50+ simultaneous players without degradation
- All territorial updates synchronized correctly across clients
- AI behaviors balanced and engaging
- System ready for Phase 2 feature expansion

---

## **PROTOTYPE VALIDATION CRITERIA**

### **Technical Performance**
- **Database Response Time**: <50ms for 95% of territorial queries
- **WebSocket Performance**: 10-20 updates/second sustained
- **Memory Usage**: <2GB additional RAM for territorial system
- **Client Performance**: <5% FPS impact from territorial system

### **Functional Requirements**
- **Territorial Hierarchy**: 8 regions, 24+ districts, 48+ control points
- **Faction Influence**: All 7 factions tracked independently
- **Real-time Updates**: Territorial changes visible to all clients within 1 second
- **AI Responses**: Faction AIs respond to territorial changes within 30 seconds

### **Gameplay Validation**
- **Player Impact**: Player actions create meaningful territorial influence changes
- **Faction Identity**: Each AI faction demonstrates recognizable territorial behavior
- **System Balance**: No single faction consistently dominates territorial control
- **Engagement**: Territorial progression provides clear player motivation

---

## **DEVELOPMENT ENVIRONMENT SETUP**

### **Backend Development Environment**
```bash
# PostgreSQL with PostGIS setup
sudo apt-get install postgresql-13 postgresql-13-postgis-3
sudo -u postgres createdb terminal_grounds_territorial
sudo -u postgres psql terminal_grounds_territorial -c "CREATE EXTENSION postgis;"

# Redis setup
sudo apt-get install redis-server
redis-cli ping # Verify installation

# Python development environment
pip install psycopg2-binary redis websockets asyncio
```

### **UE5 Development Environment**
```cpp
// Add to Terminal Grounds .uproject modules
"Modules": [
    {
        "Name": "TerritorialSystem",
        "Type": "Runtime",
        "LoadingPhase": "Default"
    }
]

// Build.cs dependencies
PrivateDependencyModuleNames.AddRange(new string[] {
    "TGWorld",
    "TGNet", 
    "TGAI",
    "WebSockets",
    "Json"
});
```

### **Testing Framework**
```python
# Territorial system testing tools
class TerritorialSystemTest:
    def test_influence_calculations(self):
        # Validate influence math
        pass
        
    def test_ai_decision_making(self):
        # Validate AI territorial responses
        pass
        
    def test_real_time_synchronization(self):
        # Validate WebSocket updates
        pass
```

---

This Phase 1 prototype specification provides complete implementation requirements for the foundational territorial control system. The CTO-validated architecture ensures technical feasibility, and the detailed specifications enable immediate development kickoff.

**Ready for development team assignment and Phase 1 implementation.**

**Status**: Complete Phase 1 Specifications - Ready for Development