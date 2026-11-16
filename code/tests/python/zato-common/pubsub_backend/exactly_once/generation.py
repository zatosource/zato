# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from dataclasses import dataclass

# pytest
import pytest

# Zato
from exactly_once.common import build, First_Output_Topic, get_lease_ms, Input_Sub_Key, lease, new_backend, publish_input
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.replaced import PubSubReplaced
from zato.common.test.pubsub_database import connect, pubsub_db_env
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.publication import BuiltPublication
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anydict, anylist, strcalldict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The pool sizes that give the replaced server and the replacing one an engine each, since engines are cached by their settings
_replaced_pool_size  = 8
_replacing_pool_size = 9

# The rows that a write of the replaced server would change
_message_rows_query  = 'select id, msg_id, payload is null from pubsub_message order by id'
_delivery_rows_query = 'select id, sub_key, attempt, leased_until_ms from pubsub_delivery order by id'
_sub_rows_query      = 'select sub_key, topic_name from pubsub_topic_sub order by sub_key, topic_name'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WriteContext:
    """ What the write operations of the replaced server act on, prepared before it was replaced.
    """

    # The message that a pull leased, with the attempt of the lease
    pulled_msg_id: 'str'
    pulled_attempt: 'int'

    # The message that a push delivery read
    pushed_message: 'anydict'

    # A publication built for the acknowledgements
    publication: 'BuiltPublication'

    # The time after which the lease of the pulled message ran out
    lease_now_ms: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _publish(backend:'SQLPubSubBackend', context:'WriteContext') -> 'None':
    _ = backend.publish(First_Output_Topic, 'replaced')

# ################################################################################################################################

def _record_attempts(backend:'SQLPubSubBackend', context:'WriteContext') -> 'None':
    messages:'anylist' = [context.pushed_message]
    _ = backend.record_attempts(messages)

# ################################################################################################################################

def _ack(backend:'SQLPubSubBackend', context:'WriteContext') -> 'None':
    msg_ids = [context.pushed_message['msg_id']]
    _ = backend.ack_messages(Input_Sub_Key, msg_ids)

# ################################################################################################################################

def _ack_with_publications(backend:'SQLPubSubBackend', context:'WriteContext') -> 'None':
    msg_ids = [context.pushed_message['msg_id']]
    sequence_ids = [context.pushed_message['sequence_id']]
    publications:'anylist' = [context.publication.pending]

    backend.ack_with_publications(Input_Sub_Key, msg_ids, sequence_ids, publications)

# ################################################################################################################################

def _ack_pulled_with_publications(backend:'SQLPubSubBackend', context:'WriteContext') -> 'None':
    consumed = [(context.pulled_msg_id, context.pulled_attempt)]
    publications = [context.publication]

    _ = backend.ack_pulled_with_publications(Input_Sub_Key, consumed, publications)

# ################################################################################################################################

def _lease_messages(backend:'SQLPubSubBackend', context:'WriteContext') -> 'None':
    _ = lease(backend, context.lease_now_ms)

# ################################################################################################################################
# ################################################################################################################################

# Each write operation of a server, by its name
_operations:'strcalldict' = {
    'publish': _publish,
    'record_attempts': _record_attempts,
    'ack': _ack,
    'ack_with_publications': _ack_with_publications,
    'ack_pulled_with_publications': _ack_pulled_with_publications,
    'lease_messages': _lease_messages,
}

Operation_Names = list(_operations)

# ################################################################################################################################
# ################################################################################################################################

def _new_env(database:'PubSubDatabase', pool_size:'int') -> 'strstrdict':
    """ Returns the environment of one server, with an engine and a generation file of its own.
    """
    work_dir = tempfile.mkdtemp(prefix='zato_pubsub_exactly_once_generation_', dir=os.environ['TMPDIR'])
    generation_file_path = os.path.join(work_dir, 'generation')

    out = dict(database.env)
    out['Zato_PubSub_Generation_File'] = generation_file_path
    out['Zato_PubSub_DB_Pool_Size'] = f'{pool_size}'

    return out

# ################################################################################################################################

def _prepare(backend:'SQLPubSubBackend') -> 'WriteContext':
    """ Publishes one message that a pull leases and one that a push delivery reads.
    """
    pulled_msg_id = publish_input(backend, 'pulled')
    pushed_msg_id = publish_input(backend, 'pushed')

    # The first message is leased ..
    now_ms = backend.clock.now_ms()
    attempts = lease(backend, now_ms, 1)

    # .. and the second one is read the way push delivery reads it.
    messages = backend.fetch_pending(Input_Sub_Key)

    for message in messages:
        if message['msg_id'] == pushed_msg_id:
            pushed_message = message
            break
    else:
        raise Exception(f'Message `{pushed_msg_id}` not read')

    lease_ms = get_lease_ms()

    out = WriteContext()
    out.pulled_msg_id  = pulled_msg_id
    out.pulled_attempt = attempts[pulled_msg_id]
    out.pushed_message = pushed_message
    out.publication    = build(backend, First_Output_Topic, 'output')
    out.lease_now_ms   = now_ms + lease_ms + 1

    return out

# ################################################################################################################################

def _read_rows(database:'PubSubDatabase') -> 'anylist':
    """ Reads the rows that a write could change, through a connection that no generation guard confirms.
    """
    connection = connect(database)
    out:'anylist' = []

    try:
        cursor = connection.cursor()

        for query in (_message_rows_query, _delivery_rows_query, _sub_rows_query):
            cursor.execute(query)
            rows = cast_('any_', cursor.fetchall())
            out.append(rows)

    finally:
        connection.close()

    return out

# ################################################################################################################################

def _take_over(env:'strstrdict') -> 'SQLPubSubBackend':
    """ Starts the backend of a server that takes over the database, resolving its engine while the environment
    selects the engine that its guard is installed on.
    """
    with pubsub_db_env(env):
        out = SQLPubSubBackend()
        out.take_over()
        _ = out.engine

    return out

# ################################################################################################################################

def _uninstall_guard(backend:'SQLPubSubBackend') -> 'None':
    """ Detaches the generation guard of a backend from its engine, which other tests reuse.
    """
    guard = backend.generation_guard

    if guard:
        guard.uninstall(backend.engine)

# ################################################################################################################################
# ################################################################################################################################

def run_replaced_generation_scenario(database:'PubSubDatabase', operation_name:'str') -> 'None':
    """ Once another server took over the database, a write operation of the replaced server is rejected
    and changes no row.
    """
    operation = _operations[operation_name]

    replaced_env = _new_env(database, _replaced_pool_size)
    replacing_env = _new_env(database, _replacing_pool_size)

    replaced:'SQLPubSubBackend | None' = None
    replacing:'SQLPubSubBackend | None' = None

    try:
        with pubsub_db_env(replaced_env):

            # The first server takes over and prepares what the operation acts on ..
            replaced = new_backend()
            replaced.take_over()
            context = _prepare(replaced)

            # .. the second server takes over ..
            replacing = _take_over(replacing_env)
            rows_before = _read_rows(database)

            # .. so the operation of the first server is rejected ..
            with pytest.raises(PubSubReplaced):
                operation(replaced, context)

            assert replaced.is_replaced

        # .. and no row changed.
        rows_after = _read_rows(database)
        assert rows_after == rows_before

    finally:
        if replaced:
            _uninstall_guard(replaced)
        if replacing:
            _uninstall_guard(replacing)

# ################################################################################################################################
# ################################################################################################################################
