param(
    [Parameter(Mandatory = $true)]
    [string]$StreamerBotDirectory,

    [Parameter(Mandatory = $true)]
    [string]$EventFile,

    [switch]$SkipProcessCheck
)

$ErrorActionPreference = "Stop"

function Assert-ChildPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Parent,
        [Parameter(Mandatory = $true)]
        [string]$Child
    )

    $parentPath = [IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
    $childPath = [IO.Path]::GetFullPath($Child)
    if (-not $childPath.StartsWith($parentPath, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify a path outside the selected Streamer.bot folder: $childPath"
    }
}

function New-Id {
    return [Guid]::NewGuid().ToString()
}

function New-Branch {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Type,
        [Parameter(Mandatory = $true)]
        [int]$Index,
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [object[]]$Children
    )

    $branchId = New-Id
    for ($childIndex = 0; $childIndex -lt $Children.Count; $childIndex++) {
        $Children[$childIndex].parentId = $branchId
        $Children[$childIndex].index = $childIndex
    }

    return [pscustomobject][ordered]@{
        random = $false
        subActions = @($Children)
        id = $branchId
        weight = 0.0
        type = $Type
        parentId = $null
        enabled = $true
        index = $Index
    }
}

function New-IfAction {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ExpectedValue,
        [Parameter(Mandatory = $true)]
        [pscustomobject]$TrueChild,
        [Parameter(Mandatory = $true)]
        [int]$Index
    )

    $trueBranch = New-Branch -Type 99901 -Index 0 -Children @($TrueChild)
    $falseBranch = New-Branch -Type 99902 -Index 1 -Children @()

    return [pscustomobject][ordered]@{
        input = "%smwCommand%"
        operation = 0
        value = $ExpectedValue
        autoType = $true
        subActions = @($trueBranch, $falseBranch)
        id = New-Id
        weight = 0.0
        type = 120
        parentId = $null
        enabled = $true
        index = $Index
    }
}

function Write-JsonAtomically {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [object]$Value
    )

    $json = $Value | ConvertTo-Json -Depth 100 -Compress
    $null = $json | ConvertFrom-Json
    $temporaryPath = "$Path.codex.tmp"
    [IO.File]::WriteAllText(
        $temporaryPath,
        $json,
        [Text.UTF8Encoding]::new($false)
    )
    Move-Item -LiteralPath $temporaryPath -Destination $Path -Force
}

$streamerBotRoot = [IO.Path]::GetFullPath($StreamerBotDirectory)
$dataDirectory = Join-Path $streamerBotRoot "data"
$settingsPath = Join-Path $dataDirectory "settings.json"
$actionsPath = Join-Path $dataDirectory "actions.json"
$eventPath = [IO.Path]::GetFullPath($EventFile)

Assert-ChildPath -Parent $streamerBotRoot -Child $settingsPath
Assert-ChildPath -Parent $streamerBotRoot -Child $actionsPath

if (-not (Test-Path -LiteralPath $settingsPath -PathType Leaf)) {
    throw "Streamer.bot settings were not found: $settingsPath"
}
if (-not (Test-Path -LiteralPath $actionsPath -PathType Leaf)) {
    throw "Streamer.bot actions were not found: $actionsPath"
}
if (-not (Test-Path -LiteralPath $eventPath -PathType Leaf)) {
    throw "The tracker event file was not found: $eventPath"
}

if (-not $SkipProcessCheck) {
    $runningInstances = @(
        Get-Process -Name "Streamer.bot" -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Path -and
                ([IO.Path]::GetFullPath($_.Path)).StartsWith(
                    $streamerBotRoot.TrimEnd('\') + '\',
                    [StringComparison]::OrdinalIgnoreCase
                )
            }
    )
    if ($runningInstances.Count -gt 0) {
        throw "Close Streamer.bot completely before installing the prediction action."
    }
}

$settings = Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8 |
    ConvertFrom-Json
