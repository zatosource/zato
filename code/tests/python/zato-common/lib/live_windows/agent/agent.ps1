# Copyright (C) 2026, Zato Source s.r.o. https://zato.io
# Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

# The agent inside each guest. It reads commands from the control share, produces, consumes and observes files,
# injects faults, and appends every event, together with the errors of Windows itself, to one JSON-lines file
# that the harness reads. All the work runs in one loop, one short step of each task per tick.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2

$ControlPath   = 'C:\shares\control'
$CommandsPath  = Join-Path $ControlPath 'commands'
$EventsPath    = Join-Path $ControlPath 'events.jsonl'
$HeartbeatPath = Join-Path $ControlPath 'heartbeat.json'

$Utf8 = New-Object System.Text.UTF8Encoding($false)

$TickMs            = 100
$HeartbeatEveryMs  = 500
$WindowsEventsEveryMs = 1000
$WriteAttempts     = 50
$WriteRetryMs      = 20
$BlockRuleName     = 'zato-test-block-smb'

$WindowsEventLogs = @(
    'Microsoft-Windows-SMBServer/Operational',
    'Microsoft-Windows-SMBServer/Security',
    'Microsoft-Windows-SMBServer/Connectivity'
)

$Started        = Get-Date
$Tasks          = [ordered]@{}
$ShareDefs      = @{}
$LastRecordIds  = @{}
$HeartbeatSeq   = 0
$LastHeartbeat  = [DateTime]::MinValue
$LastWindowsEvents = [DateTime]::MinValue

# ################################################################################################################################

function Get-NowIso {
    (Get-Date).ToUniversalTime().ToString('o')
}

function Get-Sha256Hex([byte[]]$Data) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    $hash = $algorithm.ComputeHash($Data)
    $algorithm.Dispose()
    [BitConverter]::ToString($hash).Replace('-', '').ToLowerInvariant()
}

