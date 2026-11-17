# Copyright (C) 2026, Zato Source s.r.o. https://zato.io
# Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

# Prepares a guest once, at the end of the installation. Everything that differs between test runs,
# the data shares, the exchange account and the agent, is applied after each boot instead.

$ErrorActionPreference = 'Stop'

$settings = Get-Content -Raw -Path 'C:\OEM\settings.json' | ConvertFrom-Json

$controlPath = 'C:\shares\control'
$errorPath   = Join-Path $controlPath 'provision-error.txt'
$markerPath  = Join-Path $controlPath 'provisioned.json'

# The online activation is repeated until it succeeds, since it fails while the guest network is still starting
$activationAttempts     = 20
$activationRetrySeconds = 15
$licenseLicensed        = 1
$windowsApplicationID   = '55c92734-d682-4d71-983e-d6ec3f16059f'

# The harness account and the control share come first, so that a failure in any later step
# can be read by the build through the control share.
$password = ConvertTo-SecureString $settings.harness_password -AsPlainText -Force
$null = New-LocalUser -Name $settings.harness_username -Password $password -PasswordNeverExpires -AccountNeverExpires

$null = New-Item -ItemType Directory -Force -Path $controlPath
$null = icacls $controlPath /grant "$($settings.harness_username):(OI)(CI)M"
$null = New-SmbShare -Name 'control' -Path $controlPath -FullAccess $settings.harness_username

# SMB is reachable in every network profile
Set-NetFirewallRule -Name 'FPS-SMB-In-TCP' -Enabled True -Profile Any

try {

    # The guest network is classified as private
    Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private

    # Failed logons are written to the Security log, from which the agent forwards them
    $null = auditpol /set /subcategory:"Logon" /failure:enable

    # No updates are installed and no maintenance runs while tests use the guest
    $updatePolicy = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'
    $null = New-Item -Force -Path $updatePolicy
    $null = New-ItemProperty -Force -Path $updatePolicy -Name 'NoAutoUpdate' -Value 1 -PropertyType DWord
    Stop-Service -Name 'wuauserv' -Force
    Set-Service -Name 'wuauserv' -StartupType Disabled

    $maintenance = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Maintenance'
    $null = New-ItemProperty -Force -Path $maintenance -Name 'MaintenanceDisabled' -Value 1 -PropertyType DWord

    # The evaluation license is activated online
    for ($attempt = 1; $attempt -le $activationAttempts; $attempt++) {

        $activationOutput = cscript.exe //NoLogo C:\Windows\System32\slmgr.vbs /ato | Out-String

        $license = Get-CimInstance -ClassName SoftwareLicensingProduct -Filter 'PartialProductKey IS NOT NULL' |
            Where-Object { $_.ApplicationID -eq $windowsApplicationID }

        if ($license.LicenseStatus -eq $licenseLicensed) {
            break
        }

        Start-Sleep -Seconds $activationRetrySeconds
    }

    if ($license.LicenseStatus -ne $licenseLicensed) {
        throw "Activation failed after $activationAttempts attempts, license status $($license.LicenseStatus) -> $activationOutput"
    }

    # The bootstrap runs at each startup and starts the agent that the harness uploads
    $action    = New-ScheduledTaskAction -Execute 'powershell.exe' `
        -Argument '-NoProfile -ExecutionPolicy Bypass -File C:\OEM\bootstrap.ps1'
    $trigger   = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
    $taskSettings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) `
        -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    $null = Register-ScheduledTask -TaskName 'ZatoTestBootstrap' -Action $action -Trigger $trigger `
        -Principal $principal -Settings $taskSettings

    $os = Get-CimInstance -ClassName Win32_OperatingSystem

    $marker = [ordered]@{
        caption        = $os.Caption
        version        = $os.Version
        build_number   = $os.BuildNumber
        license_status = $license.LicenseStatus
        grace_minutes  = $license.GracePeriodRemaining
    }

    $marker | ConvertTo-Json -Compress | Set-Content -Path $markerPath -Encoding ASCII
}
catch {
    $_ | Out-String | Set-Content -Path $errorPath -Encoding ASCII
}
