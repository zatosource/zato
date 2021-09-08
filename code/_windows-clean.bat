
rem
rem Local aliases
rem
set curdir=%~dp0

if exist %curdir%\bin     (rmdir /s /q %curdir%\bin)
if exist %curdir%\docs    (rmdir /s /q %curdir%\docs)
if exist %curdir%\eggs    (rmdir /s /q %curdir%\eggs)
if exist %curdir%\extlib  (rmdir /s /q %curdir%\extlib)
if exist %curdir%\include (rmdir /s /q %curdir%\include)
if exist %curdir%\lib     (rmdir /s /q %curdir%\lib)
if exist %curdir%\lib64   (rmdir /s /q %curdir%\lib64)
if exist %curdir%\local   (rmdir /s /q %curdir%\local)
if exist %curdir%\man     (rmdir /s /q %curdir%\man)
if exist %curdir%\scripts (rmdir /s /q %curdir%\scripts)
if exist %curdir%\share   (rmdir /s /q %curdir%\share)
if exist %curdir%\tests   (rmdir /s /q %curdir%\tests)
if exist %curdir%\zato_extra_paths (rmdir /s /q %curdir%\zato_extra_paths)

if exist %curdir%\zato-agent\build     (rmdir /s /q %curdir%\zato-agent\build)
if exist %curdir%\zato-broker\build    (rmdir /s /q %curdir%\zato-broker\build)
if exist %curdir%\zato-cli\build       (rmdir /s /q %curdir%\zato-cli\build)
if exist %curdir%\zato-client\build    (rmdir /s /q %curdir%\zato-client\build)
if exist %curdir%\zato-common\build    (rmdir /s /q %curdir%\zato-common\build)
if exist %curdir%\zato-cy\build        (rmdir /s /q %curdir%\zato-cy\build)
if exist %curdir%\zato-distlock\build  (rmdir /s /q %curdir%\zato-distlock\build)
if exist %curdir%\zato-hl7\build       (rmdir /s /q %curdir%\zato-hl7\build)
if exist %curdir%\zato-lib\build       (rmdir /s /q %curdir%\zato-lib\build)
if exist %curdir%\zato-scheduler\build (rmdir /s /q %curdir%\zato-scheduler\build)
if exist %curdir%\zato-server\build    (rmdir /s /q %curdir%\zato-server\build)
if exist %curdir%\zato-sso\build       (rmdir /s /q %curdir%\zato-sso\build)
if exist %curdir%\zato-testing\build   (rmdir /s /q %curdir%\zato-testing\build)
if exist %curdir%\zato-web-admin\build (rmdir /s /q %curdir%\zato-web-admin\build)

del /s /q %curdir%\*.pyc
del /s /q %curdir%\*.pyd

del /s /q %curdir%\zato-cy\*.c
del /s /q %curdir%\zato-cy\*.html

for /d /r %%i in (*.egg-info*)    do @rmdir /s /q "%%i"
for /d /r %%i in (*__pycache__*)  do @rmdir /s /q "%%i"

echo Done cleaning up
ver
