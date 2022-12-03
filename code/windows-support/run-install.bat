
rem
rem The embedded Python version
rem
set python_version=3.10.8

rem
rem Local aliases
rem
set curdir=%~dp0
set python_bin_dir=%curdir%\..\bundle-ext\python-windows\python-%python_version%
set python_cmd=%python_bin_dir%\python.exe

rem
rem Install Zato
rem
rem cd %python_bin_dir%\
%python_cmd% %curdir%\..\util\zato_environment.py install
if %errorlevel% neq 0 exit /b %errorlevel%

rem
rem Confirm the version installed
rem
%python_bin_dir%\zato.bat --version
