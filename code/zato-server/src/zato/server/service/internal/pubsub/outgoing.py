# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
from logging import getLogger

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.delivery import DeliveryExhausted, wait_between_rounds
from zato.common.pubsub.dlq import move_to_dlq
from zato.common.pubsub.outgoing import deliver_envelope
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Deliver(Service):
    """ The push subscriber behind the queue of every outgoing connection.
    """

    name = PubSub.Outgoing.Delivery_Service

    def handle(self) -> 'None':

        envelope = self.request.raw_request
        if isinstance(envelope, str):
            envelope = loads(envelope)

        try:
            deliver_envelope(self.server, self.cid, envelope)

        # A message whose attempts ran out moves to the DLQ ..
        except DeliveryExhausted as e:

            # .. and one that does not move waits before it is offered again.
            if not move_to_dlq(self.server, self.cid, envelope, e):
                wait_between_rounds()
                raise

        except Exception:
            wait_between_rounds()
            raise

# ################################################################################################################################
# ################################################################################################################################
