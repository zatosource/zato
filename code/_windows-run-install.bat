
set curdir=%~dp0

%curdir%\Scripts\python %curdir%\util\environment.py install

%curdir%\Scripts\zato --version
