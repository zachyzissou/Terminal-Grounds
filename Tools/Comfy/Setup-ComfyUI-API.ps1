param(
  [string]$ApiDir = "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API",
  # Path to your existing GUI ComfyUI root
  [string]$ElectronRoot = "C:\Users\Zachg\Documents\ComfyUI",
  # Path to your existing GUI ComfyUI models directory
  [string]$ElectronModels = "C:\Users\Zachg\Documents\ComfyUI\models",
  [string]$Port = "8188",
  [switch]$SkipClone
)

function New-Junction($Link, $Target) {
  if (Test-Path $Link) { Remove-Item -Force $Link }
  if (!(Test-Path $Target)) { Write-Error "Missing target: $Target"; return }
  cmd /c mklink /J "$Link" "$Target" | Out-Null
  Write-Host "Junction: $Link -> $Target"
}

# 1) Clone ComfyUI (unless skipped)
if (-not $SkipClone) {
  if (!(Test-Path $ApiDir)) {
    New-Item -ItemType Directory -Path (Split-Path $ApiDir) -Force | Out-Null
    Set-Location (Split-Path $ApiDir)
    git clone https://github.com/comfyanonymous/ComfyUI.git ComfyUI-API
  }
}
Set-Location $ApiDir

# 2) Junction models and custom nodes from the Electron install
# Prefer linking the entire models directory if present; else link common subfolders
if (Test-Path $ElectronModels) {
  if (Test-Path .\models) { Remove-Item -Force -Recurse .\models }
  New-Junction -Link ".\models" -Target $ElectronModels
} else {
  New-Item -ItemType Directory -Path .\models -Force | Out-Null
  $folders = @(
    "checkpoints","loras","clip","vae","unet","controlnet","upscale_models",
    "ipadapter","embeddings","clip_vision","vae_approx","ultralytics"
  )
  foreach ($f in $folders) {
    $src = Join-Path $ElectronModels $f
    $dst = Join-Path ".\models" $f
    if (Test-Path $src) { New-Junction -Link $dst -Target $src }
  }
}

# Link custom_nodes so API instance sees all your GUI nodes
$electronCustomNodes = Join-Path $ElectronRoot "custom_nodes"
if (Test-Path $electronCustomNodes) {
  $apiCustomNodes = Join-Path $ApiDir "custom_nodes"
  if (Test-Path $apiCustomNodes) { Remove-Item -Force -Recurse $apiCustomNodes }
  New-Junction -Link $apiCustomNodes -Target $electronCustomNodes
} else {
  Write-Warning "Electron custom_nodes folder not found at $electronCustomNodes"
}

# 3) Python env + requirements
if (!(Test-Path ".\.venv")) { py -3.12 -m venv .venv }
& .\.venv\Scripts\Activate.ps1
$venvPy = (Resolve-Path ".\.venv\Scripts\python.exe")
& $venvPy -m pip install --upgrade pip
if (Test-Path ".\requirements.txt") { & $venvPy -m pip install -r requirements.txt }

# 4) Run script (robust: resolve script dir, absolute venv, fallback to system python)
$run = @"
param([string]$Port = '$Port')
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$env:PYTHONUTF8 = 1
$env:COMFYUI_MODEL_DIR = (Resolve-Path .\models)

$venvPy = Join-Path $here ".venv\Scripts\python.exe"
$pyExe = $venvPy
if (!(Test-Path $pyExe)) {
  Write-Warning "Venv python not found, using system Python."
  $pyExe = "py"
}

# Detect CUDA availability and set CPU fallback
$useCpu = $false
try {
  if ($pyExe -eq "py") {
    & $pyExe -3.12 -c "import torch,sys; sys.exit(0 if getattr(torch,'cuda',None) and torch.cuda.is_available() else 1)"
  } else {
    & $pyExe -c "import torch,sys; sys.exit(0 if getattr(torch,'cuda',None) and torch.cuda.is_available() else 1)"
  }
  if ($LASTEXITCODE -ne 0) { $useCpu = $true }
} catch { $useCpu = $true }

$pyArgs = @('--listen','127.0.0.1','--port', $Port)
if ($useCpu) { $pyArgs += '--cpu' }

if ($pyExe -eq "py") {
  & $pyExe -3.12 .\main.py @pyArgs
} else {
  & $pyExe .\main.py @pyArgs
}
"@
Set-Content -Path ".\Run-ComfyUI-API.ps1" -Value $run -Encoding UTF8
Write-Host "Run script created: $ApiDir\Run-ComfyUI-API.ps1"

# 5) Helper: install requirements for all custom nodes (if any)
$installNodes = @"
param([string]$PythonExe = ".\.venv\Scripts\python.exe")
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$customNodes = Join-Path $here "custom_nodes"
if (!(Test-Path $customNodes)) { Write-Host "No custom_nodes found"; exit 0 }

if (!(Test-Path $PythonExe)) { $PythonExe = "py" }

Get-ChildItem -Path $customNodes -Directory | ForEach-Object {
  $req = Join-Path $_.FullName "requirements.txt"
  if (Test-Path $req) {
    Write-Host "Installing requirements for $($_.Name) ..."
    if ($PythonExe -eq "py") {
      & $PythonExe -3.12 -m pip install -r $req
    } else {
      & $PythonExe -m pip install -r $req
    }
  }
}
"@
Set-Content -Path ".\Install-CustomNodes-Requirements.ps1" -Value $installNodes -Encoding UTF8
Write-Host "Helper created: $ApiDir\Install-CustomNodes-Requirements.ps1"
