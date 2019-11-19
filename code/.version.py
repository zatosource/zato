# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import inspect, json, os

# sh
import sh

# Cannot use built in __file__ because we are execfile'd
_file = inspect.currentframe().f_code.co_filename

# Preapre all the directories needed
curdir = os.path.dirname(os.path.abspath(_file))
release_info_dir = os.path.join(curdir, 'release-info')
git_repo_dir = os.path.join(release_info_dir, '..')

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
with sh.pushd(release_info_dir):
    revision = sh.git('rev-parse', '--short', 'HEAD').strip()

version = '{}.{}+rev.{}'.format(release['major'], release['minor'], revision)
