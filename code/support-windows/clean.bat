
rem
rem The embedded Python version
rem
set python_version=3.10.8

rem
rem Local aliases
rem
set curdir=%~dp0
set workdir=%curdir%\..

if exist %workdir%\bin     (rmdir /s /q %workdir%\bin)
if exist %workdir%\docs    (rmdir /s /q %workdir%\docs)
if exist %workdir%\eggs    (rmdir /s /q %workdir%\eggs)
if exist %workdir%\extlib  (rmdir /s /q %workdir%\extlib)
if exist %workdir%\include (rmdir /s /q %workdir%\include)
if exist %workdir%\lib     (rmdir /s /q %workdir%\lib)
if exist %workdir%\lib64   (rmdir /s /q %workdir%\lib64)
if exist %workdir%\local   (rmdir /s /q %workdir%\local)
if exist %workdir%\man     (rmdir /s /q %workdir%\man)
if exist %workdir%\scripts (rmdir /s /q %workdir%\scripts)
if exist %workdir%\share   (rmdir /s /q %workdir%\share)
if exist %workdir%\tests   (rmdir /s /q %workdir%\tests)
if exist %workdir%\zato_extra_paths (rmdir /s /q %workdir%\zato_extra_paths)

if exist %workdir%\zato-agent\build     (rmdir /s /q %workdir%\zato-agent\build)
if exist %workdir%\zato-broker\build    (rmdir /s /q %workdir%\zato-broker\build)
if exist %workdir%\zato-cli\build       (rmdir /s /q %workdir%\zato-cli\build)
if exist %workdir%\zato-client\build    (rmdir /s /q %workdir%\zato-client\build)
if exist %workdir%\zato-common\build    (rmdir /s /q %workdir%\zato-common\build)
if exist %workdir%\zato-cy\build        (rmdir /s /q %workdir%\zato-cy\build)
if exist %workdir%\zato-distlock\build  (rmdir /s /q %workdir%\zato-distlock\build)
if exist %workdir%\zato-hl7\build       (rmdir /s /q %workdir%\zato-hl7\build)
if exist %workdir%\zato-lib\build       (rmdir /s /q %workdir%\zato-lib\build)
if exist %workdir%\zato-scheduler\build (rmdir /s /q %workdir%\zato-scheduler\build)
if exist %workdir%\zato-server\build    (rmdir /s /q %workdir%\zato-server\build)
if exist %workdir%\zato-sso\build       (rmdir /s /q %workdir%\zato-sso\build)
if exist %workdir%\zato-testing\build   (rmdir /s /q %workdir%\zato-testing\build)
if exist %workdir%\zato-web-admin\build (rmdir /s /q %workdir%\zato-web-admin\build)

del /s /q %workdir%\zato-agent\*.pyc
del /s /q %workdir%\zato-broker\*.pyc
del /s /q %workdir%\zato-cli\*.pyc
del /s /q %workdir%\zato-client\*.pyc
del /s /q %workdir%\zato-common\*.pyc
del /s /q %workdir%\zato-cy\*.pyc
del /s /q %workdir%\zato-distlock\*.pyc
del /s /q %workdir%\zato-hl7\*.pyc
del /s /q %workdir%\zato-lib\*.pyc
del /s /q %workdir%\zato-scheduler\*.pyc
del /s /q %workdir%\zato-server\*.pyc
del /s /q %workdir%\zato-sso\*.pyc
del /s /q %workdir%\zato-testing\*.pyc
del /s /q %workdir%\zato-web-admin\*.pyc

del /s /q %workdir%\zato-agent\*.pyd
del /s /q %workdir%\zato-broker\*.pyd
del /s /q %workdir%\zato-cli\*.pyd
del /s /q %workdir%\zato-client\*.pyd
del /s /q %workdir%\zato-common\*.pyd
del /s /q %workdir%\zato-cy\*.pyd
del /s /q %workdir%\zato-distlock\*.pyd
del /s /q %workdir%\zato-hl7\*.pyd
del /s /q %workdir%\zato-lib\*.pyd
del /s /q %workdir%\zato-scheduler\*.pyd
del /s /q %workdir%\zato-server\*.pyd
del /s /q %workdir%\zato-sso\*.pyd
del /s /q %workdir%\zato-testing\*.pyd
del /s /q %workdir%\zato-web-admin\*.pyd

del /s /q %workdir%\zato-cy\*.c
del /s /q %workdir%\zato-cy\*.html

del /s /q %workdir%\bundle-ext\python-windows\python-%python_version%\py.bat
del /s /q %workdir%\bundle-ext\python-windows\python-%python_version%\zato.bat

if exist %workdir%\bundle-ext\python-windows\python-%python_version%\Lib\ (rmdir /s /q %workdir%\bundle-ext\python-windows\python-%python_version%\Lib\)
if exist %workdir%\bundle-ext\python-windows\python-%python_version%\Scripts\ (rmdir /s /q %workdir%\bundle-ext\python-windows\python-%python_version%\Scripts\)

for /d /r %%i in (*.egg-info*)    do @rmdir /s /q "%%i"
for /d /r %%i in (*__pycache__*)  do @rmdir /s /q "%%i"

echo Done cleaning up
ver
