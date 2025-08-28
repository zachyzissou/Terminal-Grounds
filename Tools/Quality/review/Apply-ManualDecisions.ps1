param(
  [string]$Root = "Tools/Comfy/ComfyUI-API/output",
  [string]$Decisions = "Tools/Quality/review/manual_review_decisions.json"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$rootPath = Resolve-Path -LiteralPath $Root | Select-Object -ExpandProperty Path
$rejectedDir = Join-Path $rootPath '05_QUALITY_CONTROL/Rejected'
if (-not (Test-Path -LiteralPath $rejectedDir)) { New-Item -ItemType Directory -Path $rejectedDir | Out-Null }

# JSON produced by index.html export is an object map id -> { decision, notes }
$map = Get-Content -LiteralPath $Decisions -Raw | ConvertFrom-Json
$reasons = @()

foreach ($key in $map.PSObject.Properties.Name) {
  $entry = $map.$key
  $decision = $entry.decision
  $notes = $entry.notes
  $src = Join-Path $rootPath $key
  if ($decision -eq 'Reject') {
    if (Test-Path -LiteralPath $src) {
      $dest = Join-Path $rejectedDir ([IO.Path]::GetFileName($src))
      if (Test-Path -LiteralPath $dest) { $dest = Join-Path $rejectedDir (([IO.Path]::GetFileNameWithoutExtension($src)) + '_dup' + ([IO.Path]::GetExtension($src))) }
      Move-Item -LiteralPath $src -Destination $dest
      $reasons += [pscustomobject]@{ path = $key; decision = 'Reject'; notes = $notes }
    }
  }
}

$report = Join-Path (Split-Path -Parent $Decisions) 'manual_review_actions.json'
$reasons | ConvertTo-Json -Depth 5 | Out-File -LiteralPath $report -Encoding utf8
Write-Host "Applied" $reasons.Count "rejects. Report:" $report
