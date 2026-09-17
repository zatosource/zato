# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from logging import getLogger
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.pool import QueuePool as SAQueuePool
from sqlalchemy.pool.dbapi_proxy import _DBProxy

# Zato
from zato.common.api import MS_SQL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict, strdictnone, strset
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Matches either a single-quoted string literal, which is left as it is, or a :name marker to bind
_marker_pattern = re.compile(r"'(?:[^']|'')*'|(?<![:\w]):([A-Za-z_]\w*)")

# ################################################################################################################################
# ################################################################################################################################

def _get_marker_names(query:'str') -> 'strset':
    """ Returns the names of all the :name markers in a query, string literals excluded.
    """
    out:'strset' = set()

    for match in _marker_pattern.finditer(query):
        name = match.group(1)
        if name:
            out.add(name)

    return out

# ################################################################################################################################

def _replace_marker(match:'re.Match[str]') -> 'str':
    """ Turns a :name marker into the %(name)s form pytds binds, leaving string literals untouched.
    """
    name = match.group(1)

    if name:
        out = '%(' + name + ')s'
    else:
        out = match.group(0)

    return out

# ################################################################################################################################

def _to_pytds_query(query:'str') -> 'str':
    """ Rewrites a query with :name markers into the form pytds expects. A literal percent sign
    has to be doubled first because pytds applies percent formatting to the whole statement.
    """
    escaped = query.replace('%', '%%')

    out = _marker_pattern.sub(_replace_marker, escaped)
    return out

# ################################################################################################################################

def _validate_params(query:'str', params:'strdictnone') -> 'None':
    """ Every :name marker in the query must have a parameter and every parameter must have a marker.
    """
    marker_names = _get_marker_names(query)

    # No parameters at all means the query must not expect any ..
    if params is None:
        if marker_names:
            raise Exception(f'Query has markers with no matching parameters: {sorted(marker_names)}')
        return

    # .. otherwise the two sets have to match exactly.
    param_names = set(params)

    missing = marker_names - param_names
    unused = param_names - marker_names

    if missing:
        raise Exception(f'Query has markers with no matching parameters: {sorted(missing)}')

    if unused:
        raise Exception(f'Parameters have no matching markers in the query: {sorted(unused)}')

# ################################################################################################################################
# ################################################################################################################################

def get_queue_pool(pool_kwargs):
    class _QueuePool(SAQueuePool):
        def __init__(self, creator, *args, **kwargs):
            super(_QueuePool, self).__init__(creator, **pool_kwargs)
    return _QueuePool

# ################################################################################################################################

class SimpleSession:
    """ A simple object simulating SQLAlchemy sessions.
    """
    def __init__(self, api:'MSSQLDirectAPI') -> 'None':
        self.api = api

    def __call__(self):
        return self

    def close(self) -> 'None':
        """ There is nothing to release - each statement checks its own connection out of the pool and back in.
        """

    def execute(self, *args, **kwargs):
        return self.api.execute(*args, **kwargs)

    def callproc(self, *args, **kwargs):
        return self.api.callproc(*args, **kwargs)

    def ping(self, *args, **kwargs):
        return self.api.ping(*args, **kwargs)

# ################################################################################################################################

class MSSQLDirectAPI:
    """ An object through which MS SQL connections can be obtained and stored procedures invoked.
    """
    name = MS_SQL.ZATO_DIRECT
    ping_query = 'SELECT 1'

    def __init__(
        self,
        name,      # type: str
        pool_size, # type: int
        connect_kwargs, # type: stranydict
        extra           # type: stranydict
    ) -> 'None':

        # PyTDS
        import pytds

        # Max. overflow is user-configurable
        max_overflow = extra.get('max_overflow', 0)

        self._name = name
        self._connect_kwargs = connect_kwargs
        self._pool_kwargs = {
            'pool_size': pool_size,
            'max_overflow': max_overflow,

            # This is a pool-level checkout timeout, not an SQL query-level one
            # so we do not need to make it configurable
            'timeout': 3
        }

        self._pool = _DBProxy(pytds, get_queue_pool(self._pool_kwargs))

# ################################################################################################################################

    def connect(self):
        return self._pool.connect(**self._connect_kwargs)

# ################################################################################################################################

    def dispose(self):
        self._pool.dispose()

# ################################################################################################################################

    def execute(self, query:'str', params:'strdictnone'=None) -> 'anylist':
        """ Runs one statement. Rows come back as a list of dicts, a statement that produced
        no rows is committed and an empty list is returned.
        """
        _validate_params(query, params)

        conn = None

        try:
            conn = self.connect()

            with conn.cursor() as cursor:

                # Parameters are bound by the server, which is why the markers are rewritten to what pytds sends ..
                if params:
                    cursor.execute(_to_pytds_query(query), params)
                else:
                    cursor.execute(query)

                # .. a statement that produced rows returns them ..
                if cursor.description:
                    out = cursor.fetchall()

                # .. and one that produced none was a write, so it is committed.
                else:
                    conn.commit()
                    out = []

        finally:
            if conn:
                conn.close()

        return out

# ################################################################################################################################

    def ping(self):
        return self.execute(self.ping_query)

# ################################################################################################################################

    def _return_proc_rows(self, conn, proc_name, params=None):
        """ Calls a procedure and returns all the rows it produced as a single list.
        """
        # Result to return
        result = []

        # This is optional in case getting a new cursor will fail
        cursor = None

        # Will be set to True in the exception block
        has_exception = False

        try:

            # Obtain a connection from pool
            conn = self.connect()

            # Get a new cursor
            cursor = conn.cursor()

            # Call the proceudre
            cursor.callproc(proc_name, params or [])

            while True:
                result.append(cursor.fetchall())
                if not cursor.nextset():
                    break

        except Exception:
            has_exception = True
            logger.warning(format_exc())
            raise

        finally:
            if cursor:
                cursor.close()
            conn.commit()
            conn.close()

        # Return the result only if there was no exception along the way
        if not has_exception:
            return result

# ################################################################################################################################

    def _yield_proc_rows(self, conn, proc_name, params=None):
        """ Calls a procedure and yields all the rows it produced, one by one.
        """
        # This is optional in case getting a new cursor will fail
        cursor = None

        try:
            # Get a new cursor
            cursor = conn.cursor()

            # Call the proceudre
            cursor.callproc(proc_name, params or [])

            while True:
                yield cursor.fetchall()
                if not cursor.nextset():
                    break

        except Exception:
            logger.warning(format_exc())
            raise

        finally:
            if cursor:
                cursor.close()
            conn.commit()
            conn.close()

# ################################################################################################################################

    def callproc(self, name, params=None, use_yield=False):
        params = params or []

        # Obtain a connection from pool
        conn = self.connect()
        return self._yield_proc_rows(conn, name, params) if use_yield else self._return_proc_rows(conn, name, params)

# ################################################################################################################################
