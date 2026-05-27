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

class GraphQLTestExecute(Service):
    """ Executes a GraphQL query through a named outgoing connection.
    """
    name = 'test.graphql.execute'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']
        params = self.request.raw_request.get('params')

        conn = self.out.graphql[conn_name]
        result = conn.execute(query, params=params)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class GraphQLTestInvoke(Service):
    """ Same as execute but uses the .invoke() alias.
    """
    name = 'test.graphql.invoke'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        query = self.request.raw_request['query']
        params = self.request.raw_request.get('params')

        conn = self.out.graphql[conn_name]
        result = conn.invoke(query, params=params)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class GraphQLTestPing(Service):
    """ Pings a GraphQL connection and returns the result.
    """
    name = 'test.graphql.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        conn = self.out.graphql[conn_name]
        result = conn.ping()

        self.response.payload = json.dumps({'alive': result})

# ################################################################################################################################
# ################################################################################################################################
