# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function

# flake8: noqa
from setuptools import Extension, find_packages, setup
from Cython.Build import cythonize
from setuptools import setup, find_packages

version = '3.2'

setup(
      name = 'zato-hl7',
      version = version,

      author = 'Zato Source s.r.o.',
      author_email = 'info@zato.io',
      url = 'https://zato.io',

      package_dir = {'':'src'},
      packages = find_packages('src'),

      namespace_packages = ['zato'],
      ext_modules = cythonize([
          Extension(name='zato.hl7.cy.placeholder',  sources=['src/zato/hl7/cy/placeholder.py']),
        ], annotate=True, language_level=3),

      zip_safe = False,
)
