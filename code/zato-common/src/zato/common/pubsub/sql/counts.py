# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The counts the statistics of the pub/sub database read in place of counting rows - the depth of each
# (subscriber, topic) queue, the number of messages of each topic and the number of messages each publisher
# published to a topic in each minute. Triggers of the database update the counts in the transaction
# that inserts, updates or deletes the rows, whichever code issues the statement.
#
# SQLite keeps one row per key and updates it in place. PostgreSQL only ever inserts signed change rows,
# one per key that a statement changes, so that concurrent transactions never wait on one another for a count row,
# and compaction replaces the rows of each key with one row holding their sum. Readers add up the rows of a key.

# SQLAlchemy
from sqlalchemy import DDL, event, text

# Zato
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_, anytuple, strlist

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    MetaData = MetaData
    any_ = any_
    anytuple = anytuple
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# One minute expressed in milliseconds, the width of the publication counts.
Milliseconds_Per_Minute = 60 * 1000

# What the publisher column of a publication count holds for messages published without a publisher.
No_Publisher = ''

# The count tables, each with its key columns and the column holding the count.
_count_tables = (
    ('pubsub_queue_count', ('sub_key', 'topic_name'), 'depth'),
    ('pubsub_topic_count', ('topic_name',), 'total'),
    ('pubsub_publish_count', ('topic_name', 'minute_ms', 'publisher'), 'total'),
)

# Whether a trigger of the given name exists on the given table of PostgreSQL.
_trigger_exists_query = text("""
    select 1 from pg_trigger
    where tgname = :trigger_name and tgrelid = to_regclass(:table_name) and not tgisinternal
""")

# ################################################################################################################################
# ################################################################################################################################

def _minute(row:'str') -> 'str':
    """ The start of the minute of the publication time of a message row.
    """
    out = f'{row}.pub_time_ms - {row}.pub_time_ms % {Milliseconds_Per_Minute}'
    return out

# ################################################################################################################################

def _publisher(row:'str') -> 'str':
    """ The publisher of a message row as it is counted.
    """
    out = "coalesce({0}.publisher, '{1}')".format(row, No_Publisher)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _add_to_queue(row:'str') -> 'str':
    """ The statement that adds one to the depth of the queue of a delivery row.
    """
    out = 'INSERT INTO pubsub_queue_count (sub_key, topic_name, depth) ' + \
        f'VALUES ({row}.sub_key, {row}.topic_name, 1) ' + \
        'ON CONFLICT (sub_key, topic_name) DO UPDATE SET depth = depth + 1;'

    return out

# ################################################################################################################################

def _remove_from_queue(row:'str') -> 'str':
    """ The statement that subtracts one from the depth of the queue of a delivery row.
    """
    out = 'UPDATE pubsub_queue_count SET depth = depth - 1 ' + \
        f'WHERE sub_key = {row}.sub_key AND topic_name = {row}.topic_name;'

    return out

# ################################################################################################################################

def _add_to_topic(row:'str') -> 'str':
    """ The statements that add one to the message count of the topic of a message row
    and to the publication count of its minute and publisher.
    """
    minute = _minute(row)
    publisher = _publisher(row)

    add_message = 'INSERT INTO pubsub_topic_count (topic_name, total) ' + \
        f'VALUES ({row}.topic_name, 1) ' + \
        'ON CONFLICT (topic_name) DO UPDATE SET total = total + 1;'

    add_publication = 'INSERT INTO pubsub_publish_count (topic_name, minute_ms, publisher, total) ' + \
        f'VALUES ({row}.topic_name, {minute}, {publisher}, 1) ' + \
        'ON CONFLICT (topic_name, minute_ms, publisher) DO UPDATE SET total = total + 1;'

    out = f'{add_message} {add_publication}'
    return out

# ################################################################################################################################

def _remove_from_topic(row:'str') -> 'str':
    """ The statements that subtract one from the message count of the topic of a message row
    and from the publication count of its minute and publisher.
    """
    minute = _minute(row)
    publisher = _publisher(row)

    remove_message = 'UPDATE pubsub_topic_count SET total = total - 1 ' + \
        f'WHERE topic_name = {row}.topic_name;'

    remove_publication = 'UPDATE pubsub_publish_count SET total = total - 1 ' + \
        f'WHERE topic_name = {row}.topic_name AND minute_ms = {minute} AND publisher = {publisher};'

    out = f'{remove_message} {remove_publication}'
    return out

