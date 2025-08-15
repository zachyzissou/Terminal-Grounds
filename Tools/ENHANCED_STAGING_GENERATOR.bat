@echo off
title Terminal Grounds - Enhanced Staging Pipeline
color 0A
cls

echo ============================================================
echo      TERMINAL GROUNDS - ENHANCED STAGING PIPELINE
echo ============================================================
echo.
echo Enhanced Features:
echo   ✅ Lore-accurate faction prompts (from Art Bible)
echo   ✅ Your 150+ LoRA collection integrated  
echo   ✅ Style_Staging folder workflow support
echo   ✅ FLUX-dev quality (30+ steps vs 6 schnell)
echo   ✅ Concept staging and approval workflow
echo   ✅ Semantic UI icons (damage types, rarity, etc.)
echo.
echo Your Setup:
echo   ComfyUI: http://127.0.0.1:8000 (Running)
echo   Model: FLUX1-dev-fp8 (High Quality)
echo   LoRAs: Military, Sci-Fi, Weapons, Logos, Textures
echo   GPU: RTX 3090 Ti (24GB VRAM)
echo.
echo Staging Workflow:
echo   1. Generate concept variations
echo   2. Review in web dashboard  
echo   3. Approve/reject interactively
echo   4. Export to final UE5 locations
echo.
echo ============================================================
echo.

cd /d "%~dp0"
python "ArtGen/terminal_grounds_generator.py"

pause