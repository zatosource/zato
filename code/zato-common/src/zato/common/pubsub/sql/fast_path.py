# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The fast path of deliveries. A publication that finds a pull waiting for the messages of a subscriber, or the delivery
# greenlet of an idle push subscriber, inserts the delivery rows of that subscriber already leased or already attempted,
# in its own transaction, and the messages are handed over in memory once the transaction commits. A transaction
# that does not commit hands nothing over, and the subscribers that it claimed wait as before.

# stdlib
from dataclasses import dataclass
from types import SimpleNamespace

# gevent
from gevent.event import Event

# Zato
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.sql.clock import get_engine_clock
from zato.common.pubsub.sql.config import get_pull_lease_seconds
from zato.common.pubsub.sql.pending import new_pending_lease
from zato.common.pubsub.sql.pull import message_columns
from zato.common.pubsub.sql.schema import delivery_table
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.pubsub.sql.payload_cache import PayloadCache
    from zato.common.pubsub.sql.pending import PendingLease, pending_lease_list, PendingPublication
    from zato.common.typing_ import anydict, anylist, callable_, strlist
    from zato_common_core.zato_common_core import SubscriptionList

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    PayloadCache = PayloadCache
    PendingLease = PendingLease
    pending_lease_list = pending_lease_list
    PendingPublication = PendingPublication
    SubscriptionList = SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

pull_waiter_list     = list['PullWaiter']
push_target_list     = list['PushTarget']
cached_payload_list  = list['CachedPayload']
strpullwaiterdict    = dict[str, 'pull_waiter_list']
strpushtargetdict    = dict[str, 'PushTarget']
intpublicationdict   = dict[int, 'PendingPublication']
pull_claim_list      = list[tuple['PullWaiter', 'anylist']]
push_claim_list      = list[tuple['PushTarget', 'anylist']]

# ################################################################################################################################
# ################################################################################################################################

# The key of a message whose first push attempt was recorded before the push, with the other messages of its batch
# or by the publication that handed it over
Attempt_Recorded_Key = 'zato.pubsub.attempt_recorded'

# The states of a waiting pull and of an idle push greenlet - waiting for a publication, claimed by a publication
# whose transaction has not committed yet, handed the messages of that publication, or no longer waiting.
State_Waiting   = 'waiting'
State_Claimed   = 'claimed'
State_Delivered = 'delivered'
State_Released  = 'released'

# The attempt that a delivery row claimed by a publication has
_first_attempt = 1

# The lease of a row that no pull holds
_not_leased = 0

# How many milliseconds one second has
_ms_per_second = 1000

# The names of the columns that the builder of pulled messages reads, in the order of the rows of a lease
_id_column = 'id'
_payload_column = 'payload'

# The insert of the delivery rows that the publications claimed, which returns the ID of each row
_claimed_insert = delivery_table.insert()
_claimed_insert = _claimed_insert.returning(delivery_table.c.id, delivery_table.c.sub_key, delivery_table.c.message_id)
_claimed_insert_plain = PlainStatement(_claimed_insert)

# ################################################################################################################################
# ################################################################################################################################

def _get_message_column_names() -> 'strlist':
    """ Returns the names of the message columns of a lease, in the order of the rows that it reads.
    """
    out:'strlist' = []

    for column in message_columns:
        out.append(column.name)

    return out

_message_column_names = _get_message_column_names()

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PullWaiter:
    """ A pull of one subscriber that waits for a publication because the queue of the subscriber was empty.
    """

    # Who pulls and how much
    sub_key: 'str'
    max_messages: 'int'
    max_len: 'int'

    # What wakes the pull, where it stands and whether a publication without a claim woke it
    event: 'Event'
    state: 'str'
    is_notified: 'bool'

    # The lease that the claiming publication built, and the messages of the lease once it committed
    lease: 'PendingLease | None'
    messages: 'anylist'

# ################################################################################################################################

