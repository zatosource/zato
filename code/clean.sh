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

rm -rf ./.coverage
rm -rf ./.installed.cfg
rm -rf ./bin
rm -rf ./develop-eggs
rm -rf ./docs
rm -rf ./downloads
rm -rf ./eggs
rm -rf ./get-pip.py
rm -rf ./include
rm -rf ./lib
rm -rf ./lib64
rm -rf ./local
rm -rf ./man
rm -rf ./parts
rm -rf ./share
rm -rf ./tests
rm -rf ./zato_extra_paths

rm -rf ./zato-agent/build
rm -rf ./zato-broker/build
rm -rf ./zato-cli/build
rm -rf ./zato-client/build
rm -rf ./zato-common/build
rm -rf ./zato-cy/build
rm -rf ./zato-distlock/build
rm -rf ./zato-lib/build
rm -rf ./zato-scheduler/build
rm -rf ./zato-server/build
rm -rf ./zato-sso/build
rm -rf ./zato-testing/build
rm -rf ./zato-web-admin/build

find . -name \*~ -delete
find . -name \*.pyc -delete
find . -name \*.so -delete
find ./zato-cy/ -name \*.c -delete
find ./zato-cy/ -name \*.html -delete
