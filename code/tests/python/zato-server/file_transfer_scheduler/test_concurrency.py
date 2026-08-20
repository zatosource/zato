# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.test.file_transfer_harness.concurrency import ConcurrencyTests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.adapter import FileTransferAdapter

# ################################################################################################################################
# ################################################################################################################################

class TestSFTPConcurrency(ConcurrencyTests):

    @pytest.fixture()
    def adapter(self, sftp_adapter:'FileTransferAdapter') -> 'FileTransferAdapter':
        return sftp_adapter

# ################################################################################################################################
# ################################################################################################################################

class TestSMBConcurrency(ConcurrencyTests):

    @pytest.fixture()
    def adapter(self, smb_adapter:'FileTransferAdapter') -> 'FileTransferAdapter':
        return smb_adapter

# ################################################################################################################################
# ################################################################################################################################

class TestFTPConcurrency(ConcurrencyTests):
    """ Runs the shared concurrency tests over an FTP connection.
    """

    @pytest.fixture()
    def adapter(self, ftp_adapter:'FileTransferAdapter') -> 'FileTransferAdapter':
        return ftp_adapter

# ################################################################################################################################
# ################################################################################################################################
