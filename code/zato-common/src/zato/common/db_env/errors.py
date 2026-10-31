# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The conditions of PostgreSQL after which a transaction may be run again as it was - SQLSTATE codes
# that pg8000 reports in the first argument of its exceptions, and connections that were lost.

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

# The conflicts with concurrent transactions after which PostgreSQL rolled the transaction back as a whole.
_conflict_states = {
    SQLState.Deadlock_Detected,
    SQLState.Serialization_Failure,
    SQLState.Lock_Not_Available,
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

# The SQLSTATE classes of the errors caused by the values of one statement - data exceptions
# and integrity constraint violations.
_value_error_classes = {'22', '23'}

# ################################################################################################################################
# ################################################################################################################################

def get_sqlstate(error:'DBAPIError') -> 'str':
    """ Returns the SQLSTATE code of a PostgreSQL error, or an empty string for any other database.
    """
    args = error.orig.args

    if args and isinstance(args[0], dict):
        out = args[0]['C']
    else:
        out = ''

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
    sqlstate_class = sqlstate[:2]

    out = sqlstate_class in _value_error_classes
    return out

# ################################################################################################################################

def is_transient(error:'DBAPIError') -> 'bool':
    """ Whether a failed transaction may be started again unchanged - after a deadlock, a serialization failure,
    a lock that was not available, a server that shut down or restarted, a connection that was lost,
    or a connection that could not be opened.
    """
    if error.connection_invalidated:
        out = True

    # The driver reports each socket error, including those of a connection being opened, with the OSError as its cause.
    elif isinstance(error.orig.__cause__, OSError):
        out = True

    else:
        sqlstate = get_sqlstate(error)
        out = sqlstate in _transient_states

    return out

# ################################################################################################################################
# ################################################################################################################################
