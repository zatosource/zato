# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# flake8: noqa
from setuptools import setup

version = '3.3'

ext_modules = []

_ = setup(
      name = 'zato-lib',
      version = version,
      author = 'Zato Source s.r.o.',
      author_email = 'info@zato.io',
      url = 'https://zato.io',
      ext_modules = ext_modules,
      zip_safe = False,
)
