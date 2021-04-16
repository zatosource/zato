
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

If(-Not ("$env:PATH" -like "*$env:ProgramFiles\Git\usr\bin*")) {
    Write-Output 'Adding Git\usr\bin to PATH'
    $Env:Path += ";$env:ProgramFiles\Git\usr\bin\"
}

$installed = $null -ne (Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where { $_.DisplayName -like "*Visual C++*" })
If(-Not $installed) {
    Write-Output 'Installing Visual Studio Build Tools'
    Write-Output 'Please install C++ Build tools'
    $exeFile = 'vs_buildtools.exe'
    if (-not(Test-Path "$CURDIR\$exeFile" -PathType Leaf)) {
        Invoke-WebRequest -Uri 'https://aka.ms/vs/16/release/vs_buildtools.exe' -OutFile $exeFile
    }
    Start-Process -Filepath "$CURDIR/$exeFile" -Wait
} else {
    Write-Host "Visual Studio Build Tools is installed."
}

$installed = $null -ne (Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where { $_.DisplayName -like "Python*" })
If(-Not $installed) {
    Write-Output 'Installing Python'
    $exeFile = 'python-3.9.4-amd64.exe'
    if (-not(Test-Path "$CURDIR\$exeFile" -PathType Leaf)) {
        Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.4/python-3.9.4-amd64.exe' -OutFile $exeFile
    }
    Start-Process -Filepath "$CURDIR/$exeFile" -ArgumentList @('/quiet', 'SimpleInstall=1', 'PrependPath=1') -Wait

} else {
    Write-Host "Python is installed."
}

If(-Not ("$env:PATH" -like "*\Python*")) {
    Write-Output 'Adding Python to PATH'
    $INCLUDE = "$LocalAppDataPath\Programs\$PythonPathVersion;$LocalAppDataPath\Programs\$PythonPathVersion\Scripts"
    if (Test-Path "$LocalAppDataPath\Programs\Python\$PythonPathVersion") {
        $INCLUDE = "$LocalAppDataPath\Programs\Python\$PythonPathVersion;$LocalAppDataPath\Programs\Python\$PythonPathVersion\Scripts"
    }
    $Env:Path += ";$INCLUDE"
}

# Add Python permanently to PATH
$oldPATH = $Env:Path
$Env:Path = $oldPATH.Replace('-', '&')
Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $env:PATH

Write-Output "PATH:"
Write-Output ($env:PATH).split(";")

If(-Not (Get-Command "virtualenv.exe" | Select-Object -ExpandProperty Definition)) {
    Write-Output 'Installing virtualenv'
    Start-Process -Filepath (Get-Command "pip.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('install', 'virtualenv') -Wait
}

if (-not(Test-Path ".\Lib")) {
    Write-Output 'Creating virtualenv environment'
    Start-Process -Filepath (Get-Command "python.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('-m', 'virtualenv', '--always-copy', '.') -Wait
}

if (-not(Test-Path ".\release-info")) {
    New-Item -ItemType Directory -Name ".\release-info"
}
if (-not(Test-Path ".\release-info\revision.txt" -PathType Leaf)) {
    New-Item -ItemType File -Name ".\release-info\revision.txt"
    $revision = (git log -n 1 --pretty=format:"%H") -join "`n"
    Set-Content ".\release-info\revision.txt" $revision
}

Start-Process -Filepath (Get-Command python | Select-Object -ExpandProperty Definition) -ArgumentList @('-m', 'virtualenv', '--always-copy', '.') -Wait

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

if (-not(Test-Path ".\eggs" -PathType Any)) {
    New-Item -Path ".\eggs" -ItemType SymbolicLink -Value ".\Lib\site-packages"
}

if (-not(Test-Path ".\zato_extra_paths")) {
    New-Item -ItemType Directory -Name ".\zato_extra_paths"
}

if (-not(Test-Path ".\release-info\revision.txt" -PathType Leaf)) {
    New-Item -ItemType File -Name ".\release-info\revision.txt"
    $revision = (git log -n 1 --pretty=format:"%H") -join "`n"
    Set-Content ".\release-info\revision.txt" $revision
}
if (-not(Test-Path ".\eggs\easy-install.pth" -PathType Leaf)) {
    Set-Content ".\eggs\easy-install.pth" "$CURDIR\zato_extra_paths"
}

if (-not(Test-Path ".\extlib" -PathType Any)) {
    New-Item -Path ".\extlib" -ItemType SymbolicLink -Value ".\zato_extra_paths"
}

Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\butler\__init__.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\configobj.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\django\db\models\base.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '--binary', '-d', 'eggs', '<', 'patches\ntlm\HTTPNtlmAuthHandler.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\pykafka\topic.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\redis\redis\connection.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\requests\models.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\requests\sessions.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\ws4py\server\geventserver.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\sqlalchemy\sql\dialects\postgresql\pg8000.py.diff') -Wait
Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('--forward', '-p0', '-d', 'eggs', '<', 'patches\pg8000\core.py.diff') -Wait


if (-not(Test-Path ".\Scripts\zato.py" -PathType Leaf)) {
    New-Item -ItemType File -Name ".\Scripts\zato.py"

    $MultilineComment = @"
# -*- coding: utf-8 -*-

# Zato
from zato.cli.zato_command import main

if __name__ == '__main__':

    # stdlib
    import re
    import sys

    sys.path.append('$CURDIR\Lib\site-packages\')

    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
"@

    $MultilineComment -f 'string' | Out-File ".\Scripts\zato.py"
}