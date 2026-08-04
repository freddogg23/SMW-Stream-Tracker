param(
    [string]$Version = '1.0.3',
    [string]$ReleaseBaseUrl = 'https://github.com/freddogg23/SMW-Stream-Tracker/releases/download/v',
    [switch]$SkipAppBuild
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $projectRoot 'dist'
$appExe = Join-Path $dist 'SMWStreamTracker.exe'
$setupExe = Join-Path $dist "SMWStreamTracker_Setup_$Version.exe"
$updaterExe = Join-Path $dist "SMWStreamTracker_Update_$Version.exe"
$checksumsPath = Join-Path $dist "SHA256SUMS_$Version.txt"
$manifestPath = Join-Path $PSScriptRoot 'update_manifest.json'
$releaseNotesPath = Join-Path $PSScriptRoot 'RELEASE_NOTES.txt'

function Confirm-UnsignedArtifact([string]$Path) {
    $signature = Get-AuthenticodeSignature -LiteralPath $Path
    if ($signature.Status -ne 'NotSigned') {
        throw "Expected an unsigned artifact, but $Path has signature status $($signature.Status)."
    }
}

Set-Location $projectRoot
New-Item -ItemType Directory -Force -Path $dist | Out-Null

$sourceVersion = Select-String -LiteralPath (Join-Path $projectRoot 'SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py') -Pattern '^APP_VERSION = "([^\"]+)"$'
if (-not $sourceVersion -or $sourceVersion.Matches[0].Groups[1].Value -ne $Version) {
    throw "APP_VERSION does not match requested release $Version."
}
foreach ($scriptName in @('SMWStreamTrackerInstaller.iss', 'SMWStreamTrackerUpdater.iss')) {
    $scriptPath = Join-Path $projectRoot "installer\$scriptName"
    if (-not (Select-String -LiteralPath $scriptPath -SimpleMatch "#define AppVersion `"$Version`"")) {
        throw "$scriptName does not use version $Version."
    }
}

if (-not $SkipAppBuild) {
    if ($env:SMW_BUILD_PYTHON -and (Test-Path -LiteralPath $env:SMW_BUILD_PYTHON)) {
        $pythonPath = $env:SMW_BUILD_PYTHON
    }
    else {
        $python = Get-Command python.exe -ErrorAction SilentlyContinue
        if (-not $python) {
            throw 'python.exe was not found. Install Python or set SMW_BUILD_PYTHON to its full path.'
        }
        $pythonPath = $python.Source
    }
    & $pythonPath -m PyInstaller --noconfirm --clean (Join-Path $projectRoot 'SMWStreamTracker.spec')
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
}
if (-not (Test-Path -LiteralPath $appExe -PathType Leaf)) {
    throw "App executable was not found: $appExe"
}

Confirm-UnsignedArtifact $appExe

$isccCommand = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if ($isccCommand) {
    $isccPath = $isccCommand.Source
}
else {
    $bundledIscc = Join-Path $projectRoot 'installer_tools\InnoSetup\ISCC.exe'
    $workspaceRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $projectRoot))
    $workspaceIscc = Join-Path $workspaceRoot 'installer_tools\InnoSetup\ISCC.exe'
    $defaultIscc = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
    if (Test-Path -LiteralPath $bundledIscc) {
        $isccPath = $bundledIscc
    }
    elseif (Test-Path -LiteralPath $workspaceIscc) {
        $isccPath = $workspaceIscc
    }
    elseif (Test-Path -LiteralPath $defaultIscc) {
        $isccPath = $defaultIscc
    }
    else {
        throw 'ISCC.exe was not found. Install Inno Setup 6.'
    }
}

& $isccPath (Join-Path $projectRoot 'installer\SMWStreamTrackerInstaller.iss')
if ($LASTEXITCODE -ne 0) { throw 'Complete installer build failed.' }
& $isccPath (Join-Path $projectRoot 'installer\SMWStreamTrackerUpdater.iss')
if ($LASTEXITCODE -ne 0) { throw 'Updater build failed.' }

foreach ($artifact in @($setupExe, $updaterExe)) {
    if (-not (Test-Path -LiteralPath $artifact -PathType Leaf)) {
        throw "Expected release artifact is missing: $artifact"
    }
    Confirm-UnsignedArtifact $artifact
}

$notes = Get-Content -LiteralPath $releaseNotesPath |
    Where-Object { $_ -match '^\* ' } |
    ForEach-Object { $_.Substring(2) }
$updaterHash = (Get-FileHash -LiteralPath $updaterExe -Algorithm SHA256).Hash.ToLowerInvariant()
$updaterFileName = Split-Path -Leaf $updaterExe
$manifest = [ordered]@{
    schema = 1
    version = $Version
    release_date = (Get-Date -Format 'yyyy-MM-dd')
    notes = @($notes)
    updater_url = "$ReleaseBaseUrl$Version/$updaterFileName"
    verification = 'sha256'
    sha256 = $updaterHash
    size = (Get-Item -LiteralPath $updaterExe).Length
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding utf8

$checksumLines = @($appExe, $setupExe, $updaterExe) | ForEach-Object {
    $artifactHash = (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()
    "$artifactHash  $(Split-Path -Leaf $_)"
}
$checksumLines | Set-Content -LiteralPath $checksumsPath -Encoding ascii

Write-Host ''
Write-Host "Unsigned release $Version is ready."
Write-Host "App:       $appExe"
Write-Host "Installer: $setupExe"
Write-Host "Updater:   $updaterExe"
Write-Host "Checksums: $checksumsPath"
Write-Host "Manifest:  $manifestPath"
