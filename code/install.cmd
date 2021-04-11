
echo.&echo ============================================================================&echo Installing Git for Windows
curl -OL https://github.com/git-for-windows/git/releases/download/v2.31.1.windows.1/Git-2.31.1-64-bit.exe

Git-2.31.1-64-bit.exe /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"

setx PATH "%PATH%%ProgramFiles%\Git;"

echo.&echo ============================================================================&echo Installing Visual Studio Build Tools
curl -OL "https://aka.ms/vs/16/release/vs_buildtools.exe"
vs_buildtools.exe

pip3 install virtualenv

virtualenv --always-copy .
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