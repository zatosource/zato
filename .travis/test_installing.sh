#!/bin/bash

set -ex

if [[ "${TRAVIS_OS_NAME}" == "windows" ]];then
    choco install make
    mkdir -p $TRAVIS_BUILD_DIR/TempDir
    export TEMP="$TRAVIS_BUILD_DIR\\TempDir"
    export TEMPDIR="$TRAVIS_BUILD_DIR\\TempDir"
    export TMP="$TRAVIS_BUILD_DIR\\TempDir"
    powershell Add-MpPreference -ExclusionPath ${TEMPDIR}

    echo "DisableArchiveScanning..."
    powershell Start-Process -PassThru -Wait PowerShell -ArgumentList "'-Command Set-MpPreference -DisableArchiveScanning \$true'"
    echo "DisableBehaviorMonitoring..."
    powershell Start-Process -PassThru -Wait PowerShell -ArgumentList "'-Command Set-MpPreference -DisableBehaviorMonitoring \$true'"
    echo "DisableRealtimeMonitoring..."
    powershell Start-Process -PassThru -Wait PowerShell -ArgumentList "'-Command Set-MpPreference -DisableRealtimeMonitoring \$true'"

    powershell -Command 'Set-ExecutionPolicy -ExecutionPolicy RemoteSigned'
    [[ -f $TRAVIS_BUILD_DIR/code/install.ps1 ]]
    powershell $TRAVIS_BUILD_DIR/code/install.ps1
    cd $TRAVIS_BUILD_DIR
    # Adjusting path for Windows
    find -type f -name Makefile -exec sed -i -e 's|/bin|/Scripts|' {} \;
    make
fi