#!./bin/py
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from json import loads
import logging, glob, os

# Click
import click

# psutil
import psutil

# Sarge
from sarge import run

# Zato
from zato.cli import ZatoCommand
from zato.common.component_info import get_info

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################

curdir = os.path.dirname(os.path.abspath(__file__))

# ################################################################################################################################

@click.group()
def main():
    pass

# ################################################################################################################################

def get_conn_info_from_path(path):
    """ Returns credentials and connection's info from a local path to a server having first created
    everything that is needed - username, its password and a channel to invoke API tests through.
    """
    print(path)
    return True

def get_conn_info_from_env():
    """ Returns credentials and connection's info from environment variables.
    """

# ################################################################################################################################

def _nosetests():
    nosetests_cmd = os.path.join(curdir, 'bin', 'nosetests')
    zato_packages = ' '.join([item for item in glob.iglob(os.path.join(curdir, 'zato-*'))])

    run('{} {} --with-coverage --cover-package=zato --nocapture'.format(nosetests_cmd, zato_packages))

@click.command()
def nosetests():
    _nosetests()

def _apitests():

    # First check out if we have a process running on localhost:17010.
    # If we do, check out if it appears to belong to a server.
    # If it does, this is the server to test against.
    # Otherwise, the server's URL + credentials are read from environment variables.
    # If not env variables are present, API tests cannot run.

    conn_info = None
    server_path = None

    # We expect a process to be a Zato a server if it keeps open files containing these parts in their names.
    known_file_parts = ('logs/kvdb.log', 'logs/pubsub-overflown.log', 'logs/rbac.log')

    for item in psutil.net_connections():
        if item.status == psutil.CONN_LISTEN and item.laddr[1] == 17010:
            proc = psutil.Process(pid=item.pid)
            known_found = 0
            open_files = proc.open_files()
            for f in open_files:
                if any(part in f.path for part in known_file_parts):
                    known_found += 1

            if known_found == len(known_file_parts):
                server_path = open_files[0].path.split('/logs/')[0]
                break

    # We've got a path that for 99% is a server, but let's run zato info against it to be 100% sure.
    if server_path:
        try:
            info = get_info(server_path, None)
        except IOError:
            logger.warn('Path %s does not belong to a Zato server', server_path)
        else:
            if loads(info['component_details'])['component'] == ZatoCommand.COMPONENTS.SERVER.code:
                conn_info = get_conn_info_from_path(server_path)

    # Still no connection info, try to obtain it from environment variables then.
    if not conn_info:
        conn_info = get_conn_info_from_env()

    # Ok, give up, we don't know how to connect to the target server
    if not conn_info:
        logger.warn('Cannot run API tests, could not obtain connection info from local path nor environment.')

    else:
        apitest_cmd = 'apitest'
        tests_dir = os.path.join(curdir, 'apitest')
        #run('{} run {}'.format(apitest_cmd, tests_dir))

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
