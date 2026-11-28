# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The list of delivered-message traces, which are the message rows without a payload. Triggers of the database add
# a message to the list when it is inserted without a payload, and remove it when the message is deleted,
# in the transaction that changes the message row, whichever code issues the statement. The retention sweeps read
# the list rather than the message table, which no index of the dropped flag may serve, because such an index
# would make dropping a payload an update of every index of the message table.
#
# The same triggers release the payload of a message that is deleted before it dropped it, by listing the payload
# in pubsub_released_payload for the cleanup sweep.
#
# The statements that update message rows keep the list themselves, in the same statement or transaction as the update,
# so that no trigger reads a transition table of every update - the drop of the payloads on acknowledgement adds
# the messages to the list and releases their payloads, see payloads.py, a new payload of a message removes it
# from the list, and the rename of a topic renames its traces with its messages, see admin.py.

# Zato
from zato.common.pubsub.sql.counts import postgresql_function, register_dropped_triggers, register_triggers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from zato.common.typing_ import anytuple

    # Dummy assignments to satisfy type checkers
    MetaData = MetaData
    anytuple = anytuple

# ################################################################################################################################
# ################################################################################################################################

_insert_into = 'INSERT INTO pubsub_trace (message_id, topic_name, pub_time_ms)'

_release_into = 'INSERT INTO pubsub_released_payload (payload_id)'

# ################################################################################################################################
# ################################################################################################################################

def _trace_statements() -> 'anytuple':
    """ The statement triggers that keep the traces in step with the message rows.
    """

    # The messages a statement inserted without a payload are traces from the start ..
    add_inserted = f'{_insert_into} SELECT id, topic_name, pub_time_ms FROM new_rows WHERE payload_dropped;'

    # .. the traces it deleted leave the list ..
    remove_deleted = 'DELETE FROM pubsub_trace WHERE message_id IN (SELECT id FROM old_rows WHERE payload_dropped);'

    # .. and the payloads of the messages it deleted before they dropped them are released.
    release_deleted = f'{_release_into} SELECT payload_id FROM old_rows WHERE NOT payload_dropped AND payload_id IS NOT NULL;'

    insert_function = postgresql_function('pubsub_trace_insert', add_inserted)
    delete_function = postgresql_function('pubsub_trace_delete', f'{remove_deleted} {release_deleted}')

    after_insert = 'CREATE TRIGGER pubsub_trace_insert AFTER INSERT ON pubsub_message ' + \
        'REFERENCING NEW TABLE AS new_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_trace_insert()'

    after_delete = 'CREATE TRIGGER pubsub_trace_delete AFTER DELETE ON pubsub_message ' + \
        'REFERENCING OLD TABLE AS old_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_trace_delete()'

    functions = [insert_function, delete_function]

    triggers = [
        ('pubsub_trace_insert', 'pubsub_message', after_insert),
        ('pubsub_trace_delete', 'pubsub_message', after_delete),
    ]

    out = functions, triggers
    return out

# ################################################################################################################################
# ################################################################################################################################

def register_traces(metadata:'MetaData') -> 'None':
    """ Attaches the creation of the triggers of the traces to the creation of the schema.
    """
    statements = [_trace_statements()]
    register_triggers(metadata, statements)

    # The trigger that kept the list in step with every update of the messages is removed from a database
    # created before the statements that update the messages took this over.
    register_dropped_triggers(metadata, [('pubsub_trace_update', 'pubsub_message')])

# ################################################################################################################################
# ################################################################################################################################
