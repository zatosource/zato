# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# pg8000
from pg8000 import core
from pg8000.dbapi import ProgrammingError

# pytest
import pytest

# zato_pg_wire
from zato_pg_wire.zato_pg_wire import RowDecoder

# Zato
from zato.common.db_env import pg8000_wire

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anylist

    any_ = any_
    anylist = anylist
    Engine = Engine
    MonkeyPatch = MonkeyPatch

# ################################################################################################################################
# ################################################################################################################################

# A select of a value of each type the decoder reads natively or through a converter, NULLs and infinite timestamps included.
_typed_select = """
select
    '-32768'::int2,
    2147483647::int4,
    '-9223372036854775808'::int8,
    '1.5e300'::float8,
    '-0.0001'::float8,
    'Infinity'::float8,
    true,
    false,
    '2024-02-29 12:34:56.789012'::timestamp,
    '2024-02-29 12:34:56.789012+02'::timestamptz,
    '1999-12-31 23:59:59.999999'::timestamp,
    '0001-01-01 00:00:00'::timestamp,
    'infinity'::timestamp,
    '-infinity'::timestamptz,
    '\\x00ff10'::bytea,
    ''::bytea,
    'Jane Doe - Zürich'::text,
    'John Smith'::varchar(20),
    'pg_class'::name,
    'abc'::char(5),
    '12.345'::numeric,
    '{"amount": 1}'::json,
    null::int8,
    null::bytea,
    null::timestamptz
"""

# The same select with one parameter, which makes pg8000 execute it as a prepared statement.
_typed_select_prepared = _typed_select + ', %s::int4'

# How many rows the select of many rows returns.
_many_rows = 5000

# The sizes of the bytea values sent as parameters, one of them larger than a part of a message kept inline.
_bytea_sizes = (0, 1, 1000, pg8000_wire.Max_Inline_Size + 4464, 5_000_000)

# ################################################################################################################################
# ################################################################################################################################

class _CustomerName(str):
    """ A name of a customer as an instance of a subclass of str.
    """

# ################################################################################################################################
# ################################################################################################################################

def _execute(cursor:'any_', query:'str', params:'any_'=()) -> 'anylist':
    """ Executes a query and returns all of its rows as lists.
    """
    _ = cursor.execute(query, params)

    out:'anylist' = []

    for row in cursor.fetchall():
        out.append(list(row))

    return out

# ################################################################################################################################

