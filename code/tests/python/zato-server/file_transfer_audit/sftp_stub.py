# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an SFTP operation reaches for when it is exercised offline - a client that remembers
# the batch commands it was told to run where a live server would have executed them,
# one that always fails and the wrapper built around them.

# stdlib
from contextlib import contextmanager

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.ext.bunch import Bunch
from zato.common.sftp import SFTPOutput
from zato.common.typing_ import cast_
from zato.server.connection.sftp import SFTPConnection

# Test support
from audit_env import Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# The name the connection under test goes by
Connection_Name = 'test.sftp.audit'

# The correlation id the operations under test run with
Cid = 'cid-file-transfer-sftp-1'

# The remote path the store and delete checks move
Remote_Path = '/documents/results.csv'

# What the failing client says
Raised_Error = 'The server went away'

# ################################################################################################################################
# ################################################################################################################################

class ClientRecorder:
    """ Stands in for the SFTP client - it remembers the batch commands it was told
    to run where a live server would have executed them.
    """

    def __init__(self) -> 'None':
        self.commands:'anylist' = []

    def execute(self, cid:'str', data:'str', log_level:'int') -> 'SFTPOutput':
        self.commands.append(data)
        out = SFTPOutput(cid, 1, command=data, is_ok=True, stdout='')
        return out

# ################################################################################################################################

class RaisingClient(ClientRecorder):
    """ An SFTP client whose server went away - every command fails.
    """

    def execute(self, cid:'str', data:'str', log_level:'int') -> 'SFTPOutput':
        raise Exception(Raised_Error)

# ################################################################################################################################

class WrapperStub:
    """ Stands in for the connection wrapper - it hands over the stubbed client
    and carries the audit writer and the content storage flag the real one carries.
    """

    def __init__(self, sftp_client:'ClientRecorder', *, should_store_content:'bool') -> 'None':
        self.sftp_client = sftp_client
        self.should_store_content = should_store_content
        self.audit_log = AuditLog(Server_Name)

        self.config = Bunch()
        self.config.name = Connection_Name

    @contextmanager
    def client(self, *, should_block:'bool', block_timeout:'int') -> 'any_':
        yield self.sftp_client

# ################################################################################################################################

def new_sftp_connection(sftp_client:'ClientRecorder', *, should_store_content:'bool'=False) -> 'SFTPConnection':
    """ Builds the connection under test around one stubbed client.
    """
    wrapper = WrapperStub(sftp_client, should_store_content=should_store_content)

    out = SFTPConnection(Cid, cast_('any_', wrapper))

    return out

# ################################################################################################################################
# ################################################################################################################################
