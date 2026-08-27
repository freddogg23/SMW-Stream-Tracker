param(
    [Parameter(Mandatory = $true)]
    [string]$RewardName,
    [Parameter(Mandatory = $true)]
    [int]$Cost,
    [Parameter(Mandatory = $true)]
    [int]$Cooldown,
    [string]$SceneName = 'SNES Scene'
)

$ErrorActionPreference = 'Stop'

function Write-SetupResult {
    param(
        [bool]$Ok,
        [string]$Status,
        [string]$Message,
        [bool]$Created = $false,
        [bool]$Updated = $false,
        [bool]$ActionsInstalled = $false,
        [string]$RewardActionId = '',
        [string]$VisibilityActionId = '',
        [string]$ReplyActionId = '',
        [string]$BackupPath = ''
    )
    [ordered]@{
        ok = $Ok
        status = $Status
        message = $Message
        created = $Created
        updated = $Updated
        rewardName = $RewardName
        cost = $Cost
        cooldown = $Cooldown
        sceneName = $SceneName
        actionsInstalled = $ActionsInstalled
        rewardActionId = $RewardActionId
        visibilityActionId = $VisibilityActionId
        replyActionId = $ReplyActionId
        backupPath = $BackupPath
    } | ConvertTo-Json -Compress | Write-Output
}

