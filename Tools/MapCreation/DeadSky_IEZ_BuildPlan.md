# The Dead Sky (IEZ) - Comprehensive Build Plan

## 🎯 Executive Summary

**Goal**: Build the complete Dead Sky (REG_IEZ) region with three difficulty rings using our full MCP toolchain and procedural generation capabilities.

**Scope**: 200km radius massive multi-map area with H1/H2/H3 difficulty tiers
**Timeline**: Phase 1 (Foundation), Phase 2 (Terrain), Phase 3 (Details), Phase 4 (Integration)

---

## 📋 Requirements Validation

✅ **Architecture Foundation** - UTGProceduralWorldSubsystem implemented
✅ **MCP Infrastructure** - Multiple working MCP servers
✅ **Asset Pipeline** - ComfyUI with FLUX1-dev-fp8 proven workflows
✅ **Territorial System** - UTerritorialManager integration ready
✅ **Documentation** - Complete lore and specifications available

---

## 🏗️ Available MCP Tools Inventory

### **Unreal Engine Control**
- `unreal-mcp` (stdio) - Direct UE TCP 55557
- `flopperam-unreal-mcp` - Advanced UE tools
- `chongdashu-unreal-mcp-complete` - Complete UE bridge
- `kvick-UnrealMCP` - Additional UE integration

### **3D Content Creation**
- `3d-mcp` (stdio) - Universal 3D software interface
- `blender-mcp-integration` - Blender addon system
- `unreal-blender-mcp` (http:8300) - Unified Blender-Unreal
- `maya-mcp-integration` - Maya workflow tools
- `unity-mcp-integration` - Unity Editor bridge

### **Specialized Tools**
- `binary-reader-mcp` (stdio) - Asset analysis
- Gaea integration (via custom scripts)
- Houdini integration (via custom nodes)

### **AI Asset Generation**
- ComfyUI API (127.0.0.1:8188) - Proven FLUX1-dev workflows
- Territorial asset generation scripts
- Style-specific generation pipelines

---

## 🌍 Dead Sky Region Specification

### **REG_IEZ Structure**

**Overall Dimensions**: 200km radius (400km x 400km total area)

#### **Ring 1 - IEZ Outer Ring (H1)**
- **Type**: Learn-by-doing salvage fields
- **Radius**: 66km from center (200km total diameter outer edge)
- **Features**: EMP microbursts, basic salvage operations
- **Difficulty**: Beginner-friendly with guided learning
- **Terrain**: Tilted ferrocrete foundations, scattered debris

#### **Ring 2 - IEZ Median Ring (H2)**
- **Type**: Splice pressure zones
- **Radius**: 33km from center
- **Features**: Frequent territorial events, faction conflicts
- **Difficulty**: Intermediate tactical combat
- **Terrain**: Melted rails, industrial wreckage

#### **Ring 3 - IEZ Core Ring (H3)**
- **Type**: Monolith anomalies, Phase Pockets
- **Radius**: 16km from center
- **Features**: Limited extraction, maximum risk/reward
- **Difficulty**: Expert-only, hardcore mechanics
- **Terrain**: Monolithic shadows, reality distortions

### **Key Environmental Features**
- **Rolling EMP**: Periodic electromagnetic pulses affecting equipment
- **Phase Shears**: Reality distortion effects in H3
- **Drone Reactivation Events**: AI systems coming online
- **Monolithic Shadows**: Alien architecture casting impossible shadows

---

## 📐 Technical Implementation Strategy

### **Phase 1: Foundation Setup (Week 1)**

#### **1.1 Unreal Engine Preparation**
```cpp
// Initialize UTGProceduralWorldSubsystem for IEZ
FProceduralGenerationRequest IEZ_Request;
IEZ_Request.TerritoryID = 1001; // REG_IEZ
IEZ_Request.TerritoryType = ELocalTerritoryType::Region;
IEZ_Request.CenterLocation = FVector(0, 0, 0); // World center
IEZ_Request.GenerationRadius = 200000.0f; // 200km in UE units
```

#### **1.2 MCP Server Orchestration**
- Start all MCP servers in coordinated sequence
- Establish communication bridges between tools
- Configure asset generation pipelines
- Test cross-platform coordination

#### **1.3 Base Level Creation**
- Create `IEZ_DeadSky_Main.umap` as primary level
- Set up World Partition for 200km scale
- Configure base landscape system
- Establish coordinate system and reference points

### **Phase 2: Terrain Generation (Week 2-3)**

#### **2.1 Ring-Based Landscape Generation**

**H1 Outer Ring (66-100km radius)**
```python
# ComfyUI generation for H1 terrain
h1_terrain_prompt = """
tilted ferrocrete industrial foundation, scattered debris fields,
EMP-scarred surfaces, learn-by-doing salvage environment,
abandoned industrial infrastructure, safe learning zones
"""
```

