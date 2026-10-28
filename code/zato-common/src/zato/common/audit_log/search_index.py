# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The native text indexes behind the free-text search of the audit log. SQLite keeps FTS5 tables
# with the trigram tokenizer, maintained by triggers in the transaction that writes the event.
# PostgreSQL keeps pg_trgm GIN indexes, one over the searched event columns joined into a single text
# and one over attribute values, which serve LIKE patterns directly. MySQL keeps FULLTEXT
# indexes with the ngram parser, read through MATCH ... AGAINST. A search narrows the rows through
# the index and confirms each one with LIKE, so every database returns what LIKE alone would return.

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import and_, column, DDL, event, literal_column, select, table
from sqlalchemy.dialects.mysql import match as mysql_match

# Zato
from zato.common.db_env.common import Type_MySQL, Type_PostgreSQL, Type_SQLite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Table
    from zato.common.typing_ import any_, strlist, strtuple

    # Dummy assignments to satisfy type checkers
    any_ = any_
    strlist = strlist
    strtuple = strtuple
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# The FTS5 tables of SQLite, each indexing the text of one table under its rowid
Event_Search_Table      = 'event_search'
Event_Attr_Search_Table = 'event_attr_search'

# The shortest term the trigram tokenizer of SQLite indexes
SQLite_Min_Term_Length = 3

# The shortest term the ngram parser of MySQL indexes, which is its default ngram_token_size
MySQL_Min_Term_Length = 2

# The trigram index of PostgreSQL over the searched event columns
_postgresql_event_index = 'idx_event_search'

# What separates two columns in the text the trigram index of PostgreSQL covers
_postgresql_column_separator = "' '"

# The FULLTEXT indexes of MySQL
_mysql_event_index = 'idx_event_search'
_mysql_attr_index  = 'idx_event_attr_search'

# The event columns the free-text search covers
search_columns = ('data', 'event_type', 'msg_id', 'correl_id', 'endpoint', 'ext_client_id',
    'status', 'classification', 'sub_key')

# The attribute column the attribute search covers
_attr_search_columns = ('value',)

# The double quote that delimits a phrase in FTS5 and in the boolean mode of MySQL
_quote = '"'

# ################################################################################################################################
# ################################################################################################################################

def _sqlite_statements(table_name:'str', search_table:'str', columns:'strtuple') -> 'strlist':
    """ The FTS5 table of one table and the triggers that keep it in step with every insert, update and delete.
    """
    column_list = ', '.join(columns)

    new_values:'strlist' = []
    old_values:'strlist' = []

    for name in columns:
        new_values.append(f'new.{name}')
        old_values.append(f'old.{name}')

    new_list = ', '.join(new_values)
    old_list = ', '.join(old_values)

    # The index keeps no copy of the text - it reads it from the table it indexes ..
    fts5_options = f"content='{table_name}', content_rowid='id', tokenize='trigram'"
    create_table = f'CREATE VIRTUAL TABLE {search_table} USING fts5({column_list}, {fts5_options})'

    # .. so an indexed row is added with the values of a new row ..
    add_new = f'INSERT INTO {search_table} (rowid, {column_list}) VALUES (new.id, {new_list});'

    # .. and removed with the values it was indexed under.
    remove_old = f"INSERT INTO {search_table} ({search_table}, rowid, {column_list}) VALUES ('delete', old.id, {old_list});"

    after_insert = f'CREATE TRIGGER {search_table}_insert AFTER INSERT ON {table_name} BEGIN {add_new} END'
    after_delete = f'CREATE TRIGGER {search_table}_delete AFTER DELETE ON {table_name} BEGIN {remove_old} END'
    after_update = f'CREATE TRIGGER {search_table}_update AFTER UPDATE ON {table_name} BEGIN {remove_old} {add_new} END'

    out = [create_table, after_insert, after_delete, after_update]
    return out

# ################################################################################################################################

def _postgresql_search_text(prefix:'str') -> 'str':
    """ The searched event columns joined into one text, with each column name preceded by the given prefix.
    The index is created over this expression and a search matches the same expression, so that PostgreSQL
    finds the index for it.
    """
    parts:'strlist' = []

    for name in search_columns:
        parts.append(f"coalesce({prefix}{name}, '')")

    separator = f' || {_postgresql_column_separator} || '
    joined = separator.join(parts)

    out = f'({joined})'
    return out

# ################################################################################################################################

def _postgresql_event_statements(table_name:'str') -> 'strlist':
    """ One trigram GIN index over the searched columns of the event table. One index instead of one per column,
    because each GIN index adds its entries and its pending list to the log of every insert.
    """
    search_text = _postgresql_search_text('')
    create_index = f'CREATE INDEX {_postgresql_event_index} ON {table_name} USING gin ({search_text} gin_trgm_ops)'

    out = [create_index]
    return out

# ################################################################################################################################

def _postgresql_attr_statements(table_name:'str') -> 'strlist':
    """ One trigram GIN index over the attribute values.
    """
    out:'strlist' = []

    for name in _attr_search_columns:
        out.append(f'CREATE INDEX idx_{table_name}_search_{name} ON {table_name} USING gin ({name} gin_trgm_ops)')

    return out

# ################################################################################################################################

def _mysql_statements(table_name:'str', index_name:'str', columns:'strtuple') -> 'strlist':
    """ The FULLTEXT index of one table, created with stopwords off, because the ngram parser leaves out
    every token that contains a stopword, and the default list holds single letters.
    """
    column_list = ', '.join(columns)

    stopwords_off = 'SET SESSION innodb_ft_enable_stopword = OFF'
    create_index = f'CREATE FULLTEXT INDEX {index_name} ON {table_name} ({column_list}) WITH PARSER ngram'

    out = [stopwords_off, create_index]
    return out

