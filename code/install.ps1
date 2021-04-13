

$CURDIR = (Split-Path $myInvocation.MyCommand.Path) -join "`n"


Write-Output "Installing Git for Windows"
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.31.1.windows.1/Git-2.31.1-64-bit.exe" -OutFile "Git-2.31.1-64-bit.exe"
& Git-2.31.1-64-bit.exe "/VERYSILENT" "/NORESTART" "/NOCANCEL" "/SP-" "/CLOSEAPPLICATIONS" "/RESTARTAPPLICATIONS" '/COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"'

# setx PATH "%PATH%%ProgramFiles%\Git\bin;%ProgramFiles%\Git\usr\bin;"

Write-Output "Installing Visual Studio Build Tools"
Invoke-WebRequest -Uri "https://aka.ms/vs/16/release/vs_buildtools.exe" -OutFile "vs_buildtools.exe"
& vs_buildtools.exe

Write-Output "Installing Python"
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.9.4/python-3.9.4-amd64.exe" -OutFile "python-3.9.4-amd64.exe"
& python-3.9.4-amd64.exe

Write-Output "Installing Python PIP"
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "get-pip.py"

& python get-pip.py
& pip3 install virtualenv
& python -m virtualenv --always-copy .


if(!Test-Path "$CURDIR\release-info"){
    New-Item -ItemType Directory -Name "$CURDIR\release-info"
}
New-Item -ItemType File -Name "$CURDIR\release-info\revision.txt"
$revision = (git log -n 1 --pretty=format:"%H") -join "`n"
Set-Content "$CURDIR\release-info\revision.txt" $revision

call .\Scripts\activate.bat
.\Scripts\pip install -r .\requirements.txt
.\Scripts\pip install -e .\zato-common
.\Scripts\pip install -e .\zato-agent
.\Scripts\pip install -e .\zato-broker
.\Scripts\pip install -e .\zato-cli
.\Scripts\pip install -e .\zato-client
.\Scripts\pip install -e .\zato-cy
.\Scripts\pip install -e .\zato-distlock
.\Scripts\pip install -e .\zato-hl7
.\Scripts\pip install -e .\zato-lib
.\Scripts\pip install -e .\zato-scheduler
.\Scripts\pip install -e .\zato-server
.\Scripts\pip install -e .\zato-web-admin
.\Scripts\pip install -e .\zato-zmq
.\Scripts\pip install -e .\zato-sso
.\Scripts\pip install -e .\zato-testing

# ln -fs Lib/site-packages eggs
New-Item -Path "$CURDIR\eggs" -ItemType SymbolicLink -Value "$CURDIR\Lib\site-packages"

if(!Test-Path "$CURDIR\zato_extra_paths"){
    New-Item -ItemType Directory -Name "$CURDIR\zato_extra_paths"
}
Set-Content "$CURDIR\eggs\easy-install.pth" "$CURDIR\zato_extra_paths"

# Create a symlink to zato_extra_paths to make it easier to type it out
New-Item -Path "$CURDIR\extlib" -ItemType SymbolicLink -Value "$CURDIR\zato_extra_paths"
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

New-Item -ItemType File -Name "$CURDIR\Scripts\zato"
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
# Set-Content "$CURDIR\Scripts\zato" $ZatoScriptContent