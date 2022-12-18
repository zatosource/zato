@echo off

rem
rem The embedded Python version
rem
set python_version=3.10.8

rem
rem Local aliases
rem
set curdir=%~dp0

set bundle_ext_dir=%curdir%\..\bundle-ext
set python_bin_dir=%bundle_ext_dir%\python-windows\python-%python_version%
set pip_dir=%bundle_ext_dir%\pip

set python_cmd=%python_bin_dir%\python.exe
set pip_cmd=%pip_dir%\pip.pyz

rem
rem Run pip
rem
%python_cmd% %pip_cmd% %*
if %errorlevel% neq 0 exit /b %errorlevel%