function Write-Shared([string]$Path, [byte[]]$Bytes, [IO.FileMode]$Mode) {

    # The harness reads the same files at any time, so each write retries briefly on a sharing violation
    for ($attempt = 1; ; $attempt++) {
        try {
            $stream = New-Object IO.FileStream($Path, $Mode, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
            try {
                if ($Mode -eq [IO.FileMode]::OpenOrCreate) {
                    $stream.SetLength(0)
                }
                $stream.Write($Bytes, 0, $Bytes.Length)
            }
            finally {
                $stream.Dispose()
            }
            return
        }
        catch [IO.IOException] {
            if ($attempt -ge $WriteAttempts) {
                throw
            }
            Start-Sleep -Milliseconds $WriteRetryMs
        }
    }
}

function Write-AgentEvent([Collections.IDictionary]$Fields) {
    $Fields['time'] = Get-NowIso
    $line  = ($Fields | ConvertTo-Json -Compress -Depth 6) + "`n"
    $bytes = $Utf8.GetBytes($line)
    Write-Shared $EventsPath $bytes ([IO.FileMode]::Append)
}

function Write-ErrorEvent($Run, [string]$Source, $ErrorRecord) {
    Write-AgentEvent ([ordered]@{
        kind    = 'error'
        run     = $Run
        source  = $Source
        message = $ErrorRecord.Exception.Message
        line    = $ErrorRecord.InvocationInfo.ScriptLineNumber
        detail  = ($ErrorRecord | Out-String)
    })
}

function Write-Heartbeat {
    $script:HeartbeatSeq++
    $document = [ordered]@{ seq = $script:HeartbeatSeq; time = (Get-NowIso); tasks = $Tasks.Count } |
        ConvertTo-Json -Compress
    $bytes = $Utf8.GetBytes($document)
    Write-Shared $HeartbeatPath $bytes ([IO.FileMode]::OpenOrCreate)
}

# ################################################################################################################################

function New-FileContent([string]$Name, [int]$Size) {

    $out = New-Object byte[] $Size
    if ($Size -eq 0) {
        return ,$out
    }

    # The content repeats the file name line by line, filled by doubling what is already in place
    $line = $Utf8.GetBytes("$Name`r`n")
    $first = [Math]::Min($line.Length, $Size)
    [Buffer]::BlockCopy($line, 0, $out, 0, $first)

    $filled = $first
    while ($filled -lt $Size) {
        $count = [Math]::Min($filled, $Size - $filled)
        [Buffer]::BlockCopy($out, 0, $out, $filled, $count)
        $filled += $count
    }

    return ,$out
}

# ################################################################################################################################

function Set-Layout($Command) {

    foreach ($user in $Command.users) {
        $password = ConvertTo-SecureString $user.password -AsPlainText -Force
        if (Get-LocalUser -Name $user.name -ErrorAction SilentlyContinue) {
            Set-LocalUser -Name $user.name -Password $password
        }
        else {
            $null = New-LocalUser -Name $user.name -Password $password -PasswordNeverExpires -AccountNeverExpires
        }
    }

    foreach ($directory in $Command.directories) {
        $null = New-Item -ItemType Directory -Force -Path $directory
    }

    foreach ($share in $Command.shares) {
        $script:ShareDefs[$share.name] = $share
        New-DataShare $share
    }

    Write-AgentEvent ([ordered]@{ kind = 'layout-applied'; run = $Command.run })
}

function New-DataShare($Share) {

    if (Get-SmbShare -Name $Share.name -ErrorAction SilentlyContinue) {
        Remove-SmbShare -Name $Share.name -Force
    }

    $null = New-Item -ItemType Directory -Force -Path $Share.path

    foreach ($user in $Share.change) {
        $null = icacls $Share.path /grant "$($user):(OI)(CI)M"
    }

    foreach ($user in $Share.read) {
        $null = icacls $Share.path /grant "$($user):(OI)(CI)RX"
    }

    $options = @{ Name = $Share.name; Path = $Share.path; EncryptData = [bool]$Share.encrypt }

    if (@($Share.change).Count -gt 0) {
        $options['ChangeAccess'] = @($Share.change)
    }

    if (@($Share.read).Count -gt 0) {
        $options['ReadAccess'] = @($Share.read)
    }

    $null = New-SmbShare @options
}

# ################################################################################################################################

function Start-Producer($Command) {
    $Tasks[$Command.task] = @{
        kind     = 'produce'
        command  = $Command
        index    = 0
        next_due = Get-Date
        pending  = $null
    }
}

function Complete-Produced($Task, [string]$Name, [byte[]]$Data) {
    Write-AgentEvent ([ordered]@{
        kind      = 'produced'
        run       = $Task.command.run
        task      = $Task.command.task
        directory = $Task.command.directory
        name      = $Name
        size      = $Data.Length
        sha256    = (Get-Sha256Hex $Data)
    })
}

function Step-Producer($Task) {

    $command = $Task.command
    $now = Get-Date

    # A file that is still being written or still locked is finished before the next one starts ..
    if ($Task.pending) {

        $pending = $Task.pending

        if ($command.mode -eq 'slow') {
            if ($now -ge $pending.next_chunk_due) {
                $offset = $pending.offset
                $count  = [Math]::Min($pending.chunk_size, $pending.data.Length - $offset)
                $pending.stream.Write($pending.data, $offset, $count)
                $pending.stream.Flush()
                $pending.offset += $count
                $pending.next_chunk_due = $now.AddMilliseconds($pending.chunk_interval_ms)
            }
            if ($pending.offset -ge $pending.data.Length) {
                $pending.stream.Dispose()
                $Task.pending = $null
                Complete-Produced $Task $pending.name $pending.data
            }
        }
        else {
            if ($now -ge $pending.release_at) {
                $pending.stream.Dispose()
                $Task.pending = $null
                Write-AgentEvent ([ordered]@{ kind = 'released'; run = $command.run; name = $pending.name })
            }
        }
        return
    }

    # .. all the files were produced ..
    $names = @($command.names)
    if ($Task.index -ge $names.Count) {
        $Tasks.Remove($command.task)
        Write-AgentEvent ([ordered]@{ kind = 'task-finished'; run = $command.run; task = $command.task })
        return
    }

    # .. or the next one is not due yet ..
    if ($now -lt $Task.next_due) {
        return
    }

    $name = $names[$Task.index]
    $Task.index++
    $Task.next_due = $now.AddMilliseconds($command.interval_ms)

    $path = Join-Path $command.directory $name
    $data = New-FileContent $name $command.size

    # .. otherwise the next file is created in the way the command asks for.
    switch ($command.mode) {

        'direct' {
            [IO.File]::WriteAllBytes($path, $data)
            Complete-Produced $Task $name $data
        }

        'temp-then-rename' {
            $tempPath = $path + $command.temp_suffix
            [IO.File]::WriteAllBytes($tempPath, $data)
            [IO.File]::Move($tempPath, $path)
            Complete-Produced $Task $name $data
        }

        'slow' {
            $stream = New-Object IO.FileStream($path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::Read)
            $chunkCount = [int]$command.chunk_count
            $Task.pending = @{
                name              = $name
                data              = $data
                stream            = $stream
                offset            = 0
                chunk_size        = [Math]::Max(1, [Math]::Ceiling($data.Length / $chunkCount))
                chunk_interval_ms = [Math]::Floor($command.slow_ms / $chunkCount)
                next_chunk_due    = $now
            }
        }

        'locked' {
            $stream = New-Object IO.FileStream($path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
            $stream.Write($data, 0, $data.Length)
            $stream.Flush()
            $Task.pending = @{
                name       = $name
                stream     = $stream
                release_at = $now.AddMilliseconds($command.lock_ms)
            }
            Complete-Produced $Task $name $data
        }

        default {
            throw "Unknown producer mode $($command.mode)"
        }
    }
}

# ################################################################################################################################

function Start-Consumer($Command) {
    $Tasks[$Command.task] = @{
        kind          = 'consume'
        command       = $Command
        seen          = @{}
        reported_temp = @{}
    }
}

function Test-IgnoredName([string]$Name, $Suffixes) {
    foreach ($suffix in @($Suffixes)) {
        if ($Name.EndsWith($suffix, [StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Step-Consumer($Task) {

    $command = $Task.command
    $now = Get-Date

    foreach ($file in @(Get-ChildItem -LiteralPath $command.directory -File)) {

        $name = $file.Name

        # A temporary file that stays in place for too long means that its writer never renamed it ..
        if (Test-IgnoredName $name $command.ignore_suffixes) {
            $age = ($now - $file.LastWriteTime).TotalMilliseconds
            if ($age -gt $command.stale_temp_ms) {
                if (-not $Task.reported_temp.ContainsKey($name)) {
                    $Task.reported_temp[$name] = $true
                    Write-AgentEvent ([ordered]@{
                        kind = 'error'; run = $command.run; source = 'consumer'
                        message = "Temporary file $name in $($command.directory) was not renamed within $($command.stale_temp_ms) ms"
                    })
                }
            }
            continue
        }

        if (-not ($name -like $command.pattern)) {
            continue
        }

        if ($Task.seen.ContainsKey($name)) {
            continue
        }

        # .. a file still open in its writer is left for the next tick ..
        try {
            $stream = New-Object IO.FileStream($file.FullName, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::None)
        }
        catch [IO.IOException] {
            continue
        }

        try {
            $memory = New-Object IO.MemoryStream
            $stream.CopyTo($memory)
            $data = $memory.ToArray()
        }
        finally {
            $stream.Dispose()
        }

        Write-AgentEvent ([ordered]@{
            kind      = 'consumed'
            run       = $command.run
            task      = $command.task
            directory = $command.directory
            name      = $name
            size      = $data.Length
            sha256    = (Get-Sha256Hex $data)
        })

        # .. and a consumed file is removed, renamed as failed, or kept, as the command asks for.
        if (@($command.fail_names) -contains $name) {
            $failedName = [IO.Path]::ChangeExtension($name, 'failed')
            Rename-Item -LiteralPath $file.FullName -NewName $failedName
            Write-AgentEvent ([ordered]@{ kind = 'marked-failed'; run = $command.run; name = $name; failed_name = $failedName })
        }
        elseif ($command.action -eq 'delete') {
            Remove-Item -LiteralPath $file.FullName -Force
        }
        else {
            $Task.seen[$name] = $true
        }
    }
}

# ################################################################################################################################

function Get-Listing([string]$Root) {
    $out = @{}
    foreach ($file in @(Get-ChildItem -LiteralPath $Root -File -Recurse)) {
        $relative = $file.FullName.Substring($Root.Length).TrimStart('\')
        $out[$relative] = $file.Length
    }
    $out
}

function Start-Observer($Command) {
    $listing = Get-Listing $Command.root
    $Tasks[$Command.task] = @{
        kind    = 'observe'
        command = $Command
        listing = $listing
    }
    Write-AgentEvent ([ordered]@{ kind = 'observing'; run = $Command.run; root = $Command.root; count = $listing.Count })
}

function Step-Observer($Task) {

    $command = $Task.command
    $previous = $Task.listing
    $current = Get-Listing $command.root

    foreach ($path in $current.Keys) {
        if (-not $previous.ContainsKey($path)) {
            Write-AgentEvent ([ordered]@{ kind = 'appeared'; run = $command.run; root = $command.root; path = $path; size = $current[$path] })
        }
    }

    foreach ($path in $previous.Keys) {
        if (-not $current.ContainsKey($path)) {
            Write-AgentEvent ([ordered]@{ kind = 'disappeared'; run = $command.run; root = $command.root; path = $path })
        }
    }

    $Task.listing = $current
}

# ################################################################################################################################

function Start-SMBServiceRestart($Command) {

    # The restart runs in a process of its own, so that the heartbeat continues while the service is down
    $null = Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden `
        -ArgumentList '-NoProfile', '-Command', 'Restart-Service -Name LanmanServer -Force'

    $Tasks[$Command.task] = @{
        kind       = 'service-wait'
        command    = $Command
        was_down   = $false
    }
    Write-AgentEvent ([ordered]@{ kind = 'fault-started'; run = $Command.run; fault = 'restart-smb-service' })
}

function Step-ServiceWait($Task) {

    $command = $Task.command
    $status = (Get-Service -Name 'LanmanServer').Status

    if ($status -ne 'Running') {
        $Task.was_down = $true
        return
    }

    if ($Task.was_down) {
        $Tasks.Remove($command.task)
        Write-AgentEvent ([ordered]@{ kind = 'fault-ended'; run = $command.run; fault = 'restart-smb-service' })
    }
}

function Step-UnblockWait($Task) {

    $command = $Task.command

    if ((Get-Date) -lt $Task.release_at) {
        return
    }

    Remove-NetFirewallRule -DisplayName $BlockRuleName
    $Tasks.Remove($command.task)
    Write-AgentEvent ([ordered]@{ kind = 'fault-ended'; run = $command.run; fault = 'block-port' })
}

function Invoke-Fault($Command) {

    switch ($Command.kind) {

        'block-port' {
            $null = New-NetFirewallRule -DisplayName $BlockRuleName -Direction Inbound -Protocol TCP `
                -LocalPort 445 -Action Block

            # The block also applies to the harness, which therefore cannot send the command that lifts it
            $Tasks[$Command.task] = @{
                kind       = 'unblock-wait'
                command    = $Command
                release_at = (Get-Date).AddMilliseconds($Command.duration_ms)
            }
        }

        'unblock-port' {
            Remove-NetFirewallRule -DisplayName $BlockRuleName
        }

        'set-password' {
            $password = ConvertTo-SecureString $Command.password -AsPlainText -Force
            Set-LocalUser -Name $Command.user -Password $password
        }

        'remove-share' {
            Remove-SmbShare -Name $Command.share -Force
        }

        'restore-share' {
            New-DataShare $ShareDefs[$Command.share]
        }
    }

    Write-AgentEvent ([ordered]@{ kind = 'fault-applied'; run = $Command.run; fault = $Command.kind })
}

# ################################################################################################################################

function Stop-Run($Command) {

    foreach ($key in @($Tasks.Keys)) {
        $task = $Tasks[$key]
        if ($task.command.run -eq $Command.run) {
            if ($task.ContainsKey('pending')) {
                if ($task.pending) {
                    $task.pending.stream.Dispose()
                }
            }
            $Tasks.Remove($key)
        }
    }

    Write-AgentEvent ([ordered]@{ kind = 'run-stopped'; run = $Command.run })
}

$CommandHandlers = @{
    'apply-layout'        = { param($Command) Set-Layout $Command }
    'produce'             = { param($Command) Start-Producer $Command }
    'consume'             = { param($Command) Start-Consumer $Command }
    'observe'             = { param($Command) Start-Observer $Command }
    'restart-smb-service' = { param($Command) Start-SMBServiceRestart $Command }
    'block-port'          = { param($Command) Invoke-Fault $Command }
    'unblock-port'        = { param($Command) Invoke-Fault $Command }
    'set-password'        = { param($Command) Invoke-Fault $Command }
    'remove-share'        = { param($Command) Invoke-Fault $Command }
    'restore-share'       = { param($Command) Invoke-Fault $Command }
    'stop'                = { param($Command) Stop-Run $Command }
    'ping'                = { param($Command) Write-AgentEvent ([ordered]@{ kind = 'pong'; run = $Command.run }) }
}

$StepHandlers = @{
    'produce'      = { param($Task) Step-Producer $Task }
    'consume'      = { param($Task) Step-Consumer $Task }
    'observe'      = { param($Task) Step-Observer $Task }
    'service-wait' = { param($Task) Step-ServiceWait $Task }
    'unblock-wait' = { param($Task) Step-UnblockWait $Task }
}

function Read-Commands {

    foreach ($file in @(Get-ChildItem -LiteralPath $CommandsPath -File -Filter '*.json' | Sort-Object Name)) {

        $text = [IO.File]::ReadAllText($file.FullName, $Utf8)
        Remove-Item -LiteralPath $file.FullName -Force
        $command = $text | ConvertFrom-Json

        try {
            if (-not $CommandHandlers.ContainsKey($command.kind)) {
                throw "Unknown command $($command.kind)"
            }
            & $CommandHandlers[$command.kind] $command
            Write-AgentEvent ([ordered]@{ kind = 'command-done'; run = $command.run; command = $command.kind })
        }
        catch {
            Write-ErrorEvent $command.run "command $($command.kind)" $_
        }
    }
}

function Step-Tasks {

    foreach ($key in @($Tasks.Keys)) {

        # A task may have been removed by the step of another one
        if (-not $Tasks.Contains($key)) {
            continue
        }

        $task = $Tasks[$key]

        try {
            & $StepHandlers[$task.kind] $task
        }
        catch {
            $Tasks.Remove($key)
            Write-ErrorEvent $task.command.run "task $($task.kind) $key" $_
        }
    }
}

# ################################################################################################################################

function Get-AvailableEventLogs {
    $out = @()
    foreach ($logName in $WindowsEventLogs) {
        $log = Get-WinEvent -ListLog $logName -ErrorAction SilentlyContinue
        if ($log) {
            $out += $logName
        }
    }
    $out
}

function Send-WindowsEvents([string]$LogName, [hashtable]$Filter) {

    $Filter['LogName'] = $LogName
    $Filter['StartTime'] = $Started

    try {
        $entries = @(Get-WinEvent -FilterHashtable $Filter -Oldest)
    }
    catch {
        # Get-WinEvent reports an empty result as an error of its own
        if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') {
            return
        }
        throw
    }

    $lastKey = "$LogName|$($Filter['Id'])"
    $lastRecordId = 0
    if ($LastRecordIds.ContainsKey($lastKey)) {
        $lastRecordId = $LastRecordIds[$lastKey]
    }

    foreach ($entry in $entries) {
        if ($entry.RecordId -le $lastRecordId) {
            continue
        }
        $LastRecordIds[$lastKey] = $entry.RecordId

        Write-AgentEvent ([ordered]@{
            kind      = 'windows-event'
            log       = $LogName
            provider  = $entry.ProviderName
            event_id  = $entry.Id
            level     = $entry.Level
            record_id = $entry.RecordId
            created   = $entry.TimeCreated.ToUniversalTime().ToString('o')
            message   = $entry.Message
        })
    }
}

function Send-AllWindowsEvents {
    foreach ($logName in $AvailableEventLogs) {
        Send-WindowsEvents $logName @{ Level = 1, 2, 3 }
    }
    Send-WindowsEvents 'Security' @{ Id = 4625 }
}

# ################################################################################################################################

$null = New-Item -ItemType Directory -Force -Path $CommandsPath
$AvailableEventLogs = Get-AvailableEventLogs

$os = Get-CimInstance -ClassName Win32_OperatingSystem

Write-AgentEvent ([ordered]@{
    kind       = 'agent-started'
    caption    = $os.Caption
    version    = $os.Version
    event_logs = $AvailableEventLogs
})

while ($true) {

    $now = Get-Date

    try {
        if (($now - $LastHeartbeat).TotalMilliseconds -ge $HeartbeatEveryMs) {
            $LastHeartbeat = $now
            Write-Heartbeat
        }

        Read-Commands
        Step-Tasks

        if (($now - $LastWindowsEvents).TotalMilliseconds -ge $WindowsEventsEveryMs) {
            $LastWindowsEvents = $now
            Send-AllWindowsEvents
        }
    }
    catch {
        Write-ErrorEvent $null 'agent loop' $_
    }

    Start-Sleep -Milliseconds $TickMs
}
