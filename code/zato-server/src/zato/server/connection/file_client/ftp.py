# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from .base import BaseFileClient

# ################################################################################################################################
# ################################################################################################################################

if 0:

    # stdlib
    from typing import BinaryIO

    # pyfilesystem
    from fs.ftpfs import FTPFS
    from fs.info import Info

    BinaryIO = BinaryIO
    FTPFS = FTPFS
    Info = Info

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The 'touch' command cannot be executed for files longer than that many bytes
touch_max_size = 200_000

# ################################################################################################################################
# ################################################################################################################################

class FTPFileClient(BaseFileClient):
    def __init__(self, conn, config):
        # type: (FTPFS) -> None
        super().__init__(config)
        self.conn = conn

# ################################################################################################################################

    def create_directory(self, path):
        self.conn.makedir(path)

# ################################################################################################################################

    def delete_directory(self, path):
        self.conn.removetree(path)

# ################################################################################################################################

    def get(self, path):
        # (str, str) -> str
        return self.conn.readbytes(path)

# ################################################################################################################################

    def get_as_file_object(self, path, file_object):
        # type: (str, BinaryIO) -> None
        self.conn.download(path, file_object)

# ################################################################################################################################

    def store(self, path, data):
        # type: (str, object) -> None
        if not isinstance(data, bytes):
            data = data.encode(self.config['encoding'])

        self.conn.writebytes(path, data)

# ################################################################################################################################

    def delete_file(self, path):
        # type: (str) -> None
        self.conn.remove(path)

# ################################################################################################################################

    def list(self, path):
        """ Returns a list of directories and files for input path.
        """
        # type: (str) -> list

        # Response to produce
        out = {
            'directory_list': [],
            'file_list': [],
        }

        # Call the remote resource
        result = self.conn.scandir(path)

        # Process all items produced
        for item in result: # type: Info

            elem = {
                'name': item.name,
                'size': item.size,
                'is_dir': item.is_dir,
                'last_modified': item.modified,
                'has_touch': item.size < touch_max_size
            }

            if item.is_dir:
                out['directory_list'].append(elem)
            else:
                out['file_list'].append(elem)

        # Sort all items by name
        self.sort_result(out)

        # Return the response to our caller
        return out

# ################################################################################################################################

    def touch(self, path):
        """ Touches a remote file by overwriting its contents with itself.
        """
        with self.conn._lock:

            # Get the current size ..
            size = self.conn.getsize(path)

            # .. make sure the file is not too big ..
            if size > touch_max_size:
                raise ValueError('File `{}` is too big for the touch command; size={}; max={}'.format(
                    path, size, touch_max_size))

            # .. read all data in ..
            with conn.openbin(path) as f:
                data = f.read(size)

            # .. and write it under the same path, effectively merely changing its modification time.
            with conn.openbin(path, 'w') as f:
                f.write(data)

# ################################################################################################################################

    def ping(self):
        return self.conn.exists('.')

# ################################################################################################################################

    def close(self):
        self.conn.close()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # pyfilesystem
    from fs.ftpfs import FTPFS

    host = 'localhost'
    user = 'abc'
    password = 'def'
    port = 11021

    conn = FTPFS(host, user, password, port=port)

    config = {
        'encoding': 'utf8'
    }

    client = FTPFileClient(conn, config)

    #client.create_directory('aaa2')
    #client.delete_directory('aaa2')

    path = '/aaa2/abc.txt2'

    client.store(path, 'zzzz')
    client.touch(path)

    result = client.list('/aaa2')

    for item in result['file_list']: # type: dict
        print(111, item)

    data = client.download(path)
    print(222, data)

    client.delete_file(path)

# ################################################################################################################################
# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from sys import maxsize
from traceback import format_exc

# gevent
from gevent import sleep

# Watchdog
from watchdog.events import FileCreatedEvent, FileModifiedEvent
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

# Zato
from zato.common.api import FILE_TRANSFER
from zato.common.util.file_transfer import parse_extra_into_list
from zato.common.util.api import spawn_greenlet
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

source_ftp  = FILE_TRANSFER.SOURCE_TYPE.FTP.id
source_sftp = FILE_TRANSFER.SOURCE_TYPE.SFTP.id

# ################################################################################################################################
# ################################################################################################################################

class SnapshotMaker:

    def __init__(self, service, outconn_config):
        # type: (Service, Bunch)
        self.service = service
        self.outconn_config = outconn_config

# ################################################################################################################################

    def get_snapshot(self):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################
# ################################################################################################################################

class FTPSnapshotMaker(SnapshotMaker):
    def get_snapshot(self):
        ftp_store = self.service.server.worker_store.worker_config.out_ftp
        ftp_outconn = ftp_store.get(self.outconn_config.name)

        logger.warn('EEE %s', ftp_outconn)

        '''
        print()
        print(111, self.outconn_config)
        print()
        '''

