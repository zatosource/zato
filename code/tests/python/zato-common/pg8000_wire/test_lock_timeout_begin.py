# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# pg8000
from pg8000 import core

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.db_env.errors import is_lock_timeout
from zato.common.db_env.pg8000_common import lock_timeout_begin
from zato.common.pubsub.subscription_list import Lock_Timeout_Ms

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

    # The lock timeout of pub/sub as the server reports it, and the lock timeout of a session that sets none
    Lock_Timeout_Shown = '5s'
    Default_Lock_Timeout_Shown = '0'

    # The lock timeout of the test of a lock held by another session, in milliseconds, and how long the wait may take
    # in proportion to it
    Short_Lock_Timeout_Ms = 500
    Wait_Max_Share = 4

    # The advisory lock that one session holds and another one waits for
    Advisory_Lock_Key = 4711

    # The statement that reads the lock timeout of the transaction, and the statement that takes the advisory lock
    Show_Lock_Timeout = 'show lock_timeout'
    Take_Advisory_Lock = 'select pg_advisory_xact_lock(%s)'

# ################################################################################################################################
# ################################################################################################################################

def _show_lock_timeout(cursor:'any_') -> 'str':
    """ Returns the lock timeout of the transaction of a cursor as the server reports it.
    """
    _ = cursor.execute(ModuleCtx.Show_Lock_Timeout)
    rows = cursor.fetchall()

    out = rows[0][0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLockTimeoutBegin:
    """ A transaction begun within lock_timeout_begin sets its lock timeout in the simple query of its begin.
    """

    def test_lock_timeout_within_transaction(self, engine:'Engine') -> 'None':
        """ The transaction has the lock timeout, and the next transaction, begun outside of the block, does not.
        """
        connection = engine.raw_connection()
        cursor = connection.cursor()

        with lock_timeout_begin(Lock_Timeout_Ms):
            assert _show_lock_timeout(cursor) == ModuleCtx.Lock_Timeout_Shown

        connection.commit()

        assert _show_lock_timeout(cursor) == ModuleCtx.Default_Lock_Timeout_Shown

        connection.close()

    def test_default_without_block(self, engine:'Engine') -> 'None':
        """ A transaction begun outside of the block has the lock timeout of the server.
        """
        connection = engine.raw_connection()
        cursor = connection.cursor()

        assert _show_lock_timeout(cursor) == ModuleCtx.Default_Lock_Timeout_Shown

        connection.close()

    def test_one_round_trip(self, engine:'Engine', monkeypatch:'MonkeyPatch') -> 'None':
        """ The begin with its lock timeout and the first statement of the transaction go to the server
        in one write of the socket.
        """
        connection = engine.raw_connection()
        cursor = connection.cursor()

        # The statement is prepared in a transaction of its own ..
        _ = _show_lock_timeout(cursor)
        connection.commit()

        flushes:'anylist' = []
        core_flush = core._flush

        def count_flush(sock:'any_') -> 'None':
            flushes.append(sock)
            core_flush(sock)

        monkeypatch.setattr(core, '_flush', count_flush)

        # .. so the begin and the statement take one write.
        with lock_timeout_begin(Lock_Timeout_Ms):
            assert _show_lock_timeout(cursor) == ModuleCtx.Lock_Timeout_Shown

        assert len(flushes) == 1

        connection.rollback()
        connection.close()

    def test_rollback_restores_default(self, engine:'Engine') -> 'None':
        """ A transaction rolled back leaves the next transaction of the same connection with the lock timeout
        of the server.
        """
        connection = engine.raw_connection()
        cursor = connection.cursor()

        with lock_timeout_begin(Lock_Timeout_Ms):
            assert _show_lock_timeout(cursor) == ModuleCtx.Lock_Timeout_Shown

        connection.rollback()

        assert _show_lock_timeout(cursor) == ModuleCtx.Default_Lock_Timeout_Shown

        connection.close()

    def test_lock_held_by_other_session(self, engine:'Engine') -> 'None':
        """ A lock held by another session ends the wait of the first statement that takes it after the lock timeout,
        with the error of a lock timeout.
        """
        holder = engine.raw_connection()
        holder_cursor = holder.cursor()

        # One session holds the lock ..
        _ = holder_cursor.execute(ModuleCtx.Take_Advisory_Lock, (ModuleCtx.Advisory_Lock_Key,))

        try:

            # .. and the other one waits for it only up to its lock timeout.
            with lock_timeout_begin(ModuleCtx.Short_Lock_Timeout_Ms), engine.connect() as waiter:

                start = time.monotonic()

                with pytest.raises(DBAPIError) as raised:
                    _ = waiter.exec_driver_sql(ModuleCtx.Take_Advisory_Lock, (ModuleCtx.Advisory_Lock_Key,))

                elapsed_ms = (time.monotonic() - start) * 1000

            assert is_lock_timeout(raised.value)
            assert elapsed_ms >= ModuleCtx.Short_Lock_Timeout_Ms
            assert elapsed_ms < ModuleCtx.Short_Lock_Timeout_Ms * ModuleCtx.Wait_Max_Share

        finally:
            holder.rollback()
            holder.close()

# ################################################################################################################################
# ################################################################################################################################