# ################################################################################################################################

def _listen(target:'Table', when:'str', statements:'strlist', dialect_name:'str') -> 'None':
    """ Runs the given statements on the given dialect alone, when the table is created.
    """
    for statement in statements:
        ddl = DDL(statement)
        ddl = ddl.execute_if(dialect=dialect_name)
        event.listen(target, when, ddl)

# ################################################################################################################################

def register_search_indexes(event_table:'Table', event_attr_table:'Table') -> 'None':
    """ Attaches the native text indexes of each database to the creation of the event and attribute tables.
    """
    event_table_name = event_table.name
    attr_table_name = event_attr_table.name

    # SQLite ..
    event_sqlite = _sqlite_statements(event_table_name, Event_Search_Table, search_columns)
    attr_sqlite = _sqlite_statements(attr_table_name, Event_Attr_Search_Table, _attr_search_columns)

    _listen(event_table, 'after_create', event_sqlite, Type_SQLite)
    _listen(event_attr_table, 'after_create', attr_sqlite, Type_SQLite)

    # .. PostgreSQL, which needs its trigram extension before any of the indexes ..
    extension = ['CREATE EXTENSION IF NOT EXISTS pg_trgm']
    event_postgresql = _postgresql_event_statements(event_table_name)
    attr_postgresql = _postgresql_attr_statements(attr_table_name)

    _listen(event_table, 'before_create', extension, Type_PostgreSQL)
    _listen(event_table, 'after_create', event_postgresql, Type_PostgreSQL)
    _listen(event_attr_table, 'after_create', attr_postgresql, Type_PostgreSQL)

    # .. and MySQL.
    event_mysql = _mysql_statements(event_table_name, _mysql_event_index, search_columns)
    attr_mysql = _mysql_statements(attr_table_name, _mysql_attr_index, _attr_search_columns)

    _listen(event_table, 'after_create', event_mysql, Type_MySQL)
    _listen(event_attr_table, 'after_create', attr_mysql, Type_MySQL)

# ################################################################################################################################
# ################################################################################################################################

def _is_mysql_term_indexed(query:'str') -> 'bool':
    """ Whether the ngram index of MySQL can find the term - the parser splits it on whitespace
    and indexes no word shorter than its token, and a phrase cannot carry a double quote.
    """
    if _quote in query:
        return False

    words = query.split()

    if not words:
        return False

    for word in words:
        if len(word) < MySQL_Min_Term_Length:
            return False

    return True

# ################################################################################################################################

def _fts5_phrase(query:'str') -> 'str':
    """ The term as one FTS5 phrase, which the trigram tokenizer matches as a substring.
    """
    escaped = query.replace(_quote, _quote + _quote)

    out = _quote + escaped + _quote
    return out

# ################################################################################################################################

def _sqlite_narrowed(search_table:'str', query:'str', condition:'any_', row_id:'any_') -> 'any_':
    """ The condition, narrowed down to the rows the FTS5 table finds, when the term is long enough to be indexed.
    """
    if len(query) < SQLite_Min_Term_Length:
        return condition

    fts_table = table(search_table, column('rowid'), column(search_table))
    fts_match_column = fts_table.c[search_table]
    phrase = _fts5_phrase(query)

    matching_ids = select(fts_table.c.rowid)
    matching_ids = matching_ids.where(fts_match_column.match(phrase))

    is_indexed_match = row_id.in_(matching_ids)

    out = and_(is_indexed_match, condition)
    return out

# ################################################################################################################################

def _mysql_narrowed(columns:'any_', query:'str', condition:'any_') -> 'any_':
    """ The condition, narrowed down to the rows the FULLTEXT index finds, when the index can find the term.
    """
    if not _is_mysql_term_indexed(query):
        return condition

    phrase = _quote + query + _quote

    is_indexed_match = mysql_match(*columns, against=phrase)
    is_indexed_match = is_indexed_match.in_boolean_mode()

    out = and_(is_indexed_match, condition)
    return out

# ################################################################################################################################

def _postgresql_narrowed(event_table:'Table', pattern:'str', condition:'any_') -> 'any_':
    """ The condition, narrowed down to the rows whose joined searched columns the trigram index finds the pattern in.
    The joined text can match across two columns, which is why the condition confirms each row.
    """
    prefix = f'{event_table.name}.'
    search_text = _postgresql_search_text(prefix)
    search_column = literal_column(search_text)

    is_indexed_match = search_column.like(pattern, escape='\\')

    out = and_(is_indexed_match, condition)
    return out

# ################################################################################################################################

def narrow_event_search(dialect_name:'str', event_table:'Table', query:'str', pattern:'str', condition:'any_') -> 'any_':
    """ The LIKE condition over the searched event columns, served by the native index of the database.
    """
    if dialect_name == Type_SQLite:
        out = _sqlite_narrowed(Event_Search_Table, query, condition, event_table.c.id)

    elif dialect_name == Type_MySQL:
        columns:'list' = []
        for name in search_columns:
            columns.append(event_table.c[name])
        out = _mysql_narrowed(columns, query, condition)

    else:
        out = _postgresql_narrowed(event_table, pattern, condition)

    return out

# ################################################################################################################################

def narrow_attr_search(dialect_name:'str', event_attr_table:'Table', query:'str', condition:'any_') -> 'any_':
    """ The LIKE condition over attribute values, served by the native index of the database.
    """
    if dialect_name == Type_SQLite:
        out = _sqlite_narrowed(Event_Attr_Search_Table, query, condition, event_attr_table.c.id)

    elif dialect_name == Type_MySQL:
        columns = [event_attr_table.c.value]
        out = _mysql_narrowed(columns, query, condition)

    else:
        out = condition

    return out

# ################################################################################################################################
# ################################################################################################################################
