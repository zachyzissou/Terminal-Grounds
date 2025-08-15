# Terminal Grounds - Style Baseline Guide

## 🎨 Style Exploration System

With 168 LoRAs at your disposal, finding the perfect aesthetic for Terminal Grounds requires systematic exploration. This guide helps you establish a visual baseline.

## 📁 Staging Folder Structure

```
Terminal-Grounds/Style_Staging/
├── Gritty_Realism/
│   ├── faction_emblem/
│   ├── soldier_portrait/
│   ├── weapon_concept/
│   ├── environment_scene/
│   └── vehicle_design/
├── Stylized_Military/
├── Cyberpunk_Military/
├── Post_Apocalyptic/
├── Clean_SciFi/
├── Painted_Concept/
├── Hybrid_Tech/
├── Comic_Military/
├── Soviet_Retro/
├── Minimal_Tactical/
├── _Comparisons/        # Side-by-side comparisons
└── _Favorites/          # Your selected best styles
```

## 🎯 10 Style Presets to Explore

### 1. **Gritty Realism**
- **LoRAs**: Battlefield 2042, Detailed Textures, Reactive Armor, War
- **Best for**: AAA military shooter aesthetic
- **Vibe**: The Last of Us meets Call of Duty

### 2. **Stylized Military**
- **LoRAs**: Future Warfare, Stylized Texture, Military Tactics
- **Best for**: Overwatch-style team shooter
- **Vibe**: Team Fortress 2 meets Battlefield

### 3. **Cyberpunk Military**
- **LoRAs**: CyberPunk, Neon Noir, Future Warfare, Sci-fi Buildings
- **Best for**: High-tech faction (Corporate Combine)
- **Vibe**: Deus Ex meets Ghost in the Shell

### 4. **Post-Apocalyptic**
- **LoRAs**: Reactive Armor, War, Hand-Painted Textures
- **Best for**: Scavenger factions (Vultures Union, Nomad Clans)
- **Vibe**: Mad Max meets Fallout

### 5. **Clean Sci-Fi**
- **LoRAs**: SCIFI Concept Art, Sci-fi Environment, Futuristic Interior
- **Best for**: Advanced technology areas, alien vaults
- **Vibe**: Mass Effect meets Destiny

### 6. **Painted Concept Art**
- **LoRAs**: Hand-Painted Textures, Concept Art, Stylized Texture
- **Best for**: Artistic, painterly game aesthetic
- **Vibe**: Dishonored meets Borderlands

### 7. **Hybrid Tech**
- **LoRAs**: Future Warfare, SCIFI Concept, Synthetic Breed, Enhanced Lighting
- **Best for**: Human-alien hybrid technology
- **Vibe**: XCOM meets Half-Life

### 8. **Comic Military**
- **LoRAs**: Graffiti Logo, Ink Poster, Battlefield 2042
- **Best for**: Bold, graphic novel aesthetic
- **Vibe**: Metal Gear Solid meets Sin City

### 9. **Soviet Retro**
- **LoRAs**: USSRART, Soldart, Military Tactics
- **Best for**: Directorate faction, authoritarian aesthetic
- **Vibe**: Papers Please meets Red Alert

### 10. **Minimal Tactical**
- **LoRAs**: HMSG Logo, UI Interface, Future Warfare
- **Best for**: Clean UI, modern military aesthetic
- **Vibe**: Rainbow Six Siege meets Titanfall

## 🔬 Test Subjects

Each style will be tested on:

1. **Faction Emblem** (1024x1024) - Logo/insignia design
2. **Soldier Portrait** (1024x1024) - Character aesthetic
3. **Weapon Concept** (1536x1024) - Equipment detail
4. **Environment Scene** (1920x1080) - World atmosphere
5. **Vehicle Design** (1536x1024) - Mechanical aesthetic

## 🚀 Quick Start Process

### Step 1: Run Initial Test
```batch
STYLE_EXPLORER.bat
> Option 1 (Quick Test)
```
This generates one emblem in Gritty Realism to verify everything works.

### Step 2: Generate Single Subject Comparison
```batch
STYLE_EXPLORER.bat
> Option 2 (Single Subject - all styles)
> Select: faction_emblem
```
This generates the same emblem in all 10 styles for direct comparison.

