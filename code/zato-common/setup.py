# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# flake8: noqa

from setuptools import setup, find_packages

version = '1.2.1'

setup(
      name = 'zato-common',
      version = version,

      author = 'Zato Developers',
      author_email = 'info@zato.io',
      url = 'https://zato.io',
      license = 'GNU Lesser General Public License v3 (LGPLv3)',
      platforms = 'OS Independent',
      description = 'Constants and utils common across the whole of Zato ESB and app server (https://zato.io)',

      package_dir = {'':'src'},
      packages = find_packages('src'),
      namespace_packages = ['zato'],
      
      install_requires=[
          'anyjson==0.3.3',
          'bunch==1.0.1',
          'configobj==4.7.2',
          'bzr==2.2.3',
          'distutils2==1.0a4',
          'lxml==3.0.1',
          'mock==1.0.1',
          'nose==1.3.0',
          'pip==1.1',
          'python-dateutil==2.1',
          'pytz==2012h',
          'pyzmq==2.2.0.1',
          'pyzmq-static==2.2',
          'redis==2.7.6',
          'springpython==1.3.0RC1',
          'urllib3==1.5',
          ],
      
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
          'Topic :: Database',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Topic :: Internet',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
          'Topic :: Internet :: File Transfer Protocol (FTP)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Object Brokering',
          ],

      zip_safe = False,
)
