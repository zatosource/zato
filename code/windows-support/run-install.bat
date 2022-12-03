
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
rem Install setuptools
rem
rem cd %python_bin_dir%
%python_cmd% %python_bin_dir%\pip.pyz install setuptools==57.4.0 --prefix %python_bin_dir% --no-warn-script-location
rem %python_cmd% %python_bin_dir%\pip.pyz install --help

rem
rem Install Zato
rem
rem cd %python_bin_dir%\
%python_cmd% %curdir%\..\util\zato_environment.py install

rem
rem Confirm the version installed
rem
rem %python_cmd% %python_bin_dir%\Scripts\zato-bin.py --version
