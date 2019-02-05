# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

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

# gevent_inotifyx
import gevent_inotifyx as infx

# Zato
from zato.common.util import hot_deploy, spawn_greenlet

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

_singleton = object()

# ################################################################################################################################

class PickupEvent(object):
    """ Encapsulates information about a file picked up from file system.
    """
    __slots__ = ('base_dir', 'file_name', 'full_path', 'stanza', 'ts_utc', 'raw_data', 'data', 'has_raw_data', 'has_data',
        'parse_error')

    def __init__(self):
        self.base_dir = None
        self.file_name = None
        self.full_path = None
        self.stanza = None
        self.ts_utc = None
        self.raw_data = ''
        self.data = _singleton
        self.has_raw_data = False
        self.has_data = False
        self.parse_error = None

# ################################################################################################################################

class PickupManager(object):
    """ Manages inotify listeners and callbacks.
    """
    def __init__(self, server, config):
        self.server = server
        self.config = config
        self.keep_running = True
        self.watchers = []

        self.infx_fd = infx.init()
        self._parser_cache = {}

        # Maps inotify's watch descriptors to paths
        self.wd_to_path = {}

        # Unlike the main config dictionary, this one is keyed by incoming directories
        self.callback_config = Bunch()

        for stanza, section_config in self.config.items():
            cb_config = self.callback_config.setdefault(section_config.pickup_from, Bunch())
            cb_config.update(section_config)
            cb_config.stanza = stanza

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

        return

        try:

            for path in self.callback_config:
                if not os.path.exists(path):
                    raise Exception('Path does not exist `{}`'.format(path))

                self.wd_to_path[infx.add_watch(self.infx_fd, path, infx.IN_CLOSE_WRITE | infx.IN_MOVE)] = path

            while self.keep_running:
                try:
                    events = infx.get_events(self.infx_fd, 1.0)

                    for event in events:
                        pe = PickupEvent()

                        try:

                            pe.base_dir = self.wd_to_path[event.wd]

                            config = self.callback_config[pe.base_dir]

                            if not self.should_pick_up(event.name, config.patterns):
                                continue

                            pe.file_name = event.name
                            pe.stanza = config.stanza
                            pe.full_path = os.path.join(pe.base_dir, event.name)

                            # If we are deploying services, the path is different than for other resources
                            if config.is_service_hot_deploy:
                                spawn_greenlet(hot_deploy, self.server, pe.file_name, pe.full_path, config.delete_after_pickup)
                                continue

                            if config.read_on_pickup:

                                f = open(pe.full_path, 'rb')
                                pe.raw_data = f.read()
                                pe.has_raw_data = True
                                f.close()

                                if config.parse_on_pickup:

                                    try:
                                        pe.data = self.get_parser(config.parse_with)(pe.raw_data)
                                        pe.has_data = True
                                    except Exception as e:
                                        pe.parse_error = e

                                else:
                                    pe.data = pe.raw_data

                            spawn_greenlet(self.invoke_callbacks, pe, config.services, config.topics)
                            self.post_handle(pe.full_path, config)

                        except Exception:
                            logger.warn(format_exc())

                except KeyboardInterrupt:
                    self.keep_running = False

        except Exception:
            logger.warn(format_exc())
