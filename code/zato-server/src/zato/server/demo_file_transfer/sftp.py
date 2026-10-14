# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SFTP part of the file transfer demo - a private SSH server on 127.0.0.1 that the server's own user logs in to
# with a key of its own, and the two connections that poll directories of that server.

# stdlib
import os
from logging import getLogger

# Zato
from zato.common.sftp_local import LocalSFTPServer
from zato.server.demo_file_transfer.common import make_directory, new_connection
from zato.server.demo_file_transfer.layout import SFTP_Connections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.demo_file_transfer.common import demo_connection_list, DemoPaths

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The SSH server this very process started, if any
    Server:'LocalSFTPServer | None' = None

# ################################################################################################################################
# ################################################################################################################################

def get_server(paths:'DemoPaths', port:'int') -> 'LocalSFTPServer':
    """ The SSH server of the demo, listening on the given port, whether it runs or not.
    """
    out = LocalSFTPServer(paths.sshd_dir, port)
    out.log_path = paths.sshd_log

    return out

# ################################################################################################################################

def parse_port(address:'str') -> 'int':
    """ The port of an address stored with an SFTP connection, e.g. 127.0.0.1:22022, zero if there is none.
    """
    _, _, port = address.rpartition(':')

    if port.isdigit():
        out = int(port)
    else:
        out = 0

    return out

# ################################################################################################################################

def get_connections(paths:'DemoPaths', server:'LocalSFTPServer') -> 'demo_connection_list':
    """ The SFTP connections of the demo, creating each directory they poll if it is not there yet.
    The directories are absolute, because the server's user logs in to its own home directory.
    """
    out:'demo_connection_list' = []

    address = f'{server.host}:{server.port}'

    for spec in SFTP_Connections:

        definition = {
            'name': spec.name,
            'is_active': True,
            'address': address,
            'username': server.username,
            'private_key': server.client_key_path,
            'ignore_host_key_changes': True,
        }

        connection = new_connection(spec, definition)

        for shape in spec.shapes:
            directory = os.path.join(paths.sftp_files_dir, spec.account, shape)
            make_directory(directory)

            connection.directories[shape] = directory
            connection.local_directories[shape] = directory

        out.append(connection)

    return out

# ################################################################################################################################

def start(paths:'DemoPaths', port:'int') -> 'LocalSFTPServer':
    """ Builds whatever the SSH server is missing - the keys are kept if they exist - and starts it.
    """
    out = get_server(paths, port)
    out.prepare()
    out.start_process()

    ModuleCtx.Server = out

    logger.info('File transfer demo SSH server started on %s:%s', out.host, out.port)

    return out

# ################################################################################################################################

def stop_started() -> 'None':
    """ Stops the SSH server if this very process started it.
    """
    if server := ModuleCtx.Server:
        server.stop_process()
        ModuleCtx.Server = None

# ################################################################################################################################

def stop_any(paths:'DemoPaths') -> 'None':
    """ Stops the SSH server, whichever process started it, provided it still runs the demo's configuration.
    """
    stop_started()

    server = get_server(paths, 0)
    server.stop_process()

# ################################################################################################################################
# ################################################################################################################################
