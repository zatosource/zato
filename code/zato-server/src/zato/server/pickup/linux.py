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

# inotifyx
import inotifyx

# Spring Python
from springpython.context import ApplicationContextAware

# Zato
from zato.common.util import TRACE1
from zato.common.hotdeploy import validate_egg

__all__ = ["Pickup", "PickupEventProcessor"]


class PickupEventProcessor(ApplicationContextAware):
    def __init__(self, importer=None, pickup_dir=None, *args, **kwargs):

        self.importer = importer
        self.pickup_dir = pickup_dir
        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

        super(PickupEventProcessor, self).__init__(*args, **kwargs)

    def process(self, event):
        self.logger.debug("IN_MODIFY event %r" % event)
        self.logger.log(TRACE1, "event.name %s" % event.name)

        if not event.name.endswith(".egg"):
            self.logger.info("Ignoring event %s (not an .egg file)" % event.name)
            return
        else:
            # TODO: Well, at some point we'll have to start accepting .py files
            # and turn them automatically into .eggs.
            pass

        stream = open(os.path.join(self.pickup_dir, event.name), "rb")
        try:
            if validate_egg(stream):
                singleton_server = self.app_context.get_object("singleton_server")
                self.importer.import_services(event.name, singleton_server)
            else:
                self.logger.info("Ignoring event %s" % event.name)
        finally:
            stream.close()

class Pickup(object):
    def __init__(self, pickup_dir=None, pickup_event_processor=None):
        self.pickup_dir = pickup_dir
        self.pickup_event_processor = pickup_event_processor

        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def watch(self):

        fd = inotifyx.init()
        wd = inotifyx.add_watch(fd, self.pickup_dir, inotifyx.constants["IN_CLOSE_WRITE"])

        keep_running = True

        while keep_running:
            try:
                events = inotifyx.get_events(fd, 1.0)
                for event in events:
                    self.pickup_event_processor.process(event)

                sleep(0.1)
            except KeyboardInterrupt:
                keep_running = False

        os.close(fd)

    def stop(self):
        self.logger.debug("Stopping the notifier")
        self.notifier.stop() # TODO: 'Pickup' object has no attribute 'notifier' ?
        self.logger.debug("Successfully stopped the notifier")