$actions = Get-Content -LiteralPath $actionsPath -Raw -Encoding UTF8 |
    ConvertFrom-Json

$tailId = "1c490834-71d7-46ed-aaf6-28aad4d73cd1"
$tailName = "SMW Stream Tracker Level Events"
$actionId = "df35192d-c53b-47f8-bc60-5ce93f3a07f4"
$actionName = "SMW Tracker - Automatic Level Predictions"
$groupName = "SMW Stream Tracker"

$settings.fileTails.fileTails = @(
    @($settings.fileTails.fileTails) |
        Where-Object {
            $_.id -ne $tailId -and $_.name -ne $tailName
        }
)
$settings.fileTails.fileTails += [pscustomobject][ordered]@{
    id = $tailId
    name = $tailName
    enabled = $true
    filePath = $eventPath
}

$processorCode = @'
using System;
using System.Text;

public class CPHInline
{
    private const string Prefix = "smwTrackerPrediction.";

    public bool Execute()
    {
        CPH.SetArgument("smwCommand", "none");

        string line;
        if (!CPH.TryGetArg("line", out line) || String.IsNullOrWhiteSpace(line))
            return true;

        string[] fields = line.Split('|');
        if (fields.Length < 10 || fields[0] != "SMWTRACKER" || fields[1] != "1")
            return true;

        string eventId = fields[2];
        string eventName = fields[3].ToLowerInvariant();
        string sessionId = fields[4];
        string hackTitle = Decode(fields[5]);
        int levelId = ParseInt(fields[6], -1);
        int levelDeaths = Math.Max(0, ParseInt(fields[7], 0));
        string language = fields[9];

        string previousEventId = CPH.GetGlobalVar<string>(Prefix + "lastEventId", false);
        if (eventId == previousEventId)
            return true;
        CPH.SetGlobalVar(Prefix + "lastEventId", eventId, false);

        string activeSession = CPH.GetGlobalVar<string>(Prefix + "sessionId", false);
        bool predictionOpen = CPH.GetGlobalVar<bool>(Prefix + "open", false);
        int startingDeaths = CPH.GetGlobalVar<int>(Prefix + "startingDeaths", false);
        int lifeTarget = CPH.GetGlobalVar<int>(Prefix + "lifeTarget", false);

        if (eventName == "start")
        {
            int completedLevels = Math.Max(
                0,
                CPH.GetGlobalVar<int>(Prefix + "completedLevels", false)
            );
            int totalLivesUsed = Math.Max(
                0,
                CPH.GetGlobalVar<int>(Prefix + "totalLivesUsed", false)
            );

            lifeTarget = completedLevels == 0
                ? 100
                : Math.Max(
                    1,
                    (int)Math.Round(
                        totalLivesUsed / (double)completedLevels,
                        MidpointRounding.AwayFromZero
                    )
                );

            CPH.SetGlobalVar(Prefix + "sessionId", sessionId, false);
            CPH.SetGlobalVar(Prefix + "open", true, false);
            CPH.SetGlobalVar(Prefix + "startingDeaths", levelDeaths, false);
            CPH.SetGlobalVar(Prefix + "lifeTarget", lifeTarget, false);

            CPH.SetArgument("smwCommand", "start");
            CPH.SetArgument("smwPredictionTitle", PredictionTitle(language, lifeTarget));
            CPH.SetArgument("smwYesOutcome", YesOutcome(language));
            CPH.SetArgument("smwNoOutcome", NoOutcome(language));
            CPH.SetArgument("smwLifeTarget", lifeTarget);
            CPH.SetArgument("smwHackTitle", hackTitle);
            CPH.SetArgument("smwLevelId", levelId);
            return true;
        }

        if (sessionId != activeSession)
            return true;

        int deathsThisAttempt = Math.Max(0, levelDeaths - startingDeaths);
        CPH.SetArgument("smwLifeTarget", lifeTarget);
        CPH.SetArgument("smwLivesUsed", deathsThisAttempt + 1);
        CPH.SetArgument("smwHackTitle", hackTitle);
        CPH.SetArgument("smwLevelId", levelId);

        if (eventName == "death")
        {
            if (predictionOpen && deathsThisAttempt >= lifeTarget)
            {
                CPH.SetArgument("smwCommand", "resolve");
                CPH.SetArgument("smwWinningIndex", "1");
                CPH.SetGlobalVar(Prefix + "open", false, false);
            }
            return true;
        }

        if (eventName == "clear")
        {
            int completedLevels = Math.Max(
                0,
                CPH.GetGlobalVar<int>(Prefix + "completedLevels", false)
            );
            int totalLivesUsed = Math.Max(
                0,
                CPH.GetGlobalVar<int>(Prefix + "totalLivesUsed", false)
            );

            completedLevels += 1;
            totalLivesUsed += deathsThisAttempt + 1;
            CPH.SetGlobalVar(Prefix + "completedLevels", completedLevels, false);
            CPH.SetGlobalVar(Prefix + "totalLivesUsed", totalLivesUsed, false);

            if (predictionOpen)
            {
                CPH.SetArgument("smwCommand", "resolve");
                CPH.SetArgument(
                    "smwWinningIndex",
                    deathsThisAttempt < lifeTarget ? "0" : "1"
                );
            }

            CPH.SetGlobalVar(Prefix + "open", false, false);
            CPH.SetGlobalVar(Prefix + "sessionId", "", false);
            return true;
        }

        if (eventName == "cancel")
        {
            if (predictionOpen)
                CPH.SetArgument("smwCommand", "cancel");
            CPH.SetGlobalVar(Prefix + "open", false, false);
            CPH.SetGlobalVar(Prefix + "sessionId", "", false);
        }

        return true;
    }

