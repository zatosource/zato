# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import os
from datetime import datetime
from http.client import OK
from importlib import import_module
from mimetypes import guess_type as guess_mime_type
from re import IGNORECASE
from sys import maxsize
from traceback import format_exc

# gevent
from gevent import sleep
from gevent.lock import RLock

# globre
import globre

# Zato
from zato.common.api import FILE_TRANSFER
from zato.common.util.api import new_cid, spawn_greenlet
from zato.common.util.platform_ import is_linux
from zato.server.file_transfer.event import FileTransferEventHandler, singleton
from zato.server.file_transfer.observer.base import BackgroundPathInspector, PathCreatedEvent
from zato.server.file_transfer.observer.local_ import LocalObserver
from zato.server.file_transfer.observer.ftp import FTPObserver
from zato.server.file_transfer.observer.sftp import SFTPObserver
from zato.server.file_transfer.snapshot import FTPSnapshotMaker, LocalSnapshotMaker, SFTPSnapshotMaker

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from requests import Response
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.worker import WorkerStore
    from zato.server.file_transfer.event import FileTransferEvent
    from zato.server.file_transfer.observer.base import BaseObserver
    from zato.server.file_transfer.snapshot import BaseSnapshotMaker

    BaseObserver = BaseObserver
    BaseSnapshotMaker = BaseSnapshotMaker
    Bunch = Bunch
    FileTransferEvent
    ParallelServer = ParallelServer
    Response = Response
    WorkerStore = WorkerStore

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

source_type_ftp   = FILE_TRANSFER.SOURCE_TYPE.FTP.id
source_type_local = FILE_TRANSFER.SOURCE_TYPE.LOCAL.id
source_type_sftp  = FILE_TRANSFER.SOURCE_TYPE.SFTP.id

source_type_to_observer_class = {
    source_type_ftp:   FTPObserver,
    source_type_local: LocalObserver,
    source_type_sftp:  SFTPObserver,
}

source_type_to_config = {
    source_type_ftp:  'out_ftp',
    source_type_sftp: 'out_sftp',
}

source_type_to_snapshot_maker_class = {
    source_type_ftp:   FTPSnapshotMaker,
    source_type_local: LocalSnapshotMaker,
    source_type_sftp:  SFTPSnapshotMaker,
}

# Under Linux, we prefer to use inotify instead of snapshots.
prefer_inotify = is_linux

# ################################################################################################################################
# ################################################################################################################################

class FileTransferAPI(object):
    """ Manages file transfer observers and callbacks.
    """
    def __init__(self, server, worker_store):
        # type: (ParallelServer, WorkerStore) -> None

        self.server = server
        self.worker_store = worker_store
        self.update_lock = RLock()

        self.keep_running = True

        # A list of all observer objects
        self.observer_list = []

        # A mapping of channel_id to an observer object associated with the channel.
        # Note that only non-inotify observers are added here.
        self.observer_dict = {}

        # Caches parser objects by their name
        self._parser_cache = {}

        if is_linux:

            # inotify_simple
            from inotify_simple import flags as inotify_flags, INotify

            self.inotify_lock = RLock()

            self.inotify = INotify()
            self.inotify_flags = inotify_flags.CLOSE_WRITE

            self.inotify_wd_to_path = {}
            self.inotify_path_to_observer_list = {}

            # Inotify is used only under Linux
            self.observer_start_args = self.inotify, self.inotify_flags, self.inotify_lock, self.inotify_wd_to_path

        else:
            self.observer_start_args = ()

        # Maps channel name to a list of globre patterns for the channel's directories
        self.pattern_matcher_dict = {}

