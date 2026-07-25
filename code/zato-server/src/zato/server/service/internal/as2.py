# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The two scheduler-driven halves of AS2 reliability - the drain of the asynchronous MDN queue
# and the automatic resend of messages whose receipt never arrived. Both run from the persisted
# state rather than from anything held in memory, which is what makes them survive a restart.

# Zato
from zato.common.api import AS2
from zato.common.as2.async_mdn import AsyncMDNQueue, deliver_due, post_async_mdn
from zato.common.as2.resend import collect_candidates
from zato.common.util.api import utcnow
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.resend import ResendCandidate
    from zato.common.typing_ import dictlist
    dictlist = dictlist
    ResendCandidate = ResendCandidate

# ################################################################################################################################
# ################################################################################################################################

class DeliverAsyncMDNs(AdminService):
    """ Delivers the asynchronous MDNs that are due - the receipts an inbound message asked to have
    delivered to a separate URL, persisted before the inbound POST was answered. A receipt the peer
    accepts leaves the queue, a refused or unreachable one is retried with a widening delay,
    and one that has waited longer than the retention window is dropped.
    """
    name = AS2.Async_MDN.Service

    def handle(self) -> 'None':

        # One reference moment for the whole drain
        now = utcnow()

        queue = AsyncMDNQueue()

        delivered_count = deliver_due(queue, post_async_mdn, now)

        if delivered_count:
            suffix = 'MDN' if delivered_count == 1 else 'MDNs'
            self.logger.info('Delivered %d asynchronous AS2 %s', delivered_count, suffix)

        # The receipts nobody accepted in a week are dropped, loudly - the audit log
        # is where the operator sees which messages the partner never got a receipt for.
        _ = queue.run_retention(now)

# ################################################################################################################################
# ################################################################################################################################

class ResendOverdueMessages(AdminService):
    """ Resends every message whose MDN is overdue and which has attempts left, under its original
    Message-ID, so that the receiver's duplicate detection is what decides whether the document is
    delivered once or twice. This is the reliability behavior the EDIINT-Features header advertises,
    and it is distinct from the operator resubmit, which delivers the content as a new message.
    """
    name = AS2.Resend.Service

    def handle(self) -> 'None':

        # One reference moment for the whole run
        now = utcnow()

        # The partner configuration says which window counts as overdue, how many resends
        # each partner allows and which connection the message travels back through.
        configs:'dictlist' = []
        for config in self.server.config_manager.outconn_as2.values():
            configs.append(config)

        candidates = collect_candidates(configs, now, self.server.name)

        if not candidates:
            return

        candidate_count = len(candidates)
        suffix = 'message' if candidate_count == 1 else 'messages'

        self.logger.info('Resending %d overdue AS2 %s', candidate_count, suffix)

        for candidate in candidates:
            self._resend(candidate)

# ################################################################################################################################

    def _resend(self, candidate:'ResendCandidate') -> 'None':
        """ Makes one repeat delivery. A failure here is logged and nothing more - the message
        stays outstanding, so the next run picks it up again until its attempts run out.
        """
        try:
            invoker = self.as2[candidate.connection_name]

            result = invoker.send(
                candidate.payload,
                candidate.filename,
                message_id=candidate.message_id,
                delivery_kind=candidate.delivery_kind,
            )

            self.logger.info('AS2 %s of message `%s` over `%s` (HTTP %d), attempt %d; is_ok:%s',
                candidate.delivery_kind, candidate.message_id, candidate.connection_name,
                result.http_status, candidate.attempt_count + 1, result.is_ok)

        # The partner's endpoint is an external boundary and so is every connection behind it -
        # one message that cannot go out must not stop the rest of the run.
        except Exception as e:
            self.logger.warning('AS2 %s of message `%s` over `%s` failed; e:`%s`',
                candidate.delivery_kind, candidate.message_id, candidate.connection_name, e)

# ################################################################################################################################
# ################################################################################################################################
