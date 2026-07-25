# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.api import AS2
from zato.common.as2.async_mdn import AsyncMDNQueue, deliver, deliver_due, get_retry_delay
from zato.common.as2.inbound import PendingAsyncMDN
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# Who the exchanges of these tests travel between.
_as2_from = 'PartnerCorp'
_as2_to   = 'ZatoRetail'

# Where the receipts are addressed to.
_mdn_url = 'https://partnercorp.example.com/as2/mdn'

# ################################################################################################################################
# ################################################################################################################################

def _new_pending() -> 'PendingAsyncMDN':
    """ Returns one receipt to be delivered asynchronously, the way the inbound pipeline builds it.
    """
    out = PendingAsyncMDN()

    out.url = _mdn_url
    out.body = b'--boundary\r\nContent-Type: message/disposition-notification\r\n\r\nDisposition: processed\r\n'
    out.headers = {'Content-Type': 'multipart/signed; boundary="boundary"', 'AS2-From': _as2_to}
    out.verify_tls = True
    out.timeout_seconds = 45

    return out

# ################################################################################################################################
# ################################################################################################################################

class _PostRecorder:
    """ A stand-in for the HTTP delivery of one receipt, answering with a canned status code
    or raising, so a run of the queue can be driven without a destination.
    """

    def __init__(self, status_code:'int'=200, exception:'Exception | None'=None) -> 'None':
        self.status_code = status_code
        self.exception = exception

        # Every receipt this destination was handed, so a test can see what went out.
        self.items:'anylist' = []

# ################################################################################################################################

    def __call__(self, item:'any_') -> 'int':
        self.items.append(item)

        if self.exception:
            raise self.exception

        return self.status_code

# ################################################################################################################################
# ################################################################################################################################

class TestEnqueue:
    """ The receipt is persisted before the inbound POST is answered, which is the whole point -
    a receipt living only in a greenlet is gone the moment the process stops.
    """

    def test_a_queued_receipt_comes_back_exactly_as_it_went_in(self) -> 'None':

        queue = AsyncMDNQueue()
        pending = _new_pending()

        row_id = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', pending, 'as2-channel', 'cid-1')

        assert row_id

        item = queue.get(row_id)

        # The bytes of a signed receipt cannot be rebuilt, so they have to survive
        # the round trip through the queue unchanged.
        assert item.body == pending.body
        assert item.headers == pending.headers
        assert item.url == pending.url

        assert item.as2_from == _as2_from
        assert item.as2_to == _as2_to
        assert item.message_id == '<orders-850@partnercorp>'
        assert item.channel_name == 'as2-channel'
        assert item.cid == 'cid-1'

        # The delivery details travel with the receipt, so the attempt that resumes
        # after a restart does not need the partnership to make them up again.
        assert item.verify_tls is True
        assert item.timeout_seconds == 45

        assert item.attempt_count == 0

# ################################################################################################################################

    def test_the_same_message_cannot_queue_two_receipts(self) -> 'None':

        queue = AsyncMDNQueue()

        first_id = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', _new_pending(), 'as2-channel', 'cid-1')

        # The replay of a message whose receipt is still waiting must not queue a second one -
        # the receipt of the first delivery is the one the peer is owed.
        second_id = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', _new_pending(), 'as2-channel', 'cid-2')

        assert first_id
        assert second_id == 0

        later = utcnow() + timedelta(seconds=1)
        due = queue.due(later)

        due_count = len(due)
        assert due_count == 1

# ################################################################################################################################

    def test_a_freshly_queued_receipt_is_due_at_once(self) -> 'None':

        queue = AsyncMDNQueue()
        now = utcnow()

        _ = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', _new_pending(), 'as2-channel', 'cid-1', now=now)

        due = queue.due(now)

        due_count = len(due)
        assert due_count == 1

# ################################################################################################################################
# ################################################################################################################################

class TestDelivery:
    """ A delivered receipt leaves the queue, everything else stays in it with its next attempt
    scheduled further out - which is what turns a destination coming back in the morning
    into a receipt that still arrives.
    """

    def test_an_accepted_receipt_leaves_the_queue(self) -> 'None':

        queue = AsyncMDNQueue()
        now = utcnow()

        row_id = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', _new_pending(), 'as2-channel', 'cid-1',
            now=now)

        item = queue.get(row_id)
        post = _PostRecorder(200)

        is_delivered = deliver(queue, item, post, now)

        assert is_delivered is True
        assert queue.get(row_id) is None

# ################################################################################################################################

    def test_a_refused_receipt_stays_for_the_next_attempt(self) -> 'None':

        queue = AsyncMDNQueue()
        now = utcnow()

        row_id = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', _new_pending(), 'as2-channel', 'cid-1',
            now=now)

        item = queue.get(row_id)
        post = _PostRecorder(500)

        is_delivered = deliver(queue, item, post, now)

        assert is_delivered is False

        # The receipt is still there with one failure behind it ..
        stored = queue.get(row_id)
        assert stored.attempt_count == 1

        # .. and it is no longer due right away, so the next run of the drain
        # does not repeat the attempt immediately.
        due = queue.due(now)
        due_count = len(due)
        assert due_count == 0

        # It becomes due again once the delay has passed.
        later = now + get_retry_delay(1) + timedelta(seconds=1)
        due = queue.due(later)
        due_count = len(due)
        assert due_count == 1

