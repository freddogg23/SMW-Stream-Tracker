param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'dist')
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pluginRoot = Join-Path $PSScriptRoot 'com.freddogg23.smwstreamtracker.sdPlugin'
$manifestPath = Join-Path $pluginRoot 'manifest.json'

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Stream Deck manifest was not found: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.OS.Count -ne 1 -or $manifest.OS[0].Platform -ne 'windows') {
    throw 'The Stream Deck plugin must remain Windows-only.'
}
if ($manifest.CodePath -ne 'bin/plugin.js') {
    throw 'The Stream Deck plugin entry point is not configured correctly.'
}

$python = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-ChildItem -LiteralPath (Join-Path $env:LOCALAPPDATA 'Programs\Python') -Directory -Filter 'Python*' -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending |
        ForEach-Object { Join-Path $_.FullName 'python.exe' } |
        Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
        Select-Object -First 1
}
else {
    $python = $python.Source
}
if (-not $python) {
    throw 'Python with Pillow is required to generate the Stream Deck icons.'
}

& $python (Join-Path $PSScriptRoot 'build_icons.py')
if ($LASTEXITCODE -ne 0) {
    throw 'Stream Deck icon generation failed.'
}

$streamDeckCli = Get-Command streamdeck.cmd -ErrorAction SilentlyContinue
if (-not $streamDeckCli) {
    $streamDeckCli = Get-Command streamdeck -ErrorAction SilentlyContinue
}
if ($streamDeckCli) {
    $streamDeckCli = $streamDeckCli.Source
}
else {
    $localCli = Join-Path $PSScriptRoot '.build-tools\node_modules\.bin\streamdeck.cmd'
    if (Test-Path -LiteralPath $localCli -PathType Leaf) {
        $streamDeckCli = $localCli
        $portableNode = Join-Path $PSScriptRoot '.build-tools\node-v24.13.1-win-x64'
        if (Test-Path -LiteralPath (Join-Path $portableNode 'node.exe') -PathType Leaf) {
            $env:PATH = "$portableNode;$env:PATH"
        }
    }
}
if (-not $streamDeckCli) {
    throw 'Elgato Stream Deck CLI was not found. Install @elgato/cli or place a local copy in streamdeck\.build-tools.'
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
& $streamDeckCli pack $pluginRoot --output $OutputDirectory --force --no-update-check
if ($LASTEXITCODE -ne 0) {
    throw 'Elgato Stream Deck CLI validation or packaging failed.'
}

$generatedPackage = Get-ChildItem -LiteralPath $OutputDirectory -File -Filter '*.streamDeckPlugin' |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $generatedPackage) {
    throw 'Elgato Stream Deck CLI did not create a plugin installer.'
}
$friendlyPackage = Join-Path $OutputDirectory 'SMWStreamTracker-SPC-Controls.streamDeckPlugin'
if ($generatedPackage.FullName -ne $friendlyPackage) {
    Move-Item -LiteralPath $generatedPackage.FullName -Destination $friendlyPackage -Force
}

Write-Host "Stream Deck plugin installer: $friendlyPackage"
