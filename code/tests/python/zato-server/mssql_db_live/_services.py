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

class MSSQLConnCallProc(Service):
    """ Calls a stored procedure straight through the outgoing MS SQL connection, with no session in between.
    """
    name = 'test.mssql.db.conn-callproc'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        proc_name = self.request.raw_request['proc_name']
        params = self.request.raw_request['params']

        conn = self.out.sql[conn_name]
        result = conn.callproc(proc_name, params)

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

class MSSQLQuery(Service):
    """ Runs a query with bound parameters through the outgoing MS SQL connection.
    """
    name = 'test.mssql.db.query'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']
        params = self.request.raw_request['params']

        conn = self.out.sql[conn_name]
        result = conn.execute(query, params)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class MSSQLOne(Service):
    """ Returns exactly one row through the outgoing MS SQL connection.
    """
    name = 'test.mssql.db.one'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']
        params = self.request.raw_request['params']

        conn = self.out.sql[conn_name]
        result = conn.one(query, params)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class MSSQLOneOrNone(Service):
    """ Returns one row or None through the outgoing MS SQL connection.
    """
    name = 'test.mssql.db.one-or-none'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']
        params = self.request.raw_request['params']

        conn = self.out.sql[conn_name]
        result = conn.one_or_none(query, params)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class MSSQLWrite(Service):
    """ Runs a write statement through the outgoing MS SQL connection, then reads back what it wrote.
    """
    name = 'test.mssql.db.write'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        statement = self.request.raw_request['statement']
        params = self.request.raw_request['params']
        query = self.request.raw_request['query']
        query_params = self.request.raw_request['query_params']

        conn = self.out.sql[conn_name]

        written = conn.execute(statement, params)
        rows = conn.execute(query, query_params)

        self.response.payload = json.dumps({'written': written, 'rows': rows})

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
