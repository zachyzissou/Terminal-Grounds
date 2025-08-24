# Terminal Grounds - Sampler Comparison Guide

## Available Heun Samplers

### 1. **heun** (Standard)
- **Current proven choice** for Terminal Grounds
- Excellent quality/speed balance
- Proven parameters: CFG 3.2, 25-30 steps
- Generation time: 5-7 minutes @ 1920x1080

### 2. **heunpp2** (Heun++ v2) ⭐ NEW
- **Enhanced version** of standard heun
- Often produces better convergence
- May provide superior texture detail
- Worth testing for quality comparison

## Sampler Performance Comparison

| Sampler | Quality | Speed | Stability | Best For |
|---------|---------|-------|-----------|----------|
| heun | Excellent | Fast | Very High | Production |
| heunpp2 | Excellent+ | Medium | High | Fine Detail |
| euler | Good | Very Fast | High | Quick Tests |
| dpmpp_2m | Very Good | Medium | High | General Use |

## Testing Workflow

### A/B Comparison Test
```powershell
# Standard heun (current)
./Test-Generate.ps1 -Sampler heun -Seed 12345 -Prefix TG_Heun_Test

# Enhanced heunpp2 (new)  
./Test-Generate.ps1 -Sampler heunpp2 -Seed 12345 -Prefix TG_HeunPP_Test
```

### Quality Assessment Criteria
1. **Texture Detail**: Surface micro-detail and sharpness
2. **Material Realism**: PBR-like material properties
3. **Convergence**: Clean edges without artifacts
4. **Generation Time**: Speed vs quality trade-off

## Recommended Testing

### Phase 1: Side-by-Side Comparison
Generate identical prompts with both samplers using the same seed to compare:
- Surface texture detail
- Edge definition  
- Material properties
- Overall sharpness

### Phase 2: Production Testing
If heunpp2 shows improvement:
- Update quality_presets.json
- Update CLAUDE.md documentation
- Test with various prompt types

## Implementation in Scripts

### Update Test-Generate.ps1
The script already supports heunpp2 - no changes needed!

### Update Quality Presets
```json
{
  "sampler": "heunpp2",
  "note": "Enhanced heun sampler for superior texture detail"
}
```

## Expected Benefits of HeunPP2

### Potential Improvements:
- **Better Convergence**: More accurate representation of prompts
- **Enhanced Detail**: Superior micro-texture generation
- **Reduced Artifacts**: Cleaner edges and surfaces
- **Material Quality**: More realistic PBR-like properties

### Trade-offs:
- **Slightly Slower**: May take 10-20% longer than standard heun
- **Memory Usage**: Potentially higher VRAM consumption
- **Stability**: New sampler may need parameter tuning

## Production Recommendations

### If HeunPP2 Tests Well:
1. **Update default sampler** in all workflows
2. **Maintain heun as fallback** for speed-critical generations
3. **Document new optimal parameters** (CFG, steps)
4. **Update batch generation scripts**

### Quality Validation:
- Generate test assets for each Terminal Grounds environment
- Compare texture detail at 100% zoom
- Validate with existing quality assessment pipeline
- Confirm compatibility with upscaling workflows

## Next Steps

1. **Run A/B tests** with identical seeds
2. **Compare texture quality** at pixel level
3. **Measure generation time** differences  
4. **Update production workflows** if beneficial
5. **Document optimal parameters** for heunpp2

The addition of heunpp2 gives Terminal Grounds access to cutting-edge sampling technology for potentially superior asset quality.