# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an SMB operation reaches for when it is exercised offline - a client that remembers
# what it was told to write or delete where a live share would have been, one that always
# fails and the wrapper built around them.

# stdlib
from contextlib import contextmanager

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_
from zato.server.connection.smb import SMBConnection

# Test support
from audit_env import Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# The name the connection under test goes by
Connection_Name = 'test.smb.audit'

# The correlation id the operations under test run with
Cid = 'cid-file-transfer-1'

# The path and bytes the store checks move
Remote_Path = 'MyShare/documents/results.csv'
File_Content = b'code,label\nA1,First\nA2,Second\n'

# What the failing client says
Raised_Error = 'The share went away'

# ################################################################################################################################
# ################################################################################################################################

class ClientRecorder:
    """ Stands in for the SMB client - it remembers what it was told to do
    where a live share would have been written to.
    """

    def __init__(self) -> 'None':
        self.written:'anylist' = []
        self.removed:'anylist' = []
        self.renamed:'anylist' = []

    def write(self, remote_path:'any_', data:'any_') -> 'None':
        self.written.append((remote_path, data))

    def remove(self, remote_path:'any_') -> 'None':
        self.removed.append(remote_path)

    def rmdir(self, remote_path:'any_') -> 'None':
        self.removed.append(remote_path)

    def rename(self, from_path:'any_', to_path:'any_') -> 'None':
        self.renamed.append((from_path, to_path))

# ################################################################################################################################

class RaisingClient(ClientRecorder):
    """ An SMB client whose share went away - every operation fails.
    """

    def write(self, remote_path:'any_', data:'any_') -> 'None':
        raise Exception(Raised_Error)

    def remove(self, remote_path:'any_') -> 'None':
        raise Exception(Raised_Error)

    def rename(self, from_path:'any_', to_path:'any_') -> 'None':
        raise Exception(Raised_Error)

# ################################################################################################################################

class WrapperStub:
    """ Stands in for the connection wrapper - it hands over the stubbed client
    and carries the audit writer and the content storage flag the real one carries.
    """

    def __init__(self, smb_client:'ClientRecorder', *, should_store_content:'bool') -> 'None':
        self.smb_client = smb_client
        self.should_store_content = should_store_content
        self.audit_log = AuditLog(Server_Name)

        self.config = Bunch()
        self.config.name = Connection_Name

    @contextmanager
    def client(self, *, should_block:'bool', block_timeout:'int') -> 'any_':
        yield self.smb_client

# ################################################################################################################################

def new_smb_connection(smb_client:'ClientRecorder', *, should_store_content:'bool'=False) -> 'SMBConnection':
    """ Builds the connection under test around one stubbed client.
    """
    wrapper = WrapperStub(smb_client, should_store_content=should_store_content)

    out = SMBConnection(Cid, cast_('any_', wrapper))

    return out

# ################################################################################################################################
# ################################################################################################################################
