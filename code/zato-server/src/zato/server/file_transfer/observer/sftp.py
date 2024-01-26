# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from .base import BaseObserver

# ################################################################################################################################

if 0:
    from zato.server.file_transfer.event import FileTransferEvent
    from zato.server.file_transfer.snapshot import BaseRemoteSnapshotMaker

    BaseRemoteSnapshotMaker = BaseRemoteSnapshotMaker
    FileTransferEvent = FileTransferEvent

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SFTPObserver(BaseObserver):
    """ An observer checking remote SFTP directories.
    """
    observer_type_impl = 'sftp-snapshot'
    observer_type_name = 'SFTP'
    observer_type_name_title = observer_type_name

# ################################################################################################################################

    def path_exists(self, path:'str', snapshot_maker:'BaseRemoteSnapshotMaker') -> 'bool':
        return snapshot_maker.file_client.path_exists(path)

# ################################################################################################################################

    def path_is_directory(self, path:'str', snapshot_maker:'BaseRemoteSnapshotMaker') -> 'bool':
        raise NotImplementedError()

# ################################################################################################################################

    def is_path_valid(self, path:'str') -> 'bool':
        raise NotImplementedError()

# ################################################################################################################################

    def move_file(
        self,
        path_from, # type: str
        path_to,   # type: str
        event,     # type: FileTransferEvent
        snapshot_maker # type: BaseRemoteSnapshotMaker
    ) -> 'None':
        """ Moves a file to a selected directory.
        """

        #
        # 1) If we have the data to be moved in the event, we can just store it
        #    on the FTP server and delete the path from which it was read.
        #
        # 2) If we have no data in the event, we tell the file to move the file itself
        #
        # The reason we do not always choose path 2) is that a client move_file
        # needs to download the file first before it stores it in path_to,
        # and we can avoid this unnecessary step in path 1) whenever it is possible.
        #
        #

        # Case 1)
        if event.has_raw_data:
            snapshot_maker.file_client.store(path_to, event.raw_data)
            snapshot_maker.file_client.delete_file(path_from)

        # Case 2)
        else:
            snapshot_maker.file_client.move_file(path_from, path_to)

# ################################################################################################################################

    def delete_file(self, path:'str', snapshot_maker:'BaseRemoteSnapshotMaker') -> 'None':
        """ Deletes a file pointed to by path.
        """
        snapshot_maker.file_client.delete_file(path)

# ################################################################################################################################
# ################################################################################################################################
