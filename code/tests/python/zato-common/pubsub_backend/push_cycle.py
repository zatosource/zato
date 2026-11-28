# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The cycle of a push subscriber - the commit that acknowledges one batch and claims the next one in one transaction,
# under failures of that commit, conflicts of its publications, pauses, withdrawals and publications that arrive
# between a claim that found nothing and the wait for a publication.

# stdlib
from time import monotonic

# gevent
from gevent import spawn
from gevent.event import Event

# SQLAlchemy
from sqlalchemy import event as sa_event

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, get_event_rows, get_message_rows
from fast_path_common import wait_until
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditEvent
from zato.common.db_env.database import get_database_engine
from zato.common.db_env.outage import logger as outage_logger
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.pubsub.sql.fast_path import State_Waiting
from zato.common.pubsub.sql.publication import build_publication
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.test.expected_records import expected_records
from zato.common.typing_ import cast_
from zato.server.base.parallel.delivery import logger as delivery_logger, PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_, callnone, strlist
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# The topics, the subscriber and the target service of the scenarios
_topic = 'pubsub.backend.test.push-cycle'
_topic_output = 'pubsub.backend.test.push-cycle.output'
_sub_key = 'zpsk.test.push-cycle.1'
_service_name = 'test.push-cycle.target'

# The payloads of the scenarios
_data_first = 'Order ORD-4001 for John Smith'
_data_second = 'Order ORD-4002 for Maria Johnson'
_data_third = 'Order ORD-4003 for Robert Brown'

# The ID of a receipt that a scenario publishes twice, with two different payloads
_receipt_msg_id = 'zpsm.test.push-cycle.receipt'
_data_receipt = 'Receipt of ORD-4001'
_data_receipt_other = 'Receipt of ORD-4002'

# The text by which the statement that claims the next batch of a push subscriber is recognized
_claim_statement_marker = 'claim_claimed'

# How long a message waits between two attempts in the scenarios that retry, in seconds
_retry_sleep_time = 1

# How many retries a message of the scenarios that retry allows
_max_retries = 5

# How long a publication committed between an empty claim and the wait may take to be delivered, in seconds,
# which is shorter than the wait of an idle push greenlet for a publication
_wakeup_max_seconds = 2

# How many messages and how many bytes of payloads the claims of the budget scenarios take
_claim_max_messages = 10
_claim_max_len = 250

# The size of each payload of the budget scenarios, and of the one larger than the whole budget
_budget_message_size = 100
_oversized_message_size = 1000

# The priorities of the budget scenarios
_priority_low = 1
_priority_mid = 5
_priority_high = 9

# ################################################################################################################################
# ################################################################################################################################

class _CommitFailed(Exception):
    """ Raised by the statement that claims the next batch of a push subscriber in a cycle commit failed on purpose.
    """

# ################################################################################################################################
# ################################################################################################################################

class _StubQueueDepth:
    """ Carries the depths of the queues of outgoing connections the way the config manager does.
    """
    def lower(self, sub_key:'str', count:'int') -> 'None':
        pass

# ################################################################################################################################

class _StubConfigManager:
    """ Carries the push subscriptions the way the config manager of the server does.
    """
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}
        self.outgoing_queue_depth = _StubQueueDepth()

# ################################################################################################################################

class _StubServer:
    """ Stands in for the server, of which a delivery reads the push subscriptions alone.
    """
    def __init__(self) -> 'None':
        self.config_manager = _StubConfigManager()

# ################################################################################################################################
# ################################################################################################################################

class _CycleBackend(SQLPubSubBackend):
    """ A backend that records each cycle commit - what it acknowledged and what it claimed - and runs a hook
    after a claim that found nothing.
    """
    cycles: 'anylist'
    on_empty_claim: 'callnone'

    def ack_and_claim(
        self,
        sub_key:'str',
        msg_ids:'strlist',
        publications:'anylist',
        audit_events:'anylist',
        max_messages:'int',
        max_len:'int',
        ) -> 'tuple[anylist, int]':

        out = super().ack_and_claim(sub_key, msg_ids, publications, audit_events, max_messages, max_len)

        messages, _ = out
        claimed:'strlist' = []

        for message in messages:
            claimed.append(message['data'])

        self.cycles.append((list(msg_ids), claimed))

        return out

    def claim(self, sub_key:'str', max_messages:'int', max_len:'int') -> 'tuple[anylist, int]':

        out = super().claim(sub_key, max_messages, max_len)
        messages, _ = out

        if not messages and self.on_empty_claim:
            on_empty_claim = self.on_empty_claim
            self.on_empty_claim = None
            on_empty_claim()

        return out