# ################################################################################################################################

    def _create(self, config):
        """ Low-level implementation of self.create.
        """
        # type: (Bunch) -> None
        flags = globre.EXACT

        if not config.is_case_sensitive:
            flags |= IGNORECASE

        file_patterns = config.file_patterns
        pattern_matcher_list = [file_patterns] if not isinstance(file_patterns, list) else file_patterns
        pattern_matcher_list = [globre.compile(elem, flags) for elem in file_patterns]
        self.pattern_matcher_dict[config.name] = pattern_matcher_list

        # This will be a list in the case of pickup.conf and not a list if read from ODB-based file transfer channels
        if isinstance(config.pickup_from_list, list):
            pickup_from_list = config.pickup_from_list
        else:
            pickup_from_list = str(config.pickup_from_list) # type: str
            pickup_from_list = [elem.strip() for elem in pickup_from_list.splitlines()]

        # Make sure that a parser is given if we are to parse any input ..
        if config.should_parse_on_pickup:

            # .. log a warning and disable parsing if no parser was configured when it was expected.
            if not config.parse_with:
                logger.warn('Parsing is enabled but no parser is declared for file transfer channel `%s` (%s)',
                    config.name, config.source_type)
                config.should_parse_on_pickup = False

        # Create an observer object ..
        observer_class = source_type_to_observer_class[config.source_type]
        observer = observer_class(self, config) # type: BaseObserver

        # .. and add it to data containers ..
        self.observer_list.append(observer)

        # .. but do not add it to the mapping dict because locally-defined observers (from pickup.conf)
        # may not have any ID, or to be more precise, the may have the same ID.

        if not observer.is_notify:
            self.observer_dict[observer.channel_id] = observer

        # .. finally, set up directories and callbacks for the observer.
        event_handler = FileTransferEventHandler(self, config.name, config)
        observer.set_up(event_handler, pickup_from_list, recursive=False)

# ################################################################################################################################

    def create(self, config):
        """ Creates a file transfer channel (but does not start it).
        """
        # type: (Bunch) -> None
        with self.update_lock:
            self._create(config)

# ################################################################################################################################

    def _delete(self, config):
        """ Low-level implementation of self.delete.
        """
        # type: (Bunch) -> None

        # Observer object to delete ..
        observer_to_delete = None

        # .. paths under which the observer may be listed (used only under Linux with inotify).
        observer_path_list = []

        # .. stop its main loop ..
        for observer in self.observer_list: # type: LocalObserver
            if observer.channel_id == config.id:
                needs_log = observer.is_local and (not prefer_inotify)
                observer.stop(needs_log=needs_log)
                observer_to_delete = observer
                observer_path_list[:] = observer.path_list
                break
        else:
            raise ValueError('Could not find observer matching ID `%s` (%s)', config.id, config.type_)

        # .. if the object was found ..
        if observer_to_delete:

            # .. delete it from the main list ..
            self.observer_list.remove(observer_to_delete)

            # .. delete it from the mapping of channels to observers as well ..
            if not observer_to_delete.is_local:
                self.observer_dict.pop(observer_to_delete.channel_id)

            # .. for local transfer under Linux, delete it from any references among paths being observed via inotify.
            if prefer_inotify and config.source_type == source_type_local:
                for path in observer_path_list:
                    observer_list = self.inotify_path_to_observer_list.get(path) # type: list
                    observer_list.remove(observer_to_delete)

# ################################################################################################################################

    def delete(self, config):
        """ Deletes a file transfer channel.
        """
        # type: (Bunch) -> None
        with self.update_lock:
            self._delete(config)

# ################################################################################################################################

    def edit(self, config):
        """ Edits a file transfer channel by deleting and recreating it.
        """
        # type: (Bunch) -> None
        with self.update_lock:

            # Delte the channel first ..
            self._delete(config)

            # .. recreate it ..
            self._create(config)

            # .. and start it if it is enabled ..
            if config.is_active:

                # .. but only if it is a local one because any other is triggerd by our scheduler ..
                if config.source_type == source_type_local:
                    self.start_observer(config.name, True)

            # .. we can now find our new observer object ..
            observer = self.get_observer_by_channel_id(config.id) # type: BaseObserver

            # .. to finally store a message that we are done.
            logger.info('%s file observer `%s` set up successfully (%s) (%s)',
                observer.observer_type_name_title, observer.name, observer.observer_type_impl, observer.path_list)

# ################################################################################################################################

    def get_py_parser(self, name):
        """ Imports a Python object that represents a parser.
        """
        parts = name.split('.')
        module_path, callable_name = '.'.join(parts[0:-1]), parts[-1]

        return getattr(import_module(module_path), callable_name)

