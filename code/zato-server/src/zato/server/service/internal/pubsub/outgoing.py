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
from zato.common.pubsub.outgoing import deliver_envelope
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Deliver(Service):
    """ Delivers one published message to the outgoing connection it was addressed to. This is the subscriber
    behind the queue of every outgoing connection that anything is published to.
    """

    name = PubSub.Outgoing.Delivery_Service

    def handle(self) -> 'None':

        # The invocation machinery hands the envelope over either as a string or as a parsed dict ..
        envelope = self.request.raw_request
        if isinstance(envelope, str):
            envelope = loads(envelope)

        # .. and delivery raises on failure, which is what keeps the message queued for another attempt.
        deliver_envelope(self.server, self.cid, envelope)

# ################################################################################################################################
# ################################################################################################################################
