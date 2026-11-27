# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The conditions of PostgreSQL after which a transaction may be run again as it was - SQLSTATE codes
# that pg8000 reports in the first argument of its exceptions, and connections that were lost -
# and the errors of PostgreSQL caused by the values of one statement.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.exc import DBAPIError

    # Dummy assignments to satisfy type checkers
    DBAPIError = DBAPIError

# ################################################################################################################################
# ################################################################################################################################

class SQLState:
    Deadlock_Detected      = '40P01'
    Serialization_Failure  = '40001'
    Lock_Not_Available     = '55P03'
    Admin_Shutdown         = '57P01'
    Crash_Shutdown         = '57P02'
    Cannot_Connect_Now     = '57P03'
    Idle_Session_Timeout   = '57P05'
    Idle_In_Transaction_Session_Timeout = '25P03'

# The first two characters of an SQLSTATE code, which name the class of the condition
class SQLStateClass:
    Length                         = 2
    Data_Exception                 = '22'
    Integrity_Constraint_Violation = '23'
    Insufficient_Resources         = '53'

# The conflicts with concurrent transactions after which PostgreSQL rolled the transaction back as a whole.
# A lock timeout is not among them, a batch that reaches one is split so that only the callers of the locked rows fail.
_conflict_states = {
    SQLState.Deadlock_Detected,
    SQLState.Serialization_Failure,
}

# The conditions in which a transaction that failed may be started again unchanged.
_transient_states = {
    SQLState.Deadlock_Detected,
    SQLState.Serialization_Failure,
    SQLState.Lock_Not_Available,
    SQLState.Admin_Shutdown,
    SQLState.Crash_Shutdown,
    SQLState.Cannot_Connect_Now,
    SQLState.Idle_Session_Timeout,
    SQLState.Idle_In_Transaction_Session_Timeout,
}

# The SQLSTATE classes of the conditions in which a transaction that failed succeeds unchanged once the server
# has the resources again - insufficient resources, such as a full disk, exhausted memory or too many connections.
_transient_classes = {SQLStateClass.Insufficient_Resources}

# The SQLSTATE classes of the errors caused by the values of one statement - data exceptions
# and integrity constraint violations.
_value_error_classes = {SQLStateClass.Data_Exception, SQLStateClass.Integrity_Constraint_Violation}

# ################################################################################################################################
# ################################################################################################################################

def get_sqlstate(error:'DBAPIError') -> 'str':
    """ Returns the SQLSTATE code of a PostgreSQL error, or an empty string for an error that has none,
    such as a connection that pg8000 lost.
    """
    args = error.orig.args

    if args and isinstance(args[0], dict):
        out = args[0]['C']
    else:
        out = ''

    return out

# ################################################################################################################################

def get_sqlstate_class(sqlstate:'str') -> 'str':
    """ Returns the class of an SQLSTATE code, which is its first two characters.
    """
    out = sqlstate[:SQLStateClass.Length]
    return out

# ################################################################################################################################

def is_conflict(error:'DBAPIError') -> 'bool':
    """ Whether a transaction failed on a conflict with concurrent transactions, which leaves nothing of it committed.
    """
    sqlstate = get_sqlstate(error)
    out = sqlstate in _conflict_states

    return out

# ################################################################################################################################

def is_value_error(error:'DBAPIError') -> 'bool':
    """ Whether PostgreSQL rejected a value that a statement was to write, which fails again however often it is run.
    """
    sqlstate = get_sqlstate(error)
    sqlstate_class = get_sqlstate_class(sqlstate)

    out = sqlstate_class in _value_error_classes
    return out

# ################################################################################################################################

def is_lock_timeout(error:'DBAPIError') -> 'bool':
    """ Whether PostgreSQL ended the wait for a lock after the lock timeout of the transaction.
    """
    sqlstate = get_sqlstate(error)
    out = sqlstate == SQLState.Lock_Not_Available

    return out

# ################################################################################################################################

def is_transient(error:'DBAPIError') -> 'bool':
    """ Whether a failed transaction may be started again unchanged - after a deadlock, a serialization failure,
    a lock that was not available, a server that shut down or restarted, a connection that was lost,
    a connection that could not be opened, or a server that ran out of disk space, memory or connections.
    """
    if error.connection_invalidated:
        out = True

    # The driver reports each socket error, including those of a connection being opened, with the OSError as its cause.
    elif isinstance(error.orig.__cause__, OSError):
        out = True

    else:
        sqlstate = get_sqlstate(error)
        sqlstate_class = get_sqlstate_class(sqlstate)
        out = sqlstate in _transient_states or sqlstate_class in _transient_classes

    return out

# ################################################################################################################################
# ################################################################################################################################
