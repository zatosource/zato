# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import FILE_TRANSFER
from zato.server.file_transfer.snapshot import FTPSnapshotMaker, LocalSnapshotMaker, SFTPSnapshotMaker

# ################################################################################################################################
# ################################################################################################################################

source_type_ftp   = FILE_TRANSFER.SOURCE_TYPE.FTP.id
source_type_local = FILE_TRANSFER.SOURCE_TYPE.LOCAL.id
source_type_sftp  = FILE_TRANSFER.SOURCE_TYPE.SFTP.id

source_type_to_snapshot_maker_class = {
    source_type_ftp:   FTPSnapshotMaker,
    source_type_local: LocalSnapshotMaker,
    source_type_sftp:  SFTPSnapshotMaker,
}

# ################################################################################################################################
# ################################################################################################################################
