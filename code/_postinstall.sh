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

source ./_common.sh

PY_BINARY=$1
# Stamp the release hash.
git log -n 1 --pretty=format:"%H" > ./release-info/revision.txt

$PY_BINARY -m pip install \
    --no-warn-script-location   \
    -U setuptools pip

pip_install $VIRTUAL_ENV/

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

apply_patches $VIRTUAL_ENV/

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
