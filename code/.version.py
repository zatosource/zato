# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import inspect
import json
import os
from subprocess import PIPE, run as subprocess_run

# Cannot use built in __file__ because we are execfile'd
_file = inspect.currentframe().f_code.co_filename

# Prepare all the directories needed
curdir = os.path.dirname(os.path.abspath(_file))
release_info_dir = os.path.join(curdir, 'release-info')
git_repo_dir = os.path.abspath(os.path.join(release_info_dir, '..'))

#
# This is Zato version information
#
release = open(os.path.join(release_info_dir, 'release.json')).read()
release = json.loads(release)

#
# This is last git commit ID.
#
# Make sure to use -C to specify the git directory instead of navigating to it directly;
# the latter may result in spurious pip errors, such as:
# "error in zato-agent setup command: Distribution contains no modules or packages for namespace package 'zato'"
#
git_command = ['git', 'rev-parse', '--short', 'HEAD']

try:
    process = subprocess_run(git_command, stdout=PIPE, check=True)

    revision = process.stdout
    revision = revision.decode('utf8')
    revision = revision.strip()
except Exception as e:
    version = '3.2-nogit'
else:
    version = '{}.{}+rev.{}'.format(release['major'], release['minor'], revision)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import sys

    # Echo our version
    _ = sys.stdout.write(version)

# ################################################################################################################################
# ################################################################################################################################
