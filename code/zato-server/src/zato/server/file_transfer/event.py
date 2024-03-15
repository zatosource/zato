# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from io import StringIO
from logging import getLogger
from traceback import format_exc

# Watchdog
from watchdog.events import DirCreatedEvent

# Zato
from zato.common.util.api import hot_deploy, spawn_greenlet

if 0:
    from bunch import Bunch

    from zato.server.file_transfer.api import FileTransferAPI
    from zato.server.file_transfer.observer.base import BaseObserver, PathCreatedEvent
    from zato.server.file_transfer.snapshot import BaseRemoteSnapshotMaker

    Bunch = Bunch
    FileTransferAPI = FileTransferAPI
    BaseObserver = BaseObserver
    BaseRemoteSnapshotMaker = BaseRemoteSnapshotMaker
    PathCreatedEvent = PathCreatedEvent

# ################################################################################################################################
# ################################################################################################################################_s

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################_s

singleton = object()

# ################################################################################################################################
# ################################################################################################################################

class FileTransferEvent:
    """ Encapsulates information about a file picked up from file system.
    """
    # When this event tooks place
    timestamp: datetime

    # True if it was a creation event, False if it was a modification event
    is_create: bool

    # This is the directory where the file is located
    base_dir = 'not-set'      # type: str

    # This is the directory of the file relative to the server's base directory.
    # It will stay None if self.full_path is an absolute directory.
    relative_dir = 'not-set'  # type: str

    # This is the file name only
    file_name = 'not-set'     # type: str

    # Full path to the file
    full_path = 'not-set'     # type: str

    channel_name = 'not-set'  # type: str
    ts_utc = 'not-set'        # type: str
    raw_data = 'not-set'      # type: str
    data = singleton          # type: str
    has_raw_data = 'not-set'  # type: bool
    has_data = 'not-set'      # type: bool
    parse_error = 'not-set'   # type: str

# ################################################################################################################################
# ################################################################################################################################

class FileTransferEventHandler:

    def __init__(self, manager:'FileTransferAPI', channel_name:'str', config:'Bunch') -> 'None':

        self.manager = manager
        self.channel_name = channel_name
        self.config = config

        # Some parsers will require for input data to be a StringIO objects instead of plain str.
        self.config.parser_needs_string_io = self._check_if_parser_needs_string_io(self.config)

# ################################################################################################################################

    def _check_if_parser_needs_string_io(self, config:'Bunch'):
        return config.should_parse_on_pickup and \
               config.parse_with and \
               config.parse_with == 'py:csv.reader'

# ################################################################################################################################

    def _on_path_event_observed(
        self,
        transfer_event,      # type: PathCreatedEvent
        observer,            # type: BaseObserver
        snapshot_maker=None, # type: BaseRemoteSnapshotMaker | None
        *,
        is_create # type: bool
    ) -> 'None':

        try:

            # Ignore the event if it points to the directory itself,
            # as inotify will send CLOSE_WRITE when it is not a creation of a file
            # but a fact that a directory has been deleted that the event is about.
            # Note that we issue a log entry only if the path is not one of what
            # we observe, i.e. when one of our own directories is deleted, we do not log it here.

            # The path must have existed since we are being called
            # and we need to check why it does not exist anymore ..
            if not observer.path_exists(transfer_event.src_path, snapshot_maker):

                # .. if this type of an observer does not wait for paths, we can return immediately ..
                if not observer.should_wait_for_deleted_paths:
                    return

                # .. if it is one of the paths that we observe, it means that it has been just deleted,
                # so we need to run a background inspector which will wait until it is created once again ..
                if transfer_event.src_path in self.config.pickup_from_list:
                    self.manager.wait_for_deleted_path(transfer_event.src_path)

                else:
                    logger.info('Ignoring local file event; path not in pickup_from_list `%s` (%r -> %r)',
                        transfer_event.src_path, self.config.name, self.config.pickup_from_list)

                # .. in either case, there is nothing else we can do here.
                return

            # Get file name to check if we should handle it ..
            file_name = os.path.basename(transfer_event.src_path) # type: str

            # .. return if we should not.
            if not self.manager.should_handle(self.config.name, file_name):
                return

            event = FileTransferEvent()
            event.timestamp = datetime.utcnow()
            event.is_create = is_create
            event.full_path = transfer_event.src_path
            event.file_name = file_name
            event.base_dir = os.path.dirname(event.full_path)
            event.relative_dir = self.manager.build_relative_dir(event.full_path)
            event.channel_name = self.channel_name

            if self.config.is_hot_deploy:
                if transfer_event.is_directory:
                    if isinstance(transfer_event, DirCreatedEvent):
                        logger.info('About to add a new hot-deployment directory -> %s', event.full_path)
                        self.manager.add_pickup_dir(event.full_path, f'File transfer -> {self.channel_name}')
                else:
                    _ = spawn_greenlet(hot_deploy, self.manager.server, event.file_name, event.full_path,
                        self.config.should_delete_after_pickup, should_deploy_in_place=self.config.should_deploy_in_place)
                return

            if self.config.should_read_on_pickup:

                if snapshot_maker:
                    raw_data = snapshot_maker.get_file_data(event.full_path)
                else:
                    f = open(event.full_path, 'rb')
                    raw_data = f.read()
                    f.close

                event.raw_data = raw_data if isinstance(raw_data, str) else raw_data.decode(self.config.data_encoding) # type: str
                event.has_raw_data = True

                if self.config.should_parse_on_pickup:

                    try:
                        data_to_parse = StringIO(event.raw_data) if self.config.parser_needs_string_io else event.raw_data
                        parser = self.manager.get_parser(self.config.parse_with)
                        event.data = parser(data_to_parse)
                        event.has_data = True
                    except Exception:
                        exception = format_exc()
                        event.parse_error = exception
                        logger.warning('File transfer parsing error (%s) e:`%s`', self.config.name, exception)

            # Invokes all callbacks for the event
            spawn_greenlet(self.manager.invoke_callbacks, event, self.config.service_list, self.config.topic_list,
                self.config.outconn_rest_list)

            # Performs cleanup actions
            self.manager.post_handle(event, self.config, observer, snapshot_maker)

        except Exception:
            logger.warning('Exception in pickup event handler `%s` (%s) `%s`',
                self.config.name, transfer_event.src_path, format_exc())

# ################################################################################################################################

    def on_created(
        self,
        transfer_event,     # type: PathCreatedEvent
        observer,           # type: BaseObserver
        snapshot_maker=None # type: BaseRemoteSnapshotMaker | None
    ) -> 'None':

        # Call the parent function indicating that it was a creation
        self._on_path_event_observed(
            transfer_event,
            observer,
            snapshot_maker,
            is_create=True
        )

# ################################################################################################################################

    def on_modified(
        self,
        transfer_event,     # type: PathCreatedEvent
        observer,           # type: BaseObserver
        snapshot_maker=None # type: BaseRemoteSnapshotMaker | None
    ) -> 'None':

        # Call the parent function indicating that it was a modification
        self._on_path_event_observed(
            transfer_event,
            observer,
            snapshot_maker,
            is_create=False
        )

# ################################################################################################################################
# ################################################################################################################################
