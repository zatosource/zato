# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
import inspect
import json
import os
import platform
from subprocess import PIPE, run as subprocess_run

# ################################################################################################################################
# ################################################################################################################################

# Cannot use built in __file__ because we are execfile'd
_file = inspect.currentframe().f_code.co_filename # type: ignore

# ################################################################################################################################
# ################################################################################################################################

# Prepare all the directories needed
curdir = os.path.dirname(os.path.abspath(_file))
release_info_dir = os.path.join(curdir, 'release-info')
git_repo_dir = os.path.abspath(os.path.join(release_info_dir, '..'))

# ################################################################################################################################
# ################################################################################################################################

#
# This is Zato version information
#
with open(os.path.join(release_info_dir, 'release.json')) as f:
    release = json.loads(f.read())

# ################################################################################################################################
# ################################################################################################################################

platform_system = platform.system().lower()

is_windows = 'windows' in platform_system
is_linux   = 'linux'   in platform_system # noqa: E272

# ################################################################################################################################
# ################################################################################################################################

#
# This is the last git commit ID.
#
# Make sure to use -C to specify the git directory instead of navigating to it directly;
# the latter may result in spurious pip errors.
#
git_command_date = ['git', 'log', '-1', '--pretty=%ct']
git_command_revision = ['git', 'rev-parse', '--short=9', 'HEAD']

try:

    process_date = subprocess_run(git_command_date, stdout=PIPE, check=True)
    timestamp = process_date.stdout
    timestamp = timestamp.decode('utf8')
    timestamp = timestamp.strip()
    dt = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    date = dt.strftime('%Y%m%d.%H%M')

    process_revision = subprocess_run(git_command_revision, stdout=PIPE, check=True)
    revision = process_revision.stdout
    revision = revision.decode('utf8')
    revision = revision.strip()

except Exception as e:

    if is_windows:
        suffix = 'windows'
    elif is_linux:
        suffix = 'linux'
    else:
        suffix = platform_system

    version = f'4.1-nogit-{suffix}'
else:

    major = release['major']
    minor = release['minor']

    version = f'{major}.{minor}.{date}.{revision}'

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import sys

    # Echo our version
    _ = sys.stdout.write(version)

# ################################################################################################################################
# ################################################################################################################################
