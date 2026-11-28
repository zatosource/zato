# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pg8000
from pg8000 import core
from pg8000.dbapi import DatabaseError

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.exc import InterfaceError

# Zato
from zato.common.db_env.pg8000_common import deferred_replies
from zato.common.typing_ import cast_

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

class ModuleCtx:

    # How many rows the large result has, and how long the text of each row is
    Large_Row_Count = 20_000
    Large_Value_Size = 100

    # How many rows the statement that fails after its rows returns before the division by zero, and the SQLSTATE
    # of the division by zero
    Rows_Before_Error = 99
    Division_By_Zero = '22012'

    # How many rows the statement of the notices returns, and the prefix of the message of each notice
    Notice_Row_Count = 3
    Notice_Prefix = 'Customer '

    # The statement that returns the large result
    Select_Large = 'select g, repeat(%s, %s) from generate_series(1, %s) as g'

    # The statement that fails once it reaches the row after the ones it returned
    Select_Until_Error = 'select 1 / (%s - g) from generate_series(1, %s) as g'

    # The function that raises a notice for each row that it returns, and the statement that calls it
    Create_Notice_Function = """
        create function pg_temp.customer_notice(customer_id int4) returns int4 language plpgsql as $$
        begin
            raise notice using message = 'Customer ' || customer_id;
            return customer_id;
        end
        $$
    """
    Select_Notices = 'select pg_temp.customer_notice(g) from generate_series(1, %s) as g'

    # The statements of the deferred replies - the table of customers, the insert of a customer,
    # the select of customers up to an ID and the number of customers
    Create_Customer = 'create temporary table customer (id int4 primary key)'
    Insert_Customer = 'insert into customer values (%s)'
    Select_Customers = 'select id from customer where id <= %s order by id'
    Count_Customers = 'select count(*) from customer where id > %s'

    # How many customers the deferred replies insert
    Customer_Count = 4

    # The statement that returns the process ID of the backend of a connection
    Backend_PID = 'select pg_backend_pid()'

# ################################################################################################################################
# ################################################################################################################################

