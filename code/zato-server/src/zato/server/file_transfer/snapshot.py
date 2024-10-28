# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from logging import getLogger
from pathlib import Path
from traceback import format_exc

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# Zato
from zato.common.json_ import dumps
from zato.common.odb.query.generic import FTPFileTransferWrapper, SFTPFileTransferWrapper
from zato.common.typing_ import cast_
from zato.server.connection.file_client.base import PathAccessException
from zato.server.connection.file_client.ftp import FTPFileClient
from zato.server.connection.file_client.sftp import SFTPFileClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, anydict, anylist
    from zato.server.connection.file_client.base import BaseFileClient
    from zato.server.connection.ftp import FTPStore
    from zato.server.file_transfer.api import FileTransferAPI
    from zato.server.file_transfer.observer.base import BaseObserver

    BaseFileClient = BaseFileClient
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
default_interval = 1.1 # 0211111.1

# ################################################################################################################################
# ################################################################################################################################

class ItemInfo:
    """ Information about a single file as found by a snapshot maker.
    """
    full_path: 'str'
    name: 'str'
    size: 'int' = -1
    last_modified: 'datetime'
    is_dir: 'bool'
    is_file: 'bool'

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
    def __init__(self, path:'str') -> 'None':
        self.path = path
        self.file_data = {}

# ################################################################################################################################

    def add_item(self, data:'anylist') -> 'None':

        for item in data:
            item = cast_('anydict', item)

            item_info = ItemInfo()
            item_info.full_path = self.get_full_path(item)
            item_info.name = item['name']
            item_info.size = item['size']
            item_info.is_dir = item['is_dir']
            item_info.is_file = item['is_file']

            # This may be either string or a datetime object
            last_modified = item['last_modified']
            item_info.last_modified = last_modified if isinstance(last_modified, datetime) else parse_datetime(last_modified)

            self.file_data[item_info.full_path] = item_info

# ################################################################################################################################

    def get_full_path(self, item:'anydict') -> 'str':

        # Notifiers will sometimes have access to a full path to a file (e.g. local ones)
        # but sometimes they will only have the file name and the full path will have to be built
        # using the path assigned to us in the initialiser.
        full_path = item.get('full_path')

        if full_path:
            return full_path
        else:
            return os.path.join(self.path, item['name'])

# ################################################################################################################################

    def to_dict(self) -> 'anydict':
        dir_snapshot_file_list = []
        out = {'dir_snapshot_file_list': dir_snapshot_file_list}

        for value in self.file_data.values(): # type: (ItemInfo)
            value_as_dict = value.to_dict() # type: anydict
            dir_snapshot_file_list.append(value_as_dict)

        return out

# ################################################################################################################################

    def to_json(self) -> 'str':
        return dumps(self.to_dict())

# ################################################################################################################################

    @staticmethod
    def from_sql_dict(path:'str', sql_dict:'anydict') -> 'DirSnapshot':
        """ Builds a DirSnapshot object out of a dict read from the ODB.
        """
        snapshot = DirSnapshot(path)
        snapshot.add_item(sql_dict['dir_snapshot_file_list'])

        return snapshot

# ################################################################################################################################
# ################################################################################################################################

class DirSnapshotDiff:
    """ A difference between two DirSnapshot objects, i.e. all the files created and modified.
    """
    def __init__(self, previous_snapshot:'DirSnapshot', current_snapshot:'DirSnapshot') -> 'None':

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

        for current in current_snapshot.file_data.values():
            current = cast_('ItemInfo', current)
            previous = previous_snapshot.file_data.get(current.full_path)

            if previous:

                size_differs = current.size != previous.size
                last_modified_differs = current.last_modified != previous.last_modified

                if size_differs or last_modified_differs:
                    self.files_modified.add(current.full_path)

# ################################################################################################################################
# ################################################################################################################################

class AbstractSnapshotMaker:

    file_client: 'BaseFileClient'

    def __init__(self, file_transfer_api:'FileTransferAPI', channel_config:'any_') -> 'None':
        self.file_transfer_api = file_transfer_api
        self.channel_config = channel_config
        self.odb = self.file_transfer_api.server.odb

# ################################################################################################################################

    def connect(self) -> 'None':
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def get_snapshot(self, *args:'any_', **kwargs:'any_') -> 'None':
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def get_file_data(self, *args:'any_', **kwargs:'any_') -> 'None':
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def store_snapshot(self, snapshot:'DirSnapshot') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class LocalSnapshotMaker(AbstractSnapshotMaker):
    def connect(self):
        # Not used with local snapshots
        pass

    def get_snapshot(self, path:'str', *args:'any_', **kwargs:'any_') -> 'DirSnapshot':

        # Output to return
        snapshot = DirSnapshot(path)

        # All files found in path
        file_list = [] # type: anylist

        # Recursively, get all files
        listing = Path(path).rglob('*')

        for item in listing:
            full_path = str(item)
            stat = item.stat()
            file_list.append({
                'full_path': full_path,
                'name': item.name,
                'is_dir': item.is_dir(),
                'is_file': item.is_file(),
                'size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime)
            })

        snapshot.add_item(file_list)

        return snapshot

# ################################################################################################################################

    def get_file_data(self, path:'str') -> 'bytes':
        with open(path, 'rb') as f:
            return f.read()

# ################################################################################################################################
# ################################################################################################################################

class BaseRemoteSnapshotMaker(AbstractSnapshotMaker):
    """ Functionality shared by FTP and SFTP.
    """
    transfer_wrapper_class:'any_' = None
    worker_config_out_name = '<invalid-worker_config_out_name>'
    source_id_attr_name = '<invalid-source_id_attr_name>'
    file_client_class:'any_' = None
    has_get_by_id = False

# ################################################################################################################################

    def connect(self) -> 'None':

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

    def _get_current_snapshot(self, path:'str') -> 'DirSnapshot':

        # First, get a list of files under path ..
        result = self.file_client.list(path) # type: anydict

        # .. create a new container for the snapshot ..
        snapshot = DirSnapshot(path)

        if result:
            # .. now, populate with what we found ..
            snapshot.add_item(result['file_list'])

        # .. and return the result.
        return snapshot

# ################################################################################################################################

    def get_snapshot(
        self,
        path, # type: str
        ignored_is_recursive, # type: bool
        is_initial,           # type: bool
        needs_store           # type: bool
    ) -> 'DirSnapshot | None':

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
            logger.warning('%s. File transfer channel `%s` (%s); e:`%s`',
                e.args[0], self.channel_config.name, self.channel_config.source_type, format_exc())

        except Exception:
            logger.warning('Exception caught in get_snapshot (%s), e:`%s`', self.channel_config.source_type, format_exc())
            raise

        finally:
            if session:
                session.close()

# ################################################################################################################################

    def get_file_data(self, path:'str') -> 'bytes':
        return self.file_client.get(path)

# ################################################################################################################################
# ################################################################################################################################

class FTPSnapshotMaker(BaseRemoteSnapshotMaker):
    transfer_wrapper_class = FTPFileTransferWrapper
    worker_config_out_name = 'out_ftp'
    source_id_attr_name = 'ftp_source_id'
    file_client_class = FTPFileClient
    has_get_by_id = True

# ################################################################################################################################
# ################################################################################################################################

class SFTPSnapshotMaker(BaseRemoteSnapshotMaker):
    transfer_wrapper_class = SFTPFileTransferWrapper
    worker_config_out_name = 'out_sftp'
    source_id_attr_name = 'sftp_source_id'
    file_client_class = SFTPFileClient

# ################################################################################################################################
# ################################################################################################################################
