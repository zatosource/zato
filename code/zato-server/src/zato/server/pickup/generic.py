# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from time import sleep

# watchdog
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

# Zato
from zato.server.pickup import BasePickup, BasePickupEventProcessor

logger = logging.getLogger(__name__)

__all__ = ['Pickup', 'PickupEventProcessor']

class PickupEventProcessor(FileSystemEventHandler, BasePickupEventProcessor):
    def process(self, src_path):
        self.hot_deploy(src_path)
        
    def on_created(self, event):
        logger.debug('EVENT_TYPE_CREATED event.src_path:[{}], event:[{}]'.format(event.src_path, event))
        self.process(event.src_path)

class Pickup(BasePickup):
    def __init__(self, pickup_dir=None, pickup_event_processor=None):
        self.pickup_dir = pickup_dir
        self.pickup_event_processor = pickup_event_processor or PickupEventProcessor()
        self.keep_running = True

    def watch(self):
        observer = PollingObserver()
        observer.schedule(self.pickup_event_processor, path=self.pickup_dir)
        observer.start()
        
        try:
            while self.keep_running:
                sleep(3)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
