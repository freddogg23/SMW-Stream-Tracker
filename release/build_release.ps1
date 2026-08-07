param(
    [string]$Version = '1.0.6',
    [string]$ReleaseBaseUrl = 'https://github.com/freddogg23/SMW-Stream-Tracker/releases/download/v',
    [switch]$SkipAppBuild
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $projectRoot 'dist'
$appExe = Join-Path $dist 'SMWStreamTracker.exe'
$setupExe = Join-Path $dist "SMWStreamTracker_Setup_$Version.exe"
$updaterExe = Join-Path $dist "SMWStreamTracker_Update_$Version.exe"
$sourceZip = Join-Path $dist "SMWStreamTracker_Desktop_${Version}_Source.zip"
$checksumsPath = Join-Path $dist "SHA256SUMS_$Version.txt"
$manifestPath = Join-Path $PSScriptRoot 'update_manifest.json'
$releaseNotesPath = Join-Path $PSScriptRoot 'RELEASE_NOTES.txt'
$runtimeRoot = Join-Path $dist 'runtime'

function Confirm-UnsignedArtifact([string]$Path) {
    $signature = Get-AuthenticodeSignature -LiteralPath $Path
    if ($signature.Status -ne 'NotSigned') {
        throw "Expected an unsigned artifact, but $Path has signature status $($signature.Status)."
    }
}

function Confirm-AppStartup([string]$Path) {
    $probeRoot = Join-Path $env:TEMP ("SMWStreamTracker-StartupProbe-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $probeRoot | Out-Null
    $previousLocalAppData = $env:LOCALAPPDATA
    try {
        $env:LOCALAPPDATA = $probeRoot
        $process = Start-Process -FilePath $Path -ArgumentList '--startup-check' -Wait -PassThru
        if ($process.ExitCode -ne 0) {
            throw "The packaged app failed its Tcl/Tk startup check with exit code $($process.ExitCode)."
        }
    }
    finally {
        $env:LOCALAPPDATA = $previousLocalAppData
        if (Test-Path -LiteralPath $probeRoot) {
            Remove-Item -LiteralPath $probeRoot -Recurse -Force
        }
    }
}

function Test-BuildPython([string]$PythonPath) {
    if (-not $PythonPath -or -not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
        return $false
    }
    & $PythonPath -c "import tkinter as tk; root=tk.Tk(); root.withdraw(); root.update_idletasks(); root.destroy()" 2>$null
    return $LASTEXITCODE -eq 0
}

function Resolve-BuildPython {
    $candidates = New-Object System.Collections.Generic.List[string]
    if ($env:SMW_BUILD_PYTHON) {
        $candidates.Add($env:SMW_BUILD_PYTHON)
    }

    # Prefer a normal python.org installation. The Windows embeddable/portable
    # distribution does not include a supported Tcl/Tk installation and can
    # produce an app that builds successfully but fails before its first window.
    $localPythonRoot = Join-Path $env:LOCALAPPDATA 'Programs\Python'
    if (Test-Path -LiteralPath $localPythonRoot) {
        Get-ChildItem -LiteralPath $localPythonRoot -Directory -Filter 'Python*' |
            Sort-Object Name -Descending |
            ForEach-Object {
                $candidates.Add((Join-Path $_.FullName 'python.exe'))
            }
    }
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $candidates.Add($pythonCommand.Source)
    }

    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (Test-BuildPython $candidate) {
            return $candidate
        }
    }
    throw 'No Python installation with a working Tcl/Tk runtime was found. Install standard Python from python.org or set SMW_BUILD_PYTHON to its full path.'
}

