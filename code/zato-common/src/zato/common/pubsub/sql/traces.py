# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The list of delivered-message traces, which are the message rows without a payload. Triggers of the database add
# a message to the list when it is inserted without a payload or when its payload is dropped, and remove it
# when the message is deleted or receives a payload again, in the transaction that changes the message row,
# whichever code issues the statement. The retention sweeps read the list rather than the message table,
# which no index of payloads may serve, because an index of the payload column would make dropping a payload
# an update of every index of the message table.

# Zato
from zato.common.pubsub.sql.counts import postgresql_function, register_triggers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from zato.common.typing_ import anytuple, strlist

    # Dummy assignments to satisfy type checkers
    MetaData = MetaData
    anytuple = anytuple
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_insert_into = 'INSERT INTO pubsub_trace (message_id, topic_name, pub_time_ms)'

# ################################################################################################################################
# ################################################################################################################################

def _sqlite_statements() -> 'strlist':
    """ The row triggers of SQLite that keep the traces in step with the message rows.
    """
    add_new = f'{_insert_into} VALUES (new.id, new.topic_name, new.pub_time_ms);'

    # A message published without a payload is a trace from the start ..
    message_insert = 'CREATE TRIGGER IF NOT EXISTS pubsub_trace_insert AFTER INSERT ON pubsub_message ' + \
        f'WHEN new.payload IS NULL BEGIN {add_new} END'

    # .. a message that is or becomes a trace has its entry replaced, and one that receives a payload loses it ..
    replace_new = 'INSERT OR REPLACE INTO pubsub_trace (message_id, topic_name, pub_time_ms) ' + \
        'SELECT new.id, new.topic_name, new.pub_time_ms WHERE new.payload IS NULL;'

    remove_revived = 'DELETE FROM pubsub_trace WHERE message_id = new.id AND new.payload IS NOT NULL;'

    message_update = 'CREATE TRIGGER IF NOT EXISTS pubsub_trace_update ' + \
        'AFTER UPDATE OF payload, topic_name, pub_time_ms ON pubsub_message ' + \
        f'WHEN old.payload IS NULL OR new.payload IS NULL BEGIN {replace_new} {remove_revived} END'

    # .. and a deleted trace leaves the list.
    message_delete = 'CREATE TRIGGER IF NOT EXISTS pubsub_trace_delete AFTER DELETE ON pubsub_message ' + \
        'WHEN old.payload IS NULL BEGIN DELETE FROM pubsub_trace WHERE message_id = old.id; END'

    out = [message_insert, message_update, message_delete]
    return out

# ################################################################################################################################

def _postgresql_statements() -> 'anytuple':
    """ The statement triggers of PostgreSQL that keep the traces in step with the message rows.
    """

    # The messages a statement inserted without a payload are traces from the start ..
    add_inserted = f'{_insert_into} SELECT id, topic_name, pub_time_ms FROM new_rows WHERE payload IS NULL;'

    # .. the messages it updated are traces when they have no payload, and those that received one are traces no more.
    # .. A trigger with a list of columns cannot read the updated rows, so the trigger runs on each update of the messages ..
    add_updated = f'{_insert_into} SELECT id, topic_name, pub_time_ms FROM new_rows WHERE payload IS NULL ' + \
        'ON CONFLICT (message_id) DO UPDATE SET topic_name = excluded.topic_name, pub_time_ms = excluded.pub_time_ms;'

    remove_revived = 'DELETE FROM pubsub_trace WHERE message_id IN (SELECT id FROM new_rows WHERE payload IS NOT NULL);'

    # .. and the traces it deleted leave the list.
    remove_deleted = 'DELETE FROM pubsub_trace WHERE message_id IN (SELECT id FROM old_rows WHERE payload IS NULL);'

    insert_function = postgresql_function('pubsub_trace_insert', add_inserted)
    update_function = postgresql_function('pubsub_trace_update', f'{add_updated} {remove_revived}')
    delete_function = postgresql_function('pubsub_trace_delete', remove_deleted)

    after_insert = 'CREATE TRIGGER pubsub_trace_insert AFTER INSERT ON pubsub_message ' + \
        'REFERENCING NEW TABLE AS new_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_trace_insert()'

    after_update = 'CREATE TRIGGER pubsub_trace_update AFTER UPDATE ON pubsub_message ' + \
        'REFERENCING NEW TABLE AS new_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_trace_update()'

    after_delete = 'CREATE TRIGGER pubsub_trace_delete AFTER DELETE ON pubsub_message ' + \
        'REFERENCING OLD TABLE AS old_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_trace_delete()'

    functions = [insert_function, update_function, delete_function]

    triggers = [
        ('pubsub_trace_insert', 'pubsub_message', after_insert),
        ('pubsub_trace_update', 'pubsub_message', after_update),
        ('pubsub_trace_delete', 'pubsub_message', after_delete),
    ]

    out = functions, triggers
    return out

# ################################################################################################################################
# ################################################################################################################################

def register_traces(metadata:'MetaData') -> 'None':
    """ Attaches the creation of the triggers of the traces to the creation of the schema.
    """
    register_triggers(metadata, _sqlite_statements(), [_postgresql_statements()])

# ################################################################################################################################
# ################################################################################################################################
