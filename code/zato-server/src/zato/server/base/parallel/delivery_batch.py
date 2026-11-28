# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from functools import partial
from importlib import import_module
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import GreenletExit

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.audit_log.service import Push_Delivery_Key
from zato.common.db_env.errors import is_transient
from zato.common.pubsub.delivery_scope import close_delivery_scope, get_delivery_scope, open_delivery_scope
from zato.common.pubsub.sql.fast_path import Attempt_Recorded_Key
from zato.common.pubsub.sql.replaced import PubSubReplaced

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent.lock import BoundedSemaphore
    from zato.common.pubsub.delivery_scope import DeliveryScope
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import any_, anydict, anylist, callable_, intset, strset
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BatchCommitFailed(Exception):
    """ Raised when what a delivery batch concluded could not be committed before a wait of a retry round.
    """

    def __init__(self, error:'Exception') -> 'None':
        super().__init__(str(error))
        self.error = error

# ################################################################################################################################
# ################################################################################################################################

def _are_attempts_recorded(messages:'anylist') -> 'bool':
    """ Whether the first attempt of every message of a batch was recorded before the batch reached its delivery loop.
    """
    for message in messages:
        if Attempt_Recorded_Key not in message:
            return False

    return True

# ################################################################################################################################

def _get_delivery_ids(messages:'anylist') -> 'intset':
    """ Returns the IDs of the delivery rows of the messages of a batch.
    """
    out:'intset' = set()

    for message in messages:
        out.add(message['delivery_id'])

    return out

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
    while processing them. The messages concluded so far also commit before each wait of a retry round
    and when the delivery is stopped. A batch that does not reach its commit leaves no publication behind
    and goes out again.
    The first attempts of a batch that a publication handed over were recorded in the transaction of the publication.
    """
    # One transaction records the first attempt of every message of the batch, unless the publication
    # that handed the batch over recorded them already ..
    if _are_attempts_recorded(messages):
        pending_delivery_ids = _get_delivery_ids(messages)
    else:
        with database_slots:
            pending_delivery_ids = backend.record_attempts(messages)

    # .. what the subscriber services produce from now on commits with the acknowledgement ..
    scope = open_delivery_scope()

    # .. which is also what each wait of a retry round commits first ..
    before_wait = partial(_commit_before_wait, backend, scope, sub_key)

    try:
        for message in messages:

            # .. a queue asked to pause stops between two of its messages and keeps the rest of the batch ..
            if sub_key in paused:
                break

            # .. a message that left the queue in the meantime has no delivery row left to acknowledge ..
            if message['delivery_id'] not in pending_delivery_ids:
                logger.info('Message left the queue before delivery, sub_key `%s`, msg_id `%s`', sub_key, message['msg_id'])

            # .. and any other message is delivered, while a message that was not concluded stops the batch.
            else:
                message[Attempt_Recorded_Key] = True
                sub_config = config_by_topic[message['topic_name']]

                if not deliver_one(message, sub_config, sub_key, read_epoch, before_wait):
                    break

                scope.msg_ids.append(message['msg_id'])

    # .. a commit that failed before a wait is handled as a failed commit of the batch ..
    except BatchCommitFailed as e:
        raise e.error from e

    # .. a delivery that is stopped commits what it concluded before it ends ..
    except GreenletExit:
        _commit_on_exit(backend, scope, sub_key)
        raise

    finally:
        close_delivery_scope()

    # .. and the rest of the batch commits once the batch is over.
    commit_delivery_scope(backend, scope, sub_key)

# ################################################################################################################################

def commit_delivery_scope(backend:'SQLPubSubBackend', scope:'DeliveryScope', sub_key:'str') -> 'None':
    """ Commits what a delivery batch produced so far. The audit events of the deliveries commit with the acknowledgement
    and the publications, each publication with the audit event that records it.
    """
    msg_ids = scope.msg_ids
    publications = scope.publications
    audit_events = scope.audit_events

    # What is committed leaves the scope before the commit, so that nothing is committed twice ..
    scope.msg_ids = []
    scope.publications = []
    scope.audit_events = []

    # .. the acknowledgement, the publications and the audit events commit together ..
    if msg_ids:
        backend.ack_with_publications(sub_key, msg_ids, publications, audit_events)

    # .. while a batch that concluded no message has only its audit events to commit.
    elif audit_events:
        backend.audit_log.write_pending(audit_events)

# ################################################################################################################################

def _commit_before_wait(backend:'SQLPubSubBackend', scope:'DeliveryScope', sub_key:'str') -> 'None':
    """ Commits what a delivery batch concluded before a wait of a retry round, raising BatchCommitFailed
    if the commit fails, so that the failure is never taken for a failed delivery attempt.
    """
    try:
        commit_delivery_scope(backend, scope, sub_key)
    except Exception as e:
        raise BatchCommitFailed(e) from e

# ################################################################################################################################

def _commit_on_exit(backend:'SQLPubSubBackend', scope:'DeliveryScope', sub_key:'str') -> 'None':
    """ Commits what a delivery batch concluded before its greenlet was stopped.
    """
    try:
        commit_delivery_scope(backend, scope, sub_key)

    # A takeover by another server or an unavailable database leaves the messages unacknowledged,
    # and they are delivered again, by this server or by the one that took over ..
    except PubSubReplaced as e:
        logger.info('Concluded messages not committed when delivery stopped, sub_key `%s`, delivered again: %s', sub_key, e)

    except DBAPIError as e:
        if is_transient(e):
            logger.info('Concluded messages not committed when delivery stopped, sub_key `%s`, delivered again: %s', sub_key, e)
        else:
            logger.warning('Concluded messages not committed when delivery stopped, sub_key `%s`: %s', sub_key, format_exc())

    # .. while any other error is logged with its traceback.
    except Exception:
        logger.warning('Concluded messages not committed when delivery stopped, sub_key `%s`: %s', sub_key, format_exc())

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
    """ Invokes the service of a push subscriber. An attempt that fails or is stopped leaves none of its publications
    behind, since only the attempt that concludes a message commits with the batch.
    """
    scope = get_delivery_scope()

    # Outside of an atomic batch, the publications of the service commit on their own ..
    if not scope:
        server.invoke(service_name, payload, **kwargs)
        return

    # .. whereas inside of one, the publications of a failed or stopped attempt are discarded along with their audit events.
    publication_count = len(scope.publications)

    try:
        server.invoke(service_name, payload, **kwargs)

    except (Exception, GreenletExit):
        del scope.publications[publication_count:]
        raise

# ################################################################################################################################
# ################################################################################################################################