# ################################################################################################################################

    def get_service_parser(self, name):
        """ Returns a service that will act as a parser.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def get_parser(self, parser_name):
        """ Returns a parser by name (may possibly return an already cached one).
        """
        if parser_name in self._parser_cache:
            return self._parser_cache[parser_name]

        type, name = parser_name.strip().split(':')

        parser = self.get_py_parser(name) if type == 'py' else self.get_service_parser(name)
        self._parser_cache[parser_name] = parser

        return parser

# ################################################################################################################################

    def get_observer_by_channel_id(self, channel_id):
        # type: (int) -> BaseObserver
        return self.observer_dict[channel_id]

# ################################################################################################################################

    def should_handle(self, channel_name, file_name):
        for pattern in self.pattern_matcher_dict[channel_name]:
            if pattern.match(file_name):
                return True

# ################################################################################################################################

    def invoke_callbacks(self, event, service_list, topic_list, outconn_rest_list):
        # type: (FileTransferEvent, list, list, list) -> None

        config = self.worker_store.get_channel_file_transfer_config(event.channel_name)

        request = {
            'base_dir': event.base_dir,
            'file_name': event.file_name,
            'full_path': event.full_path,
            'channel_name': event.channel_name,
            'ts_utc': datetime.utcnow().isoformat(),
            'raw_data': event.raw_data,
            'data': event.data if event.data is not singleton else None,
            'has_raw_data': event.has_raw_data,
            'has_data': event.has_data,
            'parse_error': event.parse_error,
            'config': config,
        }

        # Services
        self.invoke_service_callbacks(service_list, request)

        # Topics
        self.invoke_topic_callbacks(topic_list, request)

        # REST outgoing connections
        self.invoke_rest_outconn_callbacks(outconn_rest_list, request)

# ################################################################################################################################

    def invoke_service_callbacks(self, service_list, request):
        # type: (list, dict) -> None

        for item in service_list: # type: str
            try:
                spawn_greenlet(self.server.invoke, item, request)
            except Exception:
                logger.warn(format_exc())

# ################################################################################################################################

    def invoke_topic_callbacks(self, topic_list, request):
        # type: (list, dict) -> None

        for item in topic_list: # type: str
            try:
                spawn_greenlet(self.server.invoke, item, request)
            except Exception:
                logger.warn(format_exc())

# ################################################################################################################################

    def _invoke_rest_outconn_callback(self, item_id, request):
        # type: (str, dict) -> None

        cid = new_cid()

        item = self.worker_store.get_outconn_rest_by_id(item_id)
        ping_response = item.ping(cid, return_response=True, log_verbose=True) # type: Response

        if ping_response.status_code != OK:

            logger.warn('Could not ping file transfer connection for `%s` (%s); config:`%s`, r:`%s`, h:`%s`',
                request['full_path'], request['config'].name, item.config, ping_response.text, ping_response.headers)

        else:

            file_name = request['file_name']

            mime_type = guess_mime_type(file_name, strict=False)
            mime_type = mime_type[0] if mime_type[0] else 'application/octet-stream'

            payload = request['raw_data']
            params = {'file_name': file_name, 'mime_type': mime_type}

            headers = {
                'X-Zato-File-Name': file_name,
                'X-Zato-Mime-Type': mime_type,
            }

            response = item.conn.post(cid, payload, params, headers=headers) # type: Response

            if response.status_code != OK:
                logger.warn('Could not send file `%s` (%s) to `%s` (p:`%s`, h:`%s`), r:`%s`, h:`%s`',
                    request['full_path'], request['config'].name, item.config, params, headers,
                    response.text, response.headers)

# ################################################################################################################################

    def invoke_rest_outconn_callbacks(self, outconn_rest_list, request):
        # type: (list, dict) -> None

        for item_id in outconn_rest_list: # type: int
            spawn_greenlet(self._invoke_rest_outconn_callback, item_id, request)

# ################################################################################################################################

    def post_handle(self, event, config, observer, snapshot_maker):
        """ Runs after callback services have been already invoked, performs clean up if configured to.
        """
        # type: (FileTransferEvent, Bunch, BaseObserver, BaseSnapshotMaker) -> None
        if config.move_processed_to:
            observer.move_file(event.full_path, config.move_processed_to, observer, snapshot_maker)

        if config.should_delete_after_pickup:
            observer.delete_file(event.full_path, snapshot_maker)

# ################################################################################################################################

    def _run_linux_inotify_loop(self):

        while self.keep_running:
            try:
                for event in self.inotify.read(0):
                    try:

                        # Build a full path to the file we are processing
                        dir_name = self.inotify_wd_to_path[event.wd]
                        src_path = os.path.normpath(os.path.join(dir_name, event.name))

                        # Get a list of all observer objects interested in that file ..
                        observer_list = self.inotify_path_to_observer_list[dir_name] # type: list

                        # .. and notify each one.
                        for observer in observer_list: # type: LocalObserver
                            observer.event_handler.on_created(PathCreatedEvent(src_path), observer)

                    except Exception:
                        logger.warn('Exception in inotify handler `%s`', format_exc())
            except Exception:
                logger.warn('Exception in inotify.read() `%s`', format_exc())
            finally:
                sleep(0.25)

# ################################################################################################################################

    def _run(self, name=None, log_after_started=False):

        # Under Linux, for each observer, map each of its watched directories
        # to the actual observer object so that when an event is emitted
        # we will know, based on the event's full path, which observers to notify.
        self.inotify_path_to_observer_list = {}

        for observer in self.observer_list: # type: LocalObserver

            for path in observer.path_list: # type: str
                observer_list = self.inotify_path_to_observer_list.setdefault(path, []) # type: list
                observer_list.append(observer)

        # Maps missing paths to all the observers interested in it.
        missing_path_to_inspector = {}

        # Start the observer objects, creating inotify watch descriptors (wd) in background ..
        for observer in self.observer_list: # type: BaseObserver

            try:

                # Skip non-local observers
                if not observer.is_local:
                    continue

                # Filter out unneeded names
                if name and name != observer.name:
                    continue

                # Quickly check if any of the observer's path is missing and if it is, do not start it now.
                # Instead, we will run a background task that will wait until the path becomes available and when it is,
                # it will add start the observer itself.
                for path in observer.path_list:
                    if not observer.is_path_valid(path):
                        path_observer_list = missing_path_to_inspector.setdefault(path, []) # type: list
                        path_observer_list.append(BackgroundPathInspector(path, observer, self.observer_start_args))

                # Inotify-based observers are set up here but their main loop is in _run_linux_inotify_loop ..
                if prefer_inotify:
                    observer.start(self.observer_start_args)

                # .. whereas snapshot observers are started here.
                else:
                    self._run_snapshot_observer(observer)

                if log_after_started:
                    logger.info('Started file observer `%s` path:`%s`', observer.name, observer.path_list)

            except Exception:
                logger.warn('File observer `%s` could not be started, path:`%s`, e:`%s`',
                    observer.name, observer.path_list, format_exc())

        # If there are any paths missing for any observer ..
        if missing_path_to_inspector:

            # .. wait for each such path in background.
            self.run_inspectors(missing_path_to_inspector)

        # Under Linux, run the inotify main loop for each watch descriptor created for paths that do exist.
        # Note that if we are not on Linux, each observer.start call above already ran a new greenlet with an observer
        # for a particular directory.
        if prefer_inotify:
            spawn_greenlet(self._run_linux_inotify_loop)

# ################################################################################################################################

    def get_inspector_list_by_path(self, path):
        # type: (str) -> dict

        # Maps the input path to inspectors.
        path_to_inspector = {}

        # For each observer defined ..
        for observer in self.observer_list: # type: BaseObserver

            # .. check if our input path is among the paths defined for that observer ..
            if path in observer.path_list:

                # .. it was, so we append an inspector for the path, pointing to current observer.
                path_observer_list = path_to_inspector.setdefault(path, []) # type: list
                path_observer_list.append(BackgroundPathInspector(path, observer, self.observer_start_args))

        return path_to_inspector

# ################################################################################################################################

    def run_inspectors(self, path_to_inspector_list):
        # type: (dict) -> None

        # Run background inspectors waiting for each path from the list
        for path, inspector_list in path_to_inspector_list.items(): # type: (str, list)
            for inspector in inspector_list: # type: BackgroundPathInspector
                inspector.start()

# ################################################################################################################################

    def wait_for_deleted_path(self, path):
        path_to_inspector = self.get_inspector_list_by_path(path)
        self.run_inspectors(path_to_inspector)

# ################################################################################################################################

    def run(self):
        self._run()

# ################################################################################################################################

    def start_observer(self, name, log_after_started=False):
        self._run(name, log_after_started)

# ################################################################################################################################

    def _run_snapshot_observer(self, observer, max_iters=maxsize):
        # type: (BaseObserver, int) -> None

        if not observer.is_active:
            return

        source_type = observer.channel_config.source_type   # type: str
        snapshot_maker_class = source_type_to_snapshot_maker_class[source_type]

        snapshot_maker = snapshot_maker_class(self, observer.channel_config) # type: (BaseSnapshotMaker)
        snapshot_maker.connect()

        for item in observer.path_list: # type: (str)
            spawn_greenlet(observer.observe_with_snapshots, snapshot_maker, item, max_iters, False)

# ################################################################################################################################

    def run_snapshot_observer(self, channel_id, max_iters):
        # type: (int, int) -> None
        observer = self.get_observer_by_channel_id(channel_id) # type: BaseObserver
        self._run_snapshot_observer(observer, max_iters)

# ################################################################################################################################
