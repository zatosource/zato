# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# This file is hot-deployed into a test Zato server by conftest.py.
# Each receiver is a subscriber on its own, without a security definition, and stores
# every message pushed to it under its own name.

_received = {}

# ################################################################################################################################
# ################################################################################################################################

def _store(service_name:'str', raw_request:'object') -> 'None':
    """ Stores the data of one message pushed to the receiver of the given name.
    """
    if service_name not in _received:
        _received[service_name] = []

    _received[service_name].append(str(raw_request))

# ################################################################################################################################
# ################################################################################################################################

class ServiceSubscriberReceiverOne(Service):
    name = 'test.pubsub.service-subscriber.receiver-1'

    def handle(self) -> 'None':
        _store(self.name, self.request.raw_request)

# ################################################################################################################################

class ServiceSubscriberReceiverTwo(Service):
    name = 'test.pubsub.service-subscriber.receiver-2'

    def handle(self) -> 'None':
        _store(self.name, self.request.raw_request)

# ################################################################################################################################

class ServiceSubscriberReceiverThree(Service):
    name = 'test.pubsub.service-subscriber.receiver-3'

    def handle(self) -> 'None':
        _store(self.name, self.request.raw_request)

# ################################################################################################################################

class ServiceSubscriberReceiverFour(Service):
    name = 'test.pubsub.service-subscriber.receiver-4'

    def handle(self) -> 'None':
        _store(self.name, self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################

class ServiceSubscriberGetReceived(Service):
    """ Returns what each receiver has stored so far, keyed by the receiver's name.
    """

    name = 'test.pubsub.service-subscriber.get-received'

    def handle(self) -> 'None':
        self.response.payload = dumps(_received)

# ################################################################################################################################
# ################################################################################################################################

class ServiceSubscriberClearReceived(Service):
    """ Clears what every receiver has stored.
    """

    name = 'test.pubsub.service-subscriber.clear-received'

    def handle(self) -> 'None':
        _received.clear()

# ################################################################################################################################
# ################################################################################################################################
