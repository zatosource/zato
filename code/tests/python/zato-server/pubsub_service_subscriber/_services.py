# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.common.test.received_store import clear, read_items, record
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# This file is hot-deployed into a test Zato server by conftest.py.
# Each receiver is a subscriber on its own, without a security definition, and stores
# every message pushed to it under its own name.

_receiver_names = (
    'test.pubsub.service-subscriber.receiver-1',
    'test.pubsub.service-subscriber.receiver-2',
    'test.pubsub.service-subscriber.receiver-3',
    'test.pubsub.service-subscriber.receiver-4',
)

# ################################################################################################################################
# ################################################################################################################################

def _store(service:'Service') -> 'None':
    """ Stores the data of one message pushed to the receiver that the service is.
    """
    record(service, service.name, str(service.request.raw_request))

# ################################################################################################################################
# ################################################################################################################################

class ServiceSubscriberReceiverOne(Service):
    name = 'test.pubsub.service-subscriber.receiver-1'

    def handle(self) -> 'None':
        _store(self)

# ################################################################################################################################

class ServiceSubscriberReceiverTwo(Service):
    name = 'test.pubsub.service-subscriber.receiver-2'

    def handle(self) -> 'None':
        _store(self)

# ################################################################################################################################

class ServiceSubscriberReceiverThree(Service):
    name = 'test.pubsub.service-subscriber.receiver-3'

    def handle(self) -> 'None':
        _store(self)

# ################################################################################################################################

class ServiceSubscriberReceiverFour(Service):
    name = 'test.pubsub.service-subscriber.receiver-4'

    def handle(self) -> 'None':
        _store(self)

# ################################################################################################################################
# ################################################################################################################################

class ServiceSubscriberGetReceived(Service):
    """ Returns what each receiver has stored so far, keyed by the receiver's name.
    """

    name = 'test.pubsub.service-subscriber.get-received'

    def handle(self) -> 'None':

        out = {}

        # A receiver that received nothing is not in the result
        for receiver_name in _receiver_names:
            if items := read_items(self, receiver_name):
                out[receiver_name] = items

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class ServiceSubscriberClearReceived(Service):
    """ Clears what every receiver has stored.
    """

    name = 'test.pubsub.service-subscriber.clear-received'

    def handle(self) -> 'None':
        for receiver_name in _receiver_names:
            clear(self, receiver_name)

# ################################################################################################################################
# ################################################################################################################################