# ################################################################################################################################

def _sqlite_statements() -> 'strlist':
    """ The row triggers of SQLite that keep the counts in step with the delivery and message rows.
    """
    add_new_delivery = _add_to_queue('new')
    remove_old_delivery = _remove_from_queue('old')

    add_new_message = _add_to_topic('new')
    remove_old_message = _remove_from_topic('old')

    # A delivery row is one message waiting in the queue of its subscriber and topic ..
    delivery_insert = 'CREATE TRIGGER IF NOT EXISTS pubsub_queue_count_insert AFTER INSERT ON pubsub_delivery ' + \
        f'BEGIN {add_new_delivery} END'

    delivery_delete = 'CREATE TRIGGER IF NOT EXISTS pubsub_queue_count_delete AFTER DELETE ON pubsub_delivery ' + \
        f'BEGIN {remove_old_delivery} END'

    # .. and an update moves it to another queue only when it changes the subscriber or the topic ..
    delivery_changed = 'old.sub_key IS NOT new.sub_key OR old.topic_name IS NOT new.topic_name'

    delivery_update = 'CREATE TRIGGER IF NOT EXISTS pubsub_queue_count_update ' + \
        f'AFTER UPDATE OF sub_key, topic_name ON pubsub_delivery WHEN {delivery_changed} ' + \
        f'BEGIN {remove_old_delivery} {add_new_delivery} END'

    # .. a message row counts towards its topic, minute and publisher ..
    message_insert = 'CREATE TRIGGER IF NOT EXISTS pubsub_topic_count_insert AFTER INSERT ON pubsub_message ' + \
        f'BEGIN {add_new_message} END'

    message_delete = 'CREATE TRIGGER IF NOT EXISTS pubsub_topic_count_delete AFTER DELETE ON pubsub_message ' + \
        f'BEGIN {remove_old_message} END'

    # .. and an update moves it to other counts only when it changes one of the three.
    message_changed = 'old.topic_name IS NOT new.topic_name OR old.pub_time_ms IS NOT new.pub_time_ms ' + \
        'OR old.publisher IS NOT new.publisher'

    message_update = 'CREATE TRIGGER IF NOT EXISTS pubsub_topic_count_update ' + \
        f'AFTER UPDATE OF topic_name, pub_time_ms, publisher ON pubsub_message WHEN {message_changed} ' + \
        f'BEGIN {remove_old_message} {add_new_message} END'

    out = [delivery_insert, delivery_delete, delivery_update, message_insert, message_delete, message_update]
    return out

# ################################################################################################################################
# ################################################################################################################################

def _postgresql_function(name:'str', body:'str') -> 'str':
    """ A PL/pgSQL trigger function running the given statements.
    """
    out = f'CREATE OR REPLACE FUNCTION {name}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN {body} RETURN NULL; END $$'
    return out

# ################################################################################################################################

def _postgresql_queue_statements() -> 'anytuple':
    """ The triggers of PostgreSQL that add change rows of the queue depths.
    """
    insert_into = 'INSERT INTO pubsub_queue_count (sub_key, topic_name, depth)'

    # The rows a statement inserted add to the depth of their queues, one change row per queue ..
    add_inserted = f'{insert_into} SELECT sub_key, topic_name, count(*) FROM new_rows GROUP BY sub_key, topic_name;'

    # .. the rows it deleted subtract from it ..
    remove_deleted = f'{insert_into} SELECT sub_key, topic_name, -count(*) FROM old_rows GROUP BY sub_key, topic_name;'

    # .. and a row whose subscriber or topic changed moves from one queue to the other. The update trigger is a row trigger
    # .. limited to these two columns, so that the updates of other columns made with each delivery attempt do not run it.
    move_updated = f'{insert_into} VALUES (OLD.sub_key, OLD.topic_name, -1), (NEW.sub_key, NEW.topic_name, 1);'

    insert_function = _postgresql_function('pubsub_queue_count_insert', add_inserted)
    delete_function = _postgresql_function('pubsub_queue_count_delete', remove_deleted)
    update_function = _postgresql_function('pubsub_queue_count_update', move_updated)

    after_insert = 'CREATE TRIGGER pubsub_queue_count_insert AFTER INSERT ON pubsub_delivery ' + \
        'REFERENCING NEW TABLE AS new_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_queue_count_insert()'

    after_delete = 'CREATE TRIGGER pubsub_queue_count_delete AFTER DELETE ON pubsub_delivery ' + \
        'REFERENCING OLD TABLE AS old_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_queue_count_delete()'

    delivery_changed = 'OLD.sub_key IS DISTINCT FROM NEW.sub_key OR OLD.topic_name IS DISTINCT FROM NEW.topic_name'

    after_update = 'CREATE TRIGGER pubsub_queue_count_update ' + \
        f'AFTER UPDATE OF sub_key, topic_name ON pubsub_delivery FOR EACH ROW WHEN ({delivery_changed}) ' + \
        'EXECUTE FUNCTION pubsub_queue_count_update()'

    functions = [insert_function, delete_function, update_function]

    triggers = [
        ('pubsub_queue_count_insert', 'pubsub_delivery', after_insert),
        ('pubsub_queue_count_delete', 'pubsub_delivery', after_delete),
        ('pubsub_queue_count_update', 'pubsub_delivery', after_update),
    ]

    out = functions, triggers
    return out

