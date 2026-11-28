# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import contextmanager

# pytest
import pytest

# prometheus_client
from prometheus_client import REGISTRY

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from common import env_value, get_delivery_rows
from exactly_once.harness import build, count_deliveries, count_messages, First_Output_Sub_Key, First_Output_Topic, \
    get_built_msg_id, get_msg_ids, Input_Sub_Key, new_backend, publish_input, Second_Output_Sub_Key, Second_Output_Topic
from zato.common.pubsub.delivery_scope import close_delivery_scope, open_delivery_scope
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.test.expected_records import expected_records
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import anylist, strlist

    recorder_iter = Iterator['PublishedRecorder']
    strtuple      = tuple[str, ...]

# ################################################################################################################################
# ################################################################################################################################

# The logger of the publication module and the beginning of the entry that it logs once a publication is committed
_publication_logger_name = 'zato.common.pubsub.sql.publication'
_published_prefix        = 'Published message -> '

# The metric that counts the committed publications of each topic
_published_metric = 'zato_pubsub_messages_published_total'

# The logger that reports a failed commit of the commit writer, and the fragment of the failure that the rollback
# scenarios cause on purpose with a publication whose size is NULL
_outage_logger_name = 'zato.common.db_env.outage'
_not_null_fragments = ('null value in column "data_size"',)

# How many messages and how many bytes of payloads the claims of the input subscriber may take
_claim_max_messages = 10
_claim_max_len      = 1024 * 1024

# The message IDs and the payloads of the publications of the batches of the scope scenarios
_repeated_msg_id = 'exactly-once.backend.scope.repeated'
_stored_msg_id   = 'exactly-once.backend.scope.stored'
_removed_msg_id  = 'exactly-once.backend.scope.removed'
_batch_msg_id    = 'exactly-once.backend.scope.batch'

_stored_payload    = 'Order ORD-0042 for Maria Johnson'
_removed_payload   = 'Invoice INV-0042 for John Smith'
_batch_payload     = 'Receipt RCP-0042 for Maria Johnson'
_different_payload = 'Shipment SHP-1203 for Jane Doe'

# How many fully delivered messages each topic retains while the over-cap sweep removes a message
_no_delivered_messages = '0'

# ################################################################################################################################
# ################################################################################################################################

class PublishedRecorder(logging.Handler):
    """ Keeps the message ID of each entry that the publication module logs once a publication is committed.
    """

    def __init__(self) -> 'None':
        super().__init__()
        self.msg_ids:'strlist' = []

# ################################################################################################################################

    def emit(self, record:'logging.LogRecord') -> 'None':
        message = record.getMessage()

        if message.startswith(_published_prefix):
            args = cast_('strtuple', record.args)
            msg_id = args[0]
            self.msg_ids.append(msg_id)

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _record_published() -> 'recorder_iter':
    """ Records the entries that the publication module logs once a publication is committed, for the duration of a block.
    """
    publication_logger = logging.getLogger(_publication_logger_name)
    level = publication_logger.level

    out = PublishedRecorder()

    publication_logger.addHandler(out)
    publication_logger.setLevel(logging.INFO)

    try:
        yield out
    finally:
        publication_logger.removeHandler(out)
        publication_logger.setLevel(level)

# ################################################################################################################################

def _get_published_count(topic_name:'str') -> 'float':
    """ Returns how many publications to a topic the publish counter of this process counted.
    """
    labels = {'topic_name': topic_name}
    out = REGISTRY.get_sample_value(_published_metric, labels)

    # A topic that nothing was published to has no sample yet.
    if out is None:
        out = 0.0

    return out

# ################################################################################################################################
# ################################################################################################################################

def _fetch_batch(backend:'SQLPubSubBackend', count:'int') -> 'strlist':
    """ Publishes the given number of input messages and returns the message IDs of the batch
    that a push delivery of the input subscriber claims.
    """
    for index in range(count):
        data = f'input-{index}'
        _ = publish_input(backend, data)

    messages, _ = backend.claim(Input_Sub_Key, _claim_max_messages, _claim_max_len)
    message_count = len(messages)

    assert message_count == count

    out:'strlist' = []

    for message in messages:
        out.append(message['msg_id'])

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_atomic_rollback_scenario() -> 'None':
    """ A push batch whose transaction fails on its second publication commits neither publication nor its acknowledgement,
    and the same batch committed again afterwards stores each publication once and acknowledges both messages.
    """
    backend = new_backend()
    msg_ids = _fetch_batch(backend, 2)

    first = build(backend, First_Output_Topic, 'output-first')
    second = build(backend, Second_Output_Topic, 'output-second')

    second_values = second.pending.message_values

    # A column that may not be NULL fails the insert of the second publication ..
    data_size = second_values['data_size']
    second_values['data_size'] = None

    publications:'anylist' = [first.pending, second.pending]

    with pytest.raises(DBAPIError), expected_records(_outage_logger_name, _not_null_fragments):
        backend.ack_with_publications(Input_Sub_Key, msg_ids, publications, [])

    # .. so neither publication is stored ..
    assert count_messages(First_Output_Topic) == 0
    assert count_messages(Second_Output_Topic) == 0

    # .. and both messages remain in the queue and are read again.
    pending = backend.fetch_pending(Input_Sub_Key)
    pending_count = len(pending)

    assert count_deliveries(Input_Sub_Key) == 2
    assert pending_count == 2

    # The same items committed again find nothing of the failed transaction ..
    second_values['data_size'] = data_size
    backend.ack_with_publications(Input_Sub_Key, msg_ids, publications, [])

    # .. each publication is stored once ..
    assert count_messages(First_Output_Topic) == 1
    assert count_messages(Second_Output_Topic) == 1
    assert count_deliveries(First_Output_Sub_Key) == 1
    assert count_deliveries(Second_Output_Sub_Key) == 1

    # .. and both messages are acknowledged.
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################

