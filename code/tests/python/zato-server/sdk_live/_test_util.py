# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# Zato
from zato.common.test.client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict

# ################################################################################################################################
# ################################################################################################################################

wait_timeout = 60
poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def get_client(zato_server:'stranydict') -> 'AdminClient':
    out = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
    return out

# ################################################################################################################################

def read_server_log(zato_server:'stranydict') -> 'str':
    log_path = os.path.join(zato_server['server_directory'], 'logs', 'server.log')

    with open(log_path, 'r') as log_file:
        out = log_file.read()

    return out

# ################################################################################################################################

def wait_for(condition:'callable_', description:'str', timeout:'int'=wait_timeout) -> 'any_':
    """ Polls the condition until it returns a truthy value or the timeout passes.
    """
    deadline = time.monotonic() + timeout
    last_error = ''

    while time.monotonic() < deadline:

        try:
            result = condition()
        except Exception as e:
            last_error = str(e)
        else:
            if result:
                return result

        time.sleep(poll_interval)

    raise Exception(f'Timed out waiting for {description} after {timeout}s, last error: {last_error}')

# ################################################################################################################################

def create_definition(zato_server:'stranydict', name:'str', type_:'str', **fields:'any_') -> 'int':
    """ Creates one definition of a custom type through the admin API and waits until it answers pings.
    """
    client = get_client(zato_server)

    response = client.create('zato.generic.connection.create',
        cluster_id=1,
        name=name,
        type_=type_,
        is_active=True,
        is_internal=False,
        is_channel=False,
        is_outconn=True,
        **fields,
    )

    conn_id = response['id']
    assert conn_id

    # The connection builds in the background, so keep pinging until it answers.
    def _ping() -> 'bool':
        ping_response = client.invoke('zato.generic.connection.ping', {'id': conn_id})
        out = ping_response['is_success'] is True
        return out

    _ = wait_for(_ping, f'connection {name} to answer pings')

    return conn_id

# ################################################################################################################################

def delete_definition(zato_server:'stranydict', conn_id:'int') -> 'None':
    client = get_client(zato_server)
    _ = client.delete('zato.generic.connection.delete', id=conn_id)

# ################################################################################################################################
# ################################################################################################################################
