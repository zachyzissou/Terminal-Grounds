param(
    [Parameter(Mandatory = $true)] [string]$UeRoot,
    [string]$PythonExe = "$PSScriptRoot/../../.venv/Scripts/python.exe"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path "$PSScriptRoot/../..\").Path.TrimEnd('\')
$UProject = "$RepoRoot/TerminalGrounds.uproject"
$McpJobs = "$RepoRoot/Tools/ArtGen/outputs/mcp_jobs.json"
$McpResults = "$RepoRoot/Tools/ArtGen/outputs/mcp_results.json"

Write-Host "[Pipeline] RepoRoot: $RepoRoot"
Write-Host "[Pipeline] UE Root:  $UeRoot"

if (-not (Test-Path $McpJobs)) {
    Write-Error "Missing $McpJobs. Run: python Tools/ArtGen/artgen_run_mcp.py"
    exit 2
}

if (-not (Test-Path $McpResults)) {
    Write-Error "Missing $McpResults. Execute the jobs via your MCP client and save the returned URLs here (array of {target_rel, url})."
    exit 2
}

# 1) Download all MCP result URLs to their output_path
Write-Host "[Pipeline] Downloading MCP results to disk..."
& $PythonExe "$RepoRoot/Tools/ArtGen/mcp_download_results.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Downloader failed with code $LASTEXITCODE"
    exit $LASTEXITCODE
}

# 2) Import into Unreal (headless)
Write-Host "[Pipeline] Importing into Unreal (headless)..."
& pwsh -NoProfile -ExecutionPolicy Bypass -File "$RepoRoot/Tools/Unreal/ps1/run_import_artgen.ps1" `
    -UeRoot $UeRoot `
    -UProject $UProject `
    -PyScript "$RepoRoot/Tools/Unreal/python/tools_import_artgen_outputs.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "UE import failed with code $LASTEXITCODE"
    exit $LASTEXITCODE
}

# 3) Rebuild docs asset manifest
Write-Host "[Pipeline] Rebuilding docs asset manifest..."
& $PythonExe "$RepoRoot/Tools/build_asset_manifest.py"
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Docs manifest build returned code $LASTEXITCODE (non-fatal)."
}

Write-Host "[Pipeline] Done."
exit 0
