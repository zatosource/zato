# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an FTP operation reaches for when it is exercised offline - the facade under test
# is built around the real pyfilesystem class whose network-facing methods are swapped
# for recorders, or for ones that always fail, for the duration of a block.

# stdlib
from contextlib import contextmanager

# pyfilesystem
from fs.ftpfs import FTPFS

# Zato
from zato.common.audit_log.api import AuditLog
from zato.server.connection.ftp import FTPFacade

# Test support
from audit_env import Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anylist

    patchgen = Iterator['FSRecorder']

# ################################################################################################################################
# ################################################################################################################################

# The name the connection under test goes by
Connection_Name = 'test.ftp.audit'

# The path and bytes the store checks move
Remote_Path = '/documents/results.csv'
File_Content = b'code,label\nA1,First\nA2,Second\n'

# What the failing filesystem says
Raised_Error = 'The server went away'

# The methods the facade routes through the underlying filesystem
_patched_names = 'writebytes', 'upload', 'remove', 'removedir'

# ################################################################################################################################
# ################################################################################################################################

class FSRecorder:
    """ Remembers what the filesystem was told to do where a live server
    would have been written to.
    """

    def __init__(self) -> 'None':
        self.written:'anylist' = []
        self.removed:'anylist' = []

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def patched_fs(*, should_raise:'bool'=False) -> 'patchgen':
    """ Swaps the network-facing methods of the pyfilesystem class for recorders,
    or for ones that always fail, for the duration of a block.
    """
    recorder = FSRecorder()

    def writebytes(fs_self:'any_', path:'str', contents:'bytes') -> 'None':
        if should_raise:
            raise Exception(Raised_Error)
        recorder.written.append((path, contents))

    def upload(fs_self:'any_', path:'str', file:'any_', chunk_size:'any_'=None, **options:'any_') -> 'None':
        if should_raise:
            raise Exception(Raised_Error)
        recorder.written.append((path, file.read()))

    def remove(fs_self:'any_', path:'str') -> 'None':
        if should_raise:
            raise Exception(Raised_Error)
        recorder.removed.append(path)

    removedir = remove

    replacements = {
        'writebytes': writebytes,
        'upload': upload,
        'remove': remove,
        'removedir': removedir,
    }

    # What the class carried before the swap, so it can be put back
    saved = {name: getattr(FTPFS, name) for name in _patched_names}

    for name in _patched_names:
        setattr(FTPFS, name, replacements[name])

    try:
        yield recorder
    finally:
        for name in _patched_names:
            setattr(FTPFS, name, saved[name])

# ################################################################################################################################
# ################################################################################################################################

def new_ftp_facade() -> 'FTPFacade':
    """ Builds the facade under test - the constructor stores the parameters only,
    no connection is made until a network-facing method runs.
    """
    out = FTPFacade('localhost', 'user', 'password', '', 10.0, 21)

    out.zato_conn_name = Connection_Name
    out.zato_audit_log = AuditLog(Server_Name)

    return out

# ################################################################################################################################
# ################################################################################################################################
