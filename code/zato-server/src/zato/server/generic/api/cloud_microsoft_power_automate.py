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
from zato.server.connection.cloud.microsoft_power_automate import MicrosoftPowerAutomateClient
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

class CloudMicrosoftPowerAutomateWrapper(Wrapper):
    """ Wraps a queue of connections to Microsoft Power Automate.
    """
    def __init__(self, config:'any_', server:'any_') -> 'None':
        config['auth_url'] = config['address']
        super(CloudMicrosoftPowerAutomateWrapper, self).__init__(config, 'Microsoft Power Automate', server)

        # Every call of this connection is recorded here - what the alerting collectors read
        self.audit_log = AuditLog(server.name)

        # A single client shared by all the services that access this connection directly,
        # e.g. through self.microsoft.power_platform. This is safe because the client acquires
        # its tokens lazily and requests sessions maintain their own HTTP connection pools.
        self.shared_client = MicrosoftPowerAutomateClient(config)
        self.shared_client.zato_audit_log = self.audit_log

# ################################################################################################################################

    def add_client(self):

        try:
            conn = MicrosoftPowerAutomateClient(self.config)
            conn.zato_audit_log = self.audit_log
            _ = self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding a Microsoft Power Automate client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client = cast_('MicrosoftPowerAutomateClient', client)
            client.ping()

# ################################################################################################################################
# ################################################################################################################################