def _get_input_attempts() -> 'anylist':
    """ Returns the attempt of each delivery of the input subscriber, in the order of the deliveries.
    """
    out:'anylist' = []

    for row in get_delivery_rows(Input_Sub_Key):
        out.append(row.attempt)

    return out

# ################################################################################################################################

def run_cycle_rollback_scenario() -> 'None':
    """ A cycle commit whose transaction fails on a publication acknowledges nothing, stores no publication and claims
    nothing, so the attempts of the batch remain as its own claim recorded them, and the next claim takes the same batch
    with the next attempt before any message published since.
    """
    backend = new_backend()
    msg_ids = _fetch_batch(backend, 2)

    # The claim of the batch recorded the first attempt of each message ..
    assert _get_input_attempts() == [1, 1]

    # .. and a message published after the claim waits for the next one.
    _ = publish_input(backend, 'input-later')

    first = build(backend, First_Output_Topic, 'output-first')
    first_values = first.pending.message_values

    # A column that may not be NULL fails the insert of the publication ..
    data_size = first_values['data_size']
    first_values['data_size'] = None

    publications:'anylist' = [first.pending]

    with pytest.raises(DBAPIError), expected_records(_outage_logger_name, _not_null_fragments):
        _ = backend.ack_and_claim(Input_Sub_Key, msg_ids, publications, [], _claim_max_messages, _claim_max_len)

    # .. so the publication is not stored, the batch is not acknowledged ..
    assert count_messages(First_Output_Topic) == 0
    assert count_deliveries(Input_Sub_Key) == 3

    # .. and the failed commit claimed nothing, the later message having no attempt yet.
    assert _get_input_attempts() == [1, 1, 0]

    # The next claim takes the batch again, with the next attempt, and the later message after it ..
    messages, _ = backend.claim(Input_Sub_Key, _claim_max_messages, _claim_max_len)
    claimed_ids:'strlist' = []

    for message in messages:
        claimed_ids.append(message['msg_id'])

    assert claimed_ids[:2] == msg_ids, claimed_ids
    assert _get_input_attempts() == [2, 2, 1]

    # .. and a commit that succeeds acknowledges the batch and stores the publication once.
    first_values['data_size'] = data_size

    _ = backend.ack_and_claim(Input_Sub_Key, claimed_ids, publications, [], _claim_max_messages, _claim_max_len)

    assert count_messages(First_Output_Topic) == 1
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################

