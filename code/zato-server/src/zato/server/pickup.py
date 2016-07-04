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
from traceback import format_exc

# gevent
from gevent import sleep

# gevent_inotifyx
import gevent_inotifyx as infx

# Bunch
from bunch import Bunch

# Zato
from zato.common.util import hot_deploy, is_archive_file, is_python_file

# ################################################################################################################################

logger = logging.getLogger(__name__)

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
    def __init__(self, config):
        self.config = config
        self.keep_running = True
        self.watchers = []
        self.infx_fd = infx.init()

        # Maps inotify's watch descriptors to paths
        self.wd_to_path = {}

        # Unlike the main config dictionary, this one is keyed by incoming directories
        self.callback_config = Bunch()

        for stanza, section_config in self.config.items():
            cb_config = self.callback_config.setdefault(section_config.pickup_from, Bunch())
            cb_config.update(section_config)
            cb_config.stanza = stanza

# ################################################################################################################################

    def parse_json(self, raw_data):
        print(111, raw_data)
        return 1,1

# ################################################################################################################################

    def parse_xml(self, raw_data):
        print(222, raw_data)
        return 2,2

# ################################################################################################################################

    def parse_csv(self, raw_data):
        print(333, raw_data)
        return 3,3

# ################################################################################################################################

    def run(self):

        # We will possibly parse files ending in these extensions
        endswith_parse = {
            '.json': self.parse_json,
            '.xml': self.parse_xml,
            '.csv': self.parse_csv,
        }

        for path in self.callback_config:
            self.wd_to_path[infx.add_watch(self.infx_fd, path, infx.IN_CLOSE_WRITE | infx.IN_MOVE)] = path

        print(self.wd_to_path)

        try:
            while self.keep_running:
                try:
                    events = infx.get_events(self.infx_fd, 1.0)
                    now = datetime.utcnow()
                    sleep(0.1)

                    for event in events:

                        try:

                            has_raw_data, has_data = False, False
                            raw_data, data = '', ''
                            parse_error = None

                            base_dir = self.wd_to_path[event.wd]
                            full_path = os.path.join(base_dir, event.name)
                            full_path_lower = full_path.lower()
                            config = self.callback_config[base_dir]

                            if config.read_on_pickup:

                                f = open(full_path, 'rb')
                                raw_data = f.read()
                                has_raw_data = True
                                f.close()

                                if config.parse_on_pickup:
                                    for ext, parser in endswith_parse.items():
                                        if full_path_lower.endswith(ext):
                                            data, parse_error = parser(raw_data)
                                            has_data = True

                            request = {
                                'base_dir': base_dir,
                                'full_path': full_path,
                                'stanza': config.stanza,
                                'ts_utc': now.isoformat(),
                                'raw_data': raw_data,
                                'data': data,
                                'has_raw_data': has_raw_data,
                                'has_data': has_data,
                                'parse_error': parse_error,
                            }

                            print(22, event.name, request)

                        except Exception, e:
                            logger.warn(format_exc(e))

                except KeyboardInterrupt:
                    self.keep_running = False

        except Exception, e:
            logger.warn(format_exc(e))

'''
class Pickup(object):
    def __init__(self, pickup_event_processor=None):
        self._pickup_dirs = []
        self.pickup_event_processor = pickup_event_processor
        self.keep_running = True

        # A dict of inotify watch descriptors to directory names.
        # Needed because inotify returns only the name of a file in events.
        self.wd_to_name = {}

    @property
    def pickup_dir(self):
        return self._pickup_dirs

    @pickup_dir.setter
    def pickup_dir(self, value):
        self._pickup_dirs = [value] if not isinstance(value, list) else value

    def watch(self):
        fd = inotifyx.init()

        for name in self.pickup_dir:
            try:
                self.wd_to_name[inotifyx.add_watch(fd, name, inotifyx.IN_CLOSE_WRITE | inotifyx.IN_MOVE)] = name
            except IOError, e:
                logger.warn('Caught IOError `%s`, name:`%s`', format_exc(e), name)

        while self.keep_running:
            try:
                events = inotifyx.get_events(fd, 1.0)
                for event in events:
                    self.pickup_event_processor.process(os.path.join(self.wd_to_name[event.wd], event.name), event)

                sleep(0.1)
            except KeyboardInterrupt:
                self.keep_running = False

        os.close(fd)

    def stop(self):
        logger.debug('Stopping pickup manager')
        self.keep_running = False
        logger.info('Pickup manager stopped')

# ################################################################################################################################
'''