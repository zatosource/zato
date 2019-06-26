# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# PyTDS
import pytds

# ################################################################################################################################

class StoredProcedureAPI(object):
    """ An object through which MS SQL stored procedures can be invoked.
    """
    def __init__(self, name, pool_size, connect_kwargs):
        # type: (str, int, dict) -> None
        self._name = name
        self._connect_kwargs = connect_kwargs
        self._pool_kwargs = {
            'pool_size': pool_size,
            'max_overflow': 0,
            'timeout': 30
        }

        self._pool = _DBProxy(pytds, get_queue_pool(self._pool_kwargs))

# ################################################################################################################################

    def _get_connection(self):
        return self._pool.connect(**self._connect_kwargs)

# ################################################################################################################################

    def ping(self):
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                # This will raise an exception if connection details are invalid
                # and we let it propagate.
                cursor.execute('select 1+1')
        finally:
            if conn:
                conn.close()

# ################################################################################################################################

    def _return_rows(self, conn, name, params=None):
        """ Calls a procedure and returns all the rows it produced as a single list.
        """
        # Result to return
        result = []

        # This is optional in case getting a new cursor will fail
        cursor = None

        try:

            # Obtain a connection from pool
            conn = self._get_connection()

            # Get a new cursor
            cursor = conn.cursor()

            # Call the proceudre
            cursor.callproc(proc_name, params or [])

            while True:
                result.append(cursor.fetchall())
                if not cursor.nextset():
                    break
        finally:
            if cursor:
                cursor.close()
            conn.commit()
            conn.close()
            return result

# ################################################################################################################################

    def _yield_rows(self, conn, name, params=None):
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
        finally:
            if cursor:
                cursor.close()
            conn.commit()
            conn.close()

# ################################################################################################################################

    def callproc(self, name, params=None, use_yield=False):
        params = params or []

        # Obtain a connection from pool
        conn = self._get_connection()
        return self._yield_rows(conn, name, params) if use_yield else self._return_rows(conn, name, params)

# ################################################################################################################################
