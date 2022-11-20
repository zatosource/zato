
set curdir=%~dp0

%curdir%\Scripts\python %curdir%\util\zato_environment.py install

%curdir%\Scripts\zato.py --version
