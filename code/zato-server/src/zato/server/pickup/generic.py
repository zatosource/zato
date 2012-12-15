# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os
from time import sleep

# Spring Python
from springpython.context import ApplicationContextAware

# watchdog
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

# Zato
from zato.common.util import hot_deploy
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
