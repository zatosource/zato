# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

class MSSQLCallProc(Service):
    """ Calls a stored procedure through the outgoing MS SQL connection and returns all its result sets.
    """
    name = 'test.mssql.db.callproc'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        proc_name = self.request.raw_request['proc_name']
        params = self.request.raw_request['params']

        conn = self.out.sql[conn_name]
        session = conn.session()
        result = session.callproc(proc_name, params)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class MSSQLCallProcYield(Service):
    """ Calls a stored procedure through the outgoing MS SQL connection, consuming its result sets one by one.
    """
    name = 'test.mssql.db.callproc-yield'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        proc_name = self.request.raw_request['proc_name']
        params = self.request.raw_request['params']

        conn = self.out.sql[conn_name]
        session = conn.session()

        result:'anylist' = []

        for result_set in session.callproc(proc_name, params, use_yield=True):
            result.append(result_set)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class MSSQLExecute(Service):
    """ Executes a statement through the outgoing MS SQL connection.
    """
    name = 'test.mssql.db.execute'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']

        conn = self.out.sql[conn_name]
        session = conn.session()
        result = session.execute(query)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class MSSQLPing(Service):
    """ Pings the outgoing MS SQL connection and returns the response time.
    """
    name = 'test.mssql.db.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.out.sql[conn_name]
        response_time = conn.pool.ping(conn.fs_sql_config)

        self.response.payload = json.dumps({'response_time': response_time})

# ################################################################################################################################
# ################################################################################################################################
