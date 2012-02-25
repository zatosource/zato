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

"""Generic pick-up manager.

Checks contents of the pickup dir every few seconds and processes new files.
Doesn't detect modifications.
"""
# stdlib
import logging
import os
import time
import threading

# Spring Python
from springpython.context import ApplicationContextAware

# Zato
from zato.common.hotdeploy import validate_egg


__all__ = ["Pickup", "PickupEventProcessor"]

_INTERVAL = 1.0


class Watcher(threading.Thread):
    def __init__(self, pickup_dir, processor):
        super(Watcher, self).__init__()
        self._pickup_dir = pickup_dir
        self._processor = processor
        self._is_running = False
        self._seen = set()
        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def run(self):
        self._is_running = True
        while self._is_running:
            self.logger.debug("Looking for new modules to load (in: %s).", self._pickup_dir)
            for entry in os.listdir(self._pickup_dir):
                # We have already seen this entry. Skip it.
                if entry in self._seen:
                    continue
                self.logger.debug("New module found: '%s'", entry)
                self._processor.process(entry)
                self._seen.add(entry)
            time.sleep(_INTERVAL)

    def stop(self):
        self._is_running = False
        self.join()


class PickupEventProcessor(ApplicationContextAware):
    def __init__(self):
        self.importer = None
        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def process(self, path):
        if not path.endswith(".egg"):
            self.logger.info("Ignoring entry %s (not an .egg file)", path)
            return

        self.logger.info("Processing '%s'", path)
        with open(path, "rb") as stream:
            if validate_egg(stream):
                singleton_server = self.app_context.get_object("singleton_server")
                self.importer.import_services(path, singleton_server)
            else:
                self.logger.info("Ingoring entry '%s' (stinky egg)", path)


class Pickup(object):
    def __init__(self, pickup_dir=None, pickup_event_processor=None):
        self.pickup_dir = pickup_dir
        self.pickup_event_processor = pickup_event_processor
        self._watcher = None

        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def watch(self):
        self._watcher = Watcher(self.pickup_dir, self.pickup_event_processor)
        self._watcher.start()

    def stop(self):
        assert self._watcher is not None, 'Watcher was not started!'
        self.logger.debug("Stopping the notifier")
        self._watcher.stop()
        self.logger.debug("Successfully stopped the notifier")

