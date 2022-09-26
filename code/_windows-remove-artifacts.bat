
rem
rem Local aliases
rem
set curdir=%~dp0

del /s /q %curdir%\*.pyc

del /s /q %curdir%\zato-cy\*.c
del /s /q %curdir%\zato-cy\*.html

for /d /r %%i in (*.egg-info*)    do @rmdir /s /q "%%i"
for /d /r %%i in (*__pycache__*)  do @rmdir /s /q "%%i"

echo Done removing artifacts
ver
