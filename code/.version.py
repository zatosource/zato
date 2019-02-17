# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import inspect, json, os

# Cannot use built in __file__ because we are execfile'd
_file = inspect.currentframe().f_code.co_filename

curdir = os.path.dirname(os.path.abspath(_file))
release_info_dir = os.path.join(curdir, 'release-info')
release = open(os.path.join(release_info_dir, 'release.json')).read()
release = json.loads(release)
revision = open(os.path.join(release_info_dir, 'revision.txt')).read()[:8]

version = '{}.{}.{}+rev.{}'.format(release['major'], release['minor'], release['micro'], revision)
