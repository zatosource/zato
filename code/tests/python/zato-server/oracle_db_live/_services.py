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
