# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SMB part of the file transfer demo - two shares of the demo server, each with the directories
# one connection's schedules poll, and the two connections, each logging in as a user of its own.

# stdlib
import os

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.util.local_server import Local_Host
from zato.server.demo_file_transfer.common import make_directory, new_connection
from zato.server.demo_file_transfer.layout import SMB_Connections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist, stranydict
    from zato.server.demo_file_transfer.common import demo_connection_list, DemoPaths
    from zato.server.demo_file_transfer.layout import ConnectionSpec

# ################################################################################################################################
# ################################################################################################################################

def _get_share_path(paths:'DemoPaths', spec:'ConnectionSpec') -> 'str':
    out = os.path.join(paths.smb_dir, spec.account)
    return out

# ################################################################################################################################

def build_tree(paths:'DemoPaths') -> 'None':
    """ Creates the directory behind each share, with the directories its schedules poll, unless they exist already.
    """
    for spec in SMB_Connections:
        share_path = _get_share_path(paths, spec)

        for shape in spec.shapes:
            directory = os.path.join(share_path, shape)
            make_directory(directory)

# ################################################################################################################################

def get_shares(paths:'DemoPaths') -> 'dictlist':
    """ The shares of the demo server, one per connection and named after its account.
    """
    out:'dictlist' = []

    for spec in SMB_Connections:

        share = {
            'name': spec.account,
            'path': _get_share_path(paths, spec),
        }

        out.append(share)

    return out

# ################################################################################################################################

def new_users() -> 'dictlist':
    """ The SMB users of the demo server, one per connection, each with a new random password.
    """
    out:'dictlist' = []

    for spec in SMB_Connections:

        user = {
            'username': spec.account,
            'password': CryptoManager.generate_password(to_str=True),
        }

        out.append(user)

    return out

# ################################################################################################################################

def get_connections(paths:'DemoPaths', server_config:'stranydict') -> 'demo_connection_list':
    """ The SMB connections of the demo, logging in as the users of the demo server's configuration.
    The directories start with the name of the share, e.g. hooli/invoices.
    """
    out:'demo_connection_list' = []

    passwords:'stranydict' = {}

    for user in server_config['smb_users']:
        username = user['username']
        passwords[username] = user['password']

    for spec in SMB_Connections:

        definition = {
            'name': spec.name,
            'is_active': True,
            'host': Local_Host,
            'port': server_config['smb_port'],
            'username': spec.account,
            'password': passwords[spec.account],
        }

        connection = new_connection(spec, definition)
        share_path = _get_share_path(paths, spec)

        for shape in spec.shapes:
            connection.directories[shape] = f'{spec.account}/{shape}'
            connection.local_directories[shape] = os.path.join(share_path, shape)

        out.append(connection)

    return out

# ################################################################################################################################
# ################################################################################################################################
