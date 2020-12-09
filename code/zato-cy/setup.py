# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function

# flake8: noqa
import os
from setuptools import Extension, find_packages, setup
from Cython.Build import cythonize

# Python 2/3 compatibility
from past.builtins import execfile

curdir = os.path.dirname(os.path.abspath(__file__))
_version_py = os.path.normpath(os.path.join(curdir, '..', '.version.py'))
_locals = {}
execfile(_version_py, _locals)
version = _locals['version']

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
          Extension(name='zato.bunch',               sources=['src/zato/cy/bunch.pyx']),
          Extension(name='zato.cache',               sources=['src/zato/cy/cache.pyx']),
          Extension(name='zato.cy.reqresp.payload',  sources=['src/zato/cy/reqresp/payload.py']),
          Extension(name='zato.cy.reqresp.request',  sources=['src/zato/cy/reqresp/request.py']),
          Extension(name='zato.cy.reqresp.response', sources=['src/zato/cy/reqresp/response.py']),
          Extension(name='zato.simpleio',            sources=['src/zato/cy/simpleio.py']),
          Extension(name='zato.url_dispatcher',      sources=['src/zato/cy/url_dispatcher.pyx']),
          Extension(name='zato.util_convert',        sources=['src/zato/cy/util/convert.pyx']),
        ], annotate=True, language_level=3),

      zip_safe = False,
)
