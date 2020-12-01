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
from shutil import copy as shutil_copy
from traceback import format_exc

# gevent
from gevent import sleep
from gevent.lock import RLock

# globre
import globre

# Zato
from zato.common.api import FILE_TRANSFER
from zato.common.util.api import hot_deploy, new_cid, spawn_greenlet
from zato.common.util.platform_ import is_linux
from .observer.base import BackgroundPathInspector
from .observer.local_ import LocalObserver, PathCreatedEvent
from .observer.ftp import FTPObserver

# ################################################################################################################################

if 0:
    from requests import Response
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.worker import WorkerStore
    from .observer.base import BaseObserver

    BaseObserver = BaseObserver
    ParallelServer = ParallelServer
    Response = Response
    WorkerStore = WorkerStore

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

_singleton = object()
_zato_orig_marker = 'zato_orig_'

# ################################################################################################################################

source_type_to_observer_class = {
    FILE_TRANSFER.SOURCE_TYPE.FTP.id:   FTPObserver,
    FILE_TRANSFER.SOURCE_TYPE.LOCAL.id: LocalObserver,
}

# ################################################################################################################################
# ################################################################################################################################

class FileTransferEventHandler:

    def __init__(self, manager, channel_name, config):
        # type: (FileTransferAPI, str, Bunch) -> None

        self.manager = manager
        self.channel_name = channel_name
        self.config = config

    def on_created(self, transfer_event):
        # type: (PathCreatedEvent) -> None

        try:

            # Ignore the event if it points to the directory itself,
            # as inotify will send CLOSE_WRITE when it is not a creation of a file
            # but a fact that a directory has been deleted that the event is about.
            # Note that we issue a log entry only if the path is not one of what
            # we observe, i.e. when one of our own directories is deleted, we do not log it here.

            # The path must have existed since we are being called
            # and we need to check why it does not exist anymore ..
            if not os.path.exists(transfer_event.src_path):

                # .. if it is one of the paths that we observe, it means that it has been just deleted,
                # so we need to run a background inspector which will wait until it is created once again ..
                if transfer_event.src_path in self.config.pickup_from_list:
                    self.manager.wait_for_deleted_path(transfer_event.src_path)

                else:
                    logger.info('Ignoring local file event; path not found `%s` (%r)', transfer_event.src_path, self.config.name)

                # .. in either case, there is nothing else we can do here.
                return

            # Get file name to check if we should handle it ..
            file_name = os.path.basename(transfer_event.src_path) # type: str

            # .. return if we should not.
            if not self.manager.should_handle(self.config.name, file_name):
                return

            event = FileTransferEvent()
            event.full_path = transfer_event.src_path
            event.base_dir = os.path.dirname(transfer_event.src_path)
            event.file_name = file_name
            event.channel_name = self.channel_name

            if self.config.is_hot_deploy:
                spawn_greenlet(hot_deploy, self.manager.server, event.file_name, event.full_path,
                    self.config.should_delete_after_pickup)
                return

            if self.config.should_read_on_pickup:

                f = open(event.full_path, 'rb')
                event.raw_data = f.read().decode(self.config.data_encoding)
                event.has_raw_data = True
                f.close()

                if self.config.should_parse_on_pickup:

                    try:
                        event.data = self.manager.get_parser(self.config.parse_with)(event.raw_data)
                        event.has_data = True
                    except Exception as e:
                        event.parse_error = e

            # Invokes all callbacks for the event
            spawn_greenlet(self.manager.invoke_callbacks, event, self.config.service_list, self.config.topic_list,
                self.config.outconn_rest_list)

            # Performs cleanup actions
            self.manager.post_handle(event.full_path, self.config)

        except Exception:
            logger.warn('Exception in pickup event handler `%s` (%s) `%s`',
                self.config.name, transfer_event.src_path, format_exc())

    on_modified = on_created

# ################################################################################################################################
# ################################################################################################################################

