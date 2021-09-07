echo
echo Zato Windows installation
ver

rem
rem Local aliases
rem
set curdir=%~dp0

rem
rem Install prerequisites
rem
python -m ensurepip
python -m pip install -U --upgrade pip
python -m pip install -U virtualenv==20.4.3

rem
rem Note that we install virtualenv but we do not activate it,
rem as it would otherwise prevent us from calling the following .bat file.
rem
echo Installing virtualenv in %curdir%
python -m virtualenv %curdir%

rem
rem Actually install all Python dependencies
rem
echo Setting up environment in %curdir%
start "Zato install" call %curdir%\_windows-run-install.bat

rem ##############################################################

rem
rem Local aliases
rem
set curdir=%~dp0

set ZATO_BIN=zato
set STEPS=7
set CLUSTER=quickstart-21078

echo Starting Zato cluster %CLUSTER%
echo Checking configuration

%ZATO_BIN% check-config %curdir%\server1

echo [1/%STEPS%] Redis connection OK
echo [2/%STEPS%] SQL ODB connection OK

rem Make sure TCP ports are available
echo [3/%STEPS%] Checking TCP ports availability

ZATO_BIN_PATH=C:\\zato\\Scripts\\zato
ZATO_BIN_DIR=C:\\zato\\Scripts
UTIL_DIR=C:\\zato\\util

%ZATO_BIN_DIR%\\py %UTIL_DIR%\\check_tcp_ports.py

rem Start the load balancer first ..
%ZATO_BIN% start %BASE_DIR%\\load-balancer --verbose
echo [4/%STEPS%] Load-balancer started

rem .. servers ..

%ZATO_BIN% start %BASE_DIR%\\server1 --verbose
echo [5/%STEPS%] server1 started

rem .. scheduler ..
%ZATO_BIN% start %BASE_DIR%\\scheduler --verbose
echo [6/%STEPS%] Scheduler started

rem .. web admin comes as the last one because it may ask Django-related questions.
%ZATO_BIN% start %BASE_DIR%\\web-admin --verbose
echo [%STEPS%/%STEPS%] Web admin started

cd %BASE_DIR%
echo Zato cluster %CLUSTER% started
echo Visit https://zato.io/support for more information and support options

goto comment
#!/bin/bash

set -e
export ZATO_CLI_DONT_SHOW_OUTPUT=1

SOURCE="${BASH_SOURCE[0]}"
BASE_DIR="$( dirname "$SOURCE" )"
while [ -h "$SOURCE" ]
do
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$BASE_DIR/$SOURCE"
  BASE_DIR="$( cd -P "$( dirname "$SOURCE"  )" && pwd )"
done
BASE_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

ZATO_BIN=zato
STEPS=7
CLUSTER=quickstart-21078

echo Starting Zato cluster $CLUSTER
echo Checking configuration

$ZATO_BIN check-config $BASE_DIR/server1

echo [1/$STEPS] Redis connection OK
echo [2/$STEPS] SQL ODB connection OK

# Make sure TCP ports are available
echo [3/$STEPS] Checking TCP ports availability

ZATO_BIN_PATH=`which zato`
ZATO_BIN_DIR=`python -c "import os; print(os.path.dirname('$ZATO_BIN_PATH'))"`
UTIL_DIR=`python -c "import os; print(os.path.join('$ZATO_BIN_DIR', '..', 'util'))"`

$ZATO_BIN_DIR/py $UTIL_DIR/check_tcp_ports.py

# Start the load balancer first ..
$ZATO_BIN start $BASE_DIR/load-balancer --verbose
echo [4/$STEPS] Load-balancer started

# .. servers ..

$ZATO_BIN start $BASE_DIR/server1 --verbose
echo [5/$STEPS] server1 started


# .. scheduler ..
$ZATO_BIN start $BASE_DIR/scheduler --verbose
echo [6/$STEPS] Scheduler started

# .. web admin comes as the last one because it may ask Django-related questions.
$ZATO_BIN start $BASE_DIR/web-admin --verbose
echo [$STEPS/$STEPS] Web admin started

cd $BASE_DIR
echo Zato cluster $CLUSTER started
echo Visit https://zato.io/support for more information and support options
exit 0
:comment
