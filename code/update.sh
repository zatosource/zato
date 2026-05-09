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

if ! [ -x "$(command -v cargo)" ] && ! [ -f "$HOME/.cargo/env" ]; then
    echo Installing Rust
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi

if [ -f "$HOME/.cargo/env" ]; then
    . "$HOME/.cargo/env"
fi

echo Installing maturin
$CURDIR/support-linux/bin/uv pip install maturin

echo Building Rust components
make -C "$CURDIR/.." build

echo ⭐ Installation updated to `zato --version`
