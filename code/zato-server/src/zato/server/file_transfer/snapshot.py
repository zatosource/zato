# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import closing
from datetime import datetime
from logging import getLogger

# Zato
from zato.common.api import FILE_TRANSFER, GENERIC
from zato.common.json_ import dumps
from zato.common.odb.query.generic import FileTransferWrapper
from zato.server.connection.file_client.ftp import FTPFileClient

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.connection.ftp import FTPStore
    from zato.server.file_transfer.api import FileTransferAPI
    from zato.server.file_transfer.observer.base import BaseObserver

    BaseObserver = BaseObserver
    Bunch = Bunch
    FileTransferAPI = FileTransferAPI
    FTPStore = FTPStore

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# This must be more than 1 because 1 second is the minimum time between two invocations of a scheduled job.
default_interval = 1.1

# ################################################################################################################################
# ################################################################################################################################

class FileInfo:
    """ Information about a single file as found by a snapshot maker.
    """
    __slots__ = 'full_path', 'name', 'size', 'last_modified'

    def __init__(self, full_path='', name='', size=-1, last_modified=None):
        self.full_path = full_path
        self.name = name
        self.size = size
        self.last_modified = last_modified

# ################################################################################################################################

    def to_dict(self):
        return {
            'full_path': self.full_path,
            'name': self.name,
            'size': self.size,
            'last_modified': self.last_modified.isoformat(),
        }

# ################################################################################################################################
# ################################################################################################################################

class DirSnapshot:
    """ Represents the state of a given directory, i.e. a list of files in it.
    """
    def __init__(self):
        self.file_data = {}

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

    def to_dict(self):
        dir_snapshot_file_list = []
        out = {'dir_snapshot_file_list': dir_snapshot_file_list}

        for value in self.file_data.values(): # type: (FileInfo)
            value_as_dict = value.to_dict()
            dir_snapshot_file_list.append(value_as_dict)

        return out

# ################################################################################################################################

    def to_json(self):
        return dumps(self.to_dict())

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

                #logger.warn('VVV-1 %s %s %s', previous.name, previous.size, previous.last_modified)
                #logger.warn('VVV-2 %s %s %s', current.name, current.size, current.last_modified)
                #logger.info('-------')

                size_differs = current.size != previous.size
                last_modified_differs = current.last_modified != previous.last_modified

                if size_differs or last_modified_differs:
                    self.files_modified.add(current.name)

# ################################################################################################################################
# ################################################################################################################################

class BaseSnapshotMaker:

    def __init__(self, file_transfer_api, channel_config):
        # type: (FileTransferAPI, Bunch)
        self.file_transfer_api = file_transfer_api
        self.channel_config = channel_config
        self.file_client = None # type: BaseFileClient
        self.odb = self.file_transfer_api.server.odb

# ################################################################################################################################

    def connect(self):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def get_snapshot(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def get_file_data(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def store_snapshot(self, snapshot):
        # type: (DirSnapshot) -> None
        pass

# ################################################################################################################################
# ################################################################################################################################

class LocalSnapshotMaker(BaseSnapshotMaker):
    def connect(self):
        # Not used with local snapshots
        pass

    def get_snapshot(self, path, *args, **kwargs):
        # type: (str, bool) -> DirSnapshot

        # Output to return
        snapshot = DirSnapshot()

        # All files found in path
        file_list = []

        for item in os.listdir(path): # type: str
            full_path = os.path.abspath(os.path.join(path, item))
            if os.path.isfile(full_path):
                stat = os.stat(full_path)
                file_list.append({
                    'name': item,
                    'size': stat.st_size,
                    'last_modified': datetime.fromtimestamp(stat.st_mtime)
                })

        snapshot.add_file_list(path, file_list)

        return snapshot

# ################################################################################################################################

    def get_file_data(self, path):
        with open(path, 'rb') as f:
            return f.read()

# ################################################################################################################################
# ################################################################################################################################

class FTPSnapshotMaker(BaseSnapshotMaker):
    def connect(self):

        # Extract all the configuration ..
        ftp_store = self.file_transfer_api.server.worker_store.worker_config.out_ftp # type: FTPStore
        ftp_outconn = ftp_store.get_by_id(self.channel_config.ftp_source_id)

        # .. connect to the remote server ..
        self.file_client = FTPFileClient(ftp_outconn, self.channel_config)

        # .. and confirm that the connection works.
        self.file_client.ping()

# ################################################################################################################################

    def get_snapshot(self, path, ignored_is_recursive, is_initial=False, needs_store=False):
        # type: (str, bool) -> DirSnapshot

        # First, get a list of files under path ..
        result = self.file_client.list(path)

        # .. create a new container for the snapshot ..
        snapshot = DirSnapshot()

        # .. now, populate with what we found ..
        snapshot.add_file_list(path, result['file_list'])

        # .. if the snapshot is an initial one, store in the database for later use ..
        if is_initial:
            with closing(self.odb.session()) as session:

                # Wrapper object for accessing snapshot data
                wrapper = FileTransferWrapper(session, self.file_transfer_api.server.cluster_id)

                # A combination of our channel's ID and directory we are checking is unique
                name = '{}; {}'.format(self.channel_config.id, path)

                # Main data to store
                opaque = snapshot.to_json()

                # Store the initial state
                wrapper.store(name, opaque)

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