# ################################################################################################################################

class _CycleDelivery(PushDelivery):
    """ A delivery whose target service records the payload and the attempt of each invocation, runs a hook on the first
    invocation of a given payload and fails the given number of invocations.
    """
    invoked: 'anylist'
    hooks: 'anydict'
    fail_count: 'int'

    def _deliver_to_service(self, message:'anydict', sub_config:'anydict') -> 'None':

        data = message['data']
        self.invoked.append((data, message['delivery_attempt']))

        if hook := self.hooks.pop(data, None):
            hook()

        if self.fail_count > 0:
            self.fail_count -= 1
            raise Exception('Simulated delivery failure')

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> '_CycleBackend':
    """ Returns a backend with one push subscriber of the topic of the scenarios, starting from empty tables.
    """
    delete_all_rows()
    delete_audit_rows()

    out = _CycleBackend(audit_log=new_test_audit_log())
    out.cycles = []
    out.on_empty_claim = None

    out.subscribe(_sub_key, _topic)

    return out

# ################################################################################################################################

def _new_delivery(backend:'SQLPubSubBackend') -> '_CycleDelivery':
    """ Returns a delivery of the subscriber of the scenarios to the target service.
    """
    server = _StubServer()
    server.config_manager._push_subs[_sub_key] = [{
        'topic_name': _topic,
        'push_type': PubSub.Push_Type.Service,
        'push_service_name': _service_name,
    }]

    out = _CycleDelivery(cast_('ParallelServer', server), backend)
    out.invoked = []
    out.hooks = {}
    out.fail_count = 0

    return out

# ################################################################################################################################

def _get_attempts(topic_name:'str', sub_key:'str') -> 'anydict':
    """ Returns the attempt of each delivery row of a subscriber, by the payload of its message.
    """
    data_by_message_id:'anydict' = {}

    for row in get_message_rows(topic_name):
        data_by_message_id[row.id] = row.payload

    out:'anydict' = {}

    for row in get_delivery_rows(sub_key):
        data = data_by_message_id[row.message_id]
        out[data] = row.attempt

    return out

# ################################################################################################################################

def _wait_until_idle(backend:'SQLPubSubBackend') -> 'None':
    """ Waits until the delivery greenlet of the subscriber waits for a publication.
    """
    def _is_idle() -> 'bool':
        if target := backend.fast_path._push_targets.get(_sub_key):
            out = target.state == State_Waiting
        else:
            out = False

        return out

    wait_until(_is_idle, 'the delivery greenlet waits for a publication')

# ################################################################################################################################

def _wait_until_concluded(delivery:'_CycleDelivery', count:'int') -> 'None':
    """ Waits until the target service was invoked the given number of times and the queue of the subscriber is empty.
    """
    def _is_concluded() -> 'bool':
        if len(delivery.invoked) == count:
            out = get_delivery_rows(_sub_key) == []
        else:
            out = False

        return out

    wait_until(_is_concluded, f'{count} invocations are concluded')

# ################################################################################################################################

def _new_blocking_hook(blocked:'Event', release:'Event', on_blocked:'callnone'=None) -> 'callable_':
    """ Returns a hook that runs on_blocked, reports that the invocation is blocked and waits until it is released.
    """
    def _hook() -> 'None':
        if on_blocked:
            on_blocked()
        blocked.set()
        _ = release.wait()

    return _hook

# ################################################################################################################################
# ################################################################################################################################

def _run_failed_commit() -> 'None':
    """ A cycle commit that fails after its claim ran claims nothing and acknowledges nothing, and the next claim
    claims the same batch again, with the next attempt, before the message published behind it.
    """
    backend = _new_backend()
    delivery = _new_delivery(backend)

    # The claim of the next cycle commit fails once it is armed ..
    fail_state = {'is_armed': False}

    def _on_execute(
        conn:'any_',
        cursor:'any_',
        statement:'str',
        parameters:'any_',
        context:'any_',
        executemany:'bool',
        ) -> 'None':
        if fail_state['is_armed'] and _claim_statement_marker in statement:
            fail_state['is_armed'] = False
            raise _CommitFailed('Cycle commit failed on purpose')

    def _arm() -> 'None':
        fail_state['is_armed'] = True

    engine = get_database_engine()
    sa_event.listen(engine, 'after_cursor_execute', _on_execute)

    # .. the batch of the first two messages is claimed at startup ..
    _ = backend.publish(_topic, _data_first, retry_sleep_time=_retry_sleep_time)
    _ = backend.publish(_topic, _data_second, retry_sleep_time=_retry_sleep_time)

    # .. and the commit that concludes it fails once the second one is delivered, after a third message was published.
    blocked = Event()
    release = Event()
    delivery.hooks[_data_second] = _new_blocking_hook(blocked, release, _arm)

    try:
        with expected_records(delivery_logger.name), expected_records(outage_logger.name):

            delivery.start_sub_key(_sub_key)
            _ = blocked.wait()

            _ = backend.publish(_topic, _data_third, retry_sleep_time=_retry_sleep_time)
            release.set()

            _wait_until_concluded(delivery, 5)

    finally:
        delivery.stop()
        sa_event.remove(engine, 'after_cursor_execute', _on_execute)

    # The batch was delivered again first, with its second attempt, and the message behind it with its first one
    expected = [
        (_data_first, 1),
        (_data_second, 1),
        (_data_first, 2),
        (_data_second, 2),
        (_data_third, 1),
    ]

    assert delivery.invoked == expected, delivery.invoked

