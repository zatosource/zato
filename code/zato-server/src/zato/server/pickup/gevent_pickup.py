# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import errno, logging, os, traceback

# gevent
from gevent import sleep

# gevent_inotifyx
import gevent_inotifyx as inotifyx

# Zato
from zato.server.pickup import BasePickupEventProcessor

__all__ = ['Pickup', 'PickupEventProcessor']

logger = logging.getLogger(__name__)

class PickupEventProcessor(BasePickupEventProcessor):
    def process(self, event):
        logger.debug('IN_MODIFY event.name:[{}], event:[{}]'.format(event.name, event))
        try:
            self.hot_deploy(event.name)
        except(IOError, OSError), e:
            if e.errno == errno.ENOENT:
                # It's OK, probably there is more than gunicorn worker and the other has already deleted
                # the deployment package before we had a chance to do the same.
                logger.debug('Caught ENOENT `%s`, e:`%s`', event, traceback.format_exc(e))
            else:
                raise

class Pickup(object):
    def __init__(self, pickup_dir=None, pickup_event_processor=None):
        self.pickup_dir = pickup_dir
        self.pickup_event_processor = pickup_event_processor or PickupEventProcessor()
        self.keep_running = True

    def watch(self):
        fd = inotifyx.init()
        inotifyx.add_watch(fd, self.pickup_dir, inotifyx.IN_CLOSE_WRITE | inotifyx.IN_MOVE)

        while self.keep_running:
            try:
                events = inotifyx.get_events(fd, 1.0)
                for event in events:
                    self.pickup_event_processor.process(event)

                sleep(0.1)
            except KeyboardInterrupt:
                self.keep_running = False

        os.close(fd)

    def stop(self):
        logger.debug('Stopping the notifier')
        self.keep_running = False
        logger.info('Successfully stopped the notifier')
