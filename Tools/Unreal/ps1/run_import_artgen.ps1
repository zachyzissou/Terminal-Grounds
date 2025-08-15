param(
    [Parameter(Mandatory = $true)][string]$UeRoot,
    [Parameter(Mandatory = $true)][string]$UProject,
    [Parameter(Mandatory = $true)][string]$PyScript
)
$exe = Join-Path $UeRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
if (-not (Test-Path $exe)) {
    Write-Error "UnrealEditor-Cmd.exe not found at $exe"
    exit 1
}
# Prepare an absolute log path so we can evaluate success independently of unrelated load errors
$projRoot = Split-Path -Parent $UProject
$logDir = Join-Path $projRoot 'Saved\Logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath = Join-Path $logDir "ImportArtGen_$timestamp.log"

# Build arguments; NullRHI keeps it fully headless and faster
$ueArgs = @(
    "$UProject",
    '-run=PythonScript',
    "-script=$PyScript",
    '-nop4',
    '-unattended',
    '-nosplash',
    '-NullRHI',
    "-abslog=$logPath"
)

& "$exe" @ueArgs
$code = $LASTEXITCODE

# Parse the log for definitive script success; some asset load errors may set non-zero exit codes
$scriptSucceeded = $false
if (Test-Path $logPath) {
    try {
        $logContent = Get-Content -Raw -ErrorAction Stop -Path $logPath
        if ($logContent -match 'LogPythonScriptCommandlet:\s+Display:\s+Python script executed successfully') {
            $scriptSucceeded = $true
        }
    }
    catch {
        # If we cannot read the log, fall back to process exit code
    }
}

if ($scriptSucceeded) {
    Write-Host "[run_import_artgen] Python script reported success. Log: $logPath"
    exit 0
}

if ($code -ne 0) {
    Write-Error "[run_import_artgen] Unreal exited with code $code. Log: $logPath"
    exit $code
}

exit 0
