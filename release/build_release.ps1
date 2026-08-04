param(
    [string]$Version = '1.0.2',
    [string]$ReleaseBaseUrl = 'https://github.com/freddogg23/SMW-Stream-Tracker/releases/download/v',
    [switch]$SkipAppBuild,
    [switch]$AllowUnsigned
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $projectRoot 'dist'
$appExe = Join-Path $dist 'SMWStreamTracker.exe'
$setupExe = Join-Path $dist "SMWStreamTracker_Setup_$Version.exe"
$updaterExe = Join-Path $dist "SMWStreamTracker_Update_$Version.exe"
$manifestPath = Join-Path $PSScriptRoot 'update_manifest.json'
$releaseNotesPath = Join-Path $PSScriptRoot 'RELEASE_NOTES.txt'

function Find-SignTool {
    $fromPath = Get-Command signtool.exe -ErrorAction SilentlyContinue
    if ($fromPath) { return $fromPath.Source }
    $kitsRoot = Join-Path ${env:ProgramFiles(x86)} 'Windows Kits\10\bin'
    if (Test-Path -LiteralPath $kitsRoot) {
        $candidate = Get-ChildItem -LiteralPath $kitsRoot -Filter signtool.exe -Recurse |
            Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
            Sort-Object FullName -Descending |
            Select-Object -First 1
        if ($candidate) { return $candidate.FullName }
    }
    throw 'signtool.exe was not found. Install the Windows SDK signing tools.'
}

function Invoke-ReleaseSignature([string]$Path, [string]$SignTool) {
    $timestamp = if ($env:SMW_TRUSTED_SIGNING_DLIB -and $env:SMW_TRUSTED_SIGNING_METADATA) {
        'http://timestamp.acs.microsoft.com'
    }
    else {
        'http://timestamp.digicert.com'
    }
    if ($env:SMW_SIGN_CERT_PFX) {
        $arguments = @('sign', '/v', '/fd', 'SHA256', '/td', 'SHA256', '/tr', $timestamp, '/f', $env:SMW_SIGN_CERT_PFX)
        if ($env:SMW_SIGN_CERT_PASSWORD) {
            $arguments += @('/p', $env:SMW_SIGN_CERT_PASSWORD)
        }
        $arguments += $Path
        & $SignTool @arguments
    }
    elseif ($env:SMW_SIGN_CERT_SHA1) {
        & $SignTool sign /v /fd SHA256 /td SHA256 /tr $timestamp /sha1 $env:SMW_SIGN_CERT_SHA1 $Path
    }
    elseif ($env:SMW_TRUSTED_SIGNING_DLIB -and $env:SMW_TRUSTED_SIGNING_METADATA) {
        & $SignTool sign /v /fd SHA256 /tr $timestamp /td SHA256 /dlib $env:SMW_TRUSTED_SIGNING_DLIB /dmdf $env:SMW_TRUSTED_SIGNING_METADATA $Path
    }
    elseif (-not $AllowUnsigned) {
        throw 'No signing identity is configured. Set SMW_SIGN_CERT_PFX, SMW_SIGN_CERT_SHA1, or the SMW_TRUSTED_SIGNING_* variables. Use -AllowUnsigned only for local testing.'
    }
}

function Confirm-ReleaseSignature([string]$Path) {
    $signature = Get-AuthenticodeSignature -LiteralPath $Path
    if ($signature.Status -ne 'Valid' -and -not $AllowUnsigned) {
        throw "Signature verification failed for $Path ($($signature.Status))."
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

$signingConfigured = [bool](
    $env:SMW_SIGN_CERT_PFX -or
    $env:SMW_SIGN_CERT_SHA1 -or
    ($env:SMW_TRUSTED_SIGNING_DLIB -and $env:SMW_TRUSTED_SIGNING_METADATA)
)
$signTool = $null
if ($signingConfigured -or -not $AllowUnsigned) {
    $signTool = Find-SignTool
}
Invoke-ReleaseSignature $appExe $signTool
Confirm-ReleaseSignature $appExe

$isccCommand = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if ($isccCommand) {
    $isccPath = $isccCommand.Source
}
else {
    $bundledIscc = Join-Path $projectRoot 'installer_tools\InnoSetup\ISCC.exe'
    $defaultIscc = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
    if (Test-Path -LiteralPath $bundledIscc) {
        $isccPath = $bundledIscc
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
    Invoke-ReleaseSignature $artifact $signTool
    Confirm-ReleaseSignature $artifact
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
    sha256 = $updaterHash
    size = (Get-Item -LiteralPath $updaterExe).Length
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding utf8

Write-Host ''
Write-Host "Release $Version is ready."
Write-Host "App:       $appExe"
Write-Host "Installer: $setupExe"
Write-Host "Updater:   $updaterExe"
Write-Host "Manifest:  $manifestPath"
