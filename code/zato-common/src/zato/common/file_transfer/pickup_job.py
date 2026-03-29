# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from threading import Event, Thread
from typing import Dict, List

# Zato
from zato.common.file_transfer.const import PostProcessingAction
from zato.common.file_transfer.engine import FileTransferEngine
from zato.common.file_transfer.model import PickupChannel
from zato.common.file_transfer.pickup import get_pickup_source, FileInfo

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.file_transfer.redis_store import FileTransferRedisStore
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class FileTransferPickupJob:

    def __init__(
        self,
        store:'FileTransferRedisStore',
        engine:'FileTransferEngine',
        connection_pool:'any_'=None,
        default_poll_interval:'float'=60.0,
    ) -> 'None':
        self.store = store
        self.engine = engine
        self.connection_pool = connection_pool
        self.default_poll_interval = default_poll_interval
        self._stop_event = Event()
        self._threads: 'Dict[str, Thread]' = {}
        self._channel_stop_events: 'Dict[str, Event]' = {}

# ################################################################################################################################

    def start(self) -> 'None':
        channels = self.store.list_enabled_pickup_channels()

        for channel in channels:
            self._start_channel(channel)

        logger.info('Pickup job started with %d channels', len(channels))

# ################################################################################################################################

    def stop(self) -> 'None':
        self._stop_event.set()

        for channel_id, stop_event in self._channel_stop_events.items():
            stop_event.set()

        for channel_id, thread in self._threads.items():
            thread.join(timeout=5.0)

        self._threads.clear()
        self._channel_stop_events.clear()

        logger.info('Pickup job stopped')

# ################################################################################################################################

    def _start_channel(self, channel:'PickupChannel') -> 'None':

        if channel.id in self._threads:
            return

        stop_event = Event()
        self._channel_stop_events[channel.id] = stop_event

        thread = Thread(
            target=self._poll_channel,
            args=(channel, stop_event),
            daemon=True,
            name=f'pickup-{channel.id}',
        )
        self._threads[channel.id] = thread
        thread.start()

        logger.info('Started pickup channel %s (%s)', channel.name, channel.id)

# ################################################################################################################################

    def _stop_channel(self, channel_id:'str') -> 'None':

        if channel_id in self._channel_stop_events:
            self._channel_stop_events[channel_id].set()

        if channel_id in self._threads:
            self._threads[channel_id].join(timeout=5.0)
            del self._threads[channel_id]

        if channel_id in self._channel_stop_events:
            del self._channel_stop_events[channel_id]

        logger.info('Stopped pickup channel %s', channel_id)

# ################################################################################################################################

    def _poll_channel(self, channel:'PickupChannel', stop_event:'Event') -> 'None':

        poll_interval = channel.poll_interval_seconds or self.default_poll_interval

        while not stop_event.is_set() and not self._stop_event.is_set():
            try:
                self._process_channel(channel)
            except Exception as e:
                logger.exception('Error processing pickup channel %s: %s', channel.id, e)

            stop_event.wait(poll_interval)

# ################################################################################################################################

    def _process_channel(self, channel:'PickupChannel') -> 'int':

        connection = None
        if self.connection_pool:
            connection = self.connection_pool.get(channel.connection_name)

        source_kwargs = {}
        if 's3' in channel.source_type.value.lower():
            parts = channel.remote_path.split('/', 1)
            source_kwargs['bucket'] = parts[0] if parts else ''
        elif 'azure' in channel.source_type.value.lower():
            parts = channel.remote_path.split('/', 1)
            source_kwargs['container'] = parts[0] if parts else ''
        elif 'imap' in channel.source_type.value.lower():
            source_kwargs['folder'] = channel.remote_path or 'INBOX'

        source = get_pickup_source(channel.source_type, connection, **source_kwargs)

        processed_count = 0

        try:
            source.connect()

            files = source.list_files(channel.remote_path, channel.file_pattern)

            for file_info in files:
                try:
                    content = source.download(file_info)

                    source_detail = f'{channel.connection_name}:{file_info.path}'

                    txn = self.engine.process_file(
                        filename=file_info.name,
                        content=content,
                        source_protocol=channel.source_type.value,
                        source_detail=source_detail,
                    )

                    source.mark_processed(
                        file_info,
                        channel.post_processing_action,
                        channel.archive_path,
                    )

                    processed_count += 1
                    logger.info('Processed file %s -> %s', file_info.name, txn.id)

                except Exception as e:
                    logger.warning('Error processing file %s: %s', file_info.name, e)

        finally:
            source.disconnect()

        return processed_count

# ################################################################################################################################

    def refresh_channels(self) -> 'None':

        current_channels = {c.id: c for c in self.store.list_enabled_pickup_channels()}

        for channel_id in list(self._threads.keys()):
            if channel_id not in current_channels:
                self._stop_channel(channel_id)

        for channel_id, channel in current_channels.items():
            if channel_id not in self._threads:
                self._start_channel(channel)

# ################################################################################################################################

    def poll_channel_once(self, channel_id:'str') -> 'int':

        channel = self.store.get_pickup_channel(channel_id)
        if not channel:
            return 0

        return self._process_channel(channel)

# ################################################################################################################################
# ################################################################################################################################
