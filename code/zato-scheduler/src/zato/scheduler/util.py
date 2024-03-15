# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.client import AnyServiceInvoker, ZatoClient
    from zato.common.typing_ import anydict
    AnyServiceInvoker = AnyServiceInvoker

# ################################################################################################################################
# ################################################################################################################################

def _set_up_zato_client_by_server_path(server_path:'str') -> 'AnyServiceInvoker':

    # Zato
    from zato.common.util.api import get_client_from_server_conf
    return get_client_from_server_conf(server_path, require_server=False)

# ################################################################################################################################

def _set_up_zato_client_by_remote_details(
    server_use_tls:  'bool',
    server_host:     'str',
    server_port:     'int',
    server_username: 'str',
    server_password: 'str'
    ) -> 'ZatoClient':

    # Zato
    from zato.client import get_client_from_credentials

    server_url = f'{server_host}:{server_port}'
    client_auth = (server_username, server_password)

    return get_client_from_credentials(server_use_tls, server_url, client_auth)

# ################################################################################################################################

def set_up_zato_client(config:'anydict') -> 'AnyServiceInvoker':

    # New in 3.2, hence optional
    server_config = config.get('server')

    # We do have server configuration available ..
    if server_config:

        if server_config.get('server_path'):
            return _set_up_zato_client_by_server_path(server_config.server_path)
        else:
            server_use_tls = server_config.get('server_use_tls')
            server_host = server_config['server_host']
            server_port = server_config['server_port']
            server_username = server_config['server_username']
            server_password = server_config['server_password']

            return _set_up_zato_client_by_remote_details(
                server_use_tls,
                server_host,
                server_port,
                server_username,
                server_password
            ) # type: ignore

    # .. no configuration, assume this is a default quickstart cluster.
    else:
        # This is what quickstart environments use by default
        server_path = '/opt/zato/env/qs-1'
        return _set_up_zato_client_by_server_path(server_path)

# ################################################################################################################################
