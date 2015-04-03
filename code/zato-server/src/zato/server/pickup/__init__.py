# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os

# Spring Python
from springpython.context import ApplicationContextAware

# Zato
from zato.common.util import hot_deploy, is_archive_file, is_python_file

logger = logging.getLogger(__name__)

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

    def hot_deploy(self, full_path, file_name):
        return hot_deploy(
            self.server.parallel_server, file_name, full_path,
            self.server.parallel_server.hot_deploy_config.delete_after_pick_up)
    
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
