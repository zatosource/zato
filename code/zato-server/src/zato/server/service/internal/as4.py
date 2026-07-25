# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The scheduler-driven half of AS4 reception awareness - the automatic repeat delivery of a message
# whose receipt has not arrived. It runs from the persisted evidence rather than from anything held
# in memory, which is what makes it survive a restart.

# Zato
from zato.common.api import AS4
from zato.common.as4.common import Default
from zato.common.as4.mpc import requeue_stale
from zato.common.as4.resend import collect_candidates, collect_missing_receipts
from zato.common.util.api import utcnow
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.as4.resend import ResendCandidate
    from zato.common.typing_ import dictlist
    datetime = datetime
    dictlist = dictlist
    ResendCandidate = ResendCandidate

# ################################################################################################################################
# ################################################################################################################################

class ResendOverdueMessages(AdminService):
    """ Repeats the delivery of every message whose receipt is overdue and which has attempts left,
    under its original eb:MessageId, so that the receiving side's duplicate detection is what decides
    whether the payload is processed once or twice. This is the AS4 reception awareness feature, and
    it is distinct from the operator resubmit, which delivers the payload as a new message.

    A message nobody answered within the window it was given is reported rather than repeated - by
    then the exchange needs an operator, not another attempt.
    """
    name = AS4.Resend.Service

    def handle(self) -> 'None':

        # One reference moment for the whole run
        now = utcnow()

        configs = self._get_configs()

        self._report_missing_receipts(configs, now)
        self._requeue_pulled(now)

        candidates = collect_candidates(configs, now, self.server.name)

        if not candidates:
            return

        candidate_count = len(candidates)
        suffix = 'message' if candidate_count == 1 else 'messages'

        self.logger.info('Resending %d overdue AS4 %s', candidate_count, suffix)

        for candidate in candidates:
            self._resend(candidate)

# ################################################################################################################################

    def _get_configs(self) -> 'dictlist':
        """ Returns the configuration of every outgoing AS4 connection - which window counts as
        overdue, how many attempts each exchange gets and which connection a message travels out
        through again.
        """

        # Our response to produce
        out:'dictlist' = []

        config_store = self.server.config_manager.config_store.out_as4

        for name in list(config_store):
            item = config_store[name]

            # The store also holds entries that are not connections of their own.
            if isinstance(item, str):
                continue

            out.append(item.config)

        return out

# ################################################################################################################################

    def _report_missing_receipts(self, configs:'dictlist', now:'datetime') -> 'None':
        """ Logs the exchanges whose receipt never arrived within the window they were given. The
        audit log is where the operator sees them message by message - this is what makes the run
        itself say that there are such messages at all.
        """
        missing = collect_missing_receipts(configs, now, self.server.name)

        if not missing:
            return

        missing_count = len(missing)
        suffix = 'message' if missing_count == 1 else 'messages'

        self.logger.warning('AS4 receipt is missing for %d %s', missing_count, suffix)

        for pending in missing:
            self.logger.warning('AS4 receipt is missing for message `%s` sent to `%s` at %s; cid:%s',
                pending.message_id, pending.to_party, pending.sent_time_iso, pending.cid)

# ################################################################################################################################

    def _requeue_pulled(self, now:'datetime') -> 'None':
        """ Puts back on their channels the messages that were handed over to a pull request whose
        receipt never arrived. The partner asks for them again and gets them under the same
        eb:MessageId, which is what its duplicate detection is for.
        """
        requeued = requeue_stale(now, Default.Pull_Receipt_Seconds)

        if not requeued:
            return

        suffix = 'message' if requeued == 1 else 'messages'

        self.logger.info('Requeued %d unacknowledged pulled AS4 %s', requeued, suffix)

# ################################################################################################################################

    def _resend(self, candidate:'ResendCandidate') -> 'None':
        """ Makes one repeat delivery. A failure here is logged and nothing more - the message stays
        outstanding, so the next run picks it up again until its attempts or its window run out.
        """
        try:
            invoker = self.as4[candidate.connection_name]
            result = invoker.resend(candidate)

            self.logger.info('AS4 resend of message `%s` over `%s` (HTTP %d), attempt %d; is_ok:%s',
                candidate.message_id, candidate.connection_name, result.http_status,
                candidate.attempt_count + 1, result.is_ok)

        # The partner's endpoint is an external boundary and so is everything behind it - one message
        # that cannot go out must not stop the rest of the run.
        except Exception as e:
            self.logger.warning('AS4 resend of message `%s` over `%s` failed; e:`%s`',
                candidate.message_id, candidate.connection_name, e)

# ################################################################################################################################
# ################################################################################################################################
