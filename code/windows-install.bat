echo
echo Zato Windows installation
ver

rem
rem Local aliases
rem
set curdir=%~dp0

rem
rem Install prerequisites
rem
python -m ensurepip
python -m pip install -U --upgrade pip
python -m pip install -U virtualenv==20.4.3

rem
rem Note that we install virtualenv but we do not activate it,
rem as it would otherwise prevent from calling the following .bat file.
rem
echo Installing virtualenv in %curdir%
python -m virtualenv %curdir%

rem
rem Actually install all Python dependencies
rem
echo Setting up environment in %curdir%
start "Zato install" call _windows-run-install.bat