    private static int ParseInt(string value, int fallback)
    {
        int parsed;
        return Int32.TryParse(value, out parsed) ? parsed : fallback;
    }

    private static string Decode(string value)
    {
        try
        {
            return Encoding.UTF8.GetString(Convert.FromBase64String(value));
        }
        catch
        {
            return "";
        }
    }

    private static string PredictionTitle(string language, int target)
    {
        switch ((language ?? "en").ToLowerInvariant())
        {
            case "es":
                return "\u00bfSuperar\u00e9 este nivel en " + target + " vidas?";
            case "fr":
                return "Vais-je finir ce niveau en " + target + " vies maximum ?";
            case "de":
                return "Schaffe ich dieses Level in " + target + " Leben?";
            case "pt-br":
                return "Vou vencer esta fase em at\u00e9 " + target + " vidas?";
            case "au":
                return "Reckon I'll beat this level within " + target + " lives, mate?";
            default:
                return "Will I beat this level within " + target + " lives?";
        }
    }

    private static string YesOutcome(string language)
    {
        switch ((language ?? "en").ToLowerInvariant())
        {
            case "es": return "S\u00ed";
            case "fr": return "Oui";
            case "de": return "Ja";
            case "pt-br": return "Sim";
            case "au": return "Yeah, mate";
            default: return "Yes";
        }
    }

    private static string NoOutcome(string language)
    {
        switch ((language ?? "en").ToLowerInvariant())
        {
            case "es": return "No";
            case "fr": return "Non";
            case "de": return "Nein";
            case "pt-br": return "N\u00e3o";
            case "au": return "No chance";
            default: return "No";
        }
    }
}
'@

$processor = [pscustomobject][ordered]@{
    name = "SMW Level Prediction Processor"
    description = "Reads SMW Stream Tracker level events and prepares Twitch prediction variables."
    references = @()
    byteCode = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($processorCode))
    precompile = $true
    delayStart = $false
    saveResultToVariable = $false
    saveToVariable = $null
    id = "98cb79d3-5513-412c-b22a-4927b9727629"
    weight = 0.0
    type = 99999
    parentId = $null
    enabled = $true
    index = 0
}

