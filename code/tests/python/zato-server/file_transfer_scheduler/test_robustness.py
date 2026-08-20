# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.test.file_transfer_harness.robustness import RobustnessTests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.file_transfer_harness.adapter import FileTransferAdapter

# ################################################################################################################################
# ################################################################################################################################

class TestSFTPRobustness(RobustnessTests):

    @pytest.fixture()
    def adapter(self, sftp_adapter:'FileTransferAdapter') -> 'FileTransferAdapter':
        return sftp_adapter

# ################################################################################################################################
# ################################################################################################################################

class TestSMBRobustness(RobustnessTests):

    @pytest.fixture()
    def adapter(self, smb_adapter:'FileTransferAdapter') -> 'FileTransferAdapter':
        return smb_adapter

# ################################################################################################################################
# ################################################################################################################################

class TestFTPRobustness(RobustnessTests):
    """ Runs the shared robustness tests over an FTP connection.
    """

    @pytest.fixture()
    def adapter(self, ftp_adapter:'FileTransferAdapter') -> 'FileTransferAdapter':
        return ftp_adapter

# ################################################################################################################################
# ################################################################################################################################
