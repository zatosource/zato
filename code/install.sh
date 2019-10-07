#!/bin/bash

set -e
set -o pipefail
shopt -s compat31

# Default python binary
PY_BINARY="python"

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



#
# Run an OS-specific installer
#

# Not installed?
if ! [ -x "$(command -v $PY_BINARY)" ]; then
  if [ "$(type -p apt-get)" ]
  then
      sudo apt-get update
      sudo apt-get install -y --reinstall ${PY_BINARY}
  elif [ "$(type -p yum)" ]
  then
      sudo yum update -y
      if ! [ -x "$(command -v lsb_release)" ]; then
          sudo yum install -y redhat-lsb-core
      fi
      if [[ $PY_BINARY != python2* && -z "$(lsb_release -r|grep '\s8.')" ]];then
        # Python3 customizations
        PY_V=3
        sudo yum install -y centos-release-scl-rh
        sudo yum-config-manager --enable centos-sclo-rh-testing

        # On RHEL, enable RHSCL and RHSCL-beta repositories for you system:
        sudo yum-config-manager --enable rhel-server-rhscl-7-rpms
        sudo yum-config-manager --enable rhel-server-rhscl-beta-7-rpms

        # 2. Install the collection:
        sudo yum install -y rh-python36

        # 3. Start using software collections:
        # scl enable rh-python36 bash
        source /opt/rh/rh-python36/enable
      else
        sudo yum install -y ${PY_BINARY}
      fi
  elif [ "$(type -p apk)" ]
  then
      sudo apk add ${PY_BINARY}
      if [[ "${PY_BINARY}" == "python3" ]]
      then
          sudo apk add python3-dev
      else
          sudo apk add python-dev
      fi
  elif [ "$(uname -s)" = "Darwin" ]
  then
      brew install  $PY_BINARY
  else
      echo "install.sh: Unsupported OS: could not detect OS X, apt-get, yum, or apk." >&2
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
