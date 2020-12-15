#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

echo "*** Downloading updates ***"
git -C $CURDIR pull

echo "*** Installing updates ***"
$CURDIR/bin/pip install \
    --no-warn-script-location   \
    -r requirements.txt

# zato-common must be first.
$CURDIR/bin/pip install \
    -e ./zato-common      \
    -e ./zato-agent       \
    -e ./zato-broker      \
    -e ./zato-cli         \
    -e ./zato-client      \
    -e ./zato-cy          \
    -e ./zato-distlock    \
    -e ./zato-hl7         \
    -e ./zato-lib         \
    -e ./zato-scheduler   \
    -e ./zato-server      \
    -e ./zato-web-admin   \
    -e ./zato-zmq         \
    -e ./zato-sso         \
    -e ./zato-testing