# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The FTP part of the file transfer demo - a plain FTP connection and an FTPS one, each logging in to the demo server
# as a user of its own, with a home directory that holds the directories its schedules poll.

# stdlib
import os

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.util.local_server import Local_Host
from zato.server.demo_file_transfer.common import make_directory, new_connection
from zato.server.demo_file_transfer.layout import FTP_Connections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist, stranydict
    from zato.server.demo_file_transfer.common import demo_connection_list, DemoPaths
    from zato.server.demo_file_transfer.layout import ConnectionSpec

# ################################################################################################################################
# ################################################################################################################################

# The connection that speaks FTPS rather than plain FTP
_ftps_connection_name = 'demo.ftps.umbrella'

# ################################################################################################################################
# ################################################################################################################################

def _get_home(paths:'DemoPaths', spec:'ConnectionSpec') -> 'str':
    out = os.path.join(paths.ftp_dir, spec.account)
    return out

# ################################################################################################################################

def build_tree(paths:'DemoPaths') -> 'None':
    """ Creates the home directory of each user, with the directories its schedules poll, unless they exist already.
    """
    for spec in FTP_Connections:
        home = _get_home(paths, spec)

        for shape in spec.shapes:
            directory = os.path.join(home, shape)
            make_directory(directory)

# ################################################################################################################################

def new_users(paths:'DemoPaths') -> 'dictlist':
    """ The FTP users of the demo server, one per connection, each with a new random password.
    """
    out:'dictlist' = []

    for spec in FTP_Connections:

        user = {
            'username': spec.account,
            'password': CryptoManager.generate_password(to_str=True),
            'home': _get_home(paths, spec),
        }

        out.append(user)

    return out

# ################################################################################################################################

def get_connections(server_config:'stranydict') -> 'demo_connection_list':
    """ The FTP connections of the demo, logging in as the users of the demo server's configuration.
    The directories are relative to each user's home directory, which is the root of what the user sees.
    """
    out:'demo_connection_list' = []

    passwords:'stranydict' = {}
    homes:'stranydict' = {}

    for user in server_config['ftp_users']:
        username = user['username']
        passwords[username] = user['password']
        homes[username] = user['home']

    for spec in FTP_Connections:

        use_ssl = spec.name == _ftps_connection_name

        if use_ssl:
            port = server_config['ftps_port']
        else:
            port = server_config['ftp_port']

        definition = {
            'name': spec.name,
            'is_active': True,
            'host': Local_Host,
            'port': port,
            'username': spec.account,
            'password': passwords[spec.account],
            'use_ssl': use_ssl,
        }

        connection = new_connection(spec, definition)
        home = homes[spec.account]

        for shape in spec.shapes:
            connection.directories[shape] = shape
            connection.local_directories[shape] = os.path.join(home, shape)

        out.append(connection)

    return out

# ################################################################################################################################
# ################################################################################################################################
