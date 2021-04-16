
$CURDIR = (Split-Path $myInvocation.MyCommand.Path) -join "`n"
$LocalAppDataPath = $env:LocalAppData
$PythonPathVersion = "Python39"

$installed = $null -ne (Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where { $_.DisplayName -like "Git version*" })
If(-Not $installed) {
    Write-Output 'Installing Git for Windows'
    $exeFile = 'Git-2.31.1-64-bit.exe'
    if (-not(Test-Path "$CURDIR\$exeFile" -PathType Leaf)){
        Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.31.1.windows.1/Git-2.31.1-64-bit.exe' -OutFile $exeFile
    }
    $exeArgs = @('/VERYSILENT', '/NORESTART', '/NOCANCEL', '/SP-', '/CLOSEAPPLICATIONS', '/RESTARTAPPLICATIONS', '/COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"')
    Start-Process -Filepath "$CURDIR/$exeFile" -ArgumentList $exeArgs -Wait
} else {
    Write-Host "Git for Windows is installed."
}

Write-Output "*** Downloading updates ***"
Start-Process -Filepath (Get-Command "git.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('pull') -Wait

# if [[ -n "${ZATO_BRANCH}" ]];then
#     # Checkout a local branch/commit or create the branch from the remote one
#     git checkout "${ZATO_BRANCH}" 2>/dev/null || git checkout -b "${ZATO_BRANCH}" "origin/${ZATO_BRANCH}"
# fi

Set-ExecutionPolicy Unrestricted -Scope Process

.\Scripts\activate.ps1
.\Scripts\pip.exe install -r .\requirements.txt
.\Scripts\pip.exe install -e .\zato-common
.\Scripts\pip.exe install -e .\zato-agent
.\Scripts\pip.exe install -e .\zato-broker
.\Scripts\pip.exe install -e .\zato-cli
.\Scripts\pip.exe install -e .\zato-client
.\Scripts\pip.exe install -e .\zato-cy
.\Scripts\pip.exe install -e .\zato-distlock
.\Scripts\pip.exe install -e .\zato-hl7
.\Scripts\pip.exe install -e .\zato-lib
.\Scripts\pip.exe install -e .\zato-scheduler
.\Scripts\pip.exe install -e .\zato-server
.\Scripts\pip.exe install -e .\zato-web-admin
.\Scripts\pip.exe install -e .\zato-zmq
.\Scripts\pip.exe install -e .\zato-sso
.\Scripts\pip.exe install -e .\zato-testing

Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\butler\__init__.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\configobj.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\django\db\models\base.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '--binary', '-d', 'eggs', '-i', 'patches\ntlm\HTTPNtlmAuthHandler.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\pykafka\topic.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\redis\redis\connection.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\requests\models.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\requests\sessions.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\ws4py\server\geventserver.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\sqlalchemy\sql\dialects\postgresql\pg8000.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\pg8000\core.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '-i', 'patches\sqlalchemy\sql\crud.py.diff') -Wait
