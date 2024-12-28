#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

# Our default branch
Zato_Default_Branch=support/3.3

# Always switch to a support branch first
git checkout "${Zato_Default_Branch}" 2>/dev/null || git checkout -b "${Zato_Default_Branch}" "origin/${Zato_Default_Branch}"

echo "*** Downloading updates ***"
git -C $CURDIR pull

# An optional, specific branch or commit provided on input
while getopts "c:" opt; do
    case "$opt" in
    c)
        Zato_Branch=$OPTARG
        ;;
    esac
done

if [[ -n "${Zato_Branch}" ]];then
    # Check out a local branch/commit or create the branch from the remote one
    git checkout "${Zato_Branch}" 2>/dev/null || git checkout -b "${Zato_Branch}" "origin/${Zato_Branch}"
fi

echo Activating virtualenv in $CURDIR
source $CURDIR/bin/activate

echo Updating environment in $CURDIR
PIP_DISABLE_PIP_VERSION_CHECK=1 $CURDIR/bin/python $CURDIR/util/zato_environment.py update

echo ⭐ Installation updated to `zato --version`
