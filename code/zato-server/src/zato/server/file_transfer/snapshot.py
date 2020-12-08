# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from logging import getLogger
from traceback import format_exc

# dateutil
from dateutil.parser import parse as dt_parse

# Zato
from zato.common.json_ import dumps
from zato.common.odb.query.generic import FTPFileTransferWrapper, SFTPFileTransferWrapper
from zato.server.connection.file_client.base import PathAccessException
from zato.server.connection.file_client.ftp import FTPFileClient
from zato.server.connection.file_client.sftp import SFTPFileClient

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
    def __init__(self, path):
        # type: (str) -> None
        self.path = path
        self.file_data = {}

# ################################################################################################################################

    def add_file_list(self, data):
        # type: (str, list) -> None
        for item in data: # type: (dict)

            file_info = FileInfo()
            file_info.full_path = os.path.join(self.path, item['name'])
            file_info.name = item['name']
            file_info.size = item['size']

            # This may be either string or a datetime object
            last_modified = item['last_modified']
            file_info.last_modified = last_modified if isinstance(last_modified, datetime) else dt_parse(last_modified)

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

    @staticmethod
    def from_sql_dict(path, sql_dict):
        """ Builds a DirSnapshot object out of a dict read from the ODB.
        """
        # type: (dict) -> DirSnapshot

        snapshot = DirSnapshot(path)
        snapshot.add_file_list(sql_dict['dir_snapshot_file_list'])

        return snapshot

# ################################################################################################################################
# ################################################################################################################################

class DirSnapshotDiff:
    """ A difference between two DirSnapshot objects, i.e. all the files created and modified.
    """
    __slots__ = 'files_created', 'files_modified'

    def __init__(self, previous_snapshot, current_snapshot):
        # type: (DirSnapshot, DirSnapshot)


        # These will be new for sure ..
        self.files_created = set()

        # .. used to prepare a list of files that were potentially modified.
        self.files_modified = set()

        # We require for both snapshots to exist, otherwise we just return.
        if not (previous_snapshot and current_snapshot):
            return

        # New files ..
        self.files_created = set(current_snapshot.file_data) - set(previous_snapshot.file_data)

        # .. now, go through each file in the current snapshot and compare its timestamps and file size
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

class AbstractSnapshotMaker:

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

class LocalSnapshotMaker(AbstractSnapshotMaker):
    def connect(self):
        # Not used with local snapshots
        pass

    def get_snapshot(self, path, *args, **kwargs):
        # type: (str, bool) -> DirSnapshot

        # Output to return
        snapshot = DirSnapshot(path)

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

        snapshot.add_file_list(file_list)

        return snapshot

# ################################################################################################################################

    def get_file_data(self, path):
        with open(path, 'rb') as f:
            return f.read()

# ################################################################################################################################
# ################################################################################################################################

class BaseSnapshotMaker(AbstractSnapshotMaker):
    """ Functionality shared by FTP and SFTP.
    """
    transfer_wrapper_class = None
    worker_config_out_name = '<invalid-worker_config_out_name>'
    source_id_attr_name = '<invalid-source_id_attr_name>'
    file_client_class = None
    has_get_by_id = False

# ################################################################################################################################

    def connect(self):

        # Extract all the configuration ..
        store = getattr(self.file_transfer_api.server.worker_store.worker_config, self.worker_config_out_name)
        source_id = int(self.channel_config[self.source_id_attr_name])

        # Some connection types will directly expose this method ..
        if self.has_get_by_id:
            outconn = store.get_by_id(source_id)

        # .. while some will not.
        else:
            for value in store.values():
                config = value['config']
                if config['id'] == source_id:
                    outconn = value.conn
                    break
            else:
                raise ValueError('ID not found in `{}`'.format(store.values()))

        # .. connect to the remote server ..
        self.file_client = self.file_client_class(outconn, self.channel_config)

        # .. and confirm that the connection works.
        self.file_client.ping()

# ################################################################################################################################

    def _get_current_snapshot(self, path):
        # type: (str) -> DirSnapshot

        # First, get a list of files under path ..
        result = self.file_client.list(path)

        #logger.warn('ZZZ-1 %s', self.file_client.list)
        #logger.warn('ZZZ-2 %s', path)
        #logger.warn('ZZZ-3 %s', result)

        # .. create a new container for the snapshot ..
        snapshot = DirSnapshot(path)

        if result:
            # .. now, populate with what we found ..
            snapshot.add_file_list(result['file_list'])

        # .. and return the result.
        return snapshot

# ################################################################################################################################

    def get_snapshot(self, path, ignored_is_recursive, is_initial, needs_store):
        # type: (str, bool) -> DirSnapshot

        # We are not sure yet if we are to need it.
        session = None

        # A combination of our channel's ID and directory we are checking is unique
        name = '{}; {}'.format(self.channel_config.id, path)

        try:
            # If we otherwise know that we will access the database,
            # we can create a new SQL session here.
            if needs_store:
                session = self.odb.session()
                wrapper = self.transfer_wrapper_class(session, self.file_transfer_api.server.cluster_id)

            # If this is the observer's initial snapshot ..
            if is_initial:

                # .. we need to check if we may perhaps have it in the ODB ..
                already_existing = wrapper.get(name)

                # .. if we do, we can return it ..
                if already_existing:
                    return DirSnapshot.from_sql_dict(path, already_existing)

                # .. otherwise, we return the current state of the remote resource.
                else:
                    return self._get_current_snapshot(path)

            # .. this is not the initial snapshot so we need to make one ..
            snapshot = self._get_current_snapshot(path)

            # .. store it if we are told to ..
            if needs_store:
                wrapper.store(name, snapshot.to_json())

            # .. and return the result to our caller.
            return snapshot

        except PathAccessException as e:
            logger.warn('%s. File transfer channel `%s` (%s); e:`%s`',
                e.args[0], self.channel_config.name, self.channel_config.source_type, format_exc())

        except Exception:
            logger.warn('Exception caught in get_snapshot (%s), e:`%s`', self.channel_config.source_type, format_exc())
            raise

        finally:
            if session:
                session.close()

# ################################################################################################################################

    def get_file_data(self, path):
        # type: (str) -> bytes
        return self.file_client.get(path)

# ################################################################################################################################
# ################################################################################################################################

class FTPSnapshotMaker(BaseSnapshotMaker):
    transfer_wrapper_class = FTPFileTransferWrapper
    worker_config_out_name = 'out_ftp'
    source_id_attr_name = 'ftp_source_id'
    file_client_class = FTPFileClient
    has_get_by_id = True

# ################################################################################################################################
# ################################################################################################################################

class SFTPSnapshotMaker(BaseSnapshotMaker):
    transfer_wrapper_class = SFTPFileTransferWrapper
    worker_config_out_name = 'out_sftp'
    source_id_attr_name = 'sftp_source_id'
    file_client_class = SFTPFileClient

# ################################################################################################################################
# ################################################################################################################################
