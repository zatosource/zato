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

PY_BINARY=$1

# If it starts with "python2" then we install extra pip dependencies for Python 2.7,
# otherwise, extra dependencies for Python 3.x will be installed.
if [[ $(${PY_BINARY} -c 'import sys; print(sys.version_info[:][0])') -eq 2 ]]
then
    HAS_PYTHON2=1
    HAS_PYTHON3=0
    EXTRA_REQ_VERSION=27
else
    HAS_PYTHON2=0
    HAS_PYTHON3=1
    EXTRA_REQ_VERSION=3
fi


# Stamp the release hash.
git log -n 1 --pretty=format:"%H" > ./release-info/revision.txt

$PY_BINARY -m pip install -U setuptools pip

# SciPy builds require NumPy available in setup.py, so install it separately.
$PY_BINARY -m pip install numpy==1.14.0
# pip install pipdeptree
$PY_BINARY -m pip install -r requirements.txt
$PY_BINARY -m pip install -r _req_py$EXTRA_REQ_VERSION.txt


# zato-common must be first.
$PY_BINARY -m pip install \
    -e ./zato-common \
    -e ./zato-agent \
    -e ./zato-broker \
    -e ./zato-cli \
    -e ./zato-client \
    -e ./zato-cy \
    -e ./zato-distlock \
    -e ./zato-scheduler \
    -e ./zato-server \
    -e ./zato-web-admin \
    -e ./zato-zmq \
    -e ./zato-sso

# Emulate zc.buildout's split-out eggs directory for simpler local development.
ln -fs $VIRTUAL_ENV/lib/python*/site-packages eggs

# Emulate zc.buildout's (now redundant) py script. Wrap rather than symlink to
# ensure argv[0] is correct.
cat > $VIRTUAL_ENV/bin/py <<-EOF
#!/bin/sh
exec "$(pwd)/bin/python" "\$@"
EOF

chmod +x $VIRTUAL_ENV/bin/py

# Create and add zato_extra_paths to the virtualenv's sys.path.
mkdir zato_extra_paths
echo "$(pwd)/zato_extra_paths" >> eggs/easy-install.pth

# Apply patches.
patch -p0 -d eggs < patches/butler/__init__.py.diff
patch -p0 -d eggs < patches/configobj.py.diff
patch -p0 -d eggs < patches/psycopg2/__init__.py.diff --forward || true
patch -p0 -d eggs < patches/redis/redis/connection.py.diff
patch -p0 -d eggs < patches/requests/models.py.diff
patch -p0 -d eggs < patches/requests/sessions.py.diff
patch -p0 -d eggs < patches/sqlalchemy/sql/crud.py.diff
patch -p0 -d eggs < patches/ws4py/server/geventserver.py.diff

if [ $HAS_PYTHON2 == 1 ]
then
    patch -p0 -d eggs < patches/jsonpointer/jsonpointer.py.diff
    patch -p0 -d eggs < patches/anyjson/__init__.py.diff
    patch -p0 -d eggs < patches/oauth/oauth.py.diff
fi
