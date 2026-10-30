# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Double, event as sa_event, Integer, LargeBinary, MetaData, \
    select, SmallInteger, String, Table, Text

# Zato
from zato.common.db_env.common import UTC_DateTime
from zato.common.db_env.pg8000_copy import copy_rows, encode_rows, get_copy_plan
from zato.common.db_env.pg8000_wire import Max_Inline_Size

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anylist, dictlist, strlist

    any_ = any_
    anylist = anylist
    dictlist = dictlist
    Engine = Engine
    strlist = strlist

    tablegen = Iterator[Table]

# ################################################################################################################################
# ################################################################################################################################

_metadata = MetaData()

# A table with a column of each type a COPY stream encodes, and an identifier its sequence assigns.
_target_table = Table('copy_target', _metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('event_id', BigInteger),
    Column('attempt', Integer),
    Column('priority', SmallInteger),
    Column('kind', String(50)),
    Column('data', Text),
    Column('content', LargeBinary),
    Column('is_final', Boolean),
    Column('score', Double),
    Column('created_at', DateTime(timezone=True)),
    Column('local_time', DateTime()),
    Column('event_time', UTC_DateTime()),
)

# The columns the rows of a test fill, without the identifier.
_value_columns = ('event_id', 'attempt', 'priority', 'kind', 'data', 'content', 'is_final', 'score', 'created_at',
    'local_time', 'event_time')

# A time zone two hours east of UTC.
_east_zone = timezone(timedelta(hours=2))

# A large content, which a COPY stream sends as a chunk of its own.
_large_content = bytes(range(256)) * ((Max_Inline_Size // 256) + 10)

# ################################################################################################################################
# ################################################################################################################################

def _new_rows() -> 'dictlist':
    """ Returns rows with values of every column type, NULLs and two large contents one after the other.
    """
    out:'dictlist' = [
        {
            'event_id': 9_000_000_000,
            'attempt': 1,
            'priority': -3,
            'kind': 'request',
            'data': 'Purchase order from John Smith - Zürich',
            'content': b'\x00\x01\x02',
            'is_final': True,
            'score': 1.5e300,
            'created_at': datetime(2026, 10, 29, 12, 0, 0, 123456, tzinfo=timezone.utc),
            'local_time': datetime(1999, 12, 31, 23, 59, 59, 999999),
            'event_time': datetime(2026, 10, 29, 14, 0, 0, tzinfo=_east_zone),
        },
        {
            'event_id': 2,
            'attempt': None,
            'priority': None,
            'kind': None,
            'data': None,
            'content': _large_content,
            'is_final': False,
            'score': None,
            'created_at': None,
            'local_time': None,
            'event_time': None,
        },
        {
            'event_id': 3,
            'attempt': 2_147_483_647,
            'priority': 32_767,
            'kind': 'response',
            'data': '',
            'content': _large_content,
            'is_final': None,
            'score': -0.0001,
            'created_at': datetime(1970, 1, 1, tzinfo=timezone.utc),
            'local_time': datetime(2024, 2, 29, 12, 34, 56, 789012),
            'event_time': datetime(2000, 1, 1, tzinfo=timezone.utc),
        },
    ]

    return out

# ################################################################################################################################

def _read_rows(engine:'Engine') -> 'dictlist':
    """ Returns the rows of the table in the order of their identifiers.
    """
    query = select(_target_table).order_by(_target_table.c.id)

    out:'dictlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def target_table(engine:'Engine') -> 'tablegen':
    """ The table the rows are copied into, created for each test and dropped after it.
    """
    _metadata.create_all(engine)
    yield _target_table

    _metadata.drop_all(engine)

# ################################################################################################################################
# ################################################################################################################################

class TestCopyRows:
    """ Rows copied in the binary format are stored as an insert would store them.
    """

    def test_values(self, engine:'Engine', target_table:'Table') -> 'None':
        rows = _new_rows()

        with engine.begin() as connection:
            copy_rows(connection, target_table, rows)

        stored = _read_rows(engine)

        assert len(stored) == len(rows)

        # The sequence of the table assigns the identifiers ..
        identifiers:'anylist' = []

        for stored_row in stored:
            identifiers.append(stored_row['id'])

        assert identifiers == [1, 2, 3]

        # .. and every value reads back as it was given, the points in time in any time zone included.
        for row, stored_row in zip(rows, stored):
            for name in _value_columns:
                assert stored_row[name] == row[name], name

    def test_same_as_insert(self, engine:'Engine', target_table:'Table') -> 'None':
        rows = _new_rows()

        with engine.begin() as connection:
            copy_rows(connection, target_table, rows)

        with engine.begin() as connection:
            _ = connection.execute(target_table.insert(), rows)

        stored = _read_rows(engine)
        copied = stored[:3]
        inserted = stored[3:]

        for copied_row, inserted_row in zip(copied, inserted):
            for name in _value_columns:
                assert copied_row[name] == inserted_row[name], name

    def test_rollback(self, engine:'Engine', target_table:'Table') -> 'None':
        rows = _new_rows()

        with engine.connect() as connection:
            transaction = connection.begin()
            copy_rows(connection, target_table, rows)
            transaction.rollback()

        assert _read_rows(engine) == []

    def test_one_statement(self, engine:'Engine', target_table:'Table') -> 'None':
        statements:'strlist' = []

        def on_execute(conn:'any_', cursor:'any_', sql:'str', parameters:'any_', context:'any_', executemany:'bool') -> 'None':
            statements.append(sql)

        sa_event.listen(engine, 'before_cursor_execute', on_execute)

        with engine.begin() as connection:
            copy_rows(connection, target_table, _new_rows())

        sa_event.remove(engine, 'before_cursor_execute', on_execute)

        column_list = ', '.join(_value_columns)
        expected = f'COPY copy_target ({column_list}) FROM STDIN WITH (FORMAT binary)'

        assert statements == [expected]

# ################################################################################################################################
# ################################################################################################################################

class TestEncodeRows:
    """ A COPY stream keeps small values in a shared chunk and sends each large value as a chunk of its own.
    """

    def test_chunks(self, engine:'Engine') -> 'None':
        names = tuple(_value_columns)
        plan = get_copy_plan(engine.dialect, _target_table, names)

        chunks = encode_rows(plan, _new_rows())

        large_chunks:'anylist' = []

        for chunk in chunks:
            if chunk is _large_content:
                large_chunks.append(chunk)

        assert len(large_chunks) == 2

        # The stream begins with the signature of the binary format and ends with the field count of -1.
        first_chunk = chunks[0]
        last_chunk = chunks[-1]

        assert first_chunk.startswith(b'PGCOPY\n\xff\r\n\x00')
        assert last_chunk.endswith(b'\xff\xff')

# ################################################################################################################################
# ################################################################################################################################
