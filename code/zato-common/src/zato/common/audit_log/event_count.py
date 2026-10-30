# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The per-minute event counts of the audit log. Each row holds a signed count of the events of one minute
# with one combination of the key columns the listing filters by. Triggers of the database add the rows
# in the transaction that inserts, updates or deletes the events, whichever code issues the statement,
# and compaction replaces the rows of one minute and key with a single row holding their sum.

# SQLAlchemy
from sqlalchemy import DDL, delete, event, func, insert, or_, select
from sqlalchemy.schema import CreateIndex

# Zato
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Index, Table
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anydict, anylist, strlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    anylist = anylist
    strlist = strlist
    Engine = Engine
    Index = Index
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# The key columns of a count - the columns of the event table the listing filters by
count_key_columns = ('source', 'object_name', 'event_type', 'outcome', 'status')

# The columns that identify one count, in the order a compaction reads them
_period_and_keys = ('period_start',) + count_key_columns

# The columns whose change moves an event from one count to another
_counted_columns = ('event_time',) + count_key_columns

# The savepoint under which SQLite creates the triggers and fills the counts in one transaction
_sqlite_savepoint = 'event_count_fill'

# ################################################################################################################################
# ################################################################################################################################

def _prefixed(prefix:'str', names:'tuple') -> 'str':
    """ The given column names, each preceded by a table name or an alias, as one comma-separated list.
    """
    parts:'strlist' = []

    for name in names:
        parts.append(f'{prefix}.{name}')

    out = ', '.join(parts)
    return out

# ################################################################################################################################

def _any_changed(left:'str', right:'str', operator:'str') -> 'str':
    """ The condition that is true when any counted column differs between two versions of a row.
    """
    parts:'strlist' = []

    for name in _counted_columns:
        parts.append(f'{left}.{name} {operator} {right}.{name}')

    out = ' OR '.join(parts)
    return out

# ################################################################################################################################

def _group_by_all() -> 'str':
    """ The GROUP BY clause over the minute and every key column, by their positions in the select list.
    """
    positions:'strlist' = []
    column_count = len(count_key_columns) + 1

    for position in range(1, column_count + 1):
        positions.append(str(position))

    joined = ', '.join(positions)

    out = f'GROUP BY {joined}'
    return out

# ################################################################################################################################

def _sqlite_minute(prefix:'str') -> 'str':
    """ The minute of an event time under SQLite, in the text form SQLAlchemy stores the time in.
    """
    out = "substr({0}.event_time, 1, 16) || ':00.000000'".format(prefix)
    return out

# ################################################################################################################################

def _postgresql_minute(prefix:'str') -> 'str':
    """ The minute of an event time under PostgreSQL, truncated in UTC.
    """
    out = "date_trunc('minute', {0}.event_time AT TIME ZONE 'UTC') AT TIME ZONE 'UTC'".format(prefix)
    return out

# ################################################################################################################################

def _sqlite_statements(event_name:'str', count_name:'str') -> 'strlist':
    """ The row triggers of SQLite that add one count row per change of an event, and the statement that fills
    the counts of the events that exist when the table is created.
    """
    key_list = ', '.join(count_key_columns)
    counted_list = ', '.join(_counted_columns)
    insert_into = f'INSERT INTO {count_name} (period_start, {key_list}, event_count)'

    new_minute = _sqlite_minute('new')
    old_minute = _sqlite_minute('old')
    new_keys = _prefixed('new', count_key_columns)
    old_keys = _prefixed('old', count_key_columns)

    # A new version of a row adds one to its count ..
    add_new = f'{insert_into} VALUES ({new_minute}, {new_keys}, 1);'

    # .. and an old one subtracts one from the count it was in ..
    remove_old = f'{insert_into} VALUES ({old_minute}, {old_keys}, -1);'

    # .. while an update moves an event only when it changes a counted column.
    changed = _any_changed('old', 'new', 'IS NOT')

    after_insert = f'CREATE TRIGGER {count_name}_insert AFTER INSERT ON {event_name} BEGIN {add_new} END'
    after_delete = f'CREATE TRIGGER {count_name}_delete AFTER DELETE ON {event_name} BEGIN {remove_old} END'
    after_update = f'CREATE TRIGGER {count_name}_update AFTER UPDATE OF {counted_list} ON {event_name} ' + \
        f'WHEN {changed} BEGIN {remove_old} {add_new} END'

    event_minute = _sqlite_minute(event_name)
    group_by = _group_by_all()
    fill = f'{insert_into} SELECT {event_minute}, {key_list}, count(*) FROM {event_name} {group_by}'

    out = [after_insert, after_delete, after_update, fill]
    return out

