param(
  [string]$Root = "Tools/Comfy/ComfyUI-API/output",
  [string]$Out = "Tools/Quality/review/review_index.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Category([string]$Path) {
  if ($Path -match '(?i)emblem|logo|wordmark|icon' -or $Path -match '(?i)\\emblems\\|/emblems/') { return 'logo' }
  if ($Path -match '(?i)Metro|IEZ|Bunker|Tech_Wastes|Security|Corporate|Territorial|Environment' -or $Path -match '(?i)\\environments\\|/environments/') { return 'environment' }
  return 'environment'
}

$rootPath = Resolve-Path -LiteralPath $Root | Select-Object -ExpandProperty Path
$items = @()
$exts = @('*.png','*.jpg','*.jpeg','*.webp','*.bmp')

Add-Type -AssemblyName System.Drawing | Out-Null

Get-ChildItem -LiteralPath $rootPath -Recurse -File -Include $exts | ForEach-Object {
  $full = $_.FullName
  $rel = $(Resolve-Path -LiteralPath $full -Relative -RelativeBasePath $rootPath 2>$null)
  if (-not $rel) { $rel = $_.FullName.Substring($rootPath.Length).TrimStart('\\','/') }
  $width = 0; $height = 0
  try { $img = [System.Drawing.Image]::FromFile($full); $width = $img.Width; $height = $img.Height; $img.Dispose() } catch { }
  $cat = Get-Category $full
  $items += [pscustomobject]@{
    id = $rel -replace '\\','/'
    name = $_.Name
    rel = "../../Comfy/ComfyUI-API/output/" + ($rel -replace '\\','/')
    width = $width
    height = $height
    category = $cat
    sharpness = $null
    edge_density = 0.0
  }
}

# Write JSON
$dir = Split-Path -Parent -Path $Out
if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
$items | ConvertTo-Json -Depth 5 | Out-File -LiteralPath $Out -Encoding utf8
Write-Host "Wrote" $items.Count "items to" $Out
