# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket

# Live HL7
from live_hl7.system import Host, LiveSystem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strintdict, strlist, strstrdict
    from live_hl7.system import Handle

# ################################################################################################################################
# ################################################################################################################################

# The one account the server has - the laboratory's drop
Username = 'laboratory'

# The service name in the compose file, which is also what other containers resolve
Service = 'sftp'

# The directories the account starts with, as the SFTP client sees them
Orders_Directory  = '/orders'
Results_Directory = '/results'

# Where the account's directories are on the container's filesystem
_home = f'/home/{Username}'

# How long a banner read may take, in seconds
_banner_timeout = 3.0

# ################################################################################################################################
# ################################################################################################################################

class SFTP(LiveSystem):
    """ An sFTP server - the laboratory's file drop, reached by OpenEMR over the shared network
    and by Zato through the published port.
    """

    name = 'sftp'
    block_number = 7
    purposes = ('ssh',)
    images = {'sftp': 'atmoz/sftp:alpine'}
    directory = os.path.dirname(__file__)
    summary = 'An sFTP server with one account holding an orders and a results directory.'

# ################################################################################################################################

    def environment(self, ports:'strintdict', password:'str') -> 'strstrdict':
        out = super().environment(ports, password)
        out['SFTP_USERNAME'] = Username

        return out

# ################################################################################################################################

    def is_ready(self, handle:'Handle') -> 'bool':
        """ True once the server greets with an SSH banner.
        """
        port = handle.port('ssh')

        with socket.create_connection((Host, port), timeout=_banner_timeout) as connection:
            connection.settimeout(_banner_timeout)
            banner = connection.recv(64)

        out = banner.startswith(b'SSH-')
        return out

# ################################################################################################################################
# ################################################################################################################################

def list_files(handle:'Handle', directory:'str') -> 'strlist':
    """ The names of the files in one of the account's directories.
    """
    path = _home + directory
    output = handle.stack.exec(Service, ['ls', '-1', path])

    out:'strlist' = []

    for line in output.splitlines():
        name = line.strip()
        if name:
            out.append(name)

    return out

# ################################################################################################################################

def read_file(handle:'Handle', directory:'str', name:'str') -> 'bytes':
    """ The contents of one file in one of the account's directories.
    """
    path = f'{_home}{directory}/{name}'

    out = handle.stack.exec_raw(Service, ['cat', path])
    return out

# ################################################################################################################################

def write_file(handle:'Handle', directory:'str', name:'str', data:'bytes') -> 'None':
    """ Writes one file into one of the account's directories, owned by the account.
    """
    path = f'{_home}{directory}/{name}'
    script = f'cat > "{path}" && chown {Username}:users "{path}"'

    _ = handle.stack.exec(Service, ['sh', '-c', script], input_data=data)

# ################################################################################################################################

def remove_file(handle:'Handle', directory:'str', name:'str') -> 'None':
    path = f'{_home}{directory}/{name}'
    _ = handle.stack.exec(Service, ['rm', '-f', path])

# ################################################################################################################################
# ################################################################################################################################
