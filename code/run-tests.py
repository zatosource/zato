#!./bin/py
# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import glob
import os

# Click
import click

# Sarge
from sarge import run

# ################################################################################################################################

curdir = os.path.dirname(os.path.abspath(__file__))

# ################################################################################################################################

@click.group()
def main():
    pass

# ################################################################################################################################

def _nosetests():
    nosetests_cmd = os.path.join(curdir, 'bin', 'nosetests')
    zato_packages = ' '.join([item for item in glob.iglob(os.path.join(curdir, 'zato-*'))])

    run('{} {} --nocapture'.format(nosetests_cmd, zato_packages))

@click.command()
def nosetests():
    _nosetests()

def _apitests():
    apitest_cmd = 'apitest'
    tests_dir = os.path.join(curdir, 'apitest')
    run('{} run {}'.format(apitest_cmd, tests_dir))

@click.command()
def apitests():
    _apitests()

@click.command()
def all():
    _nosetests()
    _apitests()

# ################################################################################################################################

main.add_command(nosetests)
main.add_command(apitests)
main.add_command(all)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
