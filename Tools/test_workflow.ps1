$w = @{
  '1' = @{class_type='CheckpointLoaderSimple'; inputs=@{ckpt_name='FLUX1\flux1-dev-fp8.safetensors'}};
  '2' = @{class_type='CLIPTextEncode'; inputs=@{text='Terminal Grounds atmospheric industrial complex, concept art, detailed illustration'; clip=@('1',1)}};
  '3' = @{class_type='CLIPTextEncode'; inputs=@{text='low quality, blurry, text'; clip=@('1',1)}};
  '4' = @{class_type='EmptyLatentImage'; inputs=@{width=1024; height=1024; batch_size=1}};
  '5' = @{class_type='KSampler'; inputs=@{seed=94887; steps=20; cfg=4.5; sampler_name='euler'; scheduler='normal'; denoise=1.0; model=@('1',0); positive=@('2',0); negative=@('3',0); latent_image=@('4',0)}};
  '6' = @{class_type='VAEDecode'; inputs=@{samples=@('5',0); vae=@('1',2)}};
  '7' = @{class_type='SaveImage'; inputs=@{filename_prefix='TG_Working_Test'; images=@('6',0)}}
}

$body = @{prompt=$w} | ConvertTo-Json -Depth 10
$r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/prompt' -Method Post -Body $body -ContentType 'application/json'
Write-Host "SUCCESS! Queued:" $r.prompt_id -ForegroundColor Green
Write-Host "Check ComfyUI output folder in 30-60 seconds!" -ForegroundColor Yellow