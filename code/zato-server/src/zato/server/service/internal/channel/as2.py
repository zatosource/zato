# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK

# Zato
from zato.common.as2.reconcile import MDNReconciler, process_incoming_mdn
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AS2MDNEndpoint(AdminService):
    """ Built-in service that receives asynchronously delivered AS2 MDNs and matches them
    to previously sent messages through the reconciliation store. The endpoint always
    answers 200 with an empty body - the MDN's meaning is in its body, not the HTTP status -
    and an MDN for an unknown or already-reconciled Message-ID is accepted and logged,
    never errored.
    """

    name = 'zato.channel.as2.mdn.endpoint'

# ################################################################################################################################

    def handle(self) -> 'None':
        """ Processes one incoming asynchronous MDN.
        """

        # The MDN parser works with the raw wire bytes.
        body = self.request.raw_request

        if isinstance(body, str):
            body = body.encode('utf8')

        content_type = self.wsgi_environ.get('CONTENT_TYPE')
        if content_type is None:
            content_type = ''

        # Match the MDN against the sent messages - everything the reconciler learns
        # is recorded and logged inside, whether the MDN matched anything or not.
        reconciler = MDNReconciler(self.server.name)
        result = process_incoming_mdn(body, content_type, reconciler, cid=self.cid)

        if result.is_matched:
            logger.info('AS2 async MDN reconciled message `%s`, ok:%s; cid:%s',
                result.pending.message_id, result.is_ok, self.cid)

        # The answer is always a plain 200 with an empty body.
        self.response.status_code = OK
        self.response.payload = ''

# ################################################################################################################################
# ################################################################################################################################