class FileTransferEvent(object):
    """ Encapsulates information about a file picked up from file system.
    """
    __slots__ = ('base_dir', 'file_name', 'full_path', 'channel_name', 'ts_utc', 'raw_data', 'data', 'has_raw_data', 'has_data',
        'parse_error')

    def __init__(self):
        self.base_dir = None      # type: str
        self.file_name = None     # type: str
        self.full_path = None     # type: str
        self.channel_name = None  # type: str
        self.ts_utc = None        # type: str
        self.raw_data = ''        # type: str
        self.data = _singleton    # type: str
        self.has_raw_data = False # type: bool
        self.has_data = False     # type: bool
        self.parse_error = None   # type: str

# ################################################################################################################################
# ################################################################################################################################

class FileTransferAPI(object):
    """ Manages file transfer observers and callbacks.
    """
    def __init__(self, server, worker_store):
        # type: (ParallelServer, WorkerStore) -> None

        self.server = server
        self.worker_store = worker_store

        self.keep_running = True

        # A list of all observer objects
        self.observer_list = []

        # A mapping of channel_id to an observer object associated with the channel
        self.observer_dict = {}

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

    def create(self, config):
        # type: (Bunch) -> None

        # Ignore internal channels
        if config.name.startswith(_zato_orig_marker):
            return

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

        # Create an observer object ..
        observer_class = source_type_to_observer_class[config.source_type]
        observer = observer_class(self, config.id, config.source_type, config.name, config.is_active, 0.25)

        # .. and add it to data containers ..
        self.observer_list.append(observer)

        # .. but do not add it to the mapping dict because locally-defined observers (from pickup.conf)
        # may not have any ID, or to be more precise, the may have the same ID.
        if not observer.is_local:
            self.observer_dict[observer.channel_id] = observer

        # .. but do not start any observer other than a local one.
        # All the non-local ones are triggered from the scheduler.
        if observer.is_local:
            event_handler = FileTransferEventHandler(self, config.name, config)
            observer.schedule(event_handler, pickup_from_list, recursive=False)

# ################################################################################################################################

    def delete(self, config):

        # Observer object to delete ..
        observer_to_delete = None

        # .. paths under which the observer may be listed (used only under Linux with inotify).
        observer_path_list = []

        # .. stop its main loop ..
        for observer in self.observer_list: # type: LocalObserver
            if observer.name == config.name:
                observer.stop()
                observer_to_delete = observer
                observer_path_list[:] = observer.path_list
                break
        else:
            raise ValueError('Could not find observer matching name `%s` (%s)', config.name, config.type_)

        # .. if the object was found ..
        if observer_to_delete:

            # .. delete it from the main list ..
            self.observer_list.remove(observer_to_delete)

            # .. delete it from the mapping of channels to observers as well ..
            self.observer_dict.pop(observer_to_delete.channel_id)

            # .. under Linux, delete it from from any references to it among paths being observed via inotify.
            if is_linux:
                for path in observer_path_list:
                    observer_list = self.inotify_path_to_observer_list.get(path) # type: list
                    observer_list.remove(observer_to_delete)

# ################################################################################################################################

    def get_py_parser(self, name):
        parts = name.split('.')
        module_path, callable_name = '.'.join(parts[0:-1]), parts[-1]

        return getattr(import_module(module_path), callable_name)

# ################################################################################################################################

    def get_service_parser(self, name):
        raise NotImplementedError('Not implemented in current version')

# ################################################################################################################################

    def get_parser(self, parser_name):
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
            'data': event.data if event.data is not _singleton else None,
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

    def post_handle(self, full_path, config):
        """ Runs after callback services have been already invoked, performs clean up if configured to.
        """
        # type: (str, Bunch) -> None

        if config.move_processed_to:
            shutil_copy(full_path, config.move_processed_to)

        if config.should_delete_after_pickup:
            os.remove(full_path)

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
                            observer.event_handler.on_created(PathCreatedEvent(src_path))

                    except Exception:
                        logger.warn('Exception in inotify handler `%s`', format_exc())
            except Exception:
                logger.warn('Exception in inotify.read() `%s`', format_exc())
            finally:
                sleep(0.25)

# ################################################################################################################################

    def _run(self, name=None):

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

                # Start the observer object.
                observer.start(self.observer_start_args)

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
        if is_linux:
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

    def start_observer(self, name):
        self._run(name)

# ################################################################################################################################
