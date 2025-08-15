# ComfyUI Windows Path Issue - CRITICAL FIX

## The Problem
On Windows, ComfyUI checkpoint paths use backslashes, but JSON requires proper escaping.
This causes "Value not in list" errors when queueing workflows.

## The Solution

### ❌ WRONG - These will fail:
```python
# Single backslash gets eaten by JSON
'ckpt_name': 'FLUX1\flux1-dev-fp8.safetensors'  

# Forward slash doesn't match Windows paths
'ckpt_name': 'FLUX1/flux1-dev-fp8.safetensors'  
```

### ✅ CORRECT - Use one of these methods:

#### Method 1: Raw string (recommended for scripts)
```python
ckpt = r'FLUX1\flux1-dev-fp8.safetensors'
workflow = {
    '1': {
        'class_type': 'CheckpointLoaderSimple',
        'inputs': {'ckpt_name': ckpt}
    }
}
```

#### Method 2: Double backslash in regular string
```python
workflow = {
    '1': {
        'class_type': 'CheckpointLoaderSimple',
        'inputs': {'ckpt_name': 'FLUX1\\flux1-dev-fp8.safetensors'}
    }
}
```

#### Method 3: Environment variable (best for flexibility)
```python
import os
# Set in .env or batch file: TG_CKPT=FLUX1\flux1-dev-fp8.safetensors
ckpt = os.getenv('TG_CKPT', r'FLUX1\flux1-dev-fp8.safetensors')
```

## Available Checkpoints (as of 2025-08-13)
- `FLUX1\flux1-dev-fp8.safetensors` - High quality, 40 steps
- `FLUX1\flux1-schnell-fp8.safetensors` - Fast, 4-8 steps
- `SDXL-TURBO\sd_xl_turbo_1.0.safetensors`
- `SDXL-TURBO\sd_xl_turbo_1.0_fp16.safetensors`

## Test Your Path
Always verify the exact checkpoint name ComfyUI expects:
```python
import urllib.request, json
resp = urllib.request.urlopen('http://127.0.0.1:8000/object_info')
data = json.loads(resp.read())
checkpoints = data['CheckpointLoaderSimple']['input']['required']['ckpt_name'][0]
for ckpt in checkpoints:
    if 'flux' in ckpt.lower():
        print(f'Use exactly: {repr(ckpt)}')
```

## Quick Test Workflow
```python
import json
import urllib.request

# This minimal workflow tests if your checkpoint path is correct
ckpt = r'FLUX1\flux1-dev-fp8.safetensors'  # Raw string!

workflow = {
    '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': ckpt}},
    '2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': 'test', 'clip': ['1', 1]}},
    '3': {'class_type': 'EmptyLatentImage', 'inputs': {'width': 512, 'height': 512, 'batch_size': 1}},
    '4': {'class_type': 'KSampler', 'inputs': {'seed': 1, 'steps': 4, 'cfg': 1.0, 'sampler_name': 'euler', 'scheduler': 'normal', 'denoise': 1.0, 'model': ['1', 0], 'positive': ['2', 0], 'negative': ['2', 0], 'latent_image': ['3', 0]}},
    '5': {'class_type': 'VAEDecode', 'inputs': {'samples': ['4', 0], 'vae': ['1', 2]}},
    '6': {'class_type': 'SaveImage', 'inputs': {'images': ['5', 0], 'filename_prefix': 'test'}}
}

data = json.dumps({'prompt': workflow}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/prompt', data=data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as r:
    print('Success!', json.loads(r.read()).get('prompt_id'))
```

## Remember
- ComfyUI on Windows ALWAYS uses backslashes in checkpoint paths
- Python raw strings (r'...') preserve single backslashes
- JSON encoding requires escaped backslashes (\\)
- When in doubt, use the test workflow above

---
Last verified: 2025-08-13
Issue discovered when atmospheric_concept_workflow.py failed with path errors