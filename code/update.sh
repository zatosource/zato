#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

# We never update base packages from this script
export Zato_Should_Update_Base=False

# Our default branch
Zato_Default_Branch=support/4.1

# Always switch to a support branch first
git checkout "${Zato_Default_Branch}" 2>/dev/null || git checkout -b "${Zato_Default_Branch}" "origin/${Zato_Default_Branch}"

echo "*** Downloading updates ***"
git_pull_output=$(git -C $CURDIR pull 2>&1)
echo "$git_pull_output"

if echo "$git_pull_output" | grep -q "zato-cy/"; then
    export Zato_Should_Update_Cy=True
else
    export Zato_Should_Update_Cy=False
fi

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