$createPrediction = [pscustomobject][ordered]@{
    title = "%smwPredictionTitle%"
    predictionWindow = "60"
    outcomes = @("%smwYesOutcome%", "%smwNoOutcome%")
    id = New-Id
    weight = 0.0
    type = 568
    parentId = $null
    enabled = $true
    index = 0
}

$resolvePrediction = [pscustomobject][ordered]@{
    winningIndex = "%smwWinningIndex%"
    id = New-Id
    weight = 0.0
    type = 571
    parentId = $null
    enabled = $true
    index = 0
}

$cancelPrediction = [pscustomobject][ordered]@{
    id = New-Id
    weight = 0.0
    type = 569
    parentId = $null
    enabled = $true
    index = 0
}

$startIf = New-IfAction -ExpectedValue "start" -TrueChild $createPrediction -Index 1
$resolveIf = New-IfAction -ExpectedValue "resolve" -TrueChild $resolvePrediction -Index 2
$cancelIf = New-IfAction -ExpectedValue "cancel" -TrueChild $cancelPrediction -Index 3

$trigger = [pscustomobject][ordered]@{
    fileTailId = $tailId
    id = "758e82fb-ac0f-48c1-84cd-b4b13eb626d0"
    type = 511
    enabled = $true
    exclusions = @()
}

$predictionAction = [pscustomobject][ordered]@{
    id = $actionId
    queue = "00000000-0000-0000-0000-000000000000"
    enabled = $true
    excludeFromHistory = $false
    excludeFromPending = $false
    name = $actionName
    group = $groupName
    alwaysRun = $false
    randomAction = $false
    concurrent = $false
    triggers = @($trigger)
    subActions = @($processor, $startIf, $resolveIf, $cancelIf)
    collapsedGroups = @()
}

$actions.actions = @(
    @($actions.actions) |
        Where-Object {
            $_.id -ne $actionId -and $_.name -ne $actionName
        }
)
$actions.actions += $predictionAction
if (-not (@($actions.groups) -contains $groupName)) {
    $actions.groups += $groupName
}
$actions.t = [DateTimeOffset]::Now.ToString("o")

$backupDirectory = Join-Path (
    Join-Path $streamerBotRoot "backup"
) ("smw-predictions-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
New-Item -ItemType Directory -Path $backupDirectory -Force | Out-Null
Copy-Item -LiteralPath $settingsPath -Destination (
    Join-Path $backupDirectory "settings.json"
)
Copy-Item -LiteralPath $actionsPath -Destination (
    Join-Path $backupDirectory "actions.json"
)

Write-JsonAtomically -Path $settingsPath -Value $settings
Write-JsonAtomically -Path $actionsPath -Value $actions

$verifiedSettings = Get-Content -LiteralPath $settingsPath -Raw -Encoding UTF8 |
    ConvertFrom-Json
$verifiedActions = Get-Content -LiteralPath $actionsPath -Raw -Encoding UTF8 |
    ConvertFrom-Json

$tailMatches = @(
    $verifiedSettings.fileTails.fileTails |
        Where-Object {
            $_.id -eq $tailId -and
            $_.filePath -eq $eventPath -and
            $_.enabled
        }
)
$actionMatches = @(
    $verifiedActions.actions |
        Where-Object {
            $_.id -eq $actionId -and
            $_.name -eq $actionName -and
            $_.enabled
        }
)

if ($tailMatches.Count -ne 1 -or $actionMatches.Count -ne 1) {
    throw "Streamer.bot prediction installation could not be verified. Backups are in $backupDirectory"
}

[pscustomobject]@{
    Installed = $true
    FileTail = $tailName
    EventFile = $eventPath
    Action = $actionName
    BackupDirectory = $backupDirectory
}
