@echo off
title Terminal Grounds - Quick Asset Generator
color 0A

echo ============================================================
echo     TERMINAL GROUNDS - QUICK ASSET GENERATOR
echo ============================================================
echo.
echo ComfyUI detected at: http://127.0.0.1:8000
echo.
echo This will generate your faction assets using the API.
echo No mouse/keyboard automation needed!
echo.
pause

echo.
echo Generating test asset to verify connection...
echo.

powershell -Command ^
"$w = @{^
  '1' = @{class_type='CheckpointLoaderSimple'; inputs=@{ckpt_name='FLUX1\flux1-dev-fp8.safetensors'}};^
  '2' = @{class_type='CLIPTextEncode'; inputs=@{text='military faction emblem, chevron, steel blue'; clip=@('1',1)}};^
  '3' = @{class_type='CLIPTextEncode'; inputs=@{text=''; clip=@('1',1)}};^
  '4' = @{class_type='EmptyLatentImage'; inputs=@{width=1024; height=1024; batch_size=1}};^
  '5' = @{class_type='KSampler'; inputs=@{seed=42; steps=10; cfg=7.5; sampler_name='euler'; scheduler='normal'; denoise=1.0; model=@('1',0); positive=@('2',0); negative=@('3',0); latent_image=@('4',0)}};^
  '6' = @{class_type='VAEDecode'; inputs=@{samples=@('5',0); vae=@('1',2)}};^
  '7' = @{class_type='SaveImage'; inputs=@{filename_prefix='TG_test'; images=@('6',0)}}^
};^
$body = @{prompt=$w} | ConvertTo-Json -Depth 10;^
$r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/prompt' -Method Post -Body $body -ContentType 'application/json';^
Write-Host 'Queued with ID:' $r.prompt_id -ForegroundColor Green;^
Write-Host 'Generating... (30-60 seconds)' -ForegroundColor Yellow;^
Start-Sleep -Seconds 30;^
Write-Host 'Check ComfyUI output folder for TG_test_*.png' -ForegroundColor Cyan"

echo.
echo ============================================================
echo Check your ComfyUI output folder:
echo C:\Users\Zachg\Documents\ComfyUI\output\
echo.
echo Files will be named: TG_test_*.png
echo ============================================================
echo.
pause
