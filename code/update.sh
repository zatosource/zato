#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

source $CURDIR/_common.sh

while getopts "c:" opt; do
    case "$opt" in
    c)
        ZATO_BRANCH=$OPTARG
        ;;
    esac
done

echo "*** Downloading updates ***"
git -C $CURDIR pull

if [[ -n "${ZATO_BRANCH}" ]];then
    # Checkout a local branch/commit or create the branch from the remote one
    git checkout "${ZATO_BRANCH}" 2>/dev/null || git checkout -b "${ZATO_BRANCH}" "origin/${ZATO_BRANCH}"
fi

pip_install $CURDIR

apply_patches $CURDIR
