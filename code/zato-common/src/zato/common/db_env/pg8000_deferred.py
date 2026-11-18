# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The replies that the connections of pg8000 read after the statements that follow them. Within deferred_replies,
# a statement is sent without its reply being read, and the reply is read when the rows of the statement are needed,
# or with the reply of the next statement that is read at once. A statement whose rows are checked, e.g. the fence
# of the generation, is confirmed before any statement that is read at once is sent, so the commit of a transaction
# never travels to the server before the checks of the transaction are confirmed.

# stdlib
from contextlib import contextmanager
from typing import NamedTuple

# pg8000
from pg8000 import core
from pg8000.core import IN_FAILED_TRANSACTION, IN_TRANSACTION
from pg8000.exceptions import DatabaseError, InterfaceError
from pg8000.legacy import IntegrityError, ProgrammingError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_, anytuple, callable_
    any_ = any_
    anytuple = anytuple
    callable_ = callable_
    Connection = Connection
    anyiter = Iterator[any_]
    noneiter = Iterator[None]

deferred_reply_list = list['DeferredReply']

# ################################################################################################################################
# ################################################################################################################################

# The driver whose connections defer their replies.
_driver_name = 'pg8000'

# The statement with which pg8000 rolls a transaction back.
_rollback_statement = 'rollback'

# The statuses of a connection within a transaction, as the server reports them.
_transaction_statuses = (IN_TRANSACTION, IN_FAILED_TRANSACTION)

# The SQLSTATE codes of a prepared statement the server no longer has, or whose result changed with the schema.
_stale_statement_codes = {'26000', '0A000'}

# The SQLSTATE codes that a cursor of pg8000 reports with an error class of their own.
_auth_error_code = '28000'
_unique_violation_code = '23505'

# ################################################################################################################################
# ################################################################################################################################

class DeferredReply(NamedTuple):
    """ A statement that was sent without its reply being read, with the key of its prepared statement.
    """
    context: 'any_'
    key: 'anytuple'

# ################################################################################################################################
# ################################################################################################################################

class PendingRows(list):
    """ The rows of a statement whose reply was not read yet, which read it before the first row is returned.
    """
    def __init__(self, connection:'any_', context:'any_') -> 'None':
        super().__init__()
        self._connection = connection
        self._context = context

    def __iter__(self) -> 'anyiter':
        out = self._iter_rows()
        return out

    def _iter_rows(self) -> 'anyiter':
        if self._context.zato_is_pending:
            read_pending(self._connection, self._context)

        yield from list.__iter__(self)

# ################################################################################################################################
# ################################################################################################################################

def in_transaction(self:'any_') -> 'bool':
    """ Whether a connection is in a transaction, including one whose begin was sent and whose reply was not read yet.
    """
    if self._zato_pending_begin is not None:
        out = True
    else:
        out = self._transaction_status in _transaction_statuses

    return out

# ################################################################################################################################

def forget_stale_statement(self:'any_', key:'anytuple', error:'DatabaseError') -> 'None':
    """ Removes a prepared statement that the server no longer has, or whose result changed with the schema,
    so that it is prepared anew next time.
    """
    error_fields = error.args[0]

    if error_fields['C'] in _stale_statement_codes:
        if key in self._zato_statements:
            del self._zato_statements[key]

# ################################################################################################################################

def _as_cursor_error(error:'Exception') -> 'Exception':
    """ Returns the error of a reply as a cursor of pg8000 raises it, with the class of its SQLSTATE code.
    """
    if type(error) is DatabaseError:
        message = error.args[0]
        code = message['C']

        if code == _auth_error_code:
            out = InterfaceError(message)
        elif code == _unique_violation_code:
            out = IntegrityError(message)
        else:
            out = ProgrammingError(message)

    else:
        out = error

    return out

# ################################################################################################################################

