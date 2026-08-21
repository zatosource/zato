# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
from time import sleep, time
from typing import NamedTuple

# Odoo
import odoolib

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Docker images the servers run from
    Odoo_Image       = 'odoo:17'
    PostgreSQL_Image = 'postgres:16'

    # The login the database is created with - the odoo image's own default
    Login = 'admin'
    Password = 'admin'

    # The port Odoo listens on inside its container
    Odoo_Port = 8069

    # How long to wait for Odoo to initialize its database and accept logins -
    # installing the base module on first start takes a while
    Ready_Timeout = 600

    # How long to sleep between login attempts
    Ready_Sleep = 2

    # After how many login attempts the wait reports its progress
    Ready_Report_Every = 10

# ################################################################################################################################
# ################################################################################################################################

class OdooServer(NamedTuple):
    container_name: str
    db_container_name: str
    network_name: str
    details: 'stranydict'

# ################################################################################################################################
# ################################################################################################################################

def _remove_stale_container(name:'str') -> 'None':
    """ Removes a container left over from a previous, possibly interrupted, run.
    """
    _ = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, check=False)

# ################################################################################################################################

def _remove_stale_network(name:'str') -> 'None':
    """ Removes a network left over from a previous, possibly interrupted, run.
    """
    _ = subprocess.run(['docker', 'network', 'rm', name], capture_output=True, check=False)

# ################################################################################################################################

def stop_odoo(server:'OdooServer') -> 'None':
    """ Stops both containers and removes the network they talked over.
    """
    _ = subprocess.run(['docker', 'stop', server.container_name], capture_output=True, check=False)
    _ = subprocess.run(['docker', 'stop', server.db_container_name], capture_output=True, check=False)
    _ = subprocess.run(['docker', 'network', 'rm', server.network_name], capture_output=True, check=False)

# ################################################################################################################################

def _wait_until_ready(port:'int', db_name:'str') -> 'None':
    """ Retries logging in until Odoo has initialized the database and accepts
    the default credentials, or the timeout is reached.
    """
    deadline = time() + ModuleCtx.Ready_Timeout
    last_error = ''
    attempt_count = 0

    while time() < deadline:

        try:
            connection = odoolib.get_connection(
                hostname='localhost', protocol='jsonrpc', port=port, # type: ignore
                database=db_name, login=ModuleCtx.Login, password=ModuleCtx.Password)

            connection.check_login()
            return

        except Exception as e:
            last_error = str(e)

            # A long wait reports its progress and the last error seen.
            attempt_count += 1

            if attempt_count % ModuleCtx.Ready_Report_Every == 0:
                print(f'Still waiting for Odoo, attempt {attempt_count}, last error: {last_error}', flush=True)

            sleep(ModuleCtx.Ready_Sleep)

    raise Exception(f'Odoo at localhost:{port} did not become ready, last error: {last_error}')

# ################################################################################################################################

def start_odoo(
    *,
    container_name:'str',
    db_container_name:'str',
    network_name:'str',
    port:'int',
    db_name:'str',
    db_password:'str',
    ) -> 'OdooServer':
    """ Starts a real Odoo server - a PostgreSQL container underneath it, both on
    a network of their own - and initializes a database with the base module
    and no demo data, waiting until logins are accepted.
    """

    # Each phase of the startup reports itself.
    print(f'Starting Odoo containers {container_name} and {db_container_name} on port {port}', flush=True)

    _remove_stale_container(container_name)
    _remove_stale_container(db_container_name)
    _remove_stale_network(network_name)

    # The two containers talk over a network of their own
    _ = subprocess.run(['docker', 'network', 'create', network_name], check=True, capture_output=True)

    # The database server underneath Odoo - the odoo user and the postgres
    # maintenance database are what the odoo image's entrypoint expects
    db_command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', db_container_name,
        '--network', network_name,
        '-e', 'POSTGRES_USER=odoo',
        '-e', 'POSTGRES_PASSWORD=' + db_password,
        '-e', 'POSTGRES_DB=postgres',
        ModuleCtx.PostgreSQL_Image,
    ]

    _ = subprocess.run(db_command, check=True, capture_output=True)

    # Odoo itself - the arguments after the image name go to the odoo process,
    # creating the database with the base module and no demo data on first start
    odoo_command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', container_name,
        '--network', network_name,
        '-p', f'{port}:{ModuleCtx.Odoo_Port}',
        '-e', 'HOST=' + db_container_name,
        '-e', 'USER=odoo',
        '-e', 'PASSWORD=' + db_password,
        ModuleCtx.Odoo_Image,
        '-d', db_name,
        '-i', 'base',
        '--without-demo=all',
    ]

    _ = subprocess.run(odoo_command, check=True, capture_output=True)

    # Wait until the database is initialized and logins are accepted
    print(f'Waiting for Odoo container {container_name} to accept logins', flush=True)
    _wait_until_ready(port, db_name)
    print(f'Odoo container {container_name} is ready', flush=True)

    details:'stranydict' = {
        'host': 'localhost',
        'port': port,
        'protocol': 'jsonrpc',
        'database': db_name,
        'user': ModuleCtx.Login,
        'password': ModuleCtx.Password,
    }

    out = OdooServer(
        container_name=container_name,
        db_container_name=db_container_name,
        network_name=network_name,
        details=details,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
