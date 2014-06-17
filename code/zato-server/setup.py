# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from setuptools import setup, find_packages

version = '1.1'

setup(
    name = 'zato-server',
    version = version,

    author = 'Zato Developers',
    author_email = 'info@zato.io',
    url = 'https://zato.io',

    package_dir = {'':'src'},
    packages = find_packages('src'),

    namespace_packages = ['zato'],
    install_requires = [
        'arrow>=0.4.2',
        'dpath>=1.2-70',
        'jsonpointer>=1.3',
        'kombu>=3.0.19',
        'pika>=0.9.13',
        'retools>=0.4.1',
        'xmltodict>=0.9.0',
    ],

    zip_safe = False,
)
