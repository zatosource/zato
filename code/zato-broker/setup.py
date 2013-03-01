# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '1.0.0'

setup(
      name = 'zato-broker',
      version = version,

      author = 'Zato',
      author_email = 'Zato',
      url = 'Zato',

      package_dir = {'':'src'},
      packages = find_packages('src'),

      namespace_packages = ['zato'],

      zip_safe = False,
)
