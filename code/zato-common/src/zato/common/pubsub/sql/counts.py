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
# The triggers only ever insert signed change rows, one per key that a statement changes, so that concurrent transactions
# never wait on one another for a count row, and compaction replaces the rows of each key with one row holding their sum.
# Readers add up the rows of a key.

# SQLAlchemy
from sqlalchemy import DDL, event, text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_, anylist, anytuple

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    MetaData = MetaData
    any_ = any_
    anylist = anylist
    anytuple = anytuple

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

def postgresql_function(name:'str', body:'str') -> 'str':
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

    insert_function = postgresql_function('pubsub_queue_count_insert', add_inserted)
    delete_function = postgresql_function('pubsub_queue_count_delete', remove_deleted)
    update_function = postgresql_function('pubsub_queue_count_update', move_updated)

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

    insert_function = postgresql_function('pubsub_topic_count_insert', f'{add_topics} {add_publications}')
    delete_function = postgresql_function('pubsub_topic_count_delete', f'{remove_topics} {remove_publications}')
    update_function = postgresql_function('pubsub_topic_count_update', f'{move_topic} {move_publication}')

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

class _TriggerExists(_TriggerIsMissing):
    """ Tells whether a trigger of PostgreSQL exists on its table. Dropping a trigger locks its table against all writes,
    so the schema setup that each starting process runs drops only the triggers that still exist.
    """
    def __call__(self, ddl:'any_', target:'any_', bind:'any_', tables:'any_'=None, state:'any_'=None,
        **kwargs:'any_') -> 'bool':
        out = not super().__call__(ddl, target, bind, tables, state, **kwargs)
        return out

# ################################################################################################################################

def _listen(metadata:'MetaData', statement:'str', condition:'_TriggerIsMissing | None') -> 'None':
    """ Runs the given statement after all the tables are created, and only when the condition holds, if there is one.
    """

    # DDL formats its statement with the % operator, so the modulo operator is written twice.
    statement = statement.replace('%', '%%')

    ddl = DDL(statement)

    if condition:
        ddl = ddl.execute_if(callable_=condition)

    event.listen(metadata, 'after_create', ddl)

# ################################################################################################################################

def register_triggers(metadata:'MetaData', statements:'anylist') -> 'None':
    """ Attaches the creation of the given triggers to the creation of the schema. The triggers are created
    after all the tables, each one only if it does not exist yet. Each element of statements
    is a pair of the trigger functions and of the triggers that run them.
    """
    for functions, triggers in statements:

        # Replacing a function locks no table, so the functions are always brought to their current bodies ..
        for statement in functions:
            _listen(metadata, statement, None)

        # .. whereas the triggers are only created.
        for trigger_name, table_name, statement in triggers:
            trigger_is_missing = _TriggerIsMissing(trigger_name, table_name)
            _listen(metadata, statement, trigger_is_missing)

# ################################################################################################################################

def register_dropped_triggers(metadata:'MetaData', triggers:'anylist') -> 'None':
    """ Attaches the removal of the given triggers, and of the functions of the same names that they run,
    to the creation of the schema. Each element of triggers is a pair of the name of a trigger and of its table.
    """
    for trigger_name, table_name in triggers:

        trigger_exists = _TriggerExists(trigger_name, table_name)
        _listen(metadata, f'DROP TRIGGER {trigger_name} ON {table_name}', trigger_exists)

        # Dropping a function locks no table.
        _listen(metadata, f'DROP FUNCTION IF EXISTS {trigger_name}()', None)

# ################################################################################################################################

def register_counts(metadata:'MetaData') -> 'None':
    """ Attaches the creation of the triggers of the counts to the creation of the schema.
    """
    statements = [_postgresql_queue_statements(), _postgresql_topic_statements()]
    register_triggers(metadata, statements)

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
    """ Compacts the change rows of all the count tables in the caller's transaction.
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
