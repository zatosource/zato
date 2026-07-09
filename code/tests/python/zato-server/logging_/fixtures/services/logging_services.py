# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class DebugWriter(Service):
    """ Emits a DEBUG line through the service logger so tests can assert it lands in server.log.
    """
    name = 'logging-tests.debug-writer'

    def handle(self):
        self.logger.debug('Refreshed the customer cache, entries: 128')
        self.response.payload = {'result': 'ok'}

# ################################################################################################################################
# ################################################################################################################################

class PIIWriter(Service):
    """ Writes an entry to the PII audit log so tests can assert it lands in audit-pii.log.
    """
    name = 'logging-tests.pii-writer'

    def handle(self):
        extra = {'remote_addr': '127.0.0.1', 'customer_id': 'CU-48291'}
        self.audit_pii.info(self.cid, 'logging-tests.customer-lookup', current_user='api.user', extra=extra)
        self.response.payload = {'result': 'ok'}

# ################################################################################################################################
# ################################################################################################################################
