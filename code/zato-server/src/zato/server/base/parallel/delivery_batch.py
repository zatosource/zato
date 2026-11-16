# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from importlib import import_module
from logging import getLogger

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.audit_log.api import AuditEvent, AuditLog
from zato.common.audit_log.service import Push_Delivery_Key
from zato.common.pubsub.delivery_scope import close_delivery_scope, get_delivery_scope, open_delivery_scope
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent.lock import BoundedSemaphore
    from zato.common.pubsub.delivery_scope import DeliveryScope
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import any_, anydict, anylist, callable_, intlist, strlist, strset
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The key of a message whose first attempt was recorded with the other messages of its batch
Attempt_Recorded_Key = 'zato.pubsub.attempt_recorded'

# ################################################################################################################################
# ################################################################################################################################

def deliver_atomic_batch(
    backend:'SQLPubSubBackend',
    database_slots:'BoundedSemaphore',
    paused:'strset',
    deliver_one:'callable_',
    messages:'anylist',
    config_by_topic:'anydict',
    sub_key:'str',
    read_epoch:'int',
) -> 'None':
    """ Delivers a batch of messages to a push subscriber as one consume-process-produce transaction. The first attempt
    of each message is recorded in one transaction before the first message is sent, and the acknowledgement
    of the concluded messages commits in one transaction with the publications that the subscriber services made
    while processing them. A batch that does not reach its commit leaves no publication behind and goes out again.
    """
    msg_ids:'strlist' = []
    sequence_ids:'intlist' = []

    # One transaction records the first attempt of every message of the batch ..
    with database_slots:
        pending_delivery_ids = backend.record_attempts(messages)

    # .. what the subscriber services produce from now on commits with the acknowledgement ..
    scope = open_delivery_scope()

    try:
        for message in messages:

            # .. a queue asked to pause stops between two of its messages and keeps the rest of the batch ..
            if sub_key in paused:
                break

            # .. a message that left the queue in the meantime has nothing left to deliver ..
            if message['delivery_id'] not in pending_delivery_ids:
                logger.info('Message left the queue before delivery, sub_key `%s`, msg_id `%s`', sub_key, message['msg_id'])

            # .. and any other message is delivered, while a message that was not concluded stops the batch.
            else:
                message[Attempt_Recorded_Key] = True
                sub_config = config_by_topic[message['topic_name']]

                if not deliver_one(message, sub_config, sub_key, read_epoch):
                    break

            msg_ids.append(message['msg_id'])
            sequence_ids.append(message['sequence_id'])

    finally:
        close_delivery_scope()

    _commit_batch(backend, scope, sub_key, msg_ids, sequence_ids)

# ################################################################################################################################

def _commit_batch(
    backend:'SQLPubSubBackend',
    scope:'DeliveryScope',
    sub_key:'str',
    msg_ids:'strlist',
    sequence_ids:'intlist',
) -> 'None':
    """ Commits what a delivery batch produced. The outcome of each delivery is recorded before the acknowledgement,
    as it is for a single message, and a publication is recorded only after it was committed.
    """
    published_events:'anylist' = []
    other_events:'anylist' = []

    for pending in scope.audit_events:
        if pending.values['event_type'] == AuditEvent.Published:
            published_events.append(pending)
        else:
            other_events.append(pending)

    # The audit log collects events only if the backend has one, which is the case outside of unit tests ..
    audit_log = cast_(AuditLog, backend.audit_log)

    if other_events:
        audit_log.write_pending(other_events)

    # .. the acknowledgement and the publications commit together ..
    if msg_ids:
        backend.ack_with_publications(sub_key, msg_ids, sequence_ids, scope.publications)

    # .. and only then are the publications recorded.
    if published_events:
        audit_log.write_pending(published_events)

# ################################################################################################################################

def deliver_to_service(server:'ParallelServer', message:'anydict', sub_config:'anydict') -> 'None':
    """ Deliver a raw message by invoking a Zato service.
    """
    service_name = sub_config['push_service_name']
    data_raw = message['data']

    # The invocation is recorded in the audit log by the Delivered event of the message alone ..
    request_ctx = {Push_Delivery_Key: True}

    # .. if a data_class was stored, reconstruct the original Model ..
    if data_class_name := message['data_class']:
        data = json.loads(data_raw)
        module_path, _, class_name = data_class_name.rpartition('.')
        module = import_module(module_path)
        model_class = getattr(module, class_name)
        payload = model_class.from_dict(data)
        _invoke_subscriber(server, service_name, payload, request_ctx=request_ctx)

    # .. otherwise, the stored text is handed over under the JSON data format, so a dict that was
    # published is parsed back into the subscriber's input and text that is not JSON stays text.
    else:
        _invoke_subscriber(server, service_name, data_raw, data_format=DATA_FORMAT.JSON, request_ctx=request_ctx)

# ################################################################################################################################

def _invoke_subscriber(server:'ParallelServer', service_name:'str', payload:'any_', **kwargs:'any_') -> 'None':
    """ Invokes the service of a push subscriber. An attempt that fails leaves none of its publications behind,
    since only the attempt that concludes a message commits with the batch.
    """
    scope = get_delivery_scope()

    # Outside of an atomic batch, the publications of the service commit on their own ..
    if not scope:
        server.invoke(service_name, payload, **kwargs)
        return

    # .. whereas inside of one, the publications of a failed attempt are discarded along with their audit events.
    publication_count = len(scope.publications)
    event_count = len(scope.audit_events)

    try:
        server.invoke(service_name, payload, **kwargs)

    except Exception:
        _discard_attempt(scope, publication_count, event_count)
        raise

# ################################################################################################################################

def _discard_attempt(scope:'DeliveryScope', publication_count:'int', event_count:'int') -> 'None':
    """ Removes from a scope the publications of a failed attempt and the events that recorded them.
    """
    del scope.publications[publication_count:]

    kept_events:'anylist' = []

    for pending in scope.audit_events[event_count:]:
        if pending.values['event_type'] != AuditEvent.Published:
            kept_events.append(pending)

    scope.audit_events[event_count:] = kept_events

# ################################################################################################################################
# ################################################################################################################################
