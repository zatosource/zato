# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""
from distutils.core import setup
from setuptools import find_packages

version = '1.1'

setup(
    name = 'zato-web-admin',
    version = version,

    author = 'Zato Developers',
    author_email = 'info@zato.io',
    url = 'https://zato.io',

    package_dir = {'':'src'},
    packages = find_packages('src'),

    namespace_packages = ['zato'],
    include_package_data = True,

    install_requires=[
        'django-openid-auth>=0.5',
        'django-settings>=1.3-11',
        'python-openid>=2.2.5',
        'Pygments>=1.6',
    ],
    zip_safe = False,
)
