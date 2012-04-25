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

# pip
from pip.download import is_archive_file

# inotifyx
import inotifyx

# Spring Python
from springpython.context import ApplicationContextAware

# Zato
from zato.common.util import is_python_file, TRACE1

__all__ = ['Pickup', 'PickupEventProcessor']

logger = logging.getLogger(__name__)

class PickupEventProcessor(ApplicationContextAware):
    def __init__(self, pickup_dir=None, server=None, *args, **kwargs):
        self.pickup_dir = pickup_dir
        self.server = server
        super(PickupEventProcessor, self).__init__(*args, **kwargs)
        
    def _should_process(self, event_name):
        """ Returns True if the file name's is either a Python source code file
        we can handle or an archive that can be uncompressed.
        """
        return is_python_file(event_name) or is_archive_file(event_name)

    def process(self, event):
        event_info = 'event:[{}], event.name:[{}]'.format(event, event.name)
        logger.debug('IN_MODIFY {}'.format(event_info))
        
        if self._should_process(event.name):
            path = os.path.abspath(os.path.join(self.pickup_dir, event.name))
            self.server.hot_deploy(path)
            os.remove(path)
        else:
            logger.info('Ignoring {}'.format(event_info))

class Pickup(object):
    def __init__(self, pickup_dir=None, pickup_event_processor=None):
        self.pickup_dir = pickup_dir
        self.pickup_event_processor = pickup_event_processor
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
        logger.debug('Successfully stopped the notifier')
