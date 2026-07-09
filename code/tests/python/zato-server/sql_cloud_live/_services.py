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

class SQLCloudExecute(Service):
    """ Executes a query through a named outgoing SQL connection.
    """
    name = 'test.sql.cloud.execute'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']

        conn = self.out.sql[conn_name]
        result = conn.execute(query)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class SQLCloudPing(Service):
    """ Pings an outgoing SQL connection and returns the response time.
    """
    name = 'test.sql.cloud.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.out.sql[conn_name]
        response_time = conn.pool.ping(conn.fs_sql_config)

        self.response.payload = json.dumps({'response_time': response_time})

# ################################################################################################################################
# ################################################################################################################################