# ################################################################################################################################
# ################################################################################################################################

class SFTPSnapshotMaker(SnapshotMaker):
    pass

# ################################################################################################################################
# ################################################################################################################################

def get_dir_snapshot(self, path, is_recursive):
    """ Returns an implementation-specific snapshot of a directory.
    """
    # type: (BaseObserver, str, bool) -> None

    logger.warn('EEE %s %s', path, is_recursive)

# ################################################################################################################################
# ################################################################################################################################

def observe_with_snapshots(self, path, max_iters=maxsize, *args, **kwargs):
    """ An observer's main loop that uses snapshots.
    """
    # type: (BaseObserver, str) -> None

    try:

        # Local aliases to avoid namespace lookups in self
        timeout = self.default_timeout
        handler_func = self.event_handler.on_created
        is_recursive = self.is_recursive

        # How many times to run the loop - either given on input or, essentially, infinitely.
        current_iter = 0

        # Take an initial snapshot
        snapshot = self.get_dir_snapshot(self, path, is_recursive)

        while self.keep_running:

            if current_iter == max_iters:
                break

            try:

                # The latest snapshot ..
                new_snapshot = self.get_dir_snapshot(self, path, is_recursive)

                # .. difference between the old and new will return, in particular, new or modified files ..
                diff = DirectorySnapshotDiff(snapshot, new_snapshot)

                for path_created in diff.files_created:
                    handler_func(FileCreatedEvent(path_created))

                for path_modified in diff.files_modified:
                    handler_func(FileModifiedEvent(path_modified))

                # .. a new snapshot which will be treated as the old one in the next iteration ..
                snapshot = self.get_dir_snapshot(self, path, is_recursive)

            except FileNotFoundError:

                # Log the error ..
                logger.warn('File not found caught in %s observer main loop `%s` (%s t:%s) e:`%s',
                    self.observer_type_name, path, format_exc(), self.name, self.observer_type_impl)

                # .. start a background inspector which will wait for the path to become available ..
                self.manager.wait_for_deleted_path(path)

                # .. and end the main loop.
                return

            except Exception:
                logger.warn('Exception in %s observer main loop `%s` e:`%s (%s t:%s)',
                    self.observer_type_name, path, format_exc(), self.name, self.observer_type_impl)
            finally:

                # Update look counter ..
                current_iter += 1

                # .. and sleep for a moment.
                sleep(timeout)

    except Exception:
        logger.warn('Exception in %s observer `%s` e:`%s (%s t:%s)',
            self.observer_type_name, path, format_exc(), self.name, self.observer_type_impl)

    # We get here only when self.keep_running is False = we are to stop
    logger.info('Stopped %s transfer observer `%s` for `%s` (snapshot:%s/%s)',
        self.observer_type_name, self.name, path, current_iter, max_iters)

# ################################################################################################################################
# ################################################################################################################################

class ChannelFileTransferHandler(Service):
    """ A no-op marker service uses by file transfer channels.
    """
    name = FILE_TRANSFER.SCHEDULER_SERVICE

# ################################################################################################################################

    def run_observer(self, channel_id):
        # type: (int) -> None

        observer = self.server.worker_store.file_transfer_api.get_observer_by_channel_id(channel_id)
        observer.get_dir_snapshot = get_dir_snapshot
        observer.observe_with_snapshots = observe_with_snapshots

        source_type_to_config = {
            source_ftp:  'out_ftp',
            source_sftp: 'out_sftp',
        }

        source_type_to_snapshot_maker_class = {
            source_ftp:  FTPSnapshotMaker,
            source_sftp: SFTPSnapshotMaker,
        }

        source_type = observer.channel_config.source_type
        source_id   = observer.channel_config.ftp_source_id

        config_key  = source_type_to_config[source_type] # type: str
        config      = self.server.worker_store.worker_config.get_config_by_item_id(config_key, source_id)

        snapshot_maker_class = source_type_to_snapshot_maker_class[source_type]
        snapshot_maker = snapshot_maker_class(self, config) # type: (SnapshotMaker)

        snapshot = snapshot_maker.get_snapshot()

        #config_key  = source_type_to_config[source_type]
        #config_dict = self.server.worker_store.worker_config[config_key]

        #config = config_dict[source_id]

        #self.logger.warn('QQQ %s', config)

        '''
        for item in observer.path_list: # type: (str)
            self.logger.warn('ZZZ-2 `%s`', item)

            observer.observe_with_snapshots(observer, item, 1)
            '''

# ################################################################################################################################

    def handle(self):

        extra = '16;'#; 17' #self.request.raw_request

        # Convert input parameters into a list of channel (observer) IDs ..
        extra = parse_extra_into_list(extra)

        # .. and run each observer in a new greenlet.
        for channel_id in extra:
            spawn_greenlet(self.run_observer, channel_id)

# ################################################################################################################################
# ################################################################################################################################
'''
