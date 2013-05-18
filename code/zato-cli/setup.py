# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '1.0'

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
      entry_points = '''
      [console_scripts]
      zato = zato.cli.zato_command:main
      '''
)
