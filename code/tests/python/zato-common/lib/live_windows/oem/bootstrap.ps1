# Copyright (C) 2026, Zato Source s.r.o. https://zato.io
# Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

# Runs at each startup as SYSTEM. It waits for the harness to upload the agent into the control share,
# runs it, and records why it stopped if it did.

$ErrorActionPreference = 'Stop'

$controlPath = 'C:\shares\control'
$agentPath   = Join-Path $controlPath 'agent\agent.ps1'
$startPath   = Join-Path $controlPath 'agent\start.json'
$errorPath   = Join-Path $controlPath 'agent-error.txt'

while ($true) {

    if (Test-Path -Path $startPath) {

        Remove-Item -Path $startPath -Force

        try {
            & $agentPath
        }
        catch {
            $_ | Out-String | Set-Content -Path $errorPath -Encoding ASCII
        }
    }

    Start-Sleep -Milliseconds 200
}
