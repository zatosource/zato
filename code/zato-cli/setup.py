# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# flake8: noqa

# flake8: noqa
import os
from json import loads
from setuptools import setup, find_packages

curdir = os.path.dirname(os.path.abspath(__file__))
release_info_dir = os.path.join(curdir, '..', 'release-info')
release = open(os.path.join(release_info_dir, 'release.json')).read()
release = loads(release)
revision = open(os.path.join(release_info_dir, 'revision.txt')).read()[:8]

version = '{}.{}.{}.rev-{}'.format(release['major'], release['minor'], release['micro'], revision)

setup(
      name = 'zato-cli',
      version = version,

      author = 'Zato Developers',
      author_email = 'info@zato.io',
      url = 'https://zato.io',

      package_dir = {'':'src'},
      packages = find_packages('src'),

      namespace_packages = ['zato'],

      zip_safe = False,
      entry_points = """
      [console_scripts]
      zato = zato.cli.zato_command:main
      """
)
