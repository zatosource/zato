# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from contextlib import closing
from random import choice
from traceback import format_exc

# gevent
from gevent import sleep

# Zato
from zato.common.odb.query.pubsub.cleanup import delete_expired, delete_delivered
from zato.common.time_util import utcnow_as_ms
from zato.server.service.internal import AdminService

# ################################################################################################################################

logger = logging.getLogger('zato_pubsub')

# ################################################################################################################################

# Jitter to add to sleep_time so as no to have all worker processes issue the same queries at the same time,
# in the range of 0.10 to 0.29, step 0.1.
sleep_jitter = [elem / 10.0 for elem in range(1, 4, 1)]

# ################################################################################################################################

class CleanupService(AdminService):
    """ Base class for services performing periodical cleanup of messages that are,
    for instance, expired or already delivered.
    """
    _cleanup_sleep_time = None

    def handle(self):
        sleep_time = int(self.request.raw_request)

        while True:
            try:
                # Sleep for a moment but add jitter to make it more random
                jitter = sleep_time * choice(sleep_jitter)
                sleep(sleep_time + jitter)

                with closing(self.odb.session()) as session:

                    # Clean up what is needed
                    number, kind = self._cleanup(session)

                    # Log what was done
                    suffix = 's' if(number==0 or number > 1) else ''
                    logger.info('GD. Deleted %s %s pub/sub message%s' % (number, kind, suffix))

                    # Actually commit on SQL level
                    session.commit()

            except Exception, e:
                logger.warn('Error in cleanup: `%s`', format_exc(e))
                sleep(sleep_time)

# ################################################################################################################################

    def _cleanup(self):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

class DeleteExpired(CleanupService):
    """ Deletes expired messages from all topics.
    """
    def _cleanup(self, session):
        number = delete_expired(session, self.server.cluster_id, utcnow_as_ms())
        return number, 'expired'

# ################################################################################################################################

class DeleteDelivered(CleanupService):
    """ Deletes delivered messages from all message queues.
    """
    def _cleanup(self, session):
        number = delete_delivered(session, self.server.cluster_id)
        return number, 'delivered'

# ################################################################################################################################