# ################################################################################################################################

def _postgresql_topic_statements() -> 'anytuple':
    """ The triggers of PostgreSQL that add change rows of the topic and publication counts.
    """
    topic_insert = 'INSERT INTO pubsub_topic_count (topic_name, total)'
    publish_insert = 'INSERT INTO pubsub_publish_count (topic_name, minute_ms, publisher, total)'

    new_minute = _minute('n')
    old_minute = _minute('o')
    new_publisher = _publisher('n')
    old_publisher = _publisher('o')

    # The messages a statement inserted add to their topics, minutes and publishers ..
    add_topics = f'{topic_insert} SELECT n.topic_name, count(*) FROM new_rows n GROUP BY 1;'
    add_publications = f'{publish_insert} SELECT n.topic_name, {new_minute}, {new_publisher}, count(*) ' + \
        'FROM new_rows n GROUP BY 1, 2, 3;'

    # .. the messages it deleted subtract from them ..
    remove_topics = f'{topic_insert} SELECT o.topic_name, -count(*) FROM old_rows o GROUP BY 1;'
    remove_publications = f'{publish_insert} SELECT o.topic_name, {old_minute}, {old_publisher}, -count(*) ' + \
        'FROM old_rows o GROUP BY 1, 2, 3;'

    # .. and a message whose topic, publication time or publisher changed moves to the other counts. As with the queues,
    # .. the update trigger is a row trigger limited to these columns, so dropping a payload does not run it.
    move_topic = f'{topic_insert} VALUES (OLD.topic_name, -1), (NEW.topic_name, 1);'
    move_publication = f'{publish_insert} VALUES ' + \
        f'(OLD.topic_name, {_minute("OLD")}, {_publisher("OLD")}, -1), ' + \
        f'(NEW.topic_name, {_minute("NEW")}, {_publisher("NEW")}, 1);'

    insert_function = _postgresql_function('pubsub_topic_count_insert', f'{add_topics} {add_publications}')
    delete_function = _postgresql_function('pubsub_topic_count_delete', f'{remove_topics} {remove_publications}')
    update_function = _postgresql_function('pubsub_topic_count_update', f'{move_topic} {move_publication}')

    after_insert = 'CREATE TRIGGER pubsub_topic_count_insert AFTER INSERT ON pubsub_message ' + \
        'REFERENCING NEW TABLE AS new_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_topic_count_insert()'

    after_delete = 'CREATE TRIGGER pubsub_topic_count_delete AFTER DELETE ON pubsub_message ' + \
        'REFERENCING OLD TABLE AS old_rows FOR EACH STATEMENT EXECUTE FUNCTION pubsub_topic_count_delete()'

    message_changed = 'OLD.topic_name IS DISTINCT FROM NEW.topic_name OR OLD.pub_time_ms IS DISTINCT FROM NEW.pub_time_ms ' + \
        'OR OLD.publisher IS DISTINCT FROM NEW.publisher'

    after_update = 'CREATE TRIGGER pubsub_topic_count_update ' + \
        f'AFTER UPDATE OF topic_name, pub_time_ms, publisher ON pubsub_message FOR EACH ROW WHEN ({message_changed}) ' + \
        'EXECUTE FUNCTION pubsub_topic_count_update()'

    functions = [insert_function, delete_function, update_function]

    triggers = [
        ('pubsub_topic_count_insert', 'pubsub_message', after_insert),
        ('pubsub_topic_count_delete', 'pubsub_message', after_delete),
        ('pubsub_topic_count_update', 'pubsub_message', after_update),
    ]

    out = functions, triggers
    return out