function Stage-TclTkRuntime([string]$PythonPath) {
    $pythonRoot = (& $PythonPath -c "import sys; print(sys.base_prefix)").Trim()
    if ($LASTEXITCODE -ne 0 -or -not $pythonRoot) {
        throw 'Could not determine the selected Python runtime folder.'
    }
    $pythonTclRoot = Join-Path $pythonRoot 'tcl'
    $tclScriptRoot = Get-ChildItem -LiteralPath $pythonTclRoot -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'init.tcl') } |
        Select-Object -First 1
    $tkScriptRoot = Get-ChildItem -LiteralPath $pythonTclRoot -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'tk.tcl') } |
        Select-Object -First 1
    if (-not $tclScriptRoot -or -not $tkScriptRoot) {
        throw "Could not locate Tcl/Tk script libraries below $pythonTclRoot."
    }

    if (Test-Path -LiteralPath $runtimeRoot) {
        Remove-Item -LiteralPath $runtimeRoot -Recurse -Force
    }
    $runtimeTcl = Join-Path $runtimeRoot 'tcl'
    $runtimeTk = Join-Path $runtimeRoot 'tk'
    New-Item -ItemType Directory -Force -Path $runtimeTcl, $runtimeTk | Out-Null
    Copy-Item -Path (Join-Path $tclScriptRoot.FullName '*') -Destination $runtimeTcl -Recurse -Force
    Copy-Item -Path (Join-Path $tkScriptRoot.FullName '*') -Destination $runtimeTk -Recurse -Force

    $stagedInitTcl = Join-Path $runtimeTcl 'init.tcl'
    $stagedTkTcl = Join-Path $runtimeTk 'tk.tcl'
    if (-not (Test-Path -LiteralPath $stagedInitTcl) -or
        -not (Test-Path -LiteralPath $stagedTkTcl)) {
        throw 'The permanent Tcl/Tk runtime fallback was not staged correctly.'
    }

    # Remove any old local-only Tcl diagnostic block before packaging.
    $initTclText = [System.IO.File]::ReadAllText($stagedInitTcl)
    $diagnosticPattern = '(?m)^[ \t]*set __smw_tcl_log.*\r?\n^[ \t]*puts \$__smw_tcl_log.*\r?\n^[ \t]*close \$__smw_tcl_log.*\r?\n^[ \t]*unset __smw_tcl_log[ \t]*\r?\n'
    $initTclText = [System.Text.RegularExpressions.Regex]::Replace(
        $initTclText,
        $diagnosticPattern,
        ''
    )
    $utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($stagedInitTcl, $initTclText, $utf8WithoutBom)
    if ($initTclText -match '__smw_tcl_log|tcl-init-log|C:/Users/|C:\\Users\\') {
        throw 'The staged Tcl startup file contains a local diagnostic or user-specific Windows path.'
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
    $pythonPath = Resolve-BuildPython
    Stage-TclTkRuntime $pythonPath
    & $pythonPath -c "from PIL import Image; print('Pillow ' + Image.__version__ + ' from ' + Image.__file__)"
    if ($LASTEXITCODE -ne 0) {
        throw 'The selected Python environment cannot load Pillow. Install a Pillow build that matches this Python version before packaging.'
    }
    & $pythonPath -c "from importlib.metadata import version; import webview, clr; print('pywebview ' + version('pywebview') + ' with pythonnet ' + version('pythonnet'))"
    if ($LASTEXITCODE -ne 0) {
        throw 'The selected Python environment cannot load pywebview and pythonnet. Install the Windows release requirements before packaging.'
    }
    & $pythonPath -m PyInstaller --noconfirm --clean (Join-Path $projectRoot 'SMWStreamTracker.spec')
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
}

if (-not $pythonPath) {
    $pythonPath = Resolve-BuildPython
    Stage-TclTkRuntime $pythonPath
}
if (-not (Test-Path -LiteralPath $appExe -PathType Leaf)) {
    throw "App executable was not found: $appExe"
}

Confirm-AppStartup $appExe
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
$manifestJson = $manifest | ConvertTo-Json -Depth 5
$utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText(
    $manifestPath,
    $manifestJson + [Environment]::NewLine,
    $utf8WithoutBom
)

$sourceItems = @(
    '.gitignore',
    'LICENSE.txt',
    'README.md',
    'SMWStreamTracker.spec',
    'SMWStreamTrackerLauncher.py',
    'SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py',
    'app_assets',
    'banner_background_assets',
    'banner_character_assets',
    'banner_character_assets_user',
    'banner_element_assets',
    'banner_foreground_assets',
    'banner_title_assets',
    'build_helpers',
    'build_tracker_icons.py',
    'create_bowser_fixed_flame_overlay.py',
    'create_bowser_uncropped_fixed_flame_overlay.py',
    'docs',
    'fix_toadette_hair_circles.py',
    'installer',
    'platform_assets',
    'prepare_user_banner_characters.py',
    'preview_consistent_ground_shadows.py',
    'release',
    'release_tools',
    'render_banner_qa.py',
    'tests',
    'version_info.txt'
) | ForEach-Object { Join-Path $projectRoot $_ }
if (Test-Path -LiteralPath $sourceZip) {
    Remove-Item -LiteralPath $sourceZip -Force
}
$sourceStaging = Join-Path $dist "source-staging-$Version"
if (Test-Path -LiteralPath $sourceStaging) {
    Remove-Item -LiteralPath $sourceStaging -Recurse -Force
}
New-Item -ItemType Directory -Path $sourceStaging | Out-Null
foreach ($sourceItem in $sourceItems) {
    Copy-Item -LiteralPath $sourceItem -Destination $sourceStaging -Recurse -Force
}
Get-ChildItem -LiteralPath $sourceStaging -Directory -Recurse -Force |
    Where-Object { $_.Name -eq '__pycache__' } |
    Remove-Item -Recurse -Force
Get-ChildItem -LiteralPath $sourceStaging -File -Recurse -Force -Filter '*.pyc' |
    Remove-Item -Force
Compress-Archive -Path (Join-Path $sourceStaging '*') -DestinationPath $sourceZip -CompressionLevel Optimal
Remove-Item -LiteralPath $sourceStaging -Recurse -Force

$checksumLines = @($appExe, $setupExe, $updaterExe, $sourceZip) | ForEach-Object {
    $artifactHash = (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()
    "$artifactHash  $(Split-Path -Leaf $_)"
}
$checksumLines | Set-Content -LiteralPath $checksumsPath -Encoding ascii

Write-Host ''
Write-Host "Unsigned release $Version is ready."
Write-Host "App:       $appExe"
Write-Host "Installer: $setupExe"
Write-Host "Updater:   $updaterExe"
Write-Host "Source:    $sourceZip"
Write-Host "Checksums: $checksumsPath"
Write-Host "Manifest:  $manifestPath"
