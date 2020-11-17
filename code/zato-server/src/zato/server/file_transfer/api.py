# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

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
from zato.common.util.api import hot_deploy, new_cid, spawn_greenlet
from zato.common.util.platform_ import is_linux
from .observer.local_ import LocalObserver, InotifyEvent

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
# ################################################################################################################################

class FileTransferEventHandler:

    def __init__(self, manager, channel_name, config):
        # type: (FileTransferAPI, str, Bunch) -> None

        self.manager = manager
        self.channel_name = channel_name
        self.config = config

    def on_created(self, transfer_event):
        # type: (FileTransferEvent) -> None

        try:

            file_name = os.path.basename(transfer_event.src_path) # type: str

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
        self.observers = []

        if is_linux:

            # inotify_simple
            from inotify_simple import flags as inotify_flags, INotify

            self.inotify_lock = RLock()

            self.inotify = INotify()
            self.inotify_flags = inotify_flags.CLOSE_WRITE

            self.inotify_wd_to_path = {}
            self.inotify_path_to_observer_list = {}

        # Maps channel name to a list of globre patterns for the channel's directories
        self.pattern_matcher_dict = {}

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

        observer = LocalObserver(config.name, config.is_active, 0.25)
        event_handler = FileTransferEventHandler(self, config.name, config)
        observer.schedule(event_handler, pickup_from_list, recursive=False)

        self.observers.append(observer)

        logger.warn('FFF %s %s', observer.name, config)

# ################################################################################################################################

    def delete(self, config):

        # Observer object to delete ..
        to_delete = None

        # .. stop its main loop ..
        for observer in self.observers: # type: LocalObserver
            if observer.name == config.name:
                observer.stop()
                to_delete = observer
                break
        else:
            raise ValueError('Could not find observer matching name `%s` (%s)', config.name, config.type_)

        # .. and delete the object now.
        if to_delete:
            self.observers.remove(observer)

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
                            observer.event_handler.on_created(InotifyEvent(src_path))

                    except Exception:
                        logger.warn('Exception in inotify handler `%s`', format_exc())
            except Exception:
                logger.warn('Exception in inotify.read() `%s`', format_exc())
            finally:
                sleep(0.25)

# ################################################################################################################################

    def _run_linux(self, name=None):

        # Under Linux, for each observer, map each of its watched directories
        # to the actual observer object so that when an event is emitted
        # we will know, based on the event's full path, which observers to notify.
        self.inotify_path_to_observer_list = {}

        for observer in self.observers: # type: LocalObserver
            for path in observer.path_list: # type: str
                observer_list = self.inotify_path_to_observer_list.setdefault(path, []) # type: list
                observer_list.append(observer)

        for observer in self.observers: # type: BaseObserver
            try:

                if name and name != observer.name:
                    continue

                observer.start(self.inotify, self.inotify_flags, self.inotify_lock, self.inotify_wd_to_path)

            except Exception:
                logger.warn('File observer `%s` could not be started, path:`%s`, e:`%s`',
                    observer.name, observer.path_list, format_exc())

        spawn_greenlet(self._run_linux_inotify_loop)

# ################################################################################################################################

    def _run_non_linux(self, name):
        raise NotImplementedError()

# ################################################################################################################################

    def _run(self, name=None):

        if is_linux:
            self._run_linux(name)
        else:
            self._run_non_linux(name)

# ################################################################################################################################

    def run(self):
        self._run()

# ################################################################################################################################

    def start_observer(self, name):
        self._run(name)

# ################################################################################################################################
