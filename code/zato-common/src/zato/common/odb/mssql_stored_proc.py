# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# PyTDS
import pytds

# SQLAlchemy
from sqlalchemy.pool import _DBProxy, QueuePool as SAQueuePool

# ################################################################################################################################

def get_queue_pool(pool_kwargs):
    class QueuePool(SAQueuePool):
        def __init__(self, creator, *args, **kwargs):
            super(QueuePool, self).__init__(creator, **pool_kwargs)
    return QueuePool

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
        conn = self._get_connection()
        with conn.cursor() as cursor:
            # This will raise an exception if connection details are invalid
            # and we let it propagate.
            cursor.execute('select 1+1')

# ################################################################################################################################

    def _return_rows(self, conn, name, params=None):
        """ Calls a procedure and returns all the rows it produced as a single list.
        """
        # Result to return
        result = []

        # Obtain a connection from pool
        conn = self._get_connection()

        # Get a new cursor
        cursor = conn.cursor()

        try:
            # Call the proceudre
            cursor.callproc(proc_name, params or [])

            while True:
                result.append(cursor.fetchall())
                if not cursor.nextset():
                    break
        finally:
            conn.commit()
            conn.close()
            return result

# ################################################################################################################################

    def _yield_rows(self, conn, name, params=None):
        """ Calls a procedure and yields all the rows it produced, one by one.
        """
        # Get a new cursor
        cursor = conn.cursor()

        try:
            # Call the proceudre
            cursor.callproc(proc_name, params or [])

            while True:
                yield cursor.fetchall()
                if not cursor.nextset():
                    break
        finally:
            conn.commit()
            conn.close()

# ################################################################################################################################

    def callproc(self, name, params=None, use_yield=False):
        params = params or []

        # Obtain a connection from pool
        conn = self._get_connection()
        return self._yield_rows(conn, name, params) if use_yield else self._return_rows(conn, name, params)

# ################################################################################################################################

if __name__ == '__main__':

    # Zato-level attributes
    name = 'My SP API'

    # Pool attributes
    pool_size = 20

    # Details of how to connect via PyTDS
    connect_kwargs = {
        'dsn': 'localhost',
        'port': 1433,
        'database': 'db1',
        'user': 'sa',
        'password': '...',
        'as_dict': True,
        'appname': 'Zato',
    }

    #proc_name = 'get_current_db'
    proc_name = 'get_user2'
    params = ['abc']

    api = StoredProcedureAPI(name, pool_size, connect_kwargs)
    api.ping()

    for x in range(1000):
        result = api.callproc(proc_name, params, use_yield=True)
        result = api.callproc(proc_name, params)

# ################################################################################################################################

