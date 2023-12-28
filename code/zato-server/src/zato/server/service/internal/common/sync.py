'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SyncObjectsRequest(Model):
    security: 'bool'= False
    pubsub: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

class SyncObjectsImpl(Service):
    """ Syncs in-RAM objects with what is in the ODB.
    """
    name = 'dev.zato.sync-objects-impl'
    input = SyncObjectsRequest

    def handle(self):

        # Local aliases
        input:'SyncObjectsRequest' = self.request.input

        # Optionally, synchronize in-RAM state of security definitions
        if input.security:
            self.logger.info('Synchronizing security definitions')

        # Optionally, synchronize in-RAM state of pub/sub
        if input.pubsub:
            self.logger.info('Synchronizing pub/sub objects')
            self.server.worker_store.sync_pubsub()

# ################################################################################################################################
# ################################################################################################################################
'''
