# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The open exchanges of the audit log - one row for each event that opens an exchange, e.g. a sent HL7 message,
# while no event that closes it, e.g. its acknowledgment, exists. Triggers of the database keep the rows
# in the transaction that inserts, updates or deletes the events, whichever code issues the statement,
# so the table always equals the anti-join of the opening events against the closing ones.

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.audit_log.event_count import listen_after_create
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Table
    from zato.common.typing_ import anylist, strlist

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    strlist = strlist
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# The columns of an event that a row of an open exchange repeats, the event id first
_event_columns = ('id', 'source', 'msg_id', 'object_name')

# The columns whose change can open or close an exchange
_exchange_columns = ('source', 'event_type', 'msg_id', 'object_name')

# A string value as an SQL literal - the values are the names of sources and event types, which hold no quotes
_sql_literal = "'{0}'"

# The transition tables of the statement triggers of PostgreSQL
_new_rows = 'FROM new_rows n'
_old_rows = 'FROM old_rows o'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ExchangePair:
    """ The events of one source that open and close an exchange, and whether the close matches
    on the object name as well as on the message id.
    """
    source: str = ''
    open_event: str = ''
    close_event: str = ''
    needs_object_name_match: bool = False

# ################################################################################################################################

def new_exchange_pair(source:'str', open_event:'str', close_event:'str', needs_object_name_match:'bool') -> 'ExchangePair':
    out = ExchangePair()
    out.source = source
    out.open_event = open_event
    out.close_event = close_event
    out.needs_object_name_match = needs_object_name_match

    return out

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
# ################################################################################################################################

class _ExchangeStatements:
    """ The SQL that keeps the open exchanges of one pair. Each statement reads the events it reacts to from a FROM clause,
    the transition table of a PostgreSQL statement trigger, or from none at all, with the row of a SQLite trigger
    referenced directly as new or old.
    """

    def __init__(self, pair:'ExchangePair', event_name:'str', open_name:'str') -> 'None':
        self.pair = pair
        self.event_name = event_name
        self.open_name = open_name

        # The triggers and functions of this pair are named after its source
        source_suffix = pair.source.replace('-', '_')
        self.object_prefix = f'{open_name}_{source_suffix}'

        self.source = _sql_literal.format(pair.source)
        self.open_event = _sql_literal.format(pair.open_event)
        self.close_event = _sql_literal.format(pair.close_event)

        self.insert_into = f'INSERT INTO {open_name} (event_id, source, msg_id, object_name)'

# ################################################################################################################################

    def match(self, left:'str', right:'str') -> 'str':
        """ The condition that two rows belong to the same exchange. A message id or an object name that is NULL
        matches nothing, as in the anti-join.
        """
        out = f'{left}.msg_id = {right}.msg_id'

        if self.pair.needs_object_name_match:
            out += f' AND {left}.object_name = {right}.object_name'

        return out

# ################################################################################################################################

    def is_kind(self, row:'str', event_type:'str') -> 'str':
        """ The condition that a row is an event of this pair's source and of the given type.
        """
        out = f'{row}.source = {self.source} AND {row}.event_type = {event_type}'
        return out

# ################################################################################################################################

    def has_close(self, row:'str') -> 'str':
        """ The condition that an event closing the exchange of the given row exists.
        """
        is_close = self.is_kind('c', self.close_event)
        match = self.match('c', row)

        out = f'EXISTS (SELECT 1 FROM {self.event_name} c WHERE {is_close} AND {match})'
        return out

# ################################################################################################################################

    def is_open(self, row:'str') -> 'str':
        """ The condition that the given event already has its row among the open exchanges.
        """
        out = f'EXISTS (SELECT 1 FROM {self.open_name} x WHERE x.event_id = {row}.id)'
        return out

# ################################################################################################################################

    def open_rows(self, rows:'str', row:'str') -> 'str':
        """ Opens the exchanges of the opening events among the given rows that are neither closed nor open already.
        """
        columns = _prefixed(row, _event_columns)
        is_open_event = self.is_kind(row, self.open_event)
        has_close = self.has_close(row)
        is_open = self.is_open(row)

        out = f'{self.insert_into} SELECT {columns} {rows} WHERE {is_open_event} AND NOT {has_close} AND NOT {is_open}'
        return out

