# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an SFTP operation reaches for when it is exercised offline - a client that remembers
# the batch commands it was told to run where a live server would have executed them,
# one that always fails and the wrapper built around them.

# stdlib
import os
import shlex
from contextlib import contextmanager

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.ext.bunch import Bunch
from zato.common.file_transfer.api import Default_Verify_How
from zato.common.sftp import SFTPOutput
from zato.common.typing_ import cast_
from zato.server.connection.sftp import SFTPConnection

# Test support
from audit_env import Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anyset

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

# The exit codes of the sftp binary - a batch that ran through and one in which a command failed
Exit_Code_OK = 0
Exit_Code_Command_Failed = 1

# The listing line the stub answers an `ls` with - a regular file of the given size,
# in the shape the sftp binary prints for `ls -ln`
Ls_Line = '-rw-r--r--    ? 1000     1000     {size} Mar  3 11:50 {name}'

# ################################################################################################################################
# ################################################################################################################################

class ClientRecorder:
    """ Stands in for the SFTP client - it remembers the batch commands it was told
    to run where a live server would have executed them.
    """

    def __init__(self) -> 'None':
        self.commands:'anylist' = []

        # The size of each file put, by its remote path, which is what an `ls` of the path reports back
        self.size_by_path:'anydict' = {}

        # What an `ls` of a path answers with, set by a test, e.g. the entries of a directory
        self.listing_by_path:'anydict' = {}

        # The paths an `ls` reports as not found
        self.missing_paths:'anyset' = set()

    def execute(self, cid:'str', data:'str', log_level:'int') -> 'SFTPOutput':
        self.commands.append(data)

        # A put is remembered by the size of the local file, as a server would hold it now ..
        parts = shlex.split(data)

        if parts[0] == 'put':
            local_path = parts[-2]
            remote_path = parts[-1]
            self.size_by_path[remote_path] = os.path.getsize(local_path)

        # .. and an ls of a path lists what a test set for it, or a file put earlier with its very size.
        is_ok = True
        exit_code = Exit_Code_OK
        stdout = ''

        if parts[0] == 'ls':
            remote_path = parts[-1]
            if remote_path in self.missing_paths:
                is_ok = False
                exit_code = Exit_Code_Command_Failed
            elif remote_path in self.listing_by_path:
                stdout = self.listing_by_path[remote_path]
            elif remote_path in self.size_by_path:
                stdout = Ls_Line.format(size=self.size_by_path[remote_path], name=remote_path)

        out = SFTPOutput(cid, 1, command=data, is_ok=is_ok, stdout=stdout, exit_code=exit_code)
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
        self.verify_how = Default_Verify_How

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