def _run_check(context:'any_') -> 'None':
    """ Gives the number of rows of a statement whose reply was read to the check of the statement, if it has one.
    """
    if context.zato_check is not None:
        row_count = len(context.rows)
        context.zato_check(row_count)

# ################################################################################################################################

def read_deferred(self:'any_', last:'any_') -> 'Exception | None':
    """ Reads the reply to a pending begin, if there is one, and then the replies to the deferred statements in the order
    they were sent, up to and including the one of the context given, or all of them for None. Returns the first error
    among them, once every reply up to there was read, so that the socket holds no reply of a statement read already.
    """
    first_error:'Exception | None' = None

    # The begin was written first ..
    begin_context = self._zato_pending_begin

    if begin_context is not None:
        self._zato_pending_begin = None

        try:
            self.handle_messages(begin_context)
        except DatabaseError as e:
            first_error = e

    # .. and the deferred statements followed it.
    deferred:'deferred_reply_list' = self._zato_deferred

    while deferred:
        reply = deferred.pop(0)
        context = reply.context
        context.zato_is_pending = False

        try:
            self.handle_messages(context)

        except DatabaseError as e:
            forget_stale_statement(self, reply.key, e)
            if first_error is None:
                first_error = e

        # A statement that succeeded has its rows checked, which raises if they are not what the check expects.
        else:
            try:
                _run_check(context)
            except Exception as e:
                if first_error is None:
                    first_error = e

        if context is last:
            break

    return first_error

# ################################################################################################################################

def read_pending(self:'any_', context:'any_') -> 'None':
    """ Reads the reply to a deferred statement, after the replies to the statements sent before it,
    and raises the first error among them as a cursor of pg8000 would.
    """
    core._flush(self._sock)
    first_error = read_deferred(self, context)

    if first_error is not None:
        raise _as_cursor_error(first_error)

# ################################################################################################################################

def confirm_checks(self:'any_', statement:'str') -> 'None':
    """ Reads the deferred replies up to the last one whose rows are checked, before a statement whose reply is read
    at once is sent, so that no such statement, e.g. the commit, travels to the server before the checks are confirmed.
    A rollback is sent without them, because it undoes whatever the checks would have refused.
    """
    if statement == _rollback_statement:
        return

    last_checked = None

    for reply in self._zato_deferred:
        if reply.context.zato_check is not None:
            last_checked = reply.context

    if last_checked is not None:
        read_pending(self, last_checked)

# ################################################################################################################################

def raises_deferred_errors(statement:'str') -> 'bool':
    """ Whether the errors of the deferred replies are raised by a statement whose reply is read after them.
    A rollback ends the transaction in which they occurred, so it does not raise them.
    """
    out = statement != _rollback_statement
    return out

# ################################################################################################################################

def can_defer_reply(self:'any_', stream:'any_') -> 'bool':
    """ Whether the reply to a statement can be read after the statement is sent - only within deferred_replies,
    only for a statement that streams nothing, and only within a transaction.
    """
    out = False

    if self._zato_defers_replies:
        if stream is None:
            out = in_transaction(self)

    return out

# ################################################################################################################################

def defer_reply(self:'any_', context:'any_', key:'anytuple') -> 'None':
    """ Records a statement whose reply is read later, giving a statement that returns rows the rows that read it.
    """
    context.zato_is_pending = True

    if context.rows is not None:
        context.rows = PendingRows(self, context)

    reply = DeferredReply(context, key)
    self._zato_deferred.append(reply)

# ################################################################################################################################

def check_rows(connection:'Connection', cursor:'any_', check:'callable_') -> 'None':
    """ Gives the number of rows of the statement that a cursor executed last to a check, once its reply is read.
    The reply to a statement of pg8000 deferred within deferred_replies is read with that of a later statement,
    and always before a statement whose reply is read at once is sent.
    """
    if connection.dialect.driver == _driver_name:
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
    if connection.dialect.driver == _driver_name:
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
