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

            # First, load up all the definitions from the database ..
            self.server.set_up_security(self.server.cluster_id)

            # .. update in-RAM config values ..
            self.worker_config.http_soap,
            self.server.odb.get_url_security(self.server.cluster_id, 'channel')[0],
            self.worker_config.basic_auth,
            self.worker_config.jwt,
            self.worker_config.ntlm,
            self.worker_config.oauth,
            self.worker_config.apikey,
            self.worker_config.aws,
            self.worker_config.tls_channel_sec,
            self.worker_config.tls_key_cert,
            self.worker_config.vault_conn_sec,
            self.kvdb,

            # .. now, initialize connections that may depend on what we have just loaded ..
            self.server.worker_store.init_http_soap(has_sec_config=False)

        # Optionally, synchronize in-RAM state of pub/sub
        if input.pubsub:
            self.logger.info('Synchronizing pub/sub objects')
            self.server.worker_store.sync_pubsub()

# ################################################################################################################################
# ################################################################################################################################
'''