@dataclass(init=False)
class PushTarget:
    """ The delivery greenlet of one push subscriber that waits for a publication because the queue of the subscriber
    was empty.
    """

    # Whose greenlet it is and how many messages one batch of it holds at most
    sub_key: 'str'
    max_messages: 'int'
    max_len: 'int'

    # What wakes the greenlet once the claiming commit has an outcome, and where it stands
    event: 'Event'
    state: 'str'

    # The messages handed over and the payload epoch under which their payloads were read
    messages: 'anylist'
    read_epoch: 'int'

# ################################################################################################################################

@dataclass(init=False)
class CachedPayload:
    """ The payload of a message handed over to a push greenlet, which the payload cache keeps once the claim commits.
    """
    msg_id: 'str'
    data: 'str'
    size: 'int'

# ################################################################################################################################

@dataclass(init=False)
class FastPathClaims:
    """ What the publications of one transaction claimed - the waiting pulls with their leases, the idle push greenlets
    and the payloads that their messages share.
    """
    pull_waiters: 'pull_waiter_list'
    leases: 'pending_lease_list'
    push_targets: 'push_target_list'
    payloads: 'cached_payload_list'
    read_epoch: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _new_claims() -> 'FastPathClaims':
    """ Returns the claims of a transaction that has claimed nothing yet.
    """
    out = FastPathClaims()
    out.pull_waiters = []
    out.leases = []
    out.push_targets = []
    out.payloads = []
    out.read_epoch = 0

    return out

# ################################################################################################################################

def _take_rows(rows:'anylist', max_messages:'int', max_len:'int', published:'intpublicationdict') -> 'tuple[anylist, anylist]':
    """ Returns the rows that one pull or one push batch takes, in the order of the queue, and the rows that remain.
    The rows taken are within the size budget, except that a message larger than the budget is taken by the batch
    that reaches it, after the messages ahead of it, and ends that batch, as a lease does.
    """
    taken:'anylist' = []
    total_len = 0

    for row in rows:

        if len(taken) == max_messages:
            break

        pending = published[row['message_id']]
        data_len = pending.message_values['data_size']
        is_oversized = data_len > max_len

        if taken:
            if total_len + data_len > max_len:
                if not is_oversized:
                    break

        taken.append(row)
        total_len += data_len

        if is_oversized:
            break

    remaining = rows[len(taken):]

    out = (taken, remaining)
    return out

# ################################################################################################################################

