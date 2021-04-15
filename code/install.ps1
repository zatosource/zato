
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

If(-Not ("$env:PATH" -like "*$PythonPathVersion*")) {
    Write-Output 'Adding Python to PATH'
    $INCLUDE = "$LocalAppDataPath\Programs\$PythonPathVersion;$LocalAppDataPath\Programs\$PythonPathVersion\Scripts"
    $Env:Path += ";$INCLUDE"
}

Write-Output "PATH:"
Write-Output ($env:PATH).split(";")

Get-Command pip | Select-Object -ExpandProperty Definition
Start-Process -Filepath (Get-Command pip | Select-Object -ExpandProperty Definition) -ArgumentList @('install', 'virtualenv') -Wait

Get-Command python | Select-Object -ExpandProperty Definition
Start-Process -Filepath (Get-Command python | Select-Object -ExpandProperty Definition) -ArgumentList @('--always-copy', '.') -Wait

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

# ln -fs Lib/site-packages eggs
New-Item -Path ".\eggs" -ItemType SymbolicLink -Value ".\Lib\site-packages"

if (-not(Test-Path ".\zato_extra_paths")) {
    New-Item -ItemType Directory -Name ".\zato_extra_paths"
}
Set-Content ".\eggs\easy-install.pth" ".\zato_extra_paths"

# Create a symlink to zato_extra_paths to make it easier to type it out
New-Item -Path ".\extlib" -ItemType SymbolicLink -Value ".\zato_extra_paths"
# ln -fs $VIRTUAL_ENV/zato_extra_paths extlib


# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\butler\__init__.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\configobj.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\django\db\models\base.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 --binary -d eggs < patches\ntlm\HTTPNtlmAuthHandler.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\pykafka\topic.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\redis\redis\connection.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\requests\models.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\requests\sessions.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\ws4py\server\geventserver.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\sqlalchemy\sql\dialects\postgresql\pg8000.py.diff
# "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\pg8000\core.py.diff

New-Item -ItemType File -Name ".\Scripts\zato"
# $ZatoScriptContent = @"#! python

# # Zato
# from zato.cli.zato_command import main

# if __name__ == '__main__':

#     # stdlib
#     import re
#     import sys

#     # This is needed by SUSE
#     sys.path.append('$VIRTUAL_ENV/lib64/python3.6/site-packages/')

#     sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
#     sys.exit(main())
# "@
# Set-Content ".\Scripts\zato" $ZatoScriptContent