param(
  [string]$Root = "docs\\Lore\\LoreBook",
  [string]$OutIndex = "Tools\\Lore\\lore_index.json",
  [string]$OutPrompts = "Tools\\Comfy\\ComfyUI-API\\lore_prompts.json",
  [string]$Baseline = "Tools\\Comfy\\ComfyUI-API\\lore_prompts.baseline.json"
)

# Require YAML parser
if (-not (Get-Module -ListAvailable powershell-yaml)) {
  try { Install-Module powershell-yaml -Scope CurrentUser -Force -AllowClobber | Out-Null } catch {}
}
Import-Module powershell-yaml -ErrorAction SilentlyContinue | Out-Null

function Ensure-Array {
  param($Value)
  if ($null -eq $Value) { return $null }
  if ($Value -is [string]) { return ,$Value }
  if ($Value -is [System.Collections.IEnumerable]) { return @($Value) }
  return ,$Value
}

function Normalize-TierToken {
  param([string]$Tier)
  if (-not $Tier) { return $null }
  switch ($Tier.ToLowerInvariant()) {
    'alien'     { return 'alien' }
    'human'     { return 'human' }
    'hybrid'    { return 'hybrid' }
    'monolith'  { return 'alien' }
    'field'     { return 'human' }
    'splice'    { return 'hybrid' }
    default     { return $Tier }
  }
}

function Merge-ById {
  param(
    [Parameter(Mandatory=$true)]$New,
    [Parameter(Mandatory=$false)]$Existing,
    [string]$Key = 'id'
  )
  $outList = @()
  $seen = @{}
  foreach ($n in ($New | Where-Object { $_ })) {
    $nid = $n.PSObject.Properties[$Key].Value
    if ($nid -and -not $seen.ContainsKey($nid)) {
      $outList += $n
      $seen[$nid] = $true
    }
  }
  foreach ($e in ($Existing | Where-Object { $_ })) {
    $eid = $e.PSObject.Properties[$Key].Value
    if ($eid -and -not $seen.ContainsKey($eid)) {
      $outList += $e
      $seen[$eid] = $true
    }
  }
  return ,$outList
}

function Read-YamlFrontMatter {
  param([string]$Path)
  $text = Get-Content -Raw -Path $Path
  if ($text -match '^---\s*([\s\S]*?)\s*---\s*') {
    $yaml = $Matches[1]
    try { return ConvertFrom-Yaml -Yaml $yaml } catch { return $null }
  }
  return $null
}

$sets = @{
  regions = @()
  factions = @()
  pois = @()
  characters = @()
  technology = @()
  events = @()
}

Get-ChildItem -Path $Root -Recurse -Filter *.md | ForEach-Object {
  $fm = Read-YamlFrontMatter -Path $_.FullName
  if (-not $fm) { return }
  if (-not $fm.id) { $fm | Add-Member -NotePropertyName id -NotePropertyValue ([IO.Path]::GetFileNameWithoutExtension($_.Name)) -Force }
  switch ($fm.type) {
    'region'     { $sets.regions    += $fm }
    'faction'    { $sets.factions   += $fm }
    'poi'        { $sets.pois       += $fm }
    'character'  { $sets.characters += $fm }
    'tech'       { $sets.technology += $fm }
    'event'      { $sets.events     += $fm }
  }
}

# Write full index of front-matter for downstream tools
$sets | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 -Path $OutIndex

# Load existing prompts (preserve where we have no new data)
$existing = $null
if (Test-Path $OutPrompts) {
  try { $existing = Get-Content $OutPrompts -Raw | ConvertFrom-Json } catch { $existing = $null }
}

# Optional baseline seed: union baseline + existing to avoid losing legacy entries
if (Test-Path $Baseline) {
  try {
    $base = Get-Content $Baseline -Raw | ConvertFrom-Json
    if ($base) {
      if (-not $existing) { $existing = $base }
      else {
        # Merge arrays from baseline into existing for reference, dedup by id
        $existing = [pscustomobject]@{
          styleCapsule = if ($existing.styleCapsule) { $existing.styleCapsule } else { $base.styleCapsule }
          termAliases  = if ($existing.termAliases) { $existing.termAliases } else { $base.termAliases }
          world        = if ($existing.world) { $existing.world } else { $base.world }
          regions      = Merge-ById -New $existing.regions -Existing $base.regions
          factions     = Merge-ById -New $existing.factions -Existing $base.factions
          pois         = Merge-ById -New $existing.pois -Existing $base.pois
          characters   = Merge-ById -New $existing.characters -Existing $base.characters
          technology   = Merge-ById -New $existing.technology -Existing $base.technology
          events       = Merge-ById -New $existing.events -Existing $base.events
        }
      }
    }
  } catch {}
}

$styleDefault = "in-engine render, Unreal Engine 5.6, Lumen GI, Nanite geometry, game-ready, gritty realism, photoreal, cinematic lighting, volumetric haze, directional key light, SSAO, high-frequency normal maps, ACES filmic, neutral grade"

