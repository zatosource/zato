#!/bin/bash

set -e
set -o pipefail
shopt -s compat31

# Default python binary
PY_BINARY="${PY_BINARY:-python3}"
INSTALL_PYTHON="y"

# Parse arguments
SKIP_OS="n"
CLEAR_VENV="n"
while [[ $# -gt 0 ]]; do
    case "$1" in
    --skip-os)
        SKIP_OS=y
        shift
        ;;
    --clear)
        CLEAR_VENV=y
        shift
        ;;
    -p)
        PY_BINARY="$2"
        shift 2
        ;;
    -s)
        INSTALL_PYTHON=n
        shift
        ;;
    *)
        shift
        ;;
    esac
done

#
# Run an OS-specific installer
#

# Not installed?
if ! [ -x "$(command -v $PY_BINARY)" ]; then
    if [[ "$SKIP_OS" != "y" ]]; then
        if [ "$(type -p apt-get)" ]
        then
            sudo apt-get update
            [ "$INSTALL_PYTHON" == "y" ] && sudo apt-get install -y --reinstall ${PY_BINARY}
        else
            echo "install.sh: Unsupported OS: only Ubuntu 24.04+ is supported." >&2
            exit 1
        fi
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

    while ([ -L "${dir}" ])
    do
        dir="$(readlink -f "$dir")"
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
# Run the Ubuntu installer
#

if [ "$(type -p apt-get)" ]
then
    source ./_install-deb.sh $PY_BINARY ${INSTALL_PYTHON} ${SKIP_OS} ${CLEAR_VENV}
else
    echo "install.sh: Unsupported OS: only Ubuntu 24.04+ is supported." >&2
    exit 1
fi
