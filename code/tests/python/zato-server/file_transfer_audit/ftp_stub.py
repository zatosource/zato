# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an FTP operation reaches for when it is exercised offline - a client that remembers
# what it was told to write or delete where a live server would have been, one that always
# fails and the wrapper built around them.

# stdlib
from contextlib import contextmanager

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.ext.bunch import Bunch
from zato.common.file_transfer.api import Default_Verify_How
from zato.common.typing_ import cast_
from zato.server.connection.ftp import FTPConnection

# Test support
from audit_env import Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# The name the connection under test goes by
Connection_Name = 'test.ftp.audit'

# The correlation id the operations under test run with
Cid = 'cid-file-transfer-ftp-1'

# The path and bytes the store checks move
Remote_Path = 'documents/results.csv'
File_Content = b'code,label\nA1,First\nA2,Second\n'

# What the failing client says
Raised_Error = 'The server went away'

# The modification time fact the stub reports of every file, in the MLST shape the connection parses
Modify_Fact = '20260820103000'

# ################################################################################################################################
# ################################################################################################################################

class ClientRecorder:
    """ Stands in for the FTP client - it remembers what it was told to do
    where a live server would have been written to.
    """

    def __init__(self) -> 'None':
        self.written:'anylist' = []
        self.removed:'anylist' = []
        self.renamed:'anylist' = []

        # The bytes of each file written, by its remote path, which is what a stat of the path reports on
        self.data_by_path:'anydict' = {}

# ################################################################################################################################

    def write(self, remote_path:'any_', data:'any_') -> 'None':
        self.written.append((remote_path, data))
        self.data_by_path[remote_path] = data

# ################################################################################################################################

    def stat(self, remote_path:'any_') -> 'anydict':
        out = {'type': 'file', 'size': str(len(self.data_by_path[remote_path])), 'modify': Modify_Fact}
        return out

# ################################################################################################################################

    def read(self, remote_path:'any_') -> 'bytes':
        out = self.data_by_path[remote_path]
        return out

# ################################################################################################################################

    def remove(self, remote_path:'any_') -> 'None':
        self.removed.append(remote_path)

# ################################################################################################################################

    def rmdir(self, remote_path:'any_') -> 'None':
        self.removed.append(remote_path)

# ################################################################################################################################

    def rename(self, from_path:'any_', to_path:'any_') -> 'None':
        self.renamed.append((from_path, to_path))

# ################################################################################################################################

class RaisingClient(ClientRecorder):
    """ An FTP client whose server went away - every operation fails.
    """

    def write(self, remote_path:'any_', data:'any_') -> 'None':
        raise Exception(Raised_Error)

# ################################################################################################################################

    def remove(self, remote_path:'any_') -> 'None':
        raise Exception(Raised_Error)

# ################################################################################################################################

    def rename(self, from_path:'any_', to_path:'any_') -> 'None':
        raise Exception(Raised_Error)

# ################################################################################################################################

class WrapperStub:
    """ Stands in for the connection wrapper - it hands over the stubbed client
    and carries the audit writer and the content storage flag the real one carries.
    """

    def __init__(self, ftp_client:'ClientRecorder', *, should_store_content:'bool') -> 'None':
        self.ftp_client = ftp_client
        self.should_store_content = should_store_content
        self.audit_log = AuditLog(Server_Name)
        self.verify_how = Default_Verify_How

        self.config = Bunch()
        self.config.name = Connection_Name

# ################################################################################################################################

    @contextmanager
    def client(self, *, should_block:'bool', block_timeout:'int') -> 'any_':
        yield self.ftp_client

# ################################################################################################################################

def new_ftp_connection(ftp_client:'ClientRecorder', *, should_store_content:'bool' = False) -> 'FTPConnection':
    """ Builds the connection under test around one stubbed client.
    """
    wrapper = WrapperStub(ftp_client, should_store_content=should_store_content)
    wrapper_typed = cast_('any_', wrapper)

    out = FTPConnection(Cid, wrapper_typed)

    return out

# ################################################################################################################################
# ################################################################################################################################