$regionsOut = @()
foreach ($r in $sets.regions) {
  $existingAliases = $null
  if ($existing -and $existing.regions) { $existingAliases = ($existing.regions | Where-Object { $_.id -eq $r.id } | Select-Object -First 1).aliases }
  $aliasesArr = Ensure-Array $existingAliases
  # Remove duplicates and primary name if present
  if ($aliasesArr) {
    $aliasesArr = @([System.Linq.Enumerable]::Distinct([string[]]$aliasesArr))
    if ($r.name) { $aliasesArr = @($aliasesArr | Where-Object { $_ -and $_ -ne $r.name }) }
    if ($aliasesArr.Count -eq 0) { $aliasesArr = $null }
  }
  $regionsOut += [pscustomobject]@{
    id        = $r.id
    name      = $r.name
    desc      = $r.desc
    motifs    = $r.motifs
    materials = $r.materials
    atmo      = $r.atmo
    aliases   = $aliasesArr
  }
}
if ($existing -and $existing.regions) { $regionsOut = Merge-ById -New $regionsOut -Existing $existing.regions }

$factionsOut = @()
foreach ($f in $sets.factions) {
  $sig = $null
  if ($f.signature) { $sig = $f.signature }
  elseif ($f.signatures) {
    $vis = @()
    if ($f.signatures.visual) { $vis += $f.signatures.visual }
    if ($f.signatures.narrative) { $vis += $f.signatures.narrative }
    if ($vis) { $sig = ($vis | Select-Object -First 6) -join ', ' }
  }
  $existingAliases = $null
  if ($existing -and $existing.factions) { $existingAliases = ($existing.factions | Where-Object { $_.id -eq $f.id } | Select-Object -First 1).aliases }
  $aliasesArr = Ensure-Array $existingAliases
  if ($aliasesArr) {
    $aliasesArr = @([System.Linq.Enumerable]::Distinct([string[]]$aliasesArr))
    if ($f.name) { $aliasesArr = @($aliasesArr | Where-Object { $_ -and $_ -ne $f.name }) }
    if ($aliasesArr.Count -eq 0) { $aliasesArr = $null }
  }
  $factionsOut += [pscustomobject]@{
    id        = $f.id
    name      = $f.name
    signature = $sig
    slogan    = if ($f.slogan) { $f.slogan } else { ($existing.factions | Where-Object { $_.id -eq $f.id } | Select-Object -First 1).slogan }
    aliases   = $aliasesArr
  }
}
if ($existing -and $existing.factions) { $factionsOut = Merge-ById -New $factionsOut -Existing $existing.factions }

$poisOut = @()
foreach ($p in $sets.pois) {
  $existingAliases = $null
  if ($existing -and $existing.pois) { $existingAliases = ($existing.pois | Where-Object { $_.id -eq $p.id } | Select-Object -First 1).aliases }
  $aliasesArr = Ensure-Array $existingAliases
  if ($aliasesArr) {
    $aliasesArr = @([System.Linq.Enumerable]::Distinct([string[]]$aliasesArr))
    if ($p.name) { $aliasesArr = @($aliasesArr | Where-Object { $_ -and $_ -ne $p.name }) }
    if ($aliasesArr.Count -eq 0) { $aliasesArr = $null }
  }
  $poisOut += [pscustomobject]@{
    id   = $p.id
    name = $p.name
    hook = $p.hook
    aliases = $aliasesArr
  }
}
if ($existing -and $existing.pois) { $poisOut = Merge-ById -New $poisOut -Existing $existing.pois }

$charactersOut = @()
foreach ($c in $sets.characters) {
  $charactersOut += [pscustomobject]@{
    id     = $c.id
    name   = $c.name
    faction= if ($c.relationships) { $c.relationships.faction } else { $null }
    tags   = $c.tags
  }
}
if ($existing -and $existing.characters) { $charactersOut = Merge-ById -New $charactersOut -Existing $existing.characters }

$techOut = @()
foreach ($t in $sets.technology) {
  $techOut += [pscustomobject]@{
    id     = $t.id
    name   = $t.name
  tier   = (Normalize-TierToken $t.tier)
    tags   = $t.tags
  }
}
if ($existing -and $existing.technology) { $techOut = Merge-ById -New $techOut -Existing $existing.technology }

$eventsOut = @()
foreach ($e in $sets.events) {
  $existingAliases = $null
  if ($existing -and $existing.events) { $existingAliases = ($existing.events | Where-Object { $_.id -eq $e.id } | Select-Object -First 1).aliases }
  $aliasesArr = Ensure-Array $existingAliases
  if ($aliasesArr) {
    $aliasesArr = @([System.Linq.Enumerable]::Distinct([string[]]$aliasesArr))
    if ($e.name) { $aliasesArr = @($aliasesArr | Where-Object { $_ -and $_ -ne $e.name }) }
    if ($aliasesArr.Count -eq 0) { $aliasesArr = $null }
  }
  $eventsOut += [pscustomobject]@{
    id   = $e.id
    name = $e.name
    tags = $e.tags
    aliases = $aliasesArr
  }
}
if ($existing -and $existing.events) { $eventsOut = Merge-ById -New $eventsOut -Existing $existing.events }

$out = [pscustomobject]@{
  styleCapsule = if ($existing -and $existing.styleCapsule) { $existing.styleCapsule } else { $styleDefault }
  termAliases  = if ($existing -and $existing.termAliases) { $existing.termAliases } else { $null }
  world        = if ($existing -and $existing.world) { $existing.world } else { $null }
  regions      = @($regionsOut)
  factions     = @($factionsOut)
  pois         = @($poisOut)
  characters   = @($charactersOut)
  technology   = @($techOut)
  events       = @($eventsOut)
}

$out | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path $OutPrompts

Write-Host "Lore index -> $OutIndex"
Write-Host "Lore prompts -> $OutPrompts"
