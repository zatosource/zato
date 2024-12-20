# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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
release = open(os.path.join(release_info_dir, 'release.json')).read()
release = json.loads(release)

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
# the latter may result in spurious pip errors, such as:
# "error in zato-agent setup command: Distribution contains no modules or packages for namespace package 'zato'"
#
git_command_date = ['git', 'log', '-1', '--pretty=%cd', '--date=format:%Y.%m.%d']
git_command_revision = ['git', 'rev-parse', '--short', 'HEAD']

try:

    process_date = subprocess_run(git_command_date, stdout=PIPE, check=True)
    date = process_date.stdout
    date = date.decode('utf8')
    date = date.strip()

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

    version = f'3.3-nogit-{suffix}'
else:

    major = release['major']
    minor = release['minor']

    version = f'{major}.{minor}.{date}+rev.{revision}'

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import sys

    # Echo our version
    _ = sys.stdout.write(version)

# ################################################################################################################################
# ################################################################################################################################
