# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# flake8: noqa
import os
from setuptools import setup, find_packages

version = '3.0.2'

long_description = description = 'Python API client for Zato - ESB, SOA, REST, APIs and Cloud Integrations in Python (https://zato.io)'

def parse_requirements(requirements):
    ignored = ['#', 'setuptools', '-e']

    with open(requirements) as f:
        return [line.split('==')[0] for line in f if line.strip() and not any(line.startswith(prefix) for prefix in ignored)]

setup(
      name = 'zato-client',
      version = version,

      author = 'Zato Source s.r.o.',
      author_email = 'info@zato.io',
      url = 'https://zato.io',
      license = 'GNU Lesser General Public License v3 (LGPLv3)',
      platforms = 'OS Independent',
      description = description,
      long_description = description,

      package_dir = {'':'src'},
      packages = find_packages('src'),
      namespace_packages = ['zato'],

      install_requires = parse_requirements(
          os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')),

      keywords=('soa eai esb middleware messaging queueing asynchronous integration performance http zeromq framework events agile broker messaging server jms enterprise python middleware clustering amqp nosql websphere mq wmq mqseries ibm amqp zmq'),
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Framework :: Buildout',
          'Intended Audience :: Customer Service',
          'Intended Audience :: Developers',
          'Intended Audience :: Financial and Insurance Industry',
          'Intended Audience :: Healthcare Industry',
          'Intended Audience :: Information Technology',
          'Intended Audience :: Telecommunications Industry',
          'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: C',
          'Programming Language :: Python :: 2 :: Only',
          'Programming Language :: Python :: 2.7',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Topic :: Communications',
          'Topic :: Database',
          'Topic :: Internet',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
          'Topic :: Internet :: File Transfer Protocol (FTP)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Object Brokering',
          ],

      zip_safe = False,
)
