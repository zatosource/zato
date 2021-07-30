#!/bin/bash

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

# Common functions

# Apply a list of patches to source code
function apply_patches() {
    # Path to code/ can be specified
    localpath="${1:-.}"

    # Apply patches.
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/butler/__init__.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/django/db/models/base.py.diff
    patch --forward -p0 --binary -d $localpath/eggs < $localpath/patches/ntlm/HTTPNtlmAuthHandler.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/pykafka/topic.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/redis/redis/connection.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/requests/models.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/requests/sessions.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/ws4py/server/geventserver.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/sqlalchemy/sql/dialects/postgresql/pg8000.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/pg8000/core.py.diff

    #
    # On SUSE, SQLAlchemy installs to lib64 instead of lib.
    #
    if [[ -e "$localpath/eggs64" && "$(type -p zypper)" ]]
    then
        patch --forward -p0 -d $localpath/eggs64 < $localpath/patches/sqlalchemy/sql/crud.py.diff || true
    else
        patch --forward -p0 -d $localpath/eggs < $localpath/patches/sqlalchemy/sql/crud.py.diff || true
    fi
}

# Install libraries using pip
function pip_install() {
    # Path to code/ can be specified
    localpath="${1:-.}"

    echo "*** Installing updates ***"

    $localpath/bin/pip install \
        --no-warn-script-location   \
        -r $CURDIR/requirements.txt

    # zato-common must be first.
    $localpath/bin/pip install \
        -e $CURDIR/zato-common      \
        -e $CURDIR/zato-agent       \
        -e $CURDIR/zato-broker      \
        -e $CURDIR/zato-cli         \
        -e $CURDIR/zato-client      \
        -e $CURDIR/zato-cy          \
        -e $CURDIR/zato-distlock    \
        -e $CURDIR/zato-hl7         \
        -e $CURDIR/zato-lib         \
        -e $CURDIR/zato-scheduler   \
        -e $CURDIR/zato-server      \
        -e $CURDIR/zato-web-admin   \
        -e $CURDIR/zato-zmq         \
        -e $CURDIR/zato-sso         \
        -e $CURDIR/zato-testing

    # Delete packages no longer needed
    $localpath/bin/pip uninstall -y \
        imbox \
        pycrypto \
        python-keyczar \
        2> /dev/null || true
}
