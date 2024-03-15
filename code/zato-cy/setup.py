# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# flake8: noqa
from platform import system as platform_system
from setuptools import Extension, find_packages, setup
from Cython.Build import cythonize

version = '3.2'

is_windows = 'windows' in platform_system().lower()

if is_windows:

    # stdlib
    import os

    # Our Python version
    python_version = '3.10.8'

    curdir = os.path.dirname(__file__)
    python_embedded_dir = os.path.join(curdir, '..', 'bundle-ext', 'python-windows', f'python-{python_version}')
    python_embedded_dir = os.path.abspath(python_embedded_dir)

    include_dirs = os.path.join(python_embedded_dir, 'Include')
    include_dirs = [os.path.join(python_embedded_dir, 'Include')]

    os.environ['PYTHONPATH'] = os.path.join(python_embedded_dir, 'Lib', 'site-packages')

else:
    include_dirs = []

setup(
      name = 'zato-cy',
      version = version,

      author = 'Zato Source s.r.o.',
      author_email = 'info@zato.io',
      url = 'https://zato.io',

      package_dir = {'':'src'},
      packages = find_packages('src'),

      include_dirs = include_dirs,

      namespace_packages = ['zato'],
      ext_modules = cythonize([
          Extension(name='zato.bunch',               sources=['src/zato/cy/bunch.pyx']),
          Extension(name='zato.cache',               sources=['src/zato/cy/cache.pyx']),
          Extension(name='zato.cy.reqresp.payload',  sources=['src/zato/cy/reqresp/payload.py']),
          Extension(name='zato.cy.reqresp.response', sources=['src/zato/cy/reqresp/response.py']),
          Extension(name='zato.simpleio',            sources=['src/zato/cy/simpleio.py']),
          Extension(name='zato.url_dispatcher',      sources=['src/zato/cy/url_dispatcher.pyx']),
          Extension(name='zato.util_convert',        sources=['src/zato/cy/util/convert.pyx']),
          Extension(name='zato.cy.wsx',              sources=['src/zato/cy/util/wsx.pyx']),
        ], annotate=True, language_level=3),

      zip_safe = False,
)
