# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# PyTDS
import pytds

# SQLAlchemy
from sqlalchemy.pool import QueuePool as SAQueuePool
from sqlalchemy.pool.dbapi_proxy import _DBProxy

# Zato
from zato.common.api import MS_SQL

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

def get_queue_pool(pool_kwargs):
    class _QueuePool(SAQueuePool):
        def __init__(self, creator, *args, **kwargs):
            super(_QueuePool, self).__init__(creator, **pool_kwargs)
    return _QueuePool

# ################################################################################################################################

class SimpleSession(object):
    """ A simple object simulating SQLAlchemy sessions.
    """
    def __init__(self, api):
        # type: (MSSQLDirectAPI)
        self.api = api

    def __call__(self):
        return self

    def execute(self, *args, **kwargs):
        return self.api.execute(*args, **kwargs)

    def callproc(self, *args, **kwargs):
        return self.api.callproc(*args, **kwargs)

    def ping(self, *args, **kwargs):
        return self.api.ping(*args, **kwargs)

# ################################################################################################################################

class MSSQLDirectAPI(object):
    """ An object through which MS SQL connections can be obtained and stored procedures invoked.
    """
    name = MS_SQL.ZATO_DIRECT
    ping_query = 'SELECT 1'

    def __init__(self, name, pool_size, connect_kwargs):
        # type: (str, int, dict) -> None
        self._name = name
        self._connect_kwargs = connect_kwargs
        self._pool_kwargs = {
            'pool_size': pool_size,
            'max_overflow': 0,

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

    def execute(self, *args, **kwargs):
        conn = None
        try:
            conn = self.connect()
            with conn.cursor() as cursor:
                cursor.execute(*args, **kwargs)
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()

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
            logger.warn(format_exc())
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
            logger.warn(format_exc())
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