# ################################################################################################################################

def _postgresql_function(name:'str', body:'str') -> 'str':
    """ A PL/pgSQL function of a statement trigger, running the given statements.
    """
    out = f'CREATE OR REPLACE FUNCTION {name}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN {body} RETURN NULL; END $$'
    return out

# ################################################################################################################################

def _postgresql_statements(event_name:'str', count_name:'str') -> 'strlist':
    """ The statement triggers of PostgreSQL that add one count row per minute and key a statement changes,
    and the statement that fills the counts of the events that exist when the table is created.
    """
    key_list = ', '.join(count_key_columns)
    insert_into = f'INSERT INTO {count_name} (period_start, {key_list}, event_count)'
    group_by = _group_by_all()

    new_minute = _postgresql_minute('n')
    old_minute = _postgresql_minute('o')
    new_keys = _prefixed('n', count_key_columns)
    old_keys = _prefixed('o', count_key_columns)

    # The rows a statement inserted add to their counts ..
    add_inserted = f'{insert_into} SELECT {new_minute}, {new_keys}, count(*) FROM new_rows n {group_by};'

    # .. the rows it deleted subtract from theirs ..
    remove_deleted = f'{insert_into} SELECT {old_minute}, {old_keys}, -count(*) FROM old_rows o {group_by};'

    # .. and the rows whose update changed a counted column move from the old count to the new one.
    changed = _any_changed('o', 'n', 'IS DISTINCT FROM')
    changed_pairs = f'FROM old_rows o JOIN new_rows n ON n.id = o.id WHERE {changed}'

    remove_updated = f'{insert_into} SELECT {old_minute}, {old_keys}, -count(*) {changed_pairs} {group_by};'
    add_updated = f'{insert_into} SELECT {new_minute}, {new_keys}, count(*) {changed_pairs} {group_by};'

    insert_function = _postgresql_function(f'{count_name}_insert', add_inserted)
    delete_function = _postgresql_function(f'{count_name}_delete', remove_deleted)
    update_function = _postgresql_function(f'{count_name}_update', f'{remove_updated} {add_updated}')

    after_insert = f'CREATE TRIGGER {count_name}_insert AFTER INSERT ON {event_name} ' + \
        f'REFERENCING NEW TABLE AS new_rows FOR EACH STATEMENT EXECUTE FUNCTION {count_name}_insert()'

    after_delete = f'CREATE TRIGGER {count_name}_delete AFTER DELETE ON {event_name} ' + \
        f'REFERENCING OLD TABLE AS old_rows FOR EACH STATEMENT EXECUTE FUNCTION {count_name}_delete()'

    after_update = f'CREATE TRIGGER {count_name}_update AFTER UPDATE ON {event_name} ' + \
        'REFERENCING OLD TABLE AS old_rows NEW TABLE AS new_rows ' + \
        f'FOR EACH STATEMENT EXECUTE FUNCTION {count_name}_update()'

    event_minute = _postgresql_minute(event_name)
    fill = f'{insert_into} SELECT {event_minute}, {key_list}, count(*) FROM {event_name} {group_by}'

    out = [insert_function, delete_function, update_function, after_insert, after_delete, after_update, fill]
    return out

# ################################################################################################################################

def listen_after_create(target:'Table', elements:'anylist', dialect_name:'str') -> 'None':
    """ Runs the given statements or DDL elements on the given dialect alone, after the table is created.
    """
    for element in elements:

        if isinstance(element, str):
            ddl = DDL(element)
        else:
            ddl = element

        ddl = ddl.execute_if(dialect=dialect_name)
        event.listen(target, 'after_create', ddl)

