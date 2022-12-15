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

set zato_cmd=%python_bin_dir%\zato.bat

rem
rem Run Zato
rem
%zato_cmd% %*
if %errorlevel% neq 0 exit /b %errorlevel%
