# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os

# gevent
from gevent import sleep

# gevent_inotifyx
import gevent_inotifyx as inotifyx

# Spring Python
from springpython.context import ApplicationContextAware

# Zato
from zato.common.util import hot_deploy
from zato.server.pickup import BasePickup, BasePickupEventProcessor

__all__ = ['Pickup', 'PickupEventProcessor']

logger = logging.getLogger(__name__)

class PickupEventProcessor(BasePickupEventProcessor):
    def process(self, event):
        logger.debug('IN_MODIFY event.name:[{}], event:[{}]'.format(event.name, event))
        self.hot_deploy(event.name)

class Pickup(object):
    def __init__(self, pickup_dir=None, pickup_event_processor=None):
        self.pickup_dir = pickup_dir
        self.pickup_event_processor = pickup_event_processor or PickupEventProcessor()
        self.keep_running = True

    def watch(self):
        fd = inotifyx.init()
        wd = inotifyx.add_watch(fd, self.pickup_dir, inotifyx.constants['IN_CLOSE_WRITE'])
        
        while self.keep_running:
            try:
                events = inotifyx.get_events(fd, 1.0)
                for event in events:
                    self.pickup_event_processor.process(event)

                sleep(0.1)
            except KeyboardInterrupt:
                keep_running = False

        os.close(fd)

    def stop(self):
        logger.debug('Stopping the notifier')
        self.keep_running = False
        logger.info('Successfully stopped the notifier')