try {
    if ([string]::IsNullOrWhiteSpace($RewardName)) {
        throw 'The channel point reward name cannot be blank.'
    }
    if ($RewardName.Length -gt 45) {
        throw 'Twitch channel point reward names cannot exceed 45 characters.'
    }
    if ($Cost -lt 1 -or $Cost -gt 1000000) {
        throw 'The reward cost must be between 1 and 1,000,000 channel points.'
    }
    if ($Cooldown -lt 0 -or $Cooldown -gt 604800) {
        throw 'The global cooldown must be between 0 and 604,800 seconds.'
    }

    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class SMWTrackerNativeInput {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extraInfo);
}
'@

    $script:Root = [System.Windows.Automation.AutomationElement]::RootElement
    $script:TreeScopeDescendants = [System.Windows.Automation.TreeScope]::Descendants
    $script:TreeScopeChildren = [System.Windows.Automation.TreeScope]::Children
    $script:TrueCondition = [System.Windows.Automation.Condition]::TrueCondition

    function Find-Element {
        param(
            [System.Windows.Automation.AutomationElement]$Root,
            [System.Windows.Automation.AutomationProperty]$Property,
            [object]$Value,
            [int]$TimeoutMilliseconds = 0
        )
        $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMilliseconds)
        do {
            $condition = [System.Windows.Automation.PropertyCondition]::new(
                $Property,
                $Value
            )
            $element = $Root.FindFirst($script:TreeScopeDescendants, $condition)
            if ($null -ne $element) {
                return $element
            }
            Start-Sleep -Milliseconds 120
        } while ([DateTime]::UtcNow -lt $deadline)
        return $null
    }

    function Find-Named-Control {
        param(
            [System.Windows.Automation.AutomationElement]$Root,
            [System.Windows.Automation.ControlType]$ControlType,
            [string]$Name,
            [int]$TimeoutMilliseconds = 0
        )
        $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMilliseconds)
        do {
            $condition = [System.Windows.Automation.AndCondition]::new(
                ([System.Windows.Automation.PropertyCondition]::new(
                    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                    $ControlType
                )),
                ([System.Windows.Automation.PropertyCondition]::new(
                    [System.Windows.Automation.AutomationElement]::NameProperty,
                    $Name
                ))
            )
            $element = $Root.FindFirst($script:TreeScopeDescendants, $condition)
            if ($null -ne $element) {
                return $element
            }
            Start-Sleep -Milliseconds 120
        } while ([DateTime]::UtcNow -lt $deadline)
        return $null
    }

    function Invoke-Element {
        param([System.Windows.Automation.AutomationElement]$Element)
        if ($null -eq $Element) {
            return $false
        }
        $pattern = $null
        if ($Element.TryGetCurrentPattern(
            [System.Windows.Automation.SelectionItemPattern]::Pattern,
            [ref]$pattern
        )) {
            $pattern.Select()
            return $true
        }
        if ($Element.TryGetCurrentPattern(
            [System.Windows.Automation.InvokePattern]::Pattern,
            [ref]$pattern
        )) {
            $pattern.Invoke()
            return $true
        }
        return $false
    }

    function Set-ElementValue {
        param(
            [System.Windows.Automation.AutomationElement]$Element,
            [string]$Value
        )
        if ($null -eq $Element) {
            throw 'A required Streamer.bot reward field was not found.'
        }
        $pattern = $null
        if (-not $Element.TryGetCurrentPattern(
            [System.Windows.Automation.ValuePattern]::Pattern,
            [ref]$pattern
        )) {
            throw 'A required Streamer.bot reward field is not editable.'
        }
        $pattern.SetValue($Value)
    }

    function Set-ToggleState {
        param(
            [System.Windows.Automation.AutomationElement]$Element,
            [bool]$Enabled
        )
        if ($null -eq $Element) {
            return
        }
        $pattern = $null
        if ($Element.TryGetCurrentPattern(
            [System.Windows.Automation.TogglePattern]::Pattern,
            [ref]$pattern
        )) {
            $isOn = $pattern.Current.ToggleState -eq [System.Windows.Automation.ToggleState]::On
            if ($isOn -ne $Enabled) {
                $pattern.Toggle()
            }
        }
    }

    function Click-Element {
        param(
            [System.Windows.Automation.AutomationElement]$Element,
            [ValidateSet('Left', 'Right')]
            [string]$Button = 'Left',
            [int]$Count = 1
        )
        if ($null -eq $Element) {
            throw 'The Streamer.bot control could not be clicked.'
        }
        $rectangle = $Element.Current.BoundingRectangle
        if ($rectangle.IsEmpty) {
            throw 'The Streamer.bot control is not currently visible.'
        }
        $x = [int]($rectangle.Left + ($rectangle.Width / 2))
        $y = [int]($rectangle.Top + ($rectangle.Height / 2))
        [SMWTrackerNativeInput]::SetCursorPos($x, $y) | Out-Null
        if ($Button -eq 'Right') {
            $down = 0x0008
            $up = 0x0010
        }
        else {
            $down = 0x0002
            $up = 0x0004
        }
        for ($index = 0; $index -lt $Count; $index++) {
            [SMWTrackerNativeInput]::mouse_event($down, 0, 0, 0, [UIntPtr]::Zero)
            [SMWTrackerNativeInput]::mouse_event($up, 0, 0, 0, [UIntPtr]::Zero)
            if ($Count -gt 1) {
                Start-Sleep -Milliseconds 75
            }
        }
    }

    function Scroll-ElementIntoView {
        param([System.Windows.Automation.AutomationElement]$Element)
        if ($null -eq $Element) {
            return $false
        }
        $pattern = $null
        if ($Element.TryGetCurrentPattern(
            [System.Windows.Automation.ScrollItemPattern]::Pattern,
            [ref]$pattern
        )) {
            try {
                $pattern.ScrollIntoView()
                Start-Sleep -Milliseconds 180
                return $true
            }
            catch {
                return $false
            }
        }
        return $false
    }

    function Open-NamedNavigationTarget {
        param(
            [System.Windows.Automation.AutomationElement]$Root,
            [System.Windows.Automation.ControlType]$PreferredControlType,
            [string]$Name,
            [int]$TimeoutMilliseconds = 0
        )
        # Streamer.bot 1.0.x exposes its NavigationView entries as TabItems,
        # but some of those entries do not publish SelectionItemPattern or
        # InvokePattern. Its large navigation cards also expose the visible
        # label as a Text child instead of giving the parent Button a name.
        # Streamer.bot can leave Platforms below the visible part of the
        # navigation rail, and selecting that TabItem does not necessarily
        # expand its Twitch child. Bring it into view and physically click it
        # first. Retain UIA invocation as a fallback for layouts that do not
        # expose clickable geometry.
        $target = Find-Named-Control `
            -Root $Root `
            -ControlType $PreferredControlType `
            -Name $Name `
            -TimeoutMilliseconds $TimeoutMilliseconds
        if ($null -eq $target) {
            $target = Find-Named-Control `
                -Root $Root `
                -ControlType ([System.Windows.Automation.ControlType]::Text) `
                -Name $Name `
                -TimeoutMilliseconds $TimeoutMilliseconds
        }
        if ($null -eq $target) {
            return $false
        }
        Scroll-ElementIntoView -Element $target | Out-Null
        try {
            Click-Element -Element $target
            return $true
        }
        catch {
            return (Invoke-Element $target)
        }
    }

    function Reward-ItemMatches {
        param(
            [System.Windows.Automation.AutomationElement]$Item,
            [string]$Name
        )
        $textCondition = [System.Windows.Automation.PropertyCondition]::new(
            [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
            [System.Windows.Automation.ControlType]::Text
        )
        $textElements = $Item.FindAll($script:TreeScopeDescendants, $textCondition)
        foreach ($textElement in $textElements) {
            if ([string]::Equals(
                [string]$textElement.Current.Name,
                $Name,
                [System.StringComparison]::OrdinalIgnoreCase
            )) {
                return $true
            }
        }
        return $false
    }

    function Find-VisibleRewardItem {
        param(
            [System.Windows.Automation.AutomationElement]$Grid,
            [string]$Name
        )
        $itemCondition = [System.Windows.Automation.PropertyCondition]::new(
            [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
            [System.Windows.Automation.ControlType]::DataItem
        )
        $items = $Grid.FindAll($script:TreeScopeDescendants, $itemCondition)
        foreach ($item in $items) {
            if (Reward-ItemMatches -Item $item -Name $Name) {
                $rectangle = $item.Current.BoundingRectangle
                if (-not $item.Current.IsOffscreen -and -not $rectangle.IsEmpty) {
                    return $item
                }
            }
        }
        return $null
    }

    function Expand-RewardGroups {
        param(
            [System.Windows.Automation.AutomationElement]$Grid
        )
        $groupCondition = [System.Windows.Automation.PropertyCondition]::new(
            [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
            [System.Windows.Automation.ControlType]::Group
        )
        $itemCondition = [System.Windows.Automation.PropertyCondition]::new(
            [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
            [System.Windows.Automation.ControlType]::DataItem
        )
        $groups = $Grid.FindAll(
            $script:TreeScopeDescendants,
            $groupCondition
        )
        foreach ($group in $groups) {
            $expandPattern = $null
            if ($group.TryGetCurrentPattern(
                [System.Windows.Automation.ExpandCollapsePattern]::Pattern,
                [ref]$expandPattern
            )) {
                if (
                    $expandPattern.Current.ExpandCollapseState -eq
                    [System.Windows.Automation.ExpandCollapseState]::Collapsed
                ) {
                    $expandPattern.Expand()
                    Start-Sleep -Milliseconds 100
                }
                continue
            }

            # Streamer.bot 1.0.4 does not publish ExpandCollapsePattern for
            # every reward group. A collapsed group has no DataItem children,
            # so clicking only those headers expands it without collapsing
            # groups that are already open.
            $visibleItems = $group.FindAll(
                $script:TreeScopeDescendants,
                $itemCondition
            )
            if ($visibleItems.Count -eq 0) {
                try {
                    Click-Element -Element $group
                    Start-Sleep -Milliseconds 100
                }
                catch {
                }
            }
        }
    }

    function Find-RewardItem {
        param(
            [System.Windows.Automation.AutomationElement]$Grid,
            [string]$Name
        )
        $scrollPattern = $null
        $canScroll = $Grid.TryGetCurrentPattern(
            [System.Windows.Automation.ScrollPattern]::Pattern,
            [ref]$scrollPattern
        )
        if ($canScroll -and $scrollPattern.Current.VerticallyScrollable) {
            try {
                $scrollPattern.SetScrollPercent(
                    [System.Windows.Automation.ScrollPattern]::NoScroll,
                    0
                )
                Start-Sleep -Milliseconds 180
            }
            catch {
            }
        }
        for ($page = 0; $page -lt 80; $page++) {
            Expand-RewardGroups -Grid $Grid
            $item = Find-VisibleRewardItem -Grid $Grid -Name $Name
            if ($null -ne $item) {
                return $item
            }
            if (-not $canScroll -or -not $scrollPattern.Current.VerticallyScrollable) {
                break
            }
            $before = $scrollPattern.Current.VerticalScrollPercent
            if ($before -ge 99.5) {
                break
            }
            $scrollPattern.Scroll(
                [System.Windows.Automation.ScrollAmount]::NoAmount,
                [System.Windows.Automation.ScrollAmount]::LargeIncrement
            )
            Start-Sleep -Milliseconds 160
            if ($scrollPattern.Current.VerticalScrollPercent -le $before) {
                break
            }
        }
        return $null
    }

    $streamerProcess = Get-Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.MainWindowHandle -ne 0 -and
            $_.MainWindowTitle -like 'Streamer.bot -*'
        } |
        Select-Object -First 1
    if ($null -eq $streamerProcess) {
        throw 'Streamer.bot is not open. Open Streamer.bot, then run setup again.'
    }

    $streamerExe = [string]$streamerProcess.Path
    if ([string]::IsNullOrWhiteSpace($streamerExe)) {
        throw 'Could not locate the running Streamer.bot application.'
    }
    $streamerFolder = [System.IO.Path]::GetDirectoryName($streamerExe)
    $dataFolder = Join-Path $streamerFolder 'data'
    $rewardsPath = Join-Path $dataFolder 'twitch_rewards.json'
    $actionsPath = Join-Path $dataFolder 'actions.json'
    $obsPath = Join-Path $dataFolder 'obs.json'
    foreach ($requiredPath in @($rewardsPath, $actionsPath, $obsPath)) {
        if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
            throw "Streamer.bot's required data file is missing: $requiredPath"
        }
    }

    $rewardActionName = 'SMW Stream Tracker - Current Level Song Reward'
    $visibilityActionName = 'SMW Stream Tracker - Song Reward Scene Visibility'
    $replyActionName = 'SMW Stream Tracker - Post Current Level Song to Chat'
    $actionGroupName = 'SMW Stream Tracker'

    # Reuse an existing tracker-owned reward whenever one is already present.
    # Streamer.bot's navigation tree changes between releases and should not be
    # opened merely to repair or refresh the tracker Actions. A new reward still
    # uses Streamer.bot's editor so Twitch receives and owns the creation.
    $rewardDocument = Get-Content -LiteralPath $rewardsPath -Raw |
        ConvertFrom-Json
    $savedReward = @($rewardDocument.rewards) |
        Where-Object {
            [string]::Equals(
                [string]$_.name,
                $RewardName,
                [System.StringComparison]::OrdinalIgnoreCase
            )
        } |
        Select-Object -First 1
    $rewardId = if ($null -ne $savedReward) {
        [string]$savedReward.id
    }
    else {
        ''
    }
    $preflightActionsDocument = Get-Content -LiteralPath $actionsPath -Raw |
        ConvertFrom-Json
    $savedRewardAction = @($preflightActionsDocument.actions) |
        Where-Object {
            [string]::Equals(
                [string]$_.name,
                $rewardActionName,
                [System.StringComparison]::OrdinalIgnoreCase
            )
        } |
        Select-Object -First 1
    if ([string]::IsNullOrWhiteSpace($rewardId) -and $null -ne $savedRewardAction) {
        $installedRewardId = @($savedRewardAction.triggers) |
            ForEach-Object { [string]$_.rewardId } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
            Select-Object -First 1
        if (-not [string]::IsNullOrWhiteSpace($installedRewardId)) {
            $savedReward = @($rewardDocument.rewards) |
                Where-Object {
                    [string]::Equals(
                        [string]$_.id,
                        $installedRewardId,
                        [System.StringComparison]::OrdinalIgnoreCase
                    )
                } |
                Select-Object -First 1
            if ($null -ne $savedReward) {
                $rewardId = [string]$savedReward.id
            }
        }
    }
    $preflightActionNames = @(
        @($preflightActionsDocument.actions) | ForEach-Object {
            [string]$_.name
        }
    )
    $repairMissingReplyAction = (
        -not [string]::IsNullOrWhiteSpace($rewardId) -and
        $preflightActionNames -contains $rewardActionName -and
        $preflightActionNames -contains $visibilityActionName -and
        $preflightActionNames -notcontains $replyActionName
    )
    $hasExistingSongReward = -not [string]::IsNullOrWhiteSpace($rewardId)
    $created = $false
    $updated = $hasExistingSongReward

    if (-not $hasExistingSongReward) {
        [SMWTrackerNativeInput]::ShowWindowAsync(
            $streamerProcess.MainWindowHandle,
            9
        ) | Out-Null
        [SMWTrackerNativeInput]::SetForegroundWindow(
            $streamerProcess.MainWindowHandle
        ) | Out-Null
        Start-Sleep -Milliseconds 250

        $mainWindow = [System.Windows.Automation.AutomationElement]::FromHandle(
            $streamerProcess.MainWindowHandle
        )
        $rewardGrid = Find-Element `
            -Root $mainWindow `
            -Property ([System.Windows.Automation.AutomationElement]::AutomationIdProperty) `
            -Value 'TwitchRewardsList'

    if ($null -eq $rewardGrid) {
        if (-not (Open-NamedNavigationTarget `
            -Root $mainWindow `
            -PreferredControlType ([System.Windows.Automation.ControlType]::TabItem) `
            -Name 'Platforms' `
            -TimeoutMilliseconds 6000)) {
            throw 'Could not open Platforms in Streamer.bot.'
        }
        Start-Sleep -Milliseconds 900
        if (-not (Open-NamedNavigationTarget `
            -Root $mainWindow `
            -PreferredControlType ([System.Windows.Automation.ControlType]::TabItem) `
            -Name 'Twitch' `
            -TimeoutMilliseconds 8000)) {
            throw 'Could not open Twitch in Streamer.bot.'
        }
        Start-Sleep -Milliseconds 900
        if (-not (Open-NamedNavigationTarget `
            -Root $mainWindow `
            -PreferredControlType ([System.Windows.Automation.ControlType]::Button) `
            -Name 'Channel Point Rewards' `
            -TimeoutMilliseconds 8000)) {
            throw 'Could not open Channel Point Rewards in Streamer.bot.'
        }
        $rewardGrid = Find-Element `
            -Root $mainWindow `
            -Property ([System.Windows.Automation.AutomationElement]::AutomationIdProperty) `
            -Value 'TwitchRewardsList' `
            -TimeoutMilliseconds 6000
    }
    if ($null -eq $rewardGrid) {
        throw 'Streamer.bot did not expose its Channel Point Rewards list.'
    }

        $rewardItem = Find-RewardItem -Grid $rewardGrid -Name $RewardName
    if ($null -ne $rewardItem) {
        Click-Element -Element $rewardItem -Button 'Right'
        $editMenuItem = Find-Named-Control `
            -Root $script:Root `
            -ControlType ([System.Windows.Automation.ControlType]::MenuItem) `
            -Name 'Edit' `
            -TimeoutMilliseconds 3000
        if ($null -eq $editMenuItem) {
            throw "Could not open Streamer.bot's Edit reward command."
        }
        if (-not (Invoke-Element $editMenuItem)) {
            Click-Element -Element $editMenuItem
        }
        $editorTitle = 'Edit Twitch Channel Reward'
        $updated = $true
    }
    else {
        Click-Element -Element $rewardGrid -Button 'Right'
        $createMenuItem = Find-Named-Control `
            -Root $script:Root `
            -ControlType ([System.Windows.Automation.ControlType]::MenuItem) `
            -Name 'Create Reward' `
            -TimeoutMilliseconds 3000
        if ($null -eq $createMenuItem) {
            throw "Could not open Streamer.bot's Create Reward command."
        }
        if (-not (Invoke-Element $createMenuItem)) {
            Click-Element -Element $createMenuItem
        }
        $editorTitle = 'Add Twitch Channel Reward'
        $created = $true
    }

    $editor = Find-Named-Control `
        -Root $script:Root `
        -ControlType ([System.Windows.Automation.ControlType]::Window) `
        -Name $editorTitle `
        -TimeoutMilliseconds 6000
    if ($null -eq $editor) {
        throw "Streamer.bot did not open the $editorTitle window."
    }

    $editCondition = [System.Windows.Automation.PropertyCondition]::new(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    )
    $editFields = $editor.FindAll($script:TreeScopeDescendants, $editCondition)
    if ($editFields.Count -lt 8) {
        throw 'Streamer.bot returned an incomplete channel point reward form.'
    }
    Set-ElementValue -Element $editFields.Item(0) -Value $RewardName
    Set-ElementValue -Element $editFields.Item(1) -Value (
        "Posts the identified song and SMW Central link for the level " +
        "currently playing on $SceneName."
    )
    if ($created) {
        Set-ElementValue -Element $editFields.Item(2) -Value '#69D893'
    }
    Set-ElementValue -Element $editFields.Item(3) -Value ([string]$Cost)
    Set-ElementValue -Element $editFields.Item(6) -Value ([string]$Cooldown)
    Set-ElementValue -Element $editFields.Item(7) -Value 'SMW Stream Tracker'

    Set-ToggleState `
        -Element (Find-Named-Control `
            -Root $editor `
            -ControlType ([System.Windows.Automation.ControlType]::Button) `
            -Name 'Enabled') `
        -Enabled $true
    Set-ToggleState `
        -Element (Find-Named-Control `
            -Root $editor `
            -ControlType ([System.Windows.Automation.ControlType]::Button) `
            -Name 'Paused') `
        -Enabled $false
    Set-ToggleState `
        -Element (Find-Named-Control `
            -Root $editor `
            -ControlType ([System.Windows.Automation.ControlType]::Button) `
            -Name 'User Input Required') `
        -Enabled $false
    Set-ToggleState `
        -Element (Find-Named-Control `
            -Root $editor `
            -ControlType ([System.Windows.Automation.ControlType]::Button) `
            -Name 'Redemption Skips Queue') `
        -Enabled $false

    Start-Sleep -Milliseconds 300
    $commitName = if ($created) { 'Create' } else { 'Save' }
    $commitButton = Find-Named-Control `
        -Root $editor `
        -ControlType ([System.Windows.Automation.ControlType]::Button) `
        -Name $commitName `
        -TimeoutMilliseconds 2000
    if (-not (Invoke-Element $commitButton)) {
        throw "Could not select $commitName in Streamer.bot."
    }

    $deadline = [DateTime]::UtcNow.AddSeconds(12)
    do {
        Start-Sleep -Milliseconds 180
        $stillOpen = Find-Named-Control `
            -Root $script:Root `
            -ControlType ([System.Windows.Automation.ControlType]::Window) `
            -Name $editorTitle
    } while ($null -ne $stillOpen -and [DateTime]::UtcNow -lt $deadline)
        if ($null -ne $stillOpen) {
            throw 'Streamer.bot did not finish saving the Twitch reward.'
        }
    }

    $rewardDeadline = [DateTime]::UtcNow.AddSeconds(10)
    do {
        Start-Sleep -Milliseconds 180
        try {
            $rewardDocument = Get-Content -LiteralPath $rewardsPath -Raw |
                ConvertFrom-Json
            $savedReward = @($rewardDocument.rewards) |
                Where-Object {
                    [string]::Equals(
                        [string]$_.name,
                        $RewardName,
                        [System.StringComparison]::OrdinalIgnoreCase
                    )
                } |
                Select-Object -First 1
            if ($null -ne $savedReward) {
                $rewardId = [string]$savedReward.id
            }
        }
        catch {
            $rewardId = ''
        }
    } while (
        [string]::IsNullOrWhiteSpace($rewardId) -and
        [DateTime]::UtcNow -lt $rewardDeadline
    )
    if ([string]::IsNullOrWhiteSpace($rewardId)) {
        throw 'Streamer.bot saved the reward, but its reward ID could not be found.'
    }

    $obsDocument = Get-Content -LiteralPath $obsPath -Raw | ConvertFrom-Json
    $obsConnection = @($obsDocument.connections) |
        Where-Object { $_.default -eq $true } |
        Select-Object -First 1
    if ($null -eq $obsConnection) {
        $obsConnection = @($obsDocument.connections) | Select-Object -First 1
    }
    $obsId = if ($null -ne $obsConnection) {
        [string]$obsConnection.id
    }
    else {
        ''
    }
    if ([string]::IsNullOrWhiteSpace($obsId)) {
        throw 'Add and connect OBS Studio in Streamer.bot before setting up the song reward.'
    }

    # Streamer.bot keeps Actions in memory, so close it before replacing the
    # actions document. The reward editor has already finished and the saved
    # reward ID above confirms its data reached disk.
    $null = $streamerProcess.CloseMainWindow()
    if (-not $streamerProcess.WaitForExit(7000)) {
        Stop-Process -Id $streamerProcess.Id -Force
        $streamerProcess.WaitForExit(5000) | Out-Null
    }

    $actionsDocument = Get-Content -LiteralPath $actionsPath -Raw |
        ConvertFrom-Json
    $existingActions = @($actionsDocument.actions)
    $keptActions = @(
        $existingActions | Where-Object {
            [string]$_.name -notin @(
                $rewardActionName,
                $visibilityActionName,
                $replyActionName
            )
        }
    )

    $rewardActionId = [guid]::NewGuid().ToString()
    $rewardTriggerId = [guid]::NewGuid().ToString()
    $fulfillId = [guid]::NewGuid().ToString()
    $rewardAction = [ordered]@{
        id = $rewardActionId
        queue = $null
        enabled = $true
        excludeFromHistory = $false
        excludeFromPending = $false
        name = $rewardActionName
        group = $actionGroupName
        alwaysRun = $true
        randomAction = $false
        concurrent = $false
        triggers = @(
            [ordered]@{
                rewardId = $rewardId
                id = $rewardTriggerId
                type = 112
                enabled = $true
                exclusions = @()
            }
        )
        subActions = @(
            [ordered]@{
                status = 1
                id = $fulfillId
                weight = 0.0
                type = 11
                parentId = $null
                enabled = $true
                index = 0
            }
        )
        collapsedGroups = @()
    }

    $visibilityActionId = [guid]::NewGuid().ToString()
    $sceneTriggerId = [guid]::NewGuid().ToString()
    $getSceneId = [guid]::NewGuid().ToString()
    $conditionId = [guid]::NewGuid().ToString()
    $trueGroupId = [guid]::NewGuid().ToString()
    $falseGroupId = [guid]::NewGuid().ToString()
    $enableRewardId = [guid]::NewGuid().ToString()
    $disableRewardId = [guid]::NewGuid().ToString()
    $visibilityAction = [ordered]@{
        id = $visibilityActionId
        queue = $null
        enabled = $true
        excludeFromHistory = $false
        excludeFromPending = $false
        name = $visibilityActionName
        group = $actionGroupName
        alwaysRun = $true
        randomAction = $false
        concurrent = $false
        triggers = @(
            [ordered]@{
                sceneName = ''
                obsId = $obsId
                id = $sceneTriggerId
                type = 14004
                enabled = $true
                exclusions = @()
            }
        )
        subActions = @(
            [ordered]@{
                connectionId = $obsId
                id = $getSceneId
                weight = 0.0
                type = 43
                parentId = $null
                enabled = $true
                index = 0
            },
            [ordered]@{
                input = '%currentScene%'
                operation = 0
                value = $SceneName
                autoType = $false
                subActions = @(
                    [ordered]@{
                        random = $false
                        subActions = @(
                            [ordered]@{
                                rewardId = $rewardId
                                state = 0
                                id = $enableRewardId
                                weight = 0.0
                                type = 200
                                parentId = $trueGroupId
                                enabled = $true
                                index = 0
                            }
                        )
                        id = $trueGroupId
                        weight = 0.0
                        type = 99901
                        parentId = $conditionId
                        enabled = $true
                        index = 0
                    },
                    [ordered]@{
                        random = $false
                        subActions = @(
                            [ordered]@{
                                rewardId = $rewardId
                                state = 1
                                id = $disableRewardId
                                weight = 0.0
                                type = 200
                                parentId = $falseGroupId
                                enabled = $true
                                index = 0
                            }
                        )
                        id = $falseGroupId
                        weight = 0.0
                        type = 99902
                        parentId = $conditionId
                        enabled = $true
                        index = 1
                    }
                )
                id = $conditionId
                weight = 0.0
                type = 120
                parentId = $null
                enabled = $true
                index = 1
            }
        )
        collapsedGroups = @()
    }

    # The WebSocket SendMessage request is privileged and requires WebSocket
    # authentication even when ordinary event subscriptions do not. Install a
    # normal Streamer.bot Action for the tracker to call with DoAction instead.
    # Streamer.bot then posts %chatMessage% using its already-connected Twitch
    # account, with broadcaster fallback when no separate bot account is set.
    $replyActionId = [guid]::NewGuid().ToString()
    $replySubActionId = [guid]::NewGuid().ToString()
    $replyAction = [ordered]@{
        id = $replyActionId
        queue = $null
        enabled = $true
        excludeFromHistory = $false
        excludeFromPending = $false
        name = $replyActionName
        group = $actionGroupName
        alwaysRun = $true
        randomAction = $false
        concurrent = $false
        triggers = @()
        subActions = @(
            [ordered]@{
                text = '%chatMessage%'
                useBot = $true
                fallback = $true
                id = $replySubActionId
                weight = 0.0
                type = 10
                parentId = $null
                enabled = $true
                index = 0
            }
        )
        collapsedGroups = @()
    }

    $actionsDocument.actions = @(
        $keptActions + @($rewardAction, $visibilityAction, $replyAction)
    )
    $groups = @($actionsDocument.groups)
    if ($groups -notcontains $actionGroupName) {
        $actionsDocument.groups = @($groups + $actionGroupName)
    }
    $backupPath = $actionsPath + '.smw-stream-tracker-backup'
    Copy-Item -LiteralPath $actionsPath -Destination $backupPath -Force
    $actionsJson = $actionsDocument | ConvertTo-Json -Depth 100
    $utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText(
        $actionsPath,
        $actionsJson,
        $utf8WithoutBom
    )

    Start-Process `
        -FilePath $streamerExe `
        -WorkingDirectory $streamerFolder `
        -WindowStyle Normal | Out-Null

    $verb = if ($created) { 'created' } else { 'updated' }
    Write-SetupResult `
        -Ok $true `
        -Status $verb `
        -Message (
            "Streamer.bot $verb the Twitch reward and installed its Actions."
        ) `
        -Created $created `
        -Updated $updated `
        -ActionsInstalled $true `
        -RewardActionId $rewardActionId `
        -VisibilityActionId $visibilityActionId `
        -ReplyActionId $replyActionId `
        -BackupPath $backupPath
    exit 0
}
catch {
    Write-SetupResult `
        -Ok $false `
        -Status 'error' `
        -Message $_.Exception.Message
    exit 1
}