# ################################################################################################################################

    def close_rows(self, rows:'str', row:'str') -> 'str':
        """ Closes the exchanges that the closing events among the given rows close.
        """
        is_close_event = self.is_kind(row, self.close_event)
        match = self.match(self.open_name, row)

        out = f'DELETE FROM {self.open_name} WHERE {self.open_name}.source = {self.source} ' + \
            f'AND EXISTS (SELECT 1 {rows} WHERE {is_close_event} AND {match})'

        return out

# ################################################################################################################################

    def drop_rows(self, rows:'str', row:'str') -> 'str':
        """ Removes the exchanges of the opening events among the given rows.
        """
        is_open_event = self.is_kind(row, self.open_event)

        out = f'DELETE FROM {self.open_name} WHERE {self.open_name}.event_id IN ' + \
            f'(SELECT {row}.id {rows} WHERE {is_open_event})'

        return out

# ################################################################################################################################

    def reopen_rows(self, rows:'str', row:'str') -> 'str':
        """ Opens again the exchanges whose closing events among the given rows are gone, unless another one closes them.
        """
        columns = _prefixed('e', _event_columns)
        is_open_event = self.is_kind('e', self.open_event)
        is_close_event = self.is_kind(row, self.close_event)
        match = self.match('e', row)
        has_close = self.has_close('e')
        is_open = self.is_open('e')

        out = f'{self.insert_into} SELECT {columns} FROM {self.event_name} e WHERE {is_open_event} ' + \
            f'AND EXISTS (SELECT 1 {rows} WHERE {is_close_event} AND {match}) AND NOT {has_close} AND NOT {is_open}'

        return out

# ################################################################################################################################

    def any_changed(self, left:'str', right:'str', operator:'str') -> 'str':
        """ The condition that an update changed a column that can open or close an exchange.
        """
        parts:'strlist' = []

        for name in _exchange_columns:
            parts.append(f'{left}.{name} {operator} {right}.{name}')

        joined = ' OR '.join(parts)

        out = f'({joined})'
        return out

# ################################################################################################################################

    def sqlite_statements(self) -> 'strlist':
        """ The row triggers of SQLite and the statement that fills the table with the exchanges open when it is created.
        """
        prefix = self.object_prefix
        event_name = self.event_name
        exchange_list = ', '.join(_exchange_columns)

        # A new event opens its own exchange or closes those of others ..
        open_new = self.open_rows('', 'new')
        close_new = self.close_rows('', 'new')

        # .. and a deleted one takes its exchange along or opens again those it closed.
        drop_old = self.drop_rows('', 'old')
        reopen_old = self.reopen_rows('', 'old')

        is_new_source = f'new.source = {self.source}'
        is_old_source = f'old.source = {self.source}'
        changed = self.any_changed('old', 'new', 'IS NOT')

        after_insert = f'CREATE TRIGGER {prefix}_insert AFTER INSERT ON {event_name} WHEN {is_new_source} ' + \
            f'BEGIN {open_new}; {close_new}; END'

        after_delete = f'CREATE TRIGGER {prefix}_delete AFTER DELETE ON {event_name} WHEN {is_old_source} ' + \
            f'BEGIN {drop_old}; {reopen_old}; END'

        after_update = f'CREATE TRIGGER {prefix}_update AFTER UPDATE OF {exchange_list} ON {event_name} ' + \
            f'WHEN ({is_old_source} OR {is_new_source}) AND {changed} ' + \
            f'BEGIN {drop_old}; {close_new}; {reopen_old}; {open_new}; END'

        fill = self.open_rows(f'FROM {event_name} e', 'e')

        out = [after_insert, after_delete, after_update, fill]
        return out

# ################################################################################################################################

    def _postgresql_lock(self, rows:'str', row:'str') -> 'str':
        """ Takes the transaction-level advisory locks of the message ids among the given rows, in a fixed order,
        so that two transactions writing the two halves of one exchange see each other's rows.
        """
        lock_class = _sql_literal.format(self.object_prefix)

        out = f'PERFORM pg_advisory_xact_lock(hashtext({lock_class}), exchange_key) ' + \
            f'FROM (SELECT DISTINCT hashtext({row}.msg_id) AS exchange_key {rows} ' + \
            f'WHERE {row}.source = {self.source} AND {row}.msg_id IS NOT NULL) AS exchange_keys ORDER BY exchange_key'

        return out

# ################################################################################################################################

    def _postgresql_function(self, name:'str', rows:'str', row:'str', statements:'strlist') -> 'str':
        """ A PL/pgSQL function of a statement trigger, running the given statements only when the rows
        of the statement include events of this pair's source.
        """
        body = '; '.join(statements)

        out = f'CREATE OR REPLACE FUNCTION {name}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN ' + \
            f'IF EXISTS (SELECT 1 {rows} WHERE {row}.source = {self.source}) THEN {body}; END IF; RETURN NULL; END $$'

        return out