def run_repeat_in_batch_scenario() -> 'None':
    """ A publication of a push batch that repeats an existing message with the same content creates no second message,
    while the acknowledgement and the other publication of the batch are committed.
    """
    backend = new_backend()
    msg_ids = _fetch_batch(backend, 1)

    repeated_msg_id = 'exactly-once.backend.repeated'
    _ = backend.publish(First_Output_Topic, 'output-first', msg_id=repeated_msg_id)

    repeated = build(backend, First_Output_Topic, 'output-first', msg_id=repeated_msg_id)
    other = build(backend, Second_Output_Topic, 'output-second')

    publications:'anylist' = [repeated.pending, other.pending]
    backend.ack_with_publications(Input_Sub_Key, msg_ids, publications, [])

    # The repetition is recognized ..
    assert repeated.pending.is_repeat
    assert get_msg_ids(First_Output_Topic) == [repeated_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 1

    # .. while the rest of the batch is committed.
    assert count_messages(Second_Output_Topic) == 1
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################

def run_batch_committed_twice_scenario() -> 'None':
    """ A push batch that is committed a second time with publications of its own, which is what a delivery that started
    before the first commit produces, is rejected, and one without publications commits nothing.
    """
    backend = new_backend()
    msg_ids = _fetch_batch(backend, 2)

    first = build(backend, First_Output_Topic, 'output-first')
    first_msg_id = get_built_msg_id(first)

    first_publications:'anylist' = [first.pending]
    backend.ack_with_publications(Input_Sub_Key, msg_ids, first_publications, [])

    # The second delivery of the same batch published again under new message IDs ..
    second = build(backend, First_Output_Topic, 'output-second')
    second_publications:'anylist' = [second.pending]

    with pytest.raises(PubSubAckConflict):
        backend.ack_with_publications(Input_Sub_Key, msg_ids, second_publications, [])

    # .. which are not stored ..
    assert get_msg_ids(First_Output_Topic) == [first_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 1

    # .. and a second delivery that published nothing concludes without an error.
    backend.ack_with_publications(Input_Sub_Key, msg_ids, [], [])

    assert count_messages(First_Output_Topic) == 1
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################

def run_announced_after_commit_scenario() -> 'None':
    """ A publication of a subscriber service that processes a push batch is logged and counted only once the batch
    is acknowledged, and a publication of the batch that repeats an existing message is neither logged nor counted.
    """
    backend = new_backend()
    msg_ids = _fetch_batch(backend, 1)

    _ = backend.publish(Second_Output_Topic, _batch_payload, msg_id=_repeated_msg_id)

    first_count = _get_published_count(First_Output_Topic)
    second_count = _get_published_count(Second_Output_Topic)

    with _record_published() as recorder:

        # The service publishes a new message and repeats an existing one ..
        scope = open_delivery_scope()

        try:
            first = backend.publish(First_Output_Topic, 'output-first')
            repeated = backend.publish(Second_Output_Topic, _batch_payload, msg_id=_repeated_msg_id)
        finally:
            close_delivery_scope()

        # .. neither of which is logged, counted or stored before the batch is acknowledged ..
        assert recorder.msg_ids == []
        assert _get_published_count(First_Output_Topic) == first_count
        assert count_messages(First_Output_Topic) == 0

        backend.ack_with_publications(Input_Sub_Key, msg_ids, scope.publications, scope.audit_events)

    # .. after which the new message is logged, counted and stored once ..
    assert recorder.msg_ids == [first.msg_id]
    assert _get_published_count(First_Output_Topic) == first_count + 1
    assert get_msg_ids(First_Output_Topic) == [first.msg_id]

    # .. while the repeat is neither logged nor counted, nor stored again.
    assert repeated.msg_id == _repeated_msg_id
    assert _get_published_count(Second_Output_Topic) == second_count
    assert get_msg_ids(Second_Output_Topic) == [_repeated_msg_id]
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################

def _remove_within_window(backend:'SQLPubSubBackend') -> 'None':
    """ Publishes a message of the second output topic, delivers it fully and lets the over-cap sweep remove it,
    which leaves its dedup record behind.
    """
    _ = backend.publish(Second_Output_Topic, _removed_payload, msg_id=_removed_msg_id)

    removed_count = backend.ack_pulled(Second_Output_Sub_Key, [_removed_msg_id])
    assert removed_count == 1

    with env_value(ModuleCtx.Env_Delivered_Max_Messages, _no_delivered_messages):
        counts = PubSubCleanup().sweep_once()

    assert counts['over_cap'] == 1, counts
    assert counts['dedup'] == 0, counts
    assert count_messages(Second_Output_Topic) == 0

# ################################################################################################################################

def run_conflicting_id_in_scope_scenario() -> 'None':
    """ A subscriber service that processes a push batch receives PubSubDuplicateMsgID from publish for a message ID
    that stands for different content - a stored message, a message removed within the dedup window or a publication
    made earlier in the same batch - and the batch keeps none of these publications, whereas the same content
    under a message ID that the batch published already is accepted.
    """
    backend = new_backend()

    _remove_within_window(backend)
    _ = backend.publish(First_Output_Topic, _stored_payload, msg_id=_stored_msg_id)

    msg_ids = _fetch_batch(backend, 1)

    # The service publishes under a message ID of its own ..
    scope = open_delivery_scope()

    try:
        _ = backend.publish(First_Output_Topic, _batch_payload, msg_id=_batch_msg_id)

        # .. it is refused the ID of a stored message with different content ..
        with pytest.raises(PubSubDuplicateMsgID):
            _ = backend.publish(First_Output_Topic, _batch_payload, msg_id=_stored_msg_id)

        # .. the ID of a removed message within the dedup window with different content ..
        with pytest.raises(PubSubDuplicateMsgID):
            _ = backend.publish(Second_Output_Topic, _different_payload, msg_id=_removed_msg_id)

        # .. and its own ID with different content ..
        with pytest.raises(PubSubDuplicateMsgID):
            _ = backend.publish(First_Output_Topic, _different_payload, msg_id=_batch_msg_id)

        # .. whereas its own ID with the same content is accepted ..
        _ = backend.publish(First_Output_Topic, _batch_payload, msg_id=_batch_msg_id)

    finally:
        close_delivery_scope()

    publication_count = len(scope.publications)
    assert publication_count == 2

    backend.ack_with_publications(Input_Sub_Key, msg_ids, scope.publications, scope.audit_events)

    # .. and the batch stores its own message once, next to the stored one, with nothing under the removed ID.
    assert get_msg_ids(First_Output_Topic) == [_stored_msg_id, _batch_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 2
    assert count_messages(Second_Output_Topic) == 0
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################
# ################################################################################################################################
