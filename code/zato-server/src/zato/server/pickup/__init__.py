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
import os

# Spring Python
from springpython.context import ApplicationContextAware

# Zato
from zato.common.util import hot_deploy

class BasePickupEventProcessor(ApplicationContextAware):
    def __init__(self, pickup_dir=None, server=None, *args, **kwargs):
        self.pickup_dir = pickup_dir
        self.server = server
        super(BasePickupEventProcessor, self).__init__(*args, **kwargs)
        
    def _should_process(self, event_name):
        """ Returns True if the file name's is either a Python source code file
        we can handle or an archive that can be uncompressed.
        """
        return is_python_file(event_name) or is_archive_file(event_name)

    def hot_deploy(self, file_name):
        return hot_deploy(self.server.parallel_server, file_name, os.path.abspath(os.path.join(self.pickup_dir, file_name)))
    
class BasePickup(object):
    def stop(self):
        logger.debug('Stopping the notifier')
        self.keep_running = False
        logger.info('Successfully stopped the notifier')

def get_pickup(needs_gevent):
    if needs_gevent:
        from zato.server.pickup.gevent_pickup import Pickup
    else:
        from zato.server.pickup.generic import Pickup

    return Pickup()
