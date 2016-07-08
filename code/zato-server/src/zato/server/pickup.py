# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import errno
import logging
import os
from datetime import datetime
from importlib import import_module
from shutil import copy as shutil_copy
from traceback import format_exc

# Bunch
from bunch import Bunch

# gevent
from gevent import sleep, spawn

# gevent_inotifyx
import gevent_inotifyx as infx

# Zato
from zato.common.util import hot_deploy, is_archive_file, is_python_file, spawn_greenlet

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

class BasePickupEventProcessor(object):
    def __init__(self, pickup_dir=None, server=None, *args, **kwargs):
        self.pickup_dir = pickup_dir
        self.server = server
        super(BasePickupEventProcessor, self).__init__(*args, **kwargs)

    def _should_process(self, event_name):
        """ By default we always let an event in.
        """
        return True

# ################################################################################################################################

class ServiceHotDeploy(BasePickupEventProcessor):
    """ Hot-deploys Zato services.
    """
    def _should_process(self, event_name):
        """ Returns True if the file name's is either a Python source code file
        we can handle or an archive that can be uncompressed.
        """
        return is_python_file(event_name) or is_archive_file(event_name)

    def hot_deploy(self, full_path, file_name):
        return hot_deploy(
            self.server.parallel_server, file_name, full_path,
            self.server.parallel_server.hot_deploy_config.delete_after_pick_up)

    def process(self, full_path, event):
        logger.debug('IN_MODIFY full_path:`%s`', full_path)
        try:
            self.hot_deploy(full_path, event.name)
        except(IOError, OSError), e:
            if e.errno == errno.ENOENT:
                # It's OK, probably there is more than gunicorn worker and the other has already deleted
                # the deployment package before we had a chance to do the same.
                logger.debug('Caught ENOENT `%s`, e:`%s`', full_path, format_exc(e))
            else:
                raise

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

    def invoke_callbacks(self, pickup_event, recipients):


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
            for recipient in recipients:
                spawn_greenlet(self.server.invoke, recipient, request)
        except Exception, e:
            logger.warn(format_exc(e))

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

                            if config.read_on_pickup:

                                f = open(pe.full_path, 'rb')
                                pe.raw_data = f.read()
                                pe.has_raw_data = True
                                f.close()

                                if config.parse_on_pickup:

                                    try:
                                        pe.data = self.get_parser(config.parse_with)(pe.raw_data)
                                        pe.has_data = True
                                    except Exception, e:
                                        pe.parse_error = e

                                else:
                                    pe.data = pe.raw_data

                            spawn_greenlet(self.invoke_callbacks, pe, config.recipients)
                            self.post_handle(pe.full_path, config)

                        except Exception, e:
                            logger.warn(format_exc(e))

                except KeyboardInterrupt:
                    self.keep_running = False

        except Exception, e:
            logger.warn(format_exc(e))
