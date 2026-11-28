# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The native text indexes behind the free-text search of the audit log. The searched event columns are indexed
# per event, and each payload is indexed once in the payload table through its search_text column, which holds
# the words, integers and decimal numbers of the payload. Each word of a query matches the indexed words it is
# a prefix of, in the event columns or in the payload of the event.
#
# A GIN index covers the words of the searched event columns joined into a single text, a GIN index covers
# the words of the payloads, and a pg_trgm GIN index over attribute values serves LIKE patterns directly.
# The message and correlation identifiers are matched whole, through their own indexes.

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import and_, DDL, event, func, literal_column, select, union

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Table
    from zato.common.typing_ import any_, anylist, strlist, strtuple

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anylist = anylist
    strlist = strlist
    strtuple = strtuple
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# The word indexes over the searched event columns and over the words of the payloads
PostgreSQL_Event_Index   = 'idx_event_search'
PostgreSQL_Payload_Index = 'idx_event_payload_search'

# How many kilobytes the pending list of a GIN index holds before an insert merges it into the index
# within its own statement. The search index merger merges the pending lists every ten seconds, well before they reach it.
PostgreSQL_Pending_List_Limit_KB = 65536

# The text search configuration that splits the searched columns into words,
# lower-cased and with no stemming and no stop words.
_postgresql_text_config = "'simple'"

# What separates two columns in the text a word index covers
_postgresql_column_separator = "' '"

# What marks a word of a query as a prefix
_postgresql_prefix_marker = ':*'

# The event columns the word index covers
search_columns = ('event_type', 'endpoint', 'ext_client_id', 'status', 'classification', 'sub_key')

# The identifiers that the free-text search matches whole, through their own indexes. Each identifier would be
# a key of its own in the word index, which would make each insert write it into the index.
id_search_columns = ('msg_id', 'correl_id')

# The payload column the free-text search covers
payload_search_columns = ('search_text',)

# The attribute column the attribute search covers
_attr_search_columns = ('value',)

# ################################################################################################################################
# ################################################################################################################################

def _postgresql_search_words(prefix:'str', columns:'strtuple') -> 'str':
    """ The words of the given columns joined into one text, with each column name preceded by the given prefix.
    The index is created over this expression and a search matches the same expression, so that PostgreSQL
    finds the index for it.
    """
    parts:'strlist' = []

    for name in columns:
        parts.append(f"coalesce({prefix}{name}, '')")

    separator = f' || {_postgresql_column_separator} || '
    joined = separator.join(parts)

    out = f'to_tsvector({_postgresql_text_config}, ({joined}))'
    return out

# ################################################################################################################################

def _postgresql_word_statements(table_name:'str', index_name:'str', columns:'strtuple') -> 'strlist':
    """ One GIN index over the words of the given columns of a table. One index instead of one per column,
    because each GIN index adds its entries and its pending list to the log of every insert.
    """
    search_words = _postgresql_search_words('', columns)
    storage = f'WITH (gin_pending_list_limit = {PostgreSQL_Pending_List_Limit_KB})'
    create_index = f'CREATE INDEX {index_name} ON {table_name} USING gin ({search_words}) {storage}'

    out = [create_index]
    return out

# ################################################################################################################################

def _postgresql_attr_index_name(table_name:'str', column_name:'str') -> 'str':
    """ The name of the trigram GIN index over one attribute column.
    """
    out = f'idx_{table_name}_search_{column_name}'
    return out

# ################################################################################################################################

def _postgresql_attr_statements(table_name:'str') -> 'strlist':
    """ One trigram GIN index over the attribute values, with the pending list limit of the word indexes.
    """
    storage = f'WITH (gin_pending_list_limit = {PostgreSQL_Pending_List_Limit_KB})'

    out:'strlist' = []

    for name in _attr_search_columns:
        index_name = _postgresql_attr_index_name(table_name, name)
        out.append(f'CREATE INDEX {index_name} ON {table_name} USING gin ({name} gin_trgm_ops) {storage}')

    return out

