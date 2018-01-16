#!/bin/bash

set -e
shopt -s compat31


#
# Ensure current working directory is the parent directory of install.sh, i.e.
# <git_repo>/code. Taken from https://gist.github.com/josephwecker/2884332
#

function switch_to_basedir()
{
    local dir="${BASH_SOURCE[0]}"

    if [[ "$(uname -s)" == 'Darwin' ]]
    then
        local f="-f"
    fi

    while ([ -L "${dir}" ])
    do
        dir="$(readlink $f "$dir")"
    done

    cd "$(dirname "${dir}")"

    if ! [ -f "install.sh" ]
    then
        echo "$0: Could not locate <git_repo>/code directory." >&2
        exit 1
    fi
}

switch_to_basedir


#
# Run an OS-specific installer
#

if [ "$(type -p apt-get)" ]
then
    source ./clean.sh
    source ./_install-deb.sh
elif [ "$(type -p yum)" ]
then
    source ./clean.sh
    source ./_install-rhel.sh
elif [ "$(type -p apk)" ]
then
    source ./clean.sh
    source ./_install-alpine.sh
else
    echo "install.sh: Unsupported OS: could not find apt-get, yum, or apk." >&2
    exit 1
fi
