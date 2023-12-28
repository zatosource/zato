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

class SyncObjects(Service):
    """ Syncs in-RAM objects with what is in the ODB.
    """
    name = 'dev.zato.sync-objects'
    input = SyncObjectsRequest

    def handle(self):

        # Local aliases
        input:'SyncObjectsRequest' = self.request.input
        input

# ################################################################################################################################
# ################################################################################################################################
'''