class _ReadCounter:
    """ Counts the reads of the socket of a connection, and resets the connection on the read given, if any.
    """
    def __init__(self, read:'any_', reset_on:'int'=0) -> 'None':
        self._read = read
        self._reset_on = reset_on
        self.count = 0

    def __call__(self, size:'int') -> 'bytes':
        self.count += 1

        if self.count == self._reset_on:
            raise ConnectionResetError('Connection reset by the test')

        out = self._read(size)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestReplyParser:
    """ zato_pg_wire parses the replies of the server for the connections of pg8000.
    """

    def test_result_larger_than_one_read(self, engine:'Engine') -> 'None':
        """ A result larger than one read of the socket returns every row in order.
        """
        connection = engine.raw_connection()
        wire = connection.driver_connection._sock

        counter = _ReadCounter(wire.read1)
        wire.read1 = counter

        value = 'x'
        cursor = connection.cursor()
        _ = cursor.execute(ModuleCtx.Select_Large, (value, ModuleCtx.Large_Value_Size, ModuleCtx.Large_Row_Count))
        rows = cursor.fetchall()

        expected_value = value * ModuleCtx.Large_Value_Size
        expected = [[idx, expected_value] for idx in range(1, ModuleCtx.Large_Row_Count + 1)]

        assert [list(row) for row in rows] == expected
        assert counter.count > 1

        wire.read1 = wire._socket.recv

        connection.rollback()
        connection.close()

    def test_error_after_rows(self, engine:'Engine') -> 'None':
        """ A statement that fails after returning rows raises its error, and the connection serves the next statement.
        """
        connection = engine.raw_connection()
        cursor = connection.cursor()

        divisor_row = ModuleCtx.Rows_Before_Error + 1
        row_count = divisor_row * 2

        with pytest.raises(DatabaseError) as raised:
            _ = cursor.execute(ModuleCtx.Select_Until_Error, (divisor_row, row_count))

        error = raised.value.args[0]
        assert error['C'] == ModuleCtx.Division_By_Zero

        connection.rollback()

        _ = cursor.execute('select %s::text', ('Anna Miller',))
        assert [list(row) for row in cursor.fetchall()] == [['Anna Miller']]

        connection.close()

    def test_notices_between_rows(self, engine:'Engine') -> 'None':
        """ A RAISE NOTICE between rows reaches the notice handler of the connection.
        """
        connection = engine.raw_connection()
        driver_connection = connection.driver_connection
        driver_connection.notices.clear()

        cursor = connection.cursor()
        _ = cursor.execute(ModuleCtx.Create_Notice_Function)
        _ = cursor.execute(ModuleCtx.Select_Notices, (ModuleCtx.Notice_Row_Count,))
        rows = cursor.fetchall()

        customer_ids = list(range(1, ModuleCtx.Notice_Row_Count + 1))
        assert [row[0] for row in rows] == customer_ids

        messages = [notice[b'M'].decode('utf8') for notice in driver_connection.notices]
        assert messages == [f'{ModuleCtx.Notice_Prefix}{customer_id}' for customer_id in customer_ids]

        connection.rollback()
        connection.close()

    def test_deferred_replies_of_several_statements(self, engine:'Engine', monkeypatch:'MonkeyPatch') -> 'None':
        """ Deferred replies of several statements followed by a statement read at once return each reply
        to its own statement.
        """
        with engine.connect() as connection:

            _ = connection.exec_driver_sql(ModuleCtx.Create_Customer)

            for customer_id in range(1, ModuleCtx.Customer_Count + 1):
                _ = connection.exec_driver_sql(ModuleCtx.Insert_Customer, (customer_id,))

            # The statements are prepared before the replies are counted ..
            _ = connection.exec_driver_sql(ModuleCtx.Select_Customers, (0,)).all()
            _ = connection.exec_driver_sql(ModuleCtx.Count_Customers, (0,)).scalar_one()

            flushes:'anylist' = []
            core_flush = core._flush

            def count_flush(sock:'any_') -> 'None':
                flushes.append(sock)
                core_flush(sock)

            monkeypatch.setattr(core, '_flush', count_flush)

            # .. the selects are sent without their replies being read ..
            with deferred_replies(connection):
                results = []

                for customer_id in range(1, ModuleCtx.Customer_Count):
                    result = connection.exec_driver_sql(ModuleCtx.Select_Customers, (customer_id,))
                    results.append(result)

                assert not flushes

                # .. the count is read at once, in one round trip with the selects before it ..
                count = connection.exec_driver_sql(ModuleCtx.Count_Customers, (1,)).scalar_one()

            assert count == ModuleCtx.Customer_Count - 1
            assert len(flushes) == 1

            # .. and each select has the rows of its own reply.
            for customer_id, result in enumerate(results, 1):
                expected = [(idx,) for idx in range(1, customer_id + 1)]
                assert result.all() == expected

    def test_connection_reset_in_reply(self, engine:'Engine') -> 'None':
        """ A connection reset in the middle of a reply raises InterfaceError, and the pool discards the connection.
        """
        with engine.connect() as connection:

            backend_pid = connection.exec_driver_sql(ModuleCtx.Backend_PID).scalar_one()

            wire = connection.connection.driver_connection._sock
            counter = _ReadCounter(wire.read1, reset_on=2)
            wire.read1 = counter

            params = ('x', ModuleCtx.Large_Value_Size, ModuleCtx.Large_Row_Count)

            with pytest.raises(InterfaceError) as raised:
                _ = connection.exec_driver_sql(ModuleCtx.Select_Large, params).all()

            assert raised.value.connection_invalidated
            assert connection.invalidated

        # The next connection of the pool is a new one, with a backend of its own.
        with engine.connect() as connection:
            next_backend_pid = connection.exec_driver_sql(ModuleCtx.Backend_PID).scalar_one()

        driver_error = cast_('BaseException', raised.value.orig)
        assert str(driver_error) == 'network error'
        assert next_backend_pid != backend_pid

# ################################################################################################################################
# ################################################################################################################################
