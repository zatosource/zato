# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a queued file is handed over to an outgoing SFTP, SMB or FTP connection.

# stdlib
import os
from json import loads

# gevent
from gevent.fileobject import FileObjectThread

# Zato
from zato.common.pubsub.outgoing import Key_Data
from zato.server.connection.file_transfer_base import Key_Remote_Path, Key_Spool_Path
from zato.server.connection.ftp import FTPConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

def _get_file_envelope(request:'stranydict') -> 'stranydict':
    """ The spool path and the remote path a file publication stored.
    """
    out = loads(request[Key_Data])
    return out

# ################################################################################################################################

def locate_sftp(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing SFTP connection by its id, as its name and its wrapper.
    """
    for item in server.config_manager.outconn_sftp.values():
        if item['id'] == conn_id:
            out = (item['name'], item['conn'])
            return out

    return ()

# ################################################################################################################################

def locate_smb(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing SMB connection by its id, as its name and its wrapper.
    """
    for item in server.config_manager.outconn_smb.values():
        if item['id'] == conn_id:
            out = (item['name'], item['conn'])
            return out

    return ()

# ################################################################################################################################

def locate_ftp(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing FTP connection by its id, as its name and its wrapper.
    """
    for item in server.config_manager.outconn_ftp.values():
        if item['id'] == conn_id:
            out = (item['name'], item['conn'])
            break
    else:
        out = ()

    return out


# ################################################################################################################################

def _read_spool_file(spool_path:'str') -> 'bytes':
    """ Reads a spool file in a thread of its own, so as not to block the event loop.
    """
    thread_file = FileObjectThread(spool_path, 'rb')
    out = thread_file.read()
    thread_file.close()

    return out


# ################################################################################################################################

def deliver_to_sftp(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Hands one queued file over to an outgoing SFTP connection.
    """

    # Imported here to avoid circular imports
    from zato.server.connection.sftp import SFTPConnection

    envelope = _get_file_envelope(request)

    payload = _read_spool_file(envelope[Key_Spool_Path])

    conn = SFTPConnection(cid, wrapper)
    conn.write(payload, envelope[Key_Remote_Path], overwrite=True)

    # The spool goes once the file is written
    os.remove(envelope[Key_Spool_Path])

# ################################################################################################################################

def deliver_to_smb(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Hands one queued file over to an outgoing SMB connection.
    """

    # Imported here to avoid circular imports
    from zato.server.connection.smb import SMBConnection

    envelope = _get_file_envelope(request)

    payload = _read_spool_file(envelope[Key_Spool_Path])

    conn = SMBConnection(cid, wrapper)
    conn.write(payload, envelope[Key_Remote_Path])

    # The spool goes once the file is written
    os.remove(envelope[Key_Spool_Path])

# ################################################################################################################################

def deliver_to_ftp(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Hands one queued file over to an outgoing FTP connection.
    """
    envelope = _get_file_envelope(request)

    spool_path = envelope[Key_Spool_Path]
    remote_path = envelope[Key_Remote_Path]

    payload = _read_spool_file(spool_path)

    conn = FTPConnection(cid, wrapper)
    conn.write(payload, remote_path)

    # The spool goes once the file is written
    os.remove(spool_path)


# ################################################################################################################################
# ################################################################################################################################

