rem
rem Local aliases
rem
rem
rem Local aliases
rem
set curdir=%~dp0

echo Downloading updates
git -C %curdir% pull

python %curdir%\util\post_install.py update_paths
%curdir%\Scripts\python %curdir%\util\post_install.py update_registry

%curdir%\Scripts\python -m pip uninstall -y pip
%curdir%\Scripts\python -m ensurepip
%curdir%\Scripts\python -m pip install -U --upgrade pip

echo Updating environment in %curdir%
%curdir%\Scripts\python %curdir%\util\zato_environment.py update

echo Installation updated
%curdir%\windows-bin\zato --version