### Step 3: Review and Select Favorites
- Open `Style_Staging\` folder
- Compare the 10 versions
- Copy best 2-3 styles to `_Favorites\` folder

### Step 4: Deep Dive on Selected Style
```batch
STYLE_EXPLORER.bat
> Option 3 (Single Style - all subjects)
> Select your favorite style
```
This generates all 5 test subjects in your chosen style.

### Step 5: Generate Full Baseline (Optional)
```batch
STYLE_EXPLORER.bat
> Option 4 (Full Baseline)
```
Generates all 50 combinations (10 styles × 5 subjects).
**Time: ~25-30 minutes**

## 📊 HTML Comparison Report

After generation, run:
```batch
STYLE_EXPLORER.bat
> Option 5 (Generate HTML Report)
```

This creates `style_baseline_report.html` with:
- Side-by-side style comparisons
- Click to enlarge images
- Style specifications (LoRAs, CFG, steps)
- Easy sharing with team/stakeholders

## 🎯 Decision Framework

### Questions to Consider:

1. **Realism Level**
   - Photorealistic? → Gritty Realism
   - Stylized? → Stylized Military, Painted Concept
   - Abstract? → Comic Military, Minimal Tactical

2. **Technology Level**
   - Near-future? → Gritty Realism, Post-Apocalyptic
   - Far-future? → Clean Sci-Fi, Cyberpunk Military
   - Mixed? → Hybrid Tech

3. **Mood/Atmosphere**
   - Dark/gritty? → Post-Apocalyptic, Gritty Realism
   - Clean/professional? → Clean Sci-Fi, Minimal Tactical
   - Vibrant/stylized? → Cyberpunk Military, Comic Military

4. **Target Audience**
   - Hardcore military sim? → Gritty Realism
   - Accessible shooter? → Stylized Military
   - Unique aesthetic? → Hybrid Tech, Soviet Retro

## 🔄 Style Mixing

Once you identify favorites, you can create custom combinations:

```python
# Example: Mix Gritty Realism with Cyberpunk elements
custom_style = {
    "loras": [
        ("battlefield 2042 style.safetensors", 0.7),  # Base military
        ("Neon_Noir_FLUX.safetensors", 0.3),         # Subtle cyber
        ("Detailed Skin&Textures Flux V3.safetensors", 0.5)  # Quality
    ]
}
```

## 📈 Recommended Workflow

1. **Day 1**: Generate emblem comparisons (10 styles)
2. **Day 1**: Select top 3 styles
3. **Day 2**: Generate all subjects in top 3 styles
4. **Day 2**: Choose final style or create hybrid
5. **Day 3**: Generate production assets in chosen style

## 💡 Pro Tips

1. **Consistent Seeds**: All tests use seed=42 for fair comparison
2. **Save Favorites**: Copy best results to `_Favorites` immediately
3. **Document Choice**: Note why you chose specific styles
4. **Test Variations**: Try different CFG/steps on favorites
5. **Get Feedback**: Share HTML report with team/community

## 🎨 Style Combination Matrix

| Style | Best For | Faction Match | LoRA Count |
|-------|----------|---------------|------------|
| Gritty Realism | Main aesthetic | Directorate, Free77 | 4 LoRAs |
| Cyberpunk Military | Tech factions | Corporate Combine | 4 LoRAs |
| Post-Apocalyptic | Scavengers | Vultures, Nomads | 3 LoRAs |
| Clean Sci-Fi | Alien tech | Vaulted Archivists | 3 LoRAs |
| Soviet Retro | Authority | Directorate | 3 LoRAs |

## 🚦 Next Steps After Baseline

1. **Lock Style**: Choose your primary aesthetic
2. **Create Style Bible**: Document exact LoRA combinations
3. **Generate Heroes**: Create key assets in chosen style
4. **Build Templates**: Save successful workflows
5. **Scale Production**: Generate all game assets

---

**Remember**: The goal is to find a distinctive visual style that:
- Supports Terminal Grounds' narrative
- Distinguishes your game in the market
- Remains consistent across all assets
- Leverages your powerful LoRA collection

Your 168 LoRAs give you unprecedented creative control. Use this systematic approach to find the perfect combination!