# ################################################################################################################################

def _run_strict_conflict() -> 'None':
    """ A cycle commit whose publication stands for a different message fails as a whole - it acknowledges nothing
    and claims nothing, and the commit that follows claims the next message.
    """
    backend = _new_backend()

    _ = backend.publish(_topic_output, _data_receipt, msg_id=_receipt_msg_id)
    _ = backend.publish(_topic, _data_first)
    _ = backend.publish(_topic, _data_second)

    # The first message is claimed alone ..
    messages, _ = backend.claim(_sub_key, 1, _claim_max_len)
    [message] = messages

    assert message['data'] == _data_first, message

    # .. and its receipt reuses the ID of another message ..
    built = build_publication(backend, _topic_output, _data_receipt_other, msg_id=_receipt_msg_id)

    try:
        _ = backend.ack_and_claim(_sub_key, [message['msg_id']], [built.pending], [], _claim_max_messages, _claim_max_len)
    except PubSubDuplicateMsgID:
        pass
    else:
        raise Exception('Expected PubSubDuplicateMsgID')

    # .. so neither the acknowledgement nor the claim was written ..
    attempts = _get_attempts(_topic, _sub_key)
    assert attempts == {_data_first: 1, _data_second: 0}, attempts

    # .. while the commit without the receipt acknowledges the first message and claims the second one.
    messages, _ = backend.ack_and_claim(_sub_key, [message['msg_id']], [], [], _claim_max_messages, _claim_max_len)
    [message] = messages

    assert message['data'] == _data_second, message
    assert message['delivery_attempt'] == 1, message

    attempts = _get_attempts(_topic, _sub_key)
    assert attempts == {_data_second: 1}, attempts

# ################################################################################################################################

def _run_publication_after_empty_claim() -> 'None':
    """ A publication committed after a claim that found nothing and before the greenlet waits as a target of the fast path
    ends the wait at once, and the next claim claims it.
    """
    backend = _new_backend()
    delivery = _new_delivery(backend)

    published_at:'anylist' = []

    def _publish() -> 'None':
        published_at.append(monotonic())
        _ = backend.publish(_topic, _data_first)

    backend.on_empty_claim = _publish

    try:
        delivery.start_sub_key(_sub_key)
        _wait_until_concluded(delivery, 1)
        delivered_at = monotonic()

    finally:
        delivery.stop()

    elapsed = delivered_at - published_at[0]

    assert elapsed < _wakeup_max_seconds, elapsed
    assert delivery.invoked == [(_data_first, 1)], delivery.invoked

# ################################################################################################################################

def _run_paused_between_cycles() -> 'None':
    """ A subscriber paused while it delivers a batch commits what the batch concluded without a claim,
    so the message published behind it keeps its attempt until the subscriber resumes.
    """
    backend = _new_backend()
    delivery = _new_delivery(backend)

    blocked = Event()
    release = Event()
    delivery.hooks[_data_first] = _new_blocking_hook(blocked, release)

    try:
        delivery.start_sub_key(_sub_key)
        _wait_until_idle(backend)

        # The first message is handed over and blocks in its invocation ..
        _ = backend.publish(_topic, _data_first)
        _ = blocked.wait()

        # .. the second one waits behind it ..
        _ = backend.publish(_topic, _data_second)
        cycle_count = len(backend.cycles)

        # .. and the subscriber is paused before the first one completes ..
        pause = spawn(delivery.pause_sub_key, _sub_key)
        wait_until(lambda: _sub_key in delivery._paused, 'the subscriber is paused')

        release.set()
        _ = pause.get()

        # .. so the first one was acknowledged without a claim of the second one ..
        assert len(backend.cycles) == cycle_count, backend.cycles

        attempts = _get_attempts(_topic, _sub_key)
        assert attempts == {_data_second: 0}, attempts

        # .. which is delivered with its first attempt once the subscriber resumes.
        delivery.resume_sub_key(_sub_key)
        _wait_until_concluded(delivery, 2)

    finally:
        delivery.stop()

    assert delivery.invoked == [(_data_first, 1), (_data_second, 1)], delivery.invoked

