# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The parts of the extensions of pg8000 that the users of the Zato database call, none of which imports pg8000,
# so that a process whose databases are all SQLite never loads the driver.

# stdlib
from contextlib import contextmanager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_, callable_
    any_ = any_
    callable_ = callable_
    Connection = Connection
    noneiter = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The driver whose connections defer their replies.
Driver_Name = 'pg8000'

# A value at least this large is written to the socket as it is, rather than copied into the buffer of its message.
Max_Inline_Size = 65536

# ################################################################################################################################
# ################################################################################################################################

def check_rows(connection:'Connection', cursor:'any_', check:'callable_') -> 'None':
    """ Gives the number of rows of the statement that a cursor executed last to a check, once its reply is read.
    The reply to a statement of pg8000 deferred within deferred_replies is read with that of a later statement,
    and always before a statement whose reply is read at once is sent.
    """
    if connection.dialect.driver == Driver_Name:
        context = cursor._context

        if context.zato_is_pending:
            context.zato_check = check
        else:
            row_count = len(context.rows)
            check(row_count)

    else:
        rows = cursor.fetchall()
        row_count = len(rows)
        check(row_count)

# ################################################################################################################################

@contextmanager
def deferred_replies(connection:'Connection') -> 'noneiter':
    """ Within the block, each statement of the connection is sent without its reply being read, and its reply is read
    when its rows are needed, or with that of the next statement whose reply is read at once, e.g. the commit.
    An error of such a statement is raised by that later read. The row count of a statement that returns no rows
    is not known within the block. A connection of a driver other than pg8000 reads each reply as usual.
    """
    if connection.dialect.driver == Driver_Name:
        dbapi_connection = connection.connection.dbapi_connection
        defers_replies = dbapi_connection._zato_defers_replies
        dbapi_connection._zato_defers_replies = True

        try:
            yield
        finally:
            dbapi_connection._zato_defers_replies = defers_replies

    else:
        yield

# ################################################################################################################################
# ################################################################################################################################
