# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# gevent
from gevent import sleep, spawn

# Zato
from zato.server.service.internal import AdminService

class MoveToTargetQueues(AdminService):
    """ Invoked when a server is starting - spawns a greenlet periodically
    in order to move published messages to recipient queues.
    """
    def _move_to_target_queues(self):
        self.pubsub.impl.move_to_target_queues()
        self.logger.debug('Messages moved to target queues')

    def handle(self):
        interval = float(self.server.fs_server_config.pubsub.move_to_target_queues_interval)
        self.logger.info('Moving messages to target queues, interval %rs', interval)

        while True:
            spawn(self._move_to_target_queues)
            sleep(interval)