# ################################################################################################################################

    def postgresql_statements(self) -> 'strlist':
        """ The statement triggers of PostgreSQL and the statement that fills the table with the exchanges open
        when it is created.
        """
        prefix = self.object_prefix
        event_name = self.event_name

        # The rows of an update that changed a column of an exchange, in their old and new versions
        changed = self.any_changed('o', 'n', 'IS DISTINCT FROM')
        changed_old = f'FROM (SELECT o.* FROM old_rows o JOIN new_rows n ON n.id = o.id WHERE {changed}) o'
        changed_new = f'FROM (SELECT n.* FROM old_rows o JOIN new_rows n ON n.id = o.id WHERE {changed}) n'
        all_updated = 'FROM (SELECT * FROM old_rows UNION ALL SELECT * FROM new_rows) u'

        # New events open their own exchanges or close those of others ..
        insert_statements = [
            self._postgresql_lock(_new_rows, 'n'),
            self.open_rows(_new_rows, 'n'),
            self.close_rows(_new_rows, 'n'),
        ]

        # .. deleted ones take their exchanges along or open again those they closed ..
        delete_statements = [
            self._postgresql_lock(_old_rows, 'o'),
            self.drop_rows(_old_rows, 'o'),
            self.reopen_rows(_old_rows, 'o'),
        ]

        # .. and updated ones do both.
        update_statements = [
            self._postgresql_lock(all_updated, 'u'),
            self.drop_rows(changed_old, 'o'),
            self.close_rows(changed_new, 'n'),
            self.reopen_rows(changed_old, 'o'),
            self.open_rows(changed_new, 'n'),
        ]

        insert_function = self._postgresql_function(f'{prefix}_insert', _new_rows, 'n', insert_statements)
        delete_function = self._postgresql_function(f'{prefix}_delete', _old_rows, 'o', delete_statements)
        update_function = self._postgresql_function(f'{prefix}_update', all_updated, 'u', update_statements)

        after_insert = f'CREATE TRIGGER {prefix}_insert AFTER INSERT ON {event_name} ' + \
            f'REFERENCING NEW TABLE AS new_rows FOR EACH STATEMENT EXECUTE FUNCTION {prefix}_insert()'

        after_delete = f'CREATE TRIGGER {prefix}_delete AFTER DELETE ON {event_name} ' + \
            f'REFERENCING OLD TABLE AS old_rows FOR EACH STATEMENT EXECUTE FUNCTION {prefix}_delete()'

        after_update = f'CREATE TRIGGER {prefix}_update AFTER UPDATE ON {event_name} ' + \
            'REFERENCING OLD TABLE AS old_rows NEW TABLE AS new_rows ' + \
            f'FOR EACH STATEMENT EXECUTE FUNCTION {prefix}_update()'

        fill = self.open_rows(f'FROM {event_name} e', 'e')

        out = [insert_function, delete_function, update_function, after_insert, after_delete, after_update, fill]
        return out

# ################################################################################################################################
# ################################################################################################################################

def register_event_open(event_table:'Table', open_table:'Table', pairs:'anylist') -> 'None':
    """ Attaches the creation of the triggers and the filling of the open exchanges to the creation of their table.
    """
    event_name = event_table.name
    open_name = open_table.name

    # SQLite creates the triggers and fills the table under one savepoint, which holds the write lock
    # from the first trigger on, so that no event is written between the two ..
    sqlite_elements:'anylist' = [f'SAVEPOINT {open_name}_fill']

    # .. while PostgreSQL does it in the transaction of the schema, in which creating a trigger
    # makes the writers of the event table wait until the table is filled.
    postgresql_elements:'anylist' = []

    for pair in pairs:
        statements = _ExchangeStatements(pair, event_name, open_name)

        sqlite_statements = statements.sqlite_statements()
        sqlite_elements.extend(sqlite_statements)

        postgresql_statements = statements.postgresql_statements()
        postgresql_elements.extend(postgresql_statements)

    sqlite_elements.append(f'RELEASE {open_name}_fill')

    listen_after_create(open_table, sqlite_elements, Type_SQLite)
    listen_after_create(open_table, postgresql_elements, Type_PostgreSQL)

# ################################################################################################################################
# ################################################################################################################################
