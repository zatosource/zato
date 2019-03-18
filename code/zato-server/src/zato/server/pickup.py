# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import os
from datetime import datetime
from importlib import import_module
from shutil import copy as shutil_copy
from traceback import format_exc

# Bunch
from bunch import Bunch

# Watchdog
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

# Zato
from zato.common.util import hot_deploy, spawn_greenlet

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

_singleton = object()

# ################################################################################################################################

class PickupEventHandler(FileSystemEventHandler):

    def __init__(self, manager, stanza, config):
        # type: (PickupManager, str, Bunch) -> None

        self.manager = manager
        self.stanza = stanza
        self.config = config

    def on_created(self, wd_event):
        # type: (FileSystemEvent) -> None

        try:

            file_name = os.path.basename(wd_event.src_path) # type: str

            if not self.manager.should_pick_up(file_name, self.config.patterns):
                return

            pe = PickupEvent()
            pe.full_path = wd_event.src_path
            pe.base_dir = os.path.dirname(wd_event.src_path)
            pe.file_name = file_name
            pe.stanza = self.stanza

            if self.config.is_service_hot_deploy:
                spawn_greenlet(hot_deploy, self.manager.server, pe.file_name, pe.full_path, self.config.delete_after_pickup)
                return

            if self.config.read_on_pickup:

                f = open(pe.full_path, 'rb')
                pe.raw_data = f.read()
                pe.has_raw_data = True
                f.close()

                if self.config.parse_on_pickup:

                    try:
                        pe.data = self.manager.get_parser(self.config.parse_with)(pe.raw_data)
                        pe.has_data = True
                    except Exception as e:
                        pe.parse_error = e

            spawn_greenlet(self.manager.invoke_callbacks, pe, self.config.services, self.config.topics)
            self.manager.post_handle(pe.full_path, self.config)

        except Exception:
            logger.warn('Exception in pickup event handler `%s`', format_exc())

    on_modified = on_created

# ################################################################################################################################

class PickupEvent(object):
    """ Encapsulates information about a file picked up from file system.
    """
    __slots__ = ('base_dir', 'file_name', 'full_path', 'stanza', 'ts_utc', 'raw_data', 'data', 'has_raw_data', 'has_data',
        'parse_error')

    def __init__(self):
        self.base_dir = None      # type: str
        self.file_name = None     # type: str
        self.full_path = None     # type: str
        self.stanza = None        # type: str
        self.ts_utc = None        # type: str
        self.raw_data = ''        # type: str
        self.data = _singleton    # type: str
        self.has_raw_data = False # type: bool
        self.has_data = False     # type: bool
        self.parse_error = None   # type: str

# ################################################################################################################################

class PickupManager(object):
    """ Manages inotify listeners and callbacks.
    """
    def __init__(self, server, config):

        self.server = server
        self.config = config
        self.keep_running = True

        self.observers = []

        # Unlike the main config dictionary, this one is keyed by incoming directories
        self.callback_config = Bunch()

        for stanza, section_config in self.config.items():
            cb_config = self.callback_config.setdefault(section_config.pickup_from, Bunch())
            cb_config.update(section_config)
            cb_config.stanza = stanza

            observer = PollingObserver(0.25)
            event_handler = PickupEventHandler(self, stanza, section_config)
            observer.schedule(event_handler, section_config.pickup_from, recursive=False)

            self.observers.append(observer)

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

    def should_pick_up(self, name, patterns):
        for pattern in patterns:
            if pattern.match(name):
                return True

# ################################################################################################################################

    def invoke_callbacks(self, pickup_event, services, topics):

        request = {
            'base_dir': pickup_event.base_dir,
            'file_name': pickup_event.file_name,
            'full_path': pickup_event.full_path,
            'stanza': pickup_event.stanza,
            'ts_utc': datetime.utcnow().isoformat(),
            'raw_data': pickup_event.raw_data,
            'data': pickup_event.data if pickup_event.data is not _singleton else None,
            'has_raw_data': pickup_event.has_raw_data,
            'has_data': pickup_event.has_data,
            'parse_error': pickup_event.parse_error,
        }

        try:
            for service in services:
                spawn_greenlet(self.server.invoke, service, request)

            for topic in topics:
                spawn_greenlet(self.server.publish_pickup, topic, request)

        except Exception:
            logger.warn(format_exc())

# ################################################################################################################################

    def post_handle(self, full_path, config):
        """ Runs after callback services have been already invoked, performs clean up if configured to.
        """
        if config.move_processed_to:
            shutil_copy(full_path, config.move_processed_to)

        if config.delete_after_pickup:
            os.remove(full_path)

# ################################################################################################################################

    def run(self):

        for observer in self.observers:
            observer.start()

# ################################################################################################################################
