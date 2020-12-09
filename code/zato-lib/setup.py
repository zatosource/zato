# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# flake8: noqa

# stdlib
import os
from glob import glob
from setuptools import setup, find_packages
from setuptools import setup

# pybind11
from pybind11.setup_helpers import Pybind11Extension

# Python 2/3 compatibility
from past.builtins import execfile

curdir = os.path.dirname(os.path.abspath(__file__))
_version_py = os.path.normpath(os.path.join(curdir, '..', '.version.py'))
_locals = {}
execfile(_version_py, _locals)
version = _locals['version']

src_files = os.path.join('src', 'cpp', '*.cpp')

ext_modules = [
    Pybind11Extension(
        'zato-lib',
        sorted(glob(src_files))
    )
]

setup(
      name = 'zato-lib',
      version = version,
      author = 'Zato Source s.r.o.',
      author_email = 'info@zato.io',
      url = 'https://zato.io',
      ext_modules = ext_modules,
      zip_safe = False,
)