def _statement_name(connection:'any_', query:'str') -> 'str':
    """ Returns the server-side name of the statement a connection prepared for a query without type OIDs.
    """
    key = (query, ())
    prepared = connection.driver_connection._zato_statements[key]

    name_bin = prepared.name_bin
    name_bin = name_bin.rstrip(b'\x00')

    out = name_bin.decode('ascii')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestStatementCache:
    """ A connection prepares each statement once and executes it by its name afterwards.
    """

    def test_prepared_once(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        for idx in range(5):
            rows = _execute(cursor, 'select %s::int4 + 1', (idx,))
            assert rows == [[idx + 1]]

        # The server has the statement once, and it was executed each time.
        name = _statement_name(connection, 'select $1::int4 + 1')
        rows = _execute(cursor, 'select generic_plans + custom_plans from pg_prepared_statements where name = %s', (name,))

        assert rows == [[5]]

        connection.close()

    def test_one_round_trip(self, engine:'Engine', monkeypatch:'MonkeyPatch') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        # The transaction is open and the statement is prepared ..
        _ = _execute(cursor, 'select %s::int4', (1,))

        flushes:'anylist' = []
        core_flush = core._flush

        def count_flush(sock:'any_') -> 'None':
            flushes.append(sock)
            core_flush(sock)

        monkeypatch.setattr(core, '_flush', count_flush)

        # .. so each execution takes one round trip ..
        for idx in range(3):
            _ = _execute(cursor, 'select %s::int4', (idx,))

        assert len(flushes) == 3

        # .. and a statement prepared anew takes two.
        flushes.clear()
        _ = _execute(cursor, 'select %s::int8', (1,))

        assert len(flushes) == 2

        connection.close()

    def test_eviction(self, engine:'Engine', monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.setattr(pg8000_wire, 'Max_Statements', 3)

        connection = engine.raw_connection()
        cursor = connection.cursor()

        for idx in range(5):
            rows = _execute(cursor, f'select %s::int4 + {idx}', (1,))
            assert rows == [[1 + idx]]

        # The statements used least recently are closed on the server too.
        rows = _execute(cursor, 'select count(*) from pg_prepared_statements where name like %s', ('zato_%',))

        assert rows == [[3]]
        assert len(connection.driver_connection._zato_statements) == 3

        connection.close()

    def test_rollback_keeps_statements(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        rows = _execute(cursor, 'select %s::text', ('John Smith',))
        assert rows == [['John Smith']]

        connection.rollback()

        rows = _execute(cursor, 'select %s::text', ('Jane Doe',))
        assert rows == [['Jane Doe']]

        connection.close()

    def test_schema_change(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        _ = cursor.execute('create temporary table customer (id int4)')
        _ = cursor.execute('insert into customer values (%s)', (1,))

        rows = _execute(cursor, 'select * from customer where id = %s', (1,))
        assert rows == [[1]]

        _ = cursor.execute("alter table customer add column name text default 'Maria Johnson'")

        # The result of the prepared statement changed, so the server rejects it once ..
        with pytest.raises(ProgrammingError) as error_info:
            _ = cursor.execute('select * from customer where id = %s', (1,))

        error = error_info.value.args[0]
        assert error['C'] == '0A000'

        connection.rollback()

        # .. and the connection prepares it anew.
        _ = cursor.execute('create temporary table customer (id int4, name text)')
        _ = cursor.execute('insert into customer values (%s, %s)', (1, 'Maria Johnson'))

        rows = _execute(cursor, 'select * from customer where id = %s', (1,))
        assert rows == [[1, 'Maria Johnson']]

        connection.close()

# ################################################################################################################################
# ################################################################################################################################

class TestResults:
    """ The rows of a prepared statement are the same as the ones pg8000 reads from the text format.
    """

    def test_types(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        # A query without parameters is executed by pg8000 itself, with every column in the text format ..
        text_rows = _execute(cursor, _typed_select)

        # .. while one with parameters is prepared and decoded by the row decoder.
        decoded_rows = _execute(cursor, _typed_select_prepared, (7,))

        text_row = text_rows[0]
        decoded_row = decoded_rows[0]
        last_value = decoded_row.pop()

        assert last_value == 7
        assert decoded_row == text_row

        # The values are compared together with their types and time zones.
        for decoded_value, text_value in zip(decoded_row, text_row):
            assert type(decoded_value) is type(text_value)

        timestamptz = decoded_row[9]
        assert timestamptz == datetime(2024, 2, 29, 10, 34, 56, 789012, tzinfo=timezone.utc)
        assert timestamptz.utcoffset() == timezone.utc.utcoffset(None)

        connection.close()

    def test_many_rows(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        query = """
            select id, id::text, now() - id * interval '1 second', mod(id, 2) = 0, decode(md5(id::text), 'hex')
            from generate_series(1, {}) as id
        """.format(_many_rows)

        text_rows = _execute(cursor, query)
        decoded_rows = _execute(cursor, query + ' where %s::int4 = 1', (1,))

        assert len(decoded_rows) == _many_rows
        assert decoded_rows == text_rows

        connection.close()

# ################################################################################################################################
# ################################################################################################################################

class TestParameters:
    """ Parameters reach the server unchanged, bytea values in the binary format and anything else as text.
    """

    def test_bytea(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        for size in _bytea_sizes:
            value = bytes(range(256)) * (size // 256) + b'\x00' * (size % 256)

            rows = _execute(cursor, 'select %s::bytea, length(%s::bytea)', (value, value))
            assert rows == [[value, size]]

        connection.close()

    def test_bytes_like(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        value = b'Purchase order 4500012345'

        for param in (bytearray(value), memoryview(value)):
            rows = _execute(cursor, 'select %s::bytea', (param,))
            assert rows == [[value]]

        connection.close()

    def test_null_and_text(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        rows = _execute(cursor, 'select %s::bytea, %s::text, %s::int8', (None, 'Anna Miller - Zürich', None))
        assert rows == [[None, 'Anna Miller - Zürich', None]]

        connection.close()

    def test_text_subclass(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        # SQLAlchemy sends names of tables as instances of a subclass of str.
        value = _CustomerName('Jane Doe')

        rows = _execute(cursor, 'select %s::text', (value,))
        assert rows == [['Jane Doe']]

        connection.close()

    def test_placeholders(self, engine:'Engine') -> 'None':
        connection = engine.raw_connection()
        cursor = connection.cursor()

        for idx in range(3):
            rows = _execute(cursor, 'select %s::int4, %s::int4 %% 2', (idx, idx))
            assert rows == [[idx, idx % 2]]

        connection.close()

# ################################################################################################################################
# ################################################################################################################################

class TestRowDecoder:
    """ The row decoder rejects a message shorter than its lengths declare.
    """

    def test_truncated(self) -> 'None':
        decoder = RowDecoder([(23, int)])

        with pytest.raises(ValueError):
            _ = decoder.decode(b'\x00\x01\x00\x00\x00\x04\x00\x00')

    def test_result_formats(self) -> 'None':
        decoder = RowDecoder([(23, int), (25, str), (1700, float), (17, bytes)])
        assert decoder.result_formats == [1, 0, 0, 1]

# ################################################################################################################################
# ################################################################################################################################
