rem
rem Local aliases
rem
set curdir=%~dp0

echo *** Downloading updates ***
git -C %curdir% pull

%curdir%\Scripts\python -m pip uninstall -y pip
%curdir%\Scripts\python -m ensurepip
%curdir%\Scripts\python -m pip install -U --upgrade pip

%curdir%\Scripts\python %curdir%\util\post_install.py

echo Updating environment in %curdir%
%curdir%\Scripts\python %curdir%\util\environment.py update

echo Installation updated
%curdir%\windows-bin\zato --version

