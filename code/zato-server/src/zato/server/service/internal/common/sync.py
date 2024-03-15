# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.broker_message import Common as BrokerMessageCommon
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SyncObjectsRequest(Model):
    security: 'bool'= True
    pubsub: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

class SyncObjectsImpl(Service):
    """ Syncs in-RAM objects with what is in the ODB.
    """
    name = 'pub.zato.common.sync-objects-impl'
    input = SyncObjectsRequest

    def handle(self):

        # Local aliases
        input:'SyncObjectsRequest' = self.request.input

        # Optionally, synchronize in-RAM state of security definitions
        if input.security:
            self.logger.info('Synchronizing security definitions')
            self.server.worker_store.sync_security()

        # Optionally, synchronize in-RAM state of pub/sub
        if input.pubsub:
            self.logger.info('Synchronizing pub/sub objects')
            self.server.worker_store.sync_pubsub()

# ################################################################################################################################
# ################################################################################################################################

class SyncObjects(Service):
    """ Syncs in-RAM objects with what is in the ODB.
    """
    name = 'pub.zato.common.sync-objects'
    input = SyncObjectsRequest

    def handle(self):

        # Local aliases
        input:'SyncObjectsRequest' = self.request.input

        # Build a dict that we can publish ..
        msg = input.to_dict()

        # .. enrich it with additional details ..
        msg['action'] = BrokerMessageCommon.Sync_Objects.value

        # .. and do publish the request now.
        self.broker_client.publish(msg)

# ################################################################################################################################
# ################################################################################################################################
