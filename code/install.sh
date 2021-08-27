#!/bin/bash

set -e
set -o pipefail
shopt -s compat31

# Default python binary
PY_BINARY="${PY_BINARY:-python3}"
INSTALL_PYTHON="y"

# Taken from https://stackoverflow.com/a/14203146
OPTIND=1
while getopts "sp:" opt; do
    case "$opt" in
    p)
        PY_BINARY=$OPTARG
        ;;
    s)
        INSTALL_PYTHON=n
        ;;
    esac
done
shift $((OPTIND-1))
[ "${1:-}" = "--" ] && shift

#
# Run an OS-specific installer
#

# Not installed?
if ! [ -x "$(command -v $PY_BINARY)" ]; then
    if [ "$(type -p apt-get)" ]
    then
        sudo apt-get update
        [ "$INSTALL_PYTHON" == "y" ] && sudo apt-get install -y --reinstall ${PY_BINARY}
    elif [ "$(type -p yum)" ]
    then
        if [ "$(type -p dnf)" ]
        then
            sudo dnf update -y

            if [ ! "$(type -p lsb_release)" ]
            then
                sudo dnf install -y redhat-lsb-core
            fi

            if [ ! "$(type -p python3)" ]
            then
                [ "$INSTALL_PYTHON" == "y" ] && sudo dnf install -y python3
            fi
        else
            sudo yum update -y

            if [ ! "$(type -p lsb_release)" ]
            then
                sudo yum install -y redhat-lsb-core
            fi

            if [ ! "$(type -p python3)" ]
            then
                [ "$INSTALL_PYTHON" == "y" ] && sudo yum install -y python3
            fi
        fi
    elif [ "$(uname -s)" = "Darwin" ]
    then
        [ "$INSTALL_PYTHON" == "y" ] && brew install  $PY_BINARY
    else
        echo "install.sh: Unsupported OS: could not detect OS X, apt-get or yum." >&2
        exit 1
    fi
fi

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
    # source ./clean.sh
    source ./_install-deb.sh $PY_BINARY ${INSTALL_PYTHON}
elif [ "$(type -p yum)" ] || [ "$(type -p dnf)" ]
then
    source ./clean.sh
    source ./_install-rhel.sh $PY_BINARY ${INSTALL_PYTHON}
elif [ "$(uname -s)" = "Darwin" ]
then
    source ./clean.sh
    source ./_install-mac.sh $PY_BINARY ${INSTALL_PYTHON}
elif [ "$(type -p zypper)" ]
then
    source ./clean.sh
    source ./_install-suse.sh $PY_BINARY ${INSTALL_PYTHON}
else
    echo "install.sh: Unsupported OS: could not detect Mac, apt-get, yum or zypper." >&2
    exit 1
fi
