# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import errno, logging, os
from traceback import format_exc

# gevent
from gevent import sleep

# gevent_inotifyx
import gevent_inotifyx as inotifyx

# Zato
from zato.server.pickup import BasePickupEventProcessor

__all__ = ['Pickup', 'PickupEventProcessor']

logger = logging.getLogger(__name__)

class PickupEventProcessor(BasePickupEventProcessor):
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

class Pickup(object):
    def __init__(self, pickup_event_processor=None):
        self._pickup_dirs = []
        self.pickup_event_processor = pickup_event_processor or PickupEventProcessor()
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
        logger.debug('Stopping the notifier')
        self.keep_running = False
        logger.info('Successfully stopped the notifier')