# ################################################################################################################################

def register_event_count(event_table:'Table', count_table:'Table', ordered_indexes:'anylist') -> 'None':
    """ Attaches the creation of the triggers and the filling of the counts to the creation of the count table.
    The ordered indexes of the event table are created with it, because a database that predates the count table
    also predates them.
    """
    event_name = event_table.name
    count_name = count_table.name

    index_elements:'anylist' = []

    for index in ordered_indexes:
        create_index = CreateIndex(index, if_not_exists=True)
        index_elements.append(create_index)

    # SQLite creates the triggers and fills the counts under one savepoint, which holds the write lock
    # from the first trigger on, so that no event is written between the two ..
    sqlite_statements = _sqlite_statements(event_name, count_name)

    sqlite_elements:'anylist' = [f'SAVEPOINT {_sqlite_savepoint}']
    sqlite_elements.extend(index_elements)
    sqlite_elements.extend(sqlite_statements)
    sqlite_elements.append(f'RELEASE {_sqlite_savepoint}')

    listen_after_create(count_table, sqlite_elements, Type_SQLite)

    # .. while PostgreSQL creates them in the transaction of the schema, and the lock that creating a trigger takes
    # on the event table makes writers wait until the counts are filled.
    postgresql_statements = _postgresql_statements(event_name, count_name)

    postgresql_elements:'anylist' = []
    postgresql_elements.extend(index_elements)
    postgresql_elements.extend(postgresql_statements)

    listen_after_create(count_table, postgresql_elements, Type_PostgreSQL)

# ################################################################################################################################
# ################################################################################################################################

def _sum_counts(rows:'any_') -> 'anydict':
    """ The sum of the counts of the given rows by their minute and key.
    """
    out:'anydict' = {}

    for row in rows:
        key = tuple(row[:-1])
        count = row[-1]

        if key not in out:
            out[key] = 0

        out[key] += count

    return out

# ################################################################################################################################

def compact_event_counts(engine:'Engine', count_table:'Table', compacted_up_to:'int') -> 'int':
    """ Replaces the rows of every minute that holds more than one row of one key, or a row whose count is zero,
    with one row per key holding their sum, looking only at the minutes that received rows above the given id.
    Returns the highest id of the table afterwards, from which the next compaction starts.
    """
    id_column = count_table.c.id
    period_column = count_table.c.period_start
    count_column = count_table.c.event_count

    key_columns:'anylist' = []

    for name in count_key_columns:
        key_columns.append(count_table.c[name])

    # The minutes that received rows since the previous compaction ..
    new_periods = select(period_column)
    new_periods = new_periods.where(id_column > compacted_up_to)

    # .. those of them with more than one row of a key or a row of nothing ..
    has_duplicates = func.count() > 1
    has_zero = func.sum(count_column) == 0

    compactable = select(period_column)
    compactable = compactable.where(period_column.in_(new_periods))
    compactable = compactable.group_by(period_column, *key_columns)
    compactable = compactable.having(or_(has_duplicates, has_zero))

    # .. lose all their rows, which the statement returns ..
    statement = delete(count_table)
    statement = statement.where(period_column.in_(compactable))
    statement = statement.returning(period_column, *key_columns, count_column)

    with engine.begin() as connection:

        result = connection.execute(statement)
        sums = _sum_counts(result)

        # .. and each minute and key comes back as one row of its sum, unless the sum is zero ..
        rows:'anylist' = []

        for key, total in sums.items():

            if total == 0:
                continue

            values:'anydict' = dict(zip(_period_and_keys, key))
            values['event_count'] = total

            rows.append(values)

        if rows:
            _ = connection.execute(insert(count_table), rows)

        # .. and the next compaction starts above everything there is now.
        highest_id = select(func.max(id_column))
        out = connection.execute(highest_id).scalar()

    # An empty table has no highest id
    if out is None:
        out = compacted_up_to

    return out

# ################################################################################################################################
# ################################################################################################################################