**H2 Median Ring (33-66km radius)**
```python
# ComfyUI generation for H2 terrain
h2_terrain_prompt = """
melted railroad infrastructure, splice pressure zones,
twisted metal rails, faction conflict evidence,
intermediate tactical environments, war-torn landscapes
"""
```

**H3 Core Ring (0-33km radius)**
```python
# ComfyUI generation for H3 terrain
h3_terrain_prompt = """
monolithic alien shadows, reality distortion effects,
Phase Pocket anomalies, impossible geometry,
hardcore survival environment, alien architecture
"""
```

#### **2.2 Heightmap Generation via Gaea**
- Use Gaea for large-scale terrain displacement
- Generate ring-specific heightmap variations
- Export at multiple resolutions for LOD system
- Integrate with UE5 landscape system

#### **2.3 Procedural Placement System**
```cpp
void UTGProceduralWorldSubsystem::GenerateIEZRings()
{
    // Generate H1 Outer Ring
    GenerateRing(1, 66000.0f, 100000.0f, EIEZRingType::Outer);

    // Generate H2 Median Ring
    GenerateRing(2, 33000.0f, 66000.0f, EIEZRingType::Median);

    // Generate H3 Core Ring
    GenerateRing(3, 0.0f, 33000.0f, EIEZRingType::Core);
}
```

### **Phase 3: Asset Generation & Placement (Week 3-4)**

#### **3.1 Faction-Specific Assets**
Using proven ComfyUI workflows for each ring:

**H1 Assets** (Beginner-friendly)
- Basic salvage equipment
- Makeshift shelters
- Clear navigation markers
- Tutorial-friendly signage

**H2 Assets** (Tactical complexity)
- Faction checkpoints
- Contested structures
- Tactical cover systems
- Advanced equipment caches

**H3 Assets** (Expert-level)
- Monolith fragments
- Phase distortion generators
- Alien technology fragments
- Hardcore extraction points

#### **3.2 Automated Asset Pipeline**
```python
# Integrate with existing asset generation
def generate_icz_assets():
    for ring in ['H1', 'H2', 'H3']:
        for faction in ['Directorate', 'Free77', 'CivicWardens', 'NomadClans']:
            generate_ring_faction_assets(ring, faction)
            place_assets_procedurally(ring, faction)
```

#### **3.3 Dynamic Event System**
```cpp
UCLASS(BlueprintType)
class TGWORLD_API AEMPBurstEvent : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere)
    float BurstRadius = 5000.0f;

    UPROPERTY(EditAnywhere)
    float BurstInterval = 180.0f; // 3 minutes

    UFUNCTION(BlueprintCallable)
    void TriggerEMPBurst();
};
```

### **Phase 4: Integration & Polish (Week 4-5)**

#### **4.1 Territorial System Integration**
- Connect to existing UTerritorialManager
- Implement real-time faction control updates
- Add territorial event triggers
- Configure WebSocket updates (127.0.0.1:8765)

#### **4.2 Gameplay Systems**
- Implement H1/H2/H3 difficulty scaling
- Configure extraction point systems
- Set up EMP burst mechanics
- Test phase pocket generation

#### **4.3 Performance Optimization**
- World Partition streaming optimization
- LOD system for 200km visibility
- Culling system for distant geometry
- Memory optimization for large-scale terrain

---

## 🚀 Immediate Action Plan

### **Step 1: MCP Coordination Test**
Test all MCP servers working together for asset generation and placement.

### **Step 2: Base Level Setup**
Create the foundational IEZ_DeadSky_Main.umap with proper scale and coordinate system.

### **Step 3: Ring System Implementation**
Implement the three-ring difficulty system in UTGProceduralWorldSubsystem.

### **Step 4: Asset Generation Pipeline**
Begin generating ring-specific assets using ComfyUI with proven parameters.

### **Step 5: Procedural Placement**
Start placing generated assets using the procedural system.

---

## 📊 Success Metrics

### **Technical Validation**
- [ ] 200km world loads without performance issues
- [ ] All three rings generate successfully
- [ ] MCP tools work in coordination
- [ ] Asset generation pipeline operates at >90% success rate

### **Gameplay Validation**
- [ ] H1 ring provides appropriate learning experience
- [ ] H2 ring offers tactical complexity
- [ ] H3 ring delivers hardcore challenge
- [ ] EMP and phase effects work correctly

### **Visual Quality**
- [ ] Ring transitions feel natural and distinct
- [ ] Faction presence is clearly identifiable
- [ ] Environmental storytelling conveys lore
- [ ] Performance maintains 60+ FPS

---

## 🔄 Next Steps

**IMMEDIATE**: Begin MCP server coordination test
**TODAY**: Set up base level and coordinate system
**WEEK 1**: Complete terrain generation for all rings
**WEEK 2**: Asset generation and procedural placement
**WEEK 3**: Integration testing and optimization

This comprehensive build plan leverages our entire MCP toolchain to create The Dead Sky region as the flagship demonstration of Terminal Grounds' procedural world generation capabilities.
