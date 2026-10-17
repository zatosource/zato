# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The demo server process with the FTP, FTPS and SMB listeners - its configuration, starting it,
# telling whether one is already running and stopping it, whichever process started it.

# stdlib
import os
import sys
from json import dumps, loads
from logging import getLogger

# Zato
from zato.common.demo.file_transfer_server import Module_Name
from zato.common.util.local_server import is_accepting_connections, is_expected_process, Local_Host, read_pid_file, \
    start_logged_process, stop_pid, stop_popen, wait_until_accepting_connections
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from zato.common.typing_ import dictlist, intlist, stranydict
    from zato.server.demo_file_transfer.common import DemoPaths

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The configuration holds passwords, so it is readable to its owner only
_config_mode = 0o600

# The keys of the configuration that hold the three ports, in the order they are picked in
Port_Keys = ['ftp_port', 'ftps_port', 'smb_port']

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The demo server this very process started, if any
    Process:'Popen | None' = None

# ################################################################################################################################
# ################################################################################################################################

def new_config(
    paths:'DemoPaths',
    ports:'intlist',
    certificate_path:'str',
    ftp_users:'dictlist',
    smb_shares:'dictlist',
    smb_users:'dictlist',
    ) -> 'stranydict':
    """ The configuration of the demo server - its three ports, in the order of Port_Keys, its files and its users.
    """
    out:'stranydict' = {
        'host': Local_Host,
        'certificate_path': certificate_path,
        'pid_file_path': paths.server_pid,
        'log_file_path': paths.server_log,
        'ftp_users': ftp_users,
        'smb_shares': smb_shares,
        'smb_users': smb_users,
    }

    for key, port in zip(Port_Keys, ports):
        out[key] = port

    return out

# ################################################################################################################################

def get_ports(config:'stranydict') -> 'intlist':
    """ The three ports of a configuration, in the order of Port_Keys.
    """
    out:'intlist' = []

    for key in Port_Keys:
        port = config[key]
        out.append(port)

    return out

# ################################################################################################################################

def write_config(paths:'DemoPaths', config:'stranydict') -> 'None':

    data = dumps(config, indent=2)

    with open_w(paths.server_config) as config_file:
        _ = config_file.write(data)

    os.chmod(paths.server_config, _config_mode)

# ################################################################################################################################

def read_config(paths:'DemoPaths') -> 'stranydict':
    """ The configuration an earlier import wrote out, an empty dict if there is none.
    """
    if not os.path.exists(paths.server_config):
        return {}

    with open(paths.server_config, encoding='utf8') as config_file:
        data = config_file.read()

    out = loads(data)
    return out

# ################################################################################################################################
# ################################################################################################################################

def is_running(paths:'DemoPaths', config:'stranydict') -> 'bool':
    """ Whether a demo server with this configuration is alive and accepting connections on all of its ports,
    whichever process started it.
    """
    pid = read_pid_file(paths.server_pid)

    # The path to the configuration is on the server's command line, which is what tells it apart ..
    if not is_expected_process(pid, paths.server_config):
        return False

    # .. and each of its listeners has to be up.
    ports = get_ports(config)

    for port in ports:
        if not is_accepting_connections(port, Local_Host):
            return False

    return True

# ################################################################################################################################

def start(paths:'DemoPaths', config:'stranydict') -> 'None':
    """ Starts the demo server with the configuration written out already and waits until all its listeners are up.
    """
    command = [sys.executable, '-m', Module_Name, '--config', paths.server_config]
    process = start_logged_process(command, paths.server_log)

    ModuleCtx.Process = process

    ports = get_ports(config)

    for port in ports:
        wait_until_accepting_connections(port, Local_Host, process=process)

    logger.info('File transfer demo server started, pid %s, ports %s', process.pid, ports)

# ################################################################################################################################

def stop_started() -> 'None':
    """ Stops the demo server if this very process started it.
    """
    if process := ModuleCtx.Process:
        stop_popen(process)
        ModuleCtx.Process = None

# ################################################################################################################################

def stop_any(paths:'DemoPaths') -> 'None':
    """ Stops the demo server, whichever process started it, provided it still runs the demo's configuration.
    """
    stop_started()

    pid = read_pid_file(paths.server_pid)
    _ = stop_pid(pid, paths.server_config)

# ################################################################################################################################
# ################################################################################################################################
