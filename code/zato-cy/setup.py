# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function

# flake8: noqa
import os
from setuptools import Extension, find_packages, setup
from Cython.Build import cythonize

version = '3.1.0'

setup(
      name = 'zato-cy',
      version = version,

      author = 'Zato Source s.r.o.',
      author_email = 'info@zato.io',
      url = 'https://zato.io',

      package_dir = {'':'src'},
      packages = find_packages('src'),

      namespace_packages = ['zato'],
      ext_modules = cythonize([
          Extension(name='zato.bunch', sources=['src/zato/cy/bunch.pyx']),
          Extension(name='zato.url_dispatcher', sources=['src/zato/cy/url_dispatcher.pyx']),
          Extension(name='zato.cache', sources=['src/zato/cy/cache.pyx']),
        ]),

      zip_safe = False,
)
