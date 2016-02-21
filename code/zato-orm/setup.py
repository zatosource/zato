# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# flake8: noqa
import os
from setuptools import setup, find_packages

curdir = os.path.dirname(os.path.abspath(__file__))
_version_py = os.path.normpath(os.path.join(curdir, '..', '.version.py'))
_locals = {}
execfile(_version_py, _locals)
version = _locals['version']

setup(
      name = 'zato-orm',
      version = version,

      author = 'Zato Developers',
      author_email = 'info@zato.io',
      url = 'https://zato.io',

      package_dir = {'':'src'},
      packages = find_packages('src'),

      namespace_packages = ['zato'],

      zip_safe = False,
)