# ################################################################################################################################
# ################################################################################################################################

class _TriggerIsMissing:
    """ Tells whether a trigger of PostgreSQL does not exist on its table yet. Creating or replacing a trigger
    locks its table against all writes, so the schema setup that each starting process runs creates only
    the triggers that are missing.
    """
    def __init__(self, trigger_name:'str', table_name:'str') -> 'None':
        self.trigger_name = trigger_name
        self.table_name = table_name

    def __call__(self, ddl:'any_', target:'any_', bind:'any_', tables:'any_'=None, state:'any_'=None,
        **kwargs:'any_') -> 'bool':
        parameters = {'trigger_name': self.trigger_name, 'table_name': self.table_name}
        existing = bind.execute(_trigger_exists_query, parameters).scalar()

        out = existing is None
        return out

# ################################################################################################################################

def _listen(metadata:'MetaData', statement:'str', dialect_name:'str', trigger_is_missing:'_TriggerIsMissing | None') -> 'None':
    """ Runs the given statement on the given dialect alone, after all the tables are created,
    and only when the trigger it creates is missing, if it creates one.
    """

    # DDL formats its statement with the % operator, so the modulo operator is written twice.
    statement = statement.replace('%', '%%')

    ddl = DDL(statement)
    ddl = ddl.execute_if(dialect=dialect_name, callable_=trigger_is_missing)
    event.listen(metadata, 'after_create', ddl)

# ################################################################################################################################

def register_counts(metadata:'MetaData') -> 'None':
    """ Attaches the creation of the triggers to the creation of the schema. The triggers are created
    after all the tables, each one only if it does not exist yet.
    """
    for statement in _sqlite_statements():
        _listen(metadata, statement, Type_SQLite, None)

    for functions, triggers in (_postgresql_queue_statements(), _postgresql_topic_statements()):

        # Replacing a function locks no table, so the functions are always brought to their current bodies ..
        for statement in functions:
            _listen(metadata, statement, Type_PostgreSQL, None)

        # .. whereas the triggers are only created.
        for trigger_name, table_name, statement in triggers:
            trigger_is_missing = _TriggerIsMissing(trigger_name, table_name)
            _listen(metadata, statement, Type_PostgreSQL, trigger_is_missing)

# ################################################################################################################################
# ################################################################################################################################

def _compaction_statement(table_name:'str', key_names:'tuple', count_name:'str') -> 'str':
    """ The statement that replaces the change rows of each key holding more than one row, or a sum of zero,
    with one row holding their sum, unless the sum is zero.
    """
    key_list = ', '.join(key_names)

    out = f"""
        WITH compacted AS (
            DELETE FROM {table_name}
            WHERE ({key_list}) IN (
                SELECT {key_list} FROM {table_name}
                GROUP BY {key_list}
                HAVING count(*) > 1 OR sum({count_name}) = 0
            )
            RETURNING {key_list}, {count_name}
        )
        INSERT INTO {table_name} ({key_list}, {count_name})
        SELECT {key_list}, sum({count_name}) FROM compacted
        GROUP BY {key_list}
        HAVING sum({count_name}) <> 0
    """

    return out

# ################################################################################################################################

# One compaction statement per count table, built once.
_compaction_statements:'list' = []

for _table_name, _key_names, _count_name in _count_tables:
    _statement = _compaction_statement(_table_name, _key_names, _count_name)
    _compaction_statements.append(text(_statement))

# ################################################################################################################################

def compact_counts(connection:'Connection') -> 'int':
    """ Compacts the change rows of all the count tables of PostgreSQL in the caller's transaction.
    A row that a concurrent transaction commits while the statement runs is not part of its snapshot,
    so it is neither removed nor added to the sum, and the sums remain exact. Returns how many rows remain.
    """
    out = 0

    for statement in _compaction_statements:
        result = connection.execute(statement)
        out += result.rowcount

    return out

# ################################################################################################################################
# ################################################################################################################################
