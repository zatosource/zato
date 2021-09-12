
rem
rem Local aliases
rem
set curdir=%~dp0

echo *** Downloading updates ***
git -C %curdir% pull

echo Updating environment in %curdir%
%curdir%\Scripts\python %curdir%\util\environment.py update

echo Installation updated
%curdir%\windows-bin\zato --version
