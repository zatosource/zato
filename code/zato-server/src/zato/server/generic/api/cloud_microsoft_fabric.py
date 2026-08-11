# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.typing_ import cast_
from zato.server.connection.cloud.microsoft_fabric import MicrosoftFabricClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CloudMicrosoftFabricWrapper(Wrapper):
    """ Wraps a queue of connections to Microsoft Fabric.
    """
    def __init__(self, config:'any_', server:'any_') -> 'None':
        config['auth_url'] = config['address']
        super(CloudMicrosoftFabricWrapper, self).__init__(config, 'Microsoft Fabric', server)

        # Every call of this connection is recorded here - what the alerting collectors read
        self.audit_log = AuditLog(server.name)

        # A single client shared by all the services that access this connection directly,
        # e.g. through self.microsoft.fabric. This is safe because the client acquires
        # its tokens lazily and requests sessions maintain their own HTTP connection pools.
        self.shared_client = MicrosoftFabricClient(config)
        self.shared_client.zato_audit_log = self.audit_log

# ################################################################################################################################

    def add_client(self):

        try:
            conn = MicrosoftFabricClient(self.config)
            conn.zato_audit_log = self.audit_log
            _ = self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding a Microsoft Fabric client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client = cast_('MicrosoftFabricClient', client)
            client.ping()

# ################################################################################################################################
# ################################################################################################################################
