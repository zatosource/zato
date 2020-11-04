#!/bin/bash

# Handles non-system aspects of Zato installation. By the time it runs:
#   * the target virtualenv must be active.
#   * the CWD must be the zato/code/ directory.
#   * all prerequisites for building dependencies must be installed.
#   * "git" and "patch" commands must be installed

if ! [ "$VIRTUAL_ENV" ]
then
    echo "_postinstall.sh: virtualenv must be active before running." >&2
    exit 1
fi

function load_basedir()
{
    if [[ "$(uname -s)" == 'Darwin' ]]
    then
        basedir="$(grealpath .)"
    else
        basedir="$(dirname "$(readlink -e "$0")")"
    fi
}

load_basedir

PY_BINARY=$1
# Stamp the release hash.
git log -n 1 --pretty=format:"%H" > ./release-info/revision.txt

$PY_BINARY -m pip install \
    --use-feature=2020-resolver \
    --no-warn-script-location   \
    -U setuptools pip

$PY_BINARY -m pip install \
    --use-feature=2020-resolver \
    --no-warn-script-location   \
    -r requirements.txt

# zato-common must be first.
$PY_BINARY -m pip install --use-feature=2020-resolver \
    -e ./zato-common    \
    -e ./zato-agent     \
    -e ./zato-broker    \
    -e ./zato-cli       \
    -e ./zato-client    \
    -e ./zato-cy        \
    -e ./zato-distlock  \
    -e ./zato-lib       \
    -e ./zato-scheduler \
    -e ./zato-server    \
    -e ./zato-web-admin \
    -e ./zato-zmq       \
    -e ./zato-sso       \
    -e ./zato-testing

# Emulate zc.buildout's split-out eggs directory for simpler local development.
ln -fs $VIRTUAL_ENV/lib/python*/site-packages $VIRTUAL_ENV/eggs

# Emulate zc.buildout's py script. Wrap rather than symlink to ensure argv[0] is correct.
cat > $VIRTUAL_ENV/bin/py <<-EOF
#!/bin/sh
exec "$VIRTUAL_ENV/bin/python" "\$@"
EOF

chmod +x $VIRTUAL_ENV/bin/py

# Create and add zato_extra_paths to the virtualenv's sys.path.
mkdir zato_extra_paths
echo "$VIRTUAL_ENV/zato_extra_paths" >> eggs/easy-install.pth

# Create a symlink to zato_extra_paths to make it easier to type it out
ln -fs $VIRTUAL_ENV/zato_extra_paths extlib

# Apply patches.
patch -p0 -d eggs < $basedir/patches/butler/__init__.py.diff
patch -p0 -d eggs < $basedir/patches/configobj.py.diff
patch -p0 -d eggs < $basedir/patches/django/db/models/base.py.diff
patch -p0 --binary -d eggs < $basedir/patches/ntlm/HTTPNtlmAuthHandler.py.diff
patch -p0 -d eggs < $basedir/patches/pykafka/topic.py.diff
patch -p0 -d eggs < $basedir/patches/redis/redis/connection.py.diff
patch -p0 -d eggs < $basedir/patches/requests/models.py.diff
patch -p0 -d eggs < $basedir/patches/requests/sessions.py.diff
patch -p0 -d eggs < $basedir/patches/ws4py/server/geventserver.py.diff

#
# On SUSE, SQLAlchemy installs to lib64 instead of lib.
#
if [ "$(type -p zypper)" ]
then
    patch -p0 -d eggs64 < $basedir/patches/sqlalchemy/sql/crud.py.diff
else
    patch -p0 -d eggs < $basedir/patches/sqlalchemy/sql/crud.py.diff
fi

# Add the 'zato' command ..
cat > $VIRTUAL_ENV/bin/zato <<-EOF
#!$VIRTUAL_ENV/bin/python3

# Zato
from zato.cli.zato_command import main

if __name__ == '__main__':

    # stdlib
    import re
    import sys

    # This is needed by SUSE
    sys.path.append('$VIRTUAL_ENV/lib64/python3.6/site-packages/')

    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())

EOF

# .. and make the command executable.
chmod 755 $VIRTUAL_ENV/bin/zato
