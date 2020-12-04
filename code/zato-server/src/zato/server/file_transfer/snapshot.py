# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from sys import maxsize
from traceback import format_exc

# gevent
from gevent import sleep

# Watchdog
from watchdog.events import FileCreatedEvent, FileModifiedEvent

# Zato
from zato.common.api import FILE_TRANSFER
from zato.common.util.api import spawn_greenlet
from zato.server.connection.file_client.base import BaseFileClient
from zato.server.connection.file_client.ftp import FTPFileClient
from zato.server.service import Service

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.service import Service
    from zato.server.file_transfer.observer.base import BaseObserver

    BaseObserver = BaseObserver
    Bunch = Bunch
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class FileInfo:
    """ Information about a single file as found by a snapshot maker.
    """
    __slots__ = 'full_path', 'name', 'size', 'last_modified'

    def __init__(self):
        self.full_path = ''
        self.name = ''
        self.size = -1
        self.last_modified = None

# ################################################################################################################################
# ################################################################################################################################

class DirSnapshot:
    """ Represents the state of a given directory, i.e. a list of files in it.
    """
    def __init__(self):
        self.file_data = {}
        self._file_set = set()

# ################################################################################################################################

    def add_file_list(self, path, data):
        # type: (str, list) -> None
        for item in data: # type: (dict)

            file_info = FileInfo()
            file_info.full_path = os.path.join(path, item['name'])
            file_info.name = item['name']
            file_info.size = item['size']
            file_info.last_modified = item['last_modified']

            self.file_data[file_info.name] = file_info

# ################################################################################################################################
# ################################################################################################################################

class DirSnapshotDiff:
    """ A difference between two DirSnapshot objects, i.e. all the files created and modified.
    """
    __slots__ = 'files_created', 'files_modified'

    def __init__(self, previous_snapshot, current_snapshot):
        # type: (DirSnapshot, DirSnapshot)

        # These are new for sure ..
        self.files_created = set(current_snapshot.file_data) - set(previous_snapshot.file_data)

        # .. now we can prepare a list for files that were potentially modified ..
        self.files_modified = set()

        # .. go through each file in the current snapshot and compare its timestamps and file size
        # with what was found the previous time. If either is different,
        # it means that the file was modified. In case that the file was modified
        # but the size remains the size and at the same time the timestamp is the same too,
        # we will not be able to tell the difference and the file will not be reported as modified
        # (we would have to download it and check its contents to cover such a case).
        for current in current_snapshot.file_data.values(): # type: FileInfo
            previous = previous_snapshot.file_data.get(current.name) # type: FileInfo
            if previous:
                size_differs = current.size != previous.size
                last_modified_differs = current.last_modified != previous.last_modified

                if size_differs or last_modified_differs:
                    self.files_modified.add(current.name)

# ################################################################################################################################
# ################################################################################################################################

class BaseSnapshotMaker:

    def __init__(self, service, outconn_config):
        # type: (Service, Bunch)
        self.service = service
        self.outconn_config = outconn_config
        self.file_client = None # type: BaseFileClient

# ################################################################################################################################

    def connect(self):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def get_snapshot(self, path, ignored_is_recursive):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def get_file_data(self, path):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################
# ################################################################################################################################

class FTPSnapshotMaker(BaseSnapshotMaker):
    def connect(self):

        # Extract all the configuration ..
        ftp_store = self.service.server.worker_store.worker_config.out_ftp
        ftp_outconn = ftp_store.get(self.outconn_config.name)

        # .. connect to the remote server ..
        self.file_client = FTPFileClient(ftp_outconn, self.outconn_config)

        # .. and confirm that the connection works.
        self.file_client.ping()

# ################################################################################################################################

    def get_snapshot(self, path, ignored_is_recursive):
        # type: (str, bool) -> DirSnapshot

        # First, get a list of files under path ..
        result = self.file_client.list(path)

        # .. create a new container for the snapshot ..
        snapshot = DirSnapshot()

        # .. now, populate with what we found ..
        snapshot.add_file_list(path, result['file_list'])

        # .. and return the result to our caller.
        return snapshot

# ################################################################################################################################

    def get_file_data(self, path):
        # type: (str) -> bytes
        return self.file_client.get(path)

# ################################################################################################################################
# ################################################################################################################################

class SFTPSnapshotMaker(BaseSnapshotMaker):
    pass

# ################################################################################################################################
# ################################################################################################################################