def _get_queue_order(row:'anydict') -> 'tuple[int, int]':
    """ Returns the key that sorts delivery rows in the order of the queue, priority highest-first and then publication order.
    """
    out = (-row['priority'], row['message_id'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class FastPath:
    """ The waiting pulls and the idle push greenlets of the subscribers of one backend, which the publications of the
    backend claim and hand their messages over to. Only the active server delivers, so both are local to its worker.
    """

    def __init__(
        self,
        *,
        subscription_list:'SubscriptionList',
        payload_cache:'PayloadCache',
        get_sub_event:'callable_',
        on_leased:'callable_',
        build_message:'callable_',
        load_payload:'callable_',
        ) -> 'None':

        # The subscriber and topic pairs that decide which topics a subscriber is handed out ..
        self.subscription_list = subscription_list

        # .. the payloads that push deliveries share ..
        self.payload_cache = payload_cache

        # .. the wake-up event of each subscriber, which its push greenlet waits on ..
        self.get_sub_event = get_sub_event

        # .. what builds the messages and the audit events of a lease ..
        self.on_leased = on_leased

        # .. and what builds the message of a push from a row and its payload, and what loads a stored payload.
        self.build_message = build_message
        self.load_payload = load_payload

        # The waiting pulls of each subscriber, in the order in which they began to wait ..
        self._pull_waiters:'strpullwaiterdict' = {}

        # .. the idle push greenlet of each subscriber ..
        self._push_targets:'strpushtargetdict' = {}

        # .. and how many times the publications of each subscriber woke it up.
        self._versions:'anydict' = {}

# ################################################################################################################################

    def get_version(self, sub_key:'str') -> 'int':
        """ Returns how many times the publications of a subscriber woke it up, by which a pull learns that a publication
        committed between its read of the queue and the beginning of its wait.
        """
        if sub_key in self._versions:
            out = self._versions[sub_key]
        else:
            out = 0

        return out

# ################################################################################################################################

    def notify(self, sub_keys:'strlist') -> 'None':
        """ Wakes up the waiting pulls of the given subscribers after a commit that wrote rows for them without a claim.
        """
        for sub_key in sub_keys:

            if sub_key in self._versions:
                self._versions[sub_key] += 1
            else:
                self._versions[sub_key] = 1

            if waiters := self._pull_waiters.get(sub_key):
                for waiter in waiters:
                    if waiter.state == State_Waiting:
                        waiter.is_notified = True
                        waiter.event.set()

# ################################################################################################################################

    def add_pull_waiter(self, sub_key:'str', max_messages:'int', max_len:'int') -> 'PullWaiter':
        """ Registers a pull that waits for the publications of its subscriber, after the pulls that wait already.
        """
        out = PullWaiter()
        out.sub_key = sub_key
        out.max_messages = max_messages
        out.max_len = max_len
        out.event = Event()
        out.state = State_Waiting
        out.is_notified = False
        out.lease = None
        out.messages = []

        if waiters := self._pull_waiters.get(sub_key):
            waiters.append(out)
        else:
            self._pull_waiters[sub_key] = [out]

        return out

# ################################################################################################################################

    def wait_pull(self, waiter:'PullWaiter', timeout:'float') -> 'None':
        """ Waits until a publication wakes the pull or the timeout runs out. A pull that a publication claimed
        waits for the outcome of the commit of the publication, whatever the timeout.
        """
        _ = waiter.event.wait(timeout)

        while waiter.state == State_Claimed:
            waiter.event.clear()
            _ = waiter.event.wait()

# ################################################################################################################################

    def remove_pull_waiter(self, waiter:'PullWaiter') -> 'None':
        """ Unregisters a pull, which no publication claims from now on.
        """
        waiters = self._pull_waiters[waiter.sub_key]
        waiters.remove(waiter)

        if not waiters:
            del self._pull_waiters[waiter.sub_key]

        if waiter.state == State_Waiting:
            waiter.state = State_Released

# ################################################################################################################################

    def add_push_target(self, sub_key:'str', max_messages:'int', max_len:'int') -> 'PushTarget':
        """ Registers the idle delivery greenlet of a push subscriber.
        """
        out = PushTarget()
        out.sub_key = sub_key
        out.max_messages = max_messages
        out.max_len = max_len
        out.event = Event()
        out.state = State_Waiting
        out.messages = []
        out.read_epoch = 0

        self._push_targets[sub_key] = out

        return out

# ################################################################################################################################

    def wait_push_outcome(self, target:'PushTarget') -> 'None':
        """ Waits for the outcome of the commit of the publication that claimed a push greenlet, if any did.
        """
        while target.state == State_Claimed:
            target.event.clear()
            _ = target.event.wait()

# ################################################################################################################################

    def remove_push_target(self, target:'PushTarget') -> 'None':
        """ Unregisters the delivery greenlet of a push subscriber, which no publication claims from now on.
        """
        if self._push_targets.get(target.sub_key) is target:
            del self._push_targets[target.sub_key]

        if target.state == State_Waiting:
            target.state = State_Released

# ################################################################################################################################

    def new_claims(self) -> 'FastPathClaims':
        """ Returns the claims of a transaction that is about to begin.
        """
        out = _new_claims()
        return out

# ################################################################################################################################

    def _is_waited_for(self, sub_key:'str') -> 'bool':
        """ Whether a pull or a push greenlet of a subscriber waits for its publications.
        """
        if sub_key in self._pull_waiters:
            out = True
        else:
            out = sub_key in self._push_targets

        return out

# ################################################################################################################################

    def _is_deliverable(self, sub_key:'str', row:'anydict', now_ms:'int') -> 'bool':
        """ Whether a delivery row may be handed out to its subscriber now - its topic is one that the subscription
        list hands out to the subscriber and its message has not expired, as a lease requires.
        """
        if row['expiration_ms'] <= now_ms:
            out = False

        elif (delivered_topics := self.subscription_list.delivered_topics(sub_key)) is None:
            out = True

        else:
            out = row['topic_name'] in delivered_topics

        return out

# ################################################################################################################################

    def claim(
        self,
        claims:'FastPathClaims',
        connection:'Connection',
        published:'intpublicationdict',
        delivery_rows:'anylist',
        ) -> 'anylist':
        """ Claims the waiting pulls and the idle push greenlets of the subscribers of the given delivery rows, inserts
        their rows leased or attempted once, in the caller's transaction, and builds their messages. Returns the delivery
        rows that nothing claimed, which the caller inserts as before. The given publications are those that inserted
        their messages, by the IDs of the messages.
        """
        # Nothing is claimed while nothing waits ..
        if not self._pull_waiters:
            if not self._push_targets:
                return delivery_rows

        out:'anylist' = []
        rows_by_sub_key:'anydict' = {}

        # .. the rows of the subscribers that something waits for are claimed and the others are inserted as before ..
        for row in delivery_rows:
            sub_key = row['sub_key']

            if self._is_waited_for(sub_key):
                if sub_key in rows_by_sub_key:
                    rows_by_sub_key[sub_key].append(row)
                else:
                    rows_by_sub_key[sub_key] = [row]
            else:
                out.append(row)

        if not rows_by_sub_key:
            return out

        # .. a pull leases its rows from the time of the database on ..
        clock = get_engine_clock(connection.engine)
        now_ms = clock.now_ms()
        leased_until_ms = now_ms + get_pull_lease_seconds() * _ms_per_second

        pull_claims:'pull_claim_list' = []
        push_claims:'push_claim_list' = []
        claimed_rows:'anylist' = []

        for sub_key, sub_key_rows in rows_by_sub_key.items():

            # .. each in the order of the queue, of the rows that may be handed out ..
            deliverable:'anylist' = []

            for row in sub_key_rows:
                if self._is_deliverable(sub_key, row, now_ms):
                    deliverable.append(row)
                else:
                    out.append(row)

            deliverable.sort(key=_get_queue_order)

            # .. the waiting pulls take theirs in the order in which they began to wait ..
            if waiters := self._pull_waiters.get(sub_key):
                for waiter in waiters:

                    if not deliverable:
                        break

                    if waiter.state != State_Waiting:
                        continue

                    taken, deliverable = _take_rows(deliverable, waiter.max_messages, waiter.max_len, published)

                    for row in taken:
                        row['attempt'] = _first_attempt
                        row['leased_until_ms'] = leased_until_ms

                    waiter.state = State_Claimed
                    claims.pull_waiters.append(waiter)
                    pull_claims.append((waiter, taken))
                    claimed_rows.extend(taken)

            # .. an idle push greenlet takes one batch ..
            elif target := self._push_targets.get(sub_key):
                if deliverable:
                    if target.state == State_Waiting:

                        taken, deliverable = _take_rows(deliverable, target.max_messages, target.max_len, published)

                        for row in taken:
                            row['attempt'] = _first_attempt
                            row['leased_until_ms'] = _not_leased

                        target.state = State_Claimed
                        claims.push_targets.append(target)
                        push_claims.append((target, taken))
                        claimed_rows.extend(taken)

            # .. and what nothing took is inserted as before.
            out.extend(deliverable)

        if claimed_rows:
            self._insert_claimed(claims, connection, published, claimed_rows, pull_claims, push_claims, now_ms, leased_until_ms)

        return out

# ################################################################################################################################

    def _insert_claimed(
        self,
        claims:'FastPathClaims',
        connection:'Connection',
        published:'intpublicationdict',
        claimed_rows:'anylist',
        pull_claims:'pull_claim_list',
        push_claims:'push_claim_list',
        now_ms:'int',
        leased_until_ms:'int',
        ) -> 'None':
        """ Inserts the claimed rows in one statement and builds the leases of the pulls and the messages of the pushes.
        """
        delivery_ids:'anydict' = {}

        for row in _claimed_insert_plain.insert_rows(connection, claimed_rows):
            delivery_ids[(row.sub_key, row.message_id)] = row.id

        # Each pull receives a lease of its rows, whose messages and reception events are built in the transaction ..
        for waiter, rows in pull_claims:

            lease = new_pending_lease(waiter.sub_key, waiter.max_messages, waiter.max_len, now_ms, leased_until_ms,
                self.on_leased)

            for row in rows:
                message_id = row['message_id']
                message_row = self._get_lease_row(message_id, published[message_id])

                lease.rows.append(message_row)
                lease.attempts[message_id] = _first_attempt

            lease.on_leased(lease)

            waiter.lease = lease
            claims.leases.append(lease)

        # .. while each push greenlet receives messages with the IDs of their rows and with their payloads,
        # .. each payload loaded once whatever the number of subscribers ..
        if push_claims:
            claims.read_epoch = self.payload_cache.get_epoch()
            data_by_message_id:'anydict' = {}

            for target, rows in push_claims:

                messages:'anylist' = []

                for row in rows:
                    message_id = row['message_id']
                    message_row = self._get_push_row(message_id, published[message_id])

                    if message_id in data_by_message_id:
                        data = data_by_message_id[message_id]
                    else:
                        data = self.load_payload(message_row)
                        data_by_message_id[message_id] = data
                        self._add_cached_payload(claims, message_row, data)

                    message = self.build_message(message_row, data)
                    message['delivery_id'] = delivery_ids[(target.sub_key, message_id)]
                    message['delivery_attempt'] = _first_attempt
                    message[Attempt_Recorded_Key] = True

                    messages.append(message)

                # .. and the messages are handed over only once the transaction commits.
                target.messages = messages
                target.read_epoch = claims.read_epoch

# ################################################################################################################################

    def _get_lease_row(self, message_id:'int', pending:'PendingPublication') -> 'tuple':
        """ Returns the row of a claimed message in the order of the message columns of a lease.
        """
        message_values = pending.message_values
        values:'anylist' = []

        for name in _message_column_names:
            if name == _id_column:
                values.append(message_id)
            elif name == _payload_column:
                values.append(pending.payload)
            else:
                values.append(message_values[name])

        out = tuple(values)
        return out

# ################################################################################################################################

    def _get_push_row(self, message_id:'int', pending:'PendingPublication') -> 'SimpleNamespace':
        """ Returns a claimed message with the attributes of a fetched row, its stored payload included.
        """
        out = SimpleNamespace(**pending.message_values)
        out.id = message_id
        out.payload = pending.payload

        return out

# ################################################################################################################################

    def _add_cached_payload(self, claims:'FastPathClaims', message_row:'SimpleNamespace', data:'str') -> 'None':
        """ Adds the payload of a claimed message to those that the payload cache keeps once the claim commits.
        """
        cached = CachedPayload()
        cached.msg_id = message_row.msg_id
        cached.data = data
        cached.size = message_row.data_size

        claims.payloads.append(cached)

# ################################################################################################################################

    def mark_committed(self, claims:'FastPathClaims') -> 'None':
        """ Hands the messages of a committed transaction over to the pulls and the push greenlets that it claimed.
        """
        # Each pull receives the messages of its lease ..
        for waiter in claims.pull_waiters:
            lease = cast_('PendingLease', waiter.lease)

            waiter.messages = lease.messages
            waiter.state = State_Delivered
            waiter.event.set()

        # .. the payloads of the pushes are kept for every push of their messages ..
        for cached in claims.payloads:
            self.payload_cache.put(cached.msg_id, cached.data, cached.size, claims.read_epoch)

        # .. and each push greenlet wakes up with its batch.
        for target in claims.push_targets:
            target.state = State_Delivered
            target.event.set()

            sub_event = self.get_sub_event(target.sub_key)
            sub_event.set()

# ################################################################################################################################

    def release(self, claims:'FastPathClaims') -> 'None':
        """ Returns the pulls and the push greenlets that a transaction which did not commit claimed to the state
        of waiting, with nothing handed over. A pull reads its queue again, because the rows of other transactions
        may have committed in the meantime.
        """
        for waiter in claims.pull_waiters:
            if waiter.state == State_Claimed:
                waiter.state = State_Waiting
                waiter.lease = None
                waiter.is_notified = True
                waiter.event.set()

        for target in claims.push_targets:
            if target.state == State_Claimed:
                target.state = State_Waiting
                target.messages = []
                target.event.set()

# ################################################################################################################################
# ################################################################################################################################