# ################################################################################################################################

def _run_withdrawn_after_claim() -> 'None':
    """ A message withdrawn from the queue after its batch was claimed is not attempted again and is not acknowledged
    as delivered, while the message behind it is delivered and acknowledged.
    """
    backend = _new_backend()
    delivery = _new_delivery(backend)

    withdrawn_msg_id = backend.publish(_topic, _data_first, retry_sleep_time=_retry_sleep_time,
        max_retries=_max_retries).msg_id

    delivered_msg_id = backend.publish(_topic, _data_second).msg_id

    # The first attempt of the first message withdraws it and fails ..
    def _withdraw() -> 'None':
        _ = backend.delete_message(_sub_key, _topic, withdrawn_msg_id)

    delivery.hooks[_data_first] = _withdraw
    delivery.fail_count = 1

    try:
        delivery.start_sub_key(_sub_key)
        _wait_until_concluded(delivery, 2)

    finally:
        delivery.stop()

    # .. so the next attempt finds it withdrawn, and only the second message is delivered.
    assert delivery.invoked == [(_data_first, 1), (_data_second, 1)], delivery.invoked

    delivered_msg_ids:'strlist' = []

    for row in get_event_rows(_topic, AuditEvent.Delivered):
        delivered_msg_ids.append(row['msg_id'])

    assert delivered_msg_ids == [delivered_msg_id], delivered_msg_ids

# ################################################################################################################################

def _run_claim_budget() -> 'None':
    """ A claim takes the messages in the order of the queue - by priority, then by the order of publication -
    within the budget of its payloads, and a message larger than the whole budget is claimed alone, after
    the messages ahead of it.
    """
    backend = _new_backend()

    _ = backend.publish(_topic, 'a' * _budget_message_size, priority=_priority_mid)
    _ = backend.publish(_topic, 'b' * _budget_message_size, priority=_priority_high)
    _ = backend.publish(_topic, 'c' * _budget_message_size, priority=_priority_mid)
    _ = backend.publish(_topic, 'd' * _budget_message_size, priority=_priority_low)

    # The first claim takes the two messages of the highest priorities that fit in the budget ..
    messages, _ = backend.claim(_sub_key, _claim_max_messages, _claim_max_len)
    claimed = _get_claimed(messages)

    assert claimed == ['b', 'a'], claimed

    # .. the commit that acknowledges them claims the next two ..
    messages, _ = backend.ack_and_claim(_sub_key, _get_msg_ids(messages), [], [], _claim_max_messages, _claim_max_len)
    claimed = _get_claimed(messages)

    assert claimed == ['c', 'd'], claimed

    # .. a message larger than the budget is claimed alone ..
    _ = backend.publish(_topic, 'e' * _oversized_message_size, priority=_priority_mid)
    _ = backend.publish(_topic, 'f' * _budget_message_size, priority=_priority_low)

    messages, _ = backend.ack_and_claim(_sub_key, _get_msg_ids(messages), [], [], _claim_max_messages, _claim_max_len)
    claimed = _get_claimed(messages)

    assert claimed == ['e'], claimed

    # .. and the count of messages limits the claim as well.
    messages, _ = backend.ack_and_claim(_sub_key, _get_msg_ids(messages), [], [], 1, _claim_max_len)
    claimed = _get_claimed(messages)

    assert claimed == ['f'], claimed

    for message in messages:
        assert message['delivery_attempt'] == 1, message

# ################################################################################################################################

def _get_claimed(messages:'anylist') -> 'strlist':
    """ Returns the first character of the payload of each claimed message, in the order of the claim.
    """
    out:'strlist' = []

    for message in messages:
        out.append(message['data'][0])

    return out

# ################################################################################################################################

def _get_msg_ids(messages:'anylist') -> 'strlist':
    """ Returns the IDs of the claimed messages.
    """
    out:'strlist' = []

    for message in messages:
        out.append(message['msg_id'])

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_push_cycle_scenario() -> 'None':
    """ The cycle commit of a push subscriber, which acknowledges one batch and claims the next one in one transaction.
    """
    _run_failed_commit()
    _run_strict_conflict()
    _run_publication_after_empty_claim()
    _run_paused_between_cycles()
    _run_withdrawn_after_claim()
    _run_claim_budget()

# ################################################################################################################################
# ################################################################################################################################
