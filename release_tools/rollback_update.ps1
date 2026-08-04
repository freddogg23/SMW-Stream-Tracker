param(
    [Parameter(Mandatory = $true)][string]$CurrentExe,
    [Parameter(Mandatory = $true)][string]$BackupExe,
    [Parameter(Mandatory = $true)][int]$ProcessId,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string]$ExpectedSha256
)

$ErrorActionPreference = 'Stop'
$rollbackRoot = Join-Path $env:LOCALAPPDATA 'SMWStreamTracker\Rollback'
$logPath = Join-Path $rollbackRoot 'rollback.log'
New-Item -ItemType Directory -Force -Path $rollbackRoot | Out-Null

try {
    try {
        Wait-Process -Id $ProcessId -Timeout 30 -ErrorAction Stop
    }
    catch {
        Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 750
    }

    if (-not (Test-Path -LiteralPath $BackupExe -PathType Leaf)) {
        throw 'The previous executable is missing.'
    }

    $backupHash = (Get-FileHash -LiteralPath $BackupExe -Algorithm SHA256).Hash
    if ($backupHash -ine $ExpectedSha256) {
        throw 'The previous executable failed its SHA-256 integrity check.'
    }

    if (Test-Path -LiteralPath $CurrentExe -PathType Leaf) {
        $failedCopy = Join-Path $rollbackRoot 'SMWStreamTracker_replaced.exe'
        Copy-Item -LiteralPath $CurrentExe -Destination $failedCopy -Force
    }
    Copy-Item -LiteralPath $BackupExe -Destination $CurrentExe -Force
    "$(Get-Date -Format o) Restored $BackupExe" | Set-Content -LiteralPath $logPath
    Start-Process -FilePath $CurrentExe
}
catch {
    "$(Get-Date -Format o) Rollback failed: $($_.Exception.Message)" | Set-Content -LiteralPath $logPath
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show(
        "SMW Stream Tracker could not restore the previous version.`n`n$($_.Exception.Message)`n`nDetails: $logPath",
        'Rollback Failed',
        'OK',
        'Error'
    ) | Out-Null
    exit 1
}
