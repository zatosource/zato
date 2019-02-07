#!/bin/bash

set -e
set -o pipefail
shopt -s compat31

PY_BINARY="python2.7"

# Taken from https://stackoverflow.com/a/14203146
OPTIND=1
while getopts "p:" opt; do
    case "$opt" in
    p)
        shift
        PY_BINARY=$1
        ;;
    esac
done
shift $((OPTIND-1))
[ "${1:-}" = "--" ] && shift

# Confirm such a Python version is accessible
if ! [ -x "$(command -v $PY_BINARY)" ]; then
  echo "Error: Could not find Python binary '$PY_BINARY'"
  exit 1
fi

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
    source ./_install-deb.sh $PY_BINARY
elif [ "$(type -p yum)" ]
then
    source ./clean.sh
    source ./_install-rhel.sh $PY_BINARY
elif [ "$(type -p apk)" ]
then
    source ./clean.sh
    source ./_install-alpine.sh $PY_BINARY
elif [ "$(uname -s)" = "Darwin" ]
then
    source ./clean.sh
    source ./_install-osx.sh $PY_BINARY
else
    echo "install.sh: Unsupported OS: could not detect OS X, apt-get, yum, or apk." >&2
    exit 1
fi
