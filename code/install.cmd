
echo
echo ============================================================================
echo Installing Git for Windows
curl -OL https://github.com/git-for-windows/git/releases/download/v2.31.1.windows.1/Git-2.31.1-64-bit.exe

Git-2.31.1-64-bit.exe /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"

setx PATH "%PATH%%ProgramFiles%\Git\bin;%ProgramFiles%\Git\usr\bin;"

echo.&echo ============================================================================&echo Installing Visual Studio Build Tools
curl -OL "https://aka.ms/vs/16/release/vs_buildtools.exe"
vs_buildtools.exe

setx PATH "%PATH%%ProgramFiles(x86)%\Microsoft Visual Studio\Shared\Python37_64\;"

echo
echo ============================================================================
echo Installing Python PIP
curl -OL https://bootstrap.pypa.io/get-pip.py

@REM TODO: Dynamic path in
"C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_64\python" get-pip.py
"C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_64\Scripts\pip3" install virtualenv
"C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_64\Scripts\virtualenv" --always-copy .

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


@REM TODO: create eggs symlink
@REM ln -fs Lib/site-packages eggs


@REM # Create and add zato_extra_paths to the virtualenv's sys.path.
@REM mkdir zato_extra_paths
@REM echo "$VIRTUAL_ENV/zato_extra_paths" >> eggs/easy-install.pth
@REM # Create a symlink to zato_extra_paths to make it easier to type it out
@REM ln -fs $VIRTUAL_ENV/zato_extra_paths extlib


@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\butler\__init__.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\configobj.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\django\db\models\base.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 --binary -d eggs < patches\ntlm\HTTPNtlmAuthHandler.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\pykafka\topic.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\redis\redis\connection.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\requests\models.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\requests\sessions.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\ws4py\server\geventserver.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\sqlalchemy\sql\dialects\postgresql\pg8000.py.diff
@REM "C:\Program Files\Git\usr\bin\patch" --forward -p0 -d eggs < patches\pg8000\core.py.diff
