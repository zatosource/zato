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
from uuid import uuid4
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
from zato.common.util import get_client_from_server_conf

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
    """ Returns a Zato client basing on a path to a local server.
    """
    client = get_client_from_server_conf(path)

    # Just to be on the safe side
    client.invoke('zato.ping')

    pubapi_id = None

    # Get pubapi user or return None to signal that no connection info could be found
    for item in client.invoke('zato.security.get-list', {'cluster_id': client.cluster_id}).data:
        if item['username'] == 'pubapi':
            pubapi_id = item['id']
            break
    else:
        return None

    # Update password to a well-known one - there is no way to learn the previous one through the API
    password = uuid4().hex
    client.invoke('zato.security.basic-auth.change-password', {'id':pubapi_id, 'password1':password, 'password2':password})

    return {
        'ZATO_API_TEST_SERVER': client.address,
        'ZATO_API_TEST_PUBAPI_USER': 'pubapi',
        'ZATO_API_TEST_PUBAPI_PASSWORD': password,
        'ZATO_API_TEST_CLUSTER_ID': str(client.cluster_id)
        }

def get_conn_info_from_env():
    """ Returns a Zato client basing on a set of environment variables allowing for a client's construction.
    """
    out = {}
    for key in ('ZATO_API_TEST_SERVER', 'ZATO_API_TEST_PUBAPI_USER', 'ZATO_API_TEST_PUBAPI_PASSWORD', 'ZATO_API_TEST_CLUSTER_ID'):
        out[key] = os.environ.get(key, 'NONE_FOUND_{}'.format(key))

    return out

# ################################################################################################################################

def _nosetests():
    nosetests_cmd = os.path.join(curdir, 'bin', 'nosetests')
    zato_packages = ' '.join([item for item in glob.iglob(os.path.join(curdir, 'zato-*'))])

    run('{} {} --nocapture'.format(nosetests_cmd, zato_packages))

@click.command()
def nosetests():
    _nosetests()

def _apitests():

    # First check out if we have a process running on localhost:17010.
    # If we do, check out if it appears to belong to a server.
    # If it does, this is the server to test against.
    # Otherwise, the server's URL + credentials are read from environment variables.
    # If no env variables are present, API tests cannot run.

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
        logger.warn('Cannot run API tests, could not obtain conn info from local path nor environment.')

    else:
        os.environ.update(**conn_info)
        apitest_cmd = 'apitest'
        tests_dir = os.path.join(curdir, 'apitest')
        run('{} run {}'.format(apitest_cmd, tests_dir))

        # TODO: The output should be consulted - it's possible that someone
        # will want to stop the tests if API test don't succeed.

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
