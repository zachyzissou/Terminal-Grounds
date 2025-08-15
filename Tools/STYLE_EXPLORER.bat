@echo off
title Terminal Grounds - Style Baseline Explorer
color 0D
cls

echo ============================================================
echo     TERMINAL GROUNDS - STYLE BASELINE EXPLORER
echo ============================================================
echo.
echo This will help you find the perfect visual style by
echo generating test assets in 10 different aesthetic approaches:
echo.
echo   1. Gritty Realism - Photorealistic military
echo   2. Stylized Military - Semi-realistic game art
echo   3. Cyberpunk Military - High-tech neon warfare
echo   4. Post-Apocalyptic - Wasteland survivor
echo   5. Clean Sci-Fi - Pristine futuristic
echo   6. Painted Concept - Hand-painted art style
echo   7. Hybrid Tech - Human-alien fusion
echo   8. Comic Military - Graphic novel style
echo   9. Soviet Retro - Cold War aesthetic
echo  10. Minimal Tactical - Clean modern design
echo.
echo Each style uses different LoRA combinations from your
echo collection of 168 LoRAs.
echo.
echo Results will be organized in: Style_Staging\
echo ============================================================
echo.
pause

cd /d "%~dp0ArtGen"
python style_baseline_explorer.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo ERROR: Script failed. Check the error message above.
    echo ============================================================
    pause
    exit /b %ERRORLEVEL%
)

REM Script completed successfully, window stays open
exit /b 0