# ################################################################################################################################

def get_postgresql_index_names(attr_table_name:'str') -> 'strtuple':
    """ The names of all the GIN indexes, the word indexes first.
    """
    names:'strlist' = [PostgreSQL_Event_Index, PostgreSQL_Payload_Index]

    for name in _attr_search_columns:
        index_name = _postgresql_attr_index_name(attr_table_name, name)
        names.append(index_name)

    out = tuple(names)
    return out

# ################################################################################################################################

def _listen(target:'Table', when:'str', statements:'strlist') -> 'None':
    """ Runs the given statements when the table is created.
    """
    for statement in statements:
        ddl = DDL(statement)
        event.listen(target, when, ddl)

# ################################################################################################################################

def register_search_indexes(event_table:'Table', event_payload_table:'Table', event_attr_table:'Table') -> 'None':
    """ Attaches the native text indexes to the creation of the event, payload and attribute tables.
    """
    event_table_name = event_table.name
    payload_table_name = event_payload_table.name
    attr_table_name = event_attr_table.name

    # The trigram extension is required before the index of attribute values ..
    extension = ['CREATE EXTENSION IF NOT EXISTS pg_trgm']

    # .. and each table receives its own indexes.
    event_postgresql = _postgresql_word_statements(event_table_name, PostgreSQL_Event_Index, search_columns)
    payload_postgresql = _postgresql_word_statements(payload_table_name, PostgreSQL_Payload_Index, payload_search_columns)
    attr_postgresql = _postgresql_attr_statements(attr_table_name)

    _listen(event_table, 'before_create', extension)
    _listen(event_table, 'after_create', event_postgresql)
    _listen(event_payload_table, 'after_create', payload_postgresql)
    _listen(event_attr_table, 'after_create', attr_postgresql)

# ################################################################################################################################
# ################################################################################################################################

def _postgresql_word_match(event_table:'Table', event_payload_table:'Table', word:'str') -> 'any_':
    """ The events whose joined searched columns or payload have a word the given word is a prefix of,
    found by the GIN indexes. The word consists of letters, digits and decimal points, none of which
    is an operator of a text search query.
    """
    text_query = func.to_tsquery(literal_column(_postgresql_text_config), f'{word}{_postgresql_prefix_marker}')

    # The events matching through their own columns ..
    event_words = _postgresql_search_words(f'{event_table.name}.', search_columns)
    is_event_match = literal_column(event_words).op('@@')(text_query)

    # .. and the ones matching through their payload.
    payload_words = _postgresql_search_words(f'{event_payload_table.name}.', payload_search_columns)
    is_matching_payload = literal_column(payload_words).op('@@')(text_query)

    matching_payload_ids = select(event_payload_table.c.id)
    matching_payload_ids = matching_payload_ids.where(is_matching_payload)
    is_payload_match = event_table.c.payload_id.in_(matching_payload_ids)

    # PostgreSQL reads an OR of the two conditions with a scan of the whole table, so each one selects its ids
    # through its own index, the GIN index of the event words and the index of payload ids, and the event matches
    # when its id is in their union.
    event_match_ids = select(event_table.c.id)
    event_match_ids = event_match_ids.where(is_event_match)

    payload_match_ids = select(event_table.c.id)
    payload_match_ids = payload_match_ids.where(is_payload_match)

    out = event_table.c.id.in_(union(event_match_ids, payload_match_ids))
    return out

# ################################################################################################################################

def match_event_search(event_table:'Table', event_payload_table:'Table', words:'strlist') -> 'any_':
    """ The events that have, for each of the words of a query, a word it is a prefix of, in their searched columns
    or in their payload, found by the native indexes of the database.
    """
    word_conditions:'anylist' = []

    for word in words:
        condition = _postgresql_word_match(event_table, event_payload_table, word)
        word_conditions.append(condition)

    out = and_(*word_conditions)
    return out

# ################################################################################################################################
# ################################################################################################################################
