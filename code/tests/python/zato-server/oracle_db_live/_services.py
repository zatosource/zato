# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.common.oracledb import NumberIn, RowsOut, StringIn, StringOut
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class OracleDBCallProcOut(Service):
    """ Calls a procedure that hands a value back through an OUT parameter.
    """
    name = 'test.oracle.db.callproc-out'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        proc_name = self.request.raw_request['proc_name']
        employee_id = self.request.raw_request['employee_id']

        conn = self.out.sql[conn_name]

        name_out = StringOut()
        out_values = conn.callproc(proc_name, [NumberIn(employee_id), name_out])

        self.response.payload = json.dumps({'out_values': out_values, 'name': name_out.get()})

# ################################################################################################################################
# ################################################################################################################################

class OracleDBCallProcRows(Service):
    """ Calls a procedure that hands rows back through a REF CURSOR.
    """
    name = 'test.oracle.db.callproc-rows'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        proc_name = self.request.raw_request['proc_name']
        department = self.request.raw_request['department']

        conn = self.out.sql[conn_name]

        rows_out = RowsOut()
        out_values = conn.callproc(proc_name, [StringIn(department), rows_out])

        self.response.payload = json.dumps({'out_values': out_values, 'rows': rows_out.get()})

# ################################################################################################################################
# ################################################################################################################################

class OracleDBExecute(Service):
    """ Executes a query through the outgoing Oracle connection.
    """
    name = 'test.oracle.db.execute'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']

        conn = self.out.sql[conn_name]
        result = conn.execute(query)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class OracleDBOne(Service):
    """ Returns exactly one row through the outgoing Oracle connection.
    """
    name = 'test.oracle.db.one'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']

        conn = self.out.sql[conn_name]
        result = conn.one(query)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class OracleDBOneOrNone(Service):
    """ Returns one row or None through the outgoing Oracle connection.
    """
    name = 'test.oracle.db.one-or-none'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']

        conn = self.out.sql[conn_name]
        result = conn.one_or_none(query)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class OracleDBPing(Service):
    """ Pings the outgoing Oracle connection and returns the response time.
    """
    name = 'test.oracle.db.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.out.sql[conn_name]
        response_time = conn.pool.ping(conn.fs_sql_config)

        self.response.payload = json.dumps({'response_time': response_time})

# ################################################################################################################################
# ################################################################################################################################
