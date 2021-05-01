#!/bin/bash

set -ex

if [[ "${TRAVIS_OS_NAME}" == "windows" ]];then
    choco install make
    powershell -Command 'Set-ExecutionPolicy -ExecutionPolicy RemoteSigned'
    cd $TRAVIS_BUILD_DIR/code
    [[ -f ./install.ps1 ]]
    powershell ./install.ps1
    cd $TRAVIS_BUILD_DIR
    make
fi