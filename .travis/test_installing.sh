#!/bin/bash

set -ex

if [[ "${TRAVIS_OS_NAME}" == "windows" ]];then
    powershell -Command 'Set-ExecutionPolicy -ExecutionPolicy RemoteSigned'
    [[ -f $TRAVIS_BUILD_DIR/code/install.ps1 ]]
    powershell $TRAVIS_BUILD_DIR/code/install.ps1
    cd $TRAVIS_BUILD_DIR
    make
fi