# ################################################################################################################################

    def test_an_unreachable_destination_stays_for_the_next_attempt(self) -> 'None':

        queue = AsyncMDNQueue()
        now = utcnow()

        row_id = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', _new_pending(), 'as2-channel', 'cid-1',
            now=now)

        item = queue.get(row_id)
        post = _PostRecorder(exception=Exception('Connection refused'))

        is_delivered = deliver(queue, item, post, now)

        assert is_delivered is False

        stored = queue.get(row_id)
        assert stored.attempt_count == 1

# ################################################################################################################################

    def test_a_receipt_is_given_up_on_at_the_attempt_ceiling(self) -> 'None':

        queue = AsyncMDNQueue()
        now = utcnow()

        row_id = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', _new_pending(), 'as2-channel', 'cid-1',
            now=now)

        post = _PostRecorder(503)

        # Every attempt fails, with the clock moved past each scheduled delay so that
        # the receipt is due again each time.
        attempt_number = 0

        while attempt_number < AS2.Async_MDN.Max_Attempts:
            attempt_number += 1

            item = queue.get(row_id)
            assert item is not None

            _ = deliver(queue, item, post, now)
            now = now + timedelta(seconds=AS2.Async_MDN.Max_Retry_Seconds + 1)

        # The receipt is gone from the queue and it was attempted exactly as many times
        # as the ceiling allows - a destination that refused ten times is not going
        # to accept the eleventh.
        assert queue.get(row_id) is None

        attempted_count = len(post.items)
        assert attempted_count == AS2.Async_MDN.Max_Attempts

# ################################################################################################################################

    def test_the_drain_delivers_every_due_receipt(self) -> 'None':

        queue = AsyncMDNQueue()
        now = utcnow()

        _ = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', _new_pending(), 'as2-channel', 'cid-1', now=now)
        _ = queue.enqueue(_as2_from, _as2_to, '<invoice-810@partnercorp>', _new_pending(), 'as2-channel', 'cid-2', now=now)
        _ = queue.enqueue('OtherPartner', _as2_to, '<orders-850@other>', _new_pending(), 'as2-channel', 'cid-3', now=now)

        post = _PostRecorder(200)

        delivered_count = deliver_due(queue, post, now)

        assert delivered_count == 3

        due = queue.due(now)
        due_count = len(due)
        assert due_count == 0

# ################################################################################################################################

    def test_a_restart_resumes_the_delivery(self) -> 'None':

        # The channel that accepted the message queues the receipt and then the process stops
        # before anything is delivered - which is the failure this whole queue exists for.
        queue = AsyncMDNQueue()
        now = utcnow()

        _ = queue.enqueue(_as2_from, _as2_to, '<orders-850@partnercorp>', _new_pending(), 'as2-channel', 'cid-1', now=now)

        # A fresh queue over the same database is what a restarted server sees.
        restarted = AsyncMDNQueue()
        post = _PostRecorder(200)

        delivered_count = deliver_due(restarted, post, now)

        assert delivered_count == 1

        delivered = post.items[0]
        assert delivered.message_id == '<orders-850@partnercorp>'

# ################################################################################################################################
# ################################################################################################################################

class TestRetryDelay:
    """ The wait doubles per failure and then stops doubling, so that a destination which is down
    is not hammered while a receipt still goes out hourly for as long as the queue holds it.
    """

    def test_the_delay_doubles_per_failure(self) -> 'None':

        first = get_retry_delay(1)
        second = get_retry_delay(2)
        third = get_retry_delay(3)

        assert first.total_seconds() == AS2.Async_MDN.First_Retry_Seconds
        assert second.total_seconds() == AS2.Async_MDN.First_Retry_Seconds * 2
        assert third.total_seconds() == AS2.Async_MDN.First_Retry_Seconds * 4

# ################################################################################################################################

    def test_the_delay_stops_at_the_ceiling(self) -> 'None':

        delay = get_retry_delay(AS2.Async_MDN.Max_Attempts)
        assert delay.total_seconds() == AS2.Async_MDN.Max_Retry_Seconds

# ################################################################################################################################
# ################################################################################################################################

class TestRetention:
    """ A receipt nobody accepted for a week is dropped - the sender has long since alerted
    on the missing MDN and resent the message itself.
    """

    def test_a_stale_receipt_is_dropped(self) -> 'None':

        queue = AsyncMDNQueue()
        now = utcnow()

        long_ago = now - timedelta(days=AS2.Async_MDN.Retention_Days + 1)

        stale_id = queue.enqueue(_as2_from, _as2_to, '<old@partnercorp>', _new_pending(), 'as2-channel', 'cid-old',
            now=long_ago)
        fresh_id = queue.enqueue(_as2_from, _as2_to, '<new@partnercorp>', _new_pending(), 'as2-channel', 'cid-new',
            now=now)

        dropped_count = queue.run_retention(now)

        assert dropped_count == 1
        assert queue.get(stale_id) is None
        assert queue.get(fresh_id) is not None

# ################################################################################################################################
# ################################################################################################################################
