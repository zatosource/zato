# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# The subscribers of the Dashboard tests of service subscriptions - a service has at most one subscription,
# so each test picks services of its own from this set.

# ################################################################################################################################
# ################################################################################################################################

class PubSubServiceSubscriberCreateOne(Service):
    name = 'test.pubsub.dashboard-service-subscriber.create-1'

    def handle(self) -> 'None':
        self.logger.info('Received -> %s', self.request.raw_request)

# ################################################################################################################################

class PubSubServiceSubscriberManyOne(Service):
    name = 'test.pubsub.dashboard-service-subscriber.many-1'

    def handle(self) -> 'None':
        self.logger.info('Received -> %s', self.request.raw_request)

# ################################################################################################################################

class PubSubServiceSubscriberManyTwo(Service):
    name = 'test.pubsub.dashboard-service-subscriber.many-2'

    def handle(self) -> 'None':
        self.logger.info('Received -> %s', self.request.raw_request)

# ################################################################################################################################

class PubSubServiceSubscriberListed(Service):
    name = 'test.pubsub.dashboard-service-subscriber.listed'

    def handle(self) -> 'None':
        self.logger.info('Received -> %s', self.request.raw_request)

# ################################################################################################################################

class PubSubServiceSubscriberEdit(Service):
    name = 'test.pubsub.dashboard-service-subscriber.edit'

    def handle(self) -> 'None':
        self.logger.info('Received -> %s', self.request.raw_request)

# ################################################################################################################################

class PubSubServiceSubscriberDelete(Service):
    name = 'test.pubsub.dashboard-service-subscriber.delete'

    def handle(self) -> 'None':
        self.logger.info('Received -> %s', self.request.raw_request)

# ################################################################################################################################

class PubSubServiceSubscriberDelivery(Service):
    name = 'test.pubsub.dashboard-service-subscriber.delivery'

    def handle(self) -> 'None':
        self.logger.info('Service %s received -> %s', self.name, self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################
