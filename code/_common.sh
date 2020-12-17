#!/bin/bash

# Common functions

# Apply a list of patches to source code
function apply_patches() {
    # Path to code/ can be specified
    localpath="${1:-.}"

    # Apply patches.
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/butler/__init__.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/configobj.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/django/db/models/base.py.diff
    patch --forward -p0 --binary -d $localpath/eggs < $localpath/patches/ntlm/HTTPNtlmAuthHandler.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/pykafka/topic.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/redis/redis/connection.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/requests/models.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/requests/sessions.py.diff
    patch --forward -p0 -d $localpath/eggs < $localpath/patches/ws4py/server/geventserver.py.diff

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
        -r requirements.txt

    # zato-common must be first.
    $localpath/bin/pip install \
        -e ./zato-common      \
        -e ./zato-agent       \
        -e ./zato-broker      \
        -e ./zato-cli         \
        -e ./zato-client      \
        -e ./zato-cy          \
        -e ./zato-distlock    \
        -e ./zato-hl7         \
        -e ./zato-lib         \
        -e ./zato-scheduler   \
        -e ./zato-server      \
        -e ./zato-web-admin   \
        -e ./zato-zmq         \
        -e ./zato-sso         \
        -e ./zato-testing
}