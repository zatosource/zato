# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# PyPI

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.graphql_live')

_flights_query = '{ flights { id flight_number origin destination status gate } }'

# ################################################################################################################################
# ################################################################################################################################

class _AdminClient:
    """ Minimal admin client for invoking Zato services.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self.password = password

    def invoke(self, service_name:'str', payload:'anydict') -> 'anydict':
        from base64 import b64encode
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode()

        credentials = f'admin.invoke:{self.password}'
        auth = b64encode(credentials.encode()).decode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        if not raw:
            return {}

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestGraphQLExecute:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_execute_query(self, zato_server:'anydict') -> 'None':
        """ Execute a simple query through the no-auth connection.
        """
        from _graphql_server import GraphQLTestHandler

        GraphQLTestHandler.expected_auth = None
        GraphQLTestHandler.expected_apikey_header = None

        client = self._get_client(zato_server)
        result = client.invoke('test.graphql.execute', {
            'conn_name': 'test.graphql.no_auth',
            'query': _flights_query,
        })

        flights = result['flights']
        assert len(flights) == 3
        assert flights[0]['flight_number'] == 'ZA-101'

# ################################################################################################################################

    def test_invoke_alias(self, zato_server:'anydict') -> 'None':
        """ .invoke() returns the same result as .execute().
        """
        from _graphql_server import GraphQLTestHandler

        GraphQLTestHandler.expected_auth = None
        GraphQLTestHandler.expected_apikey_header = None

        client = self._get_client(zato_server)

        execute_result = client.invoke('test.graphql.execute', {
            'conn_name': 'test.graphql.no_auth',
            'query': _flights_query,
        })

        invoke_result = client.invoke('test.graphql.invoke', {
            'conn_name': 'test.graphql.no_auth',
            'query': _flights_query,
        })

        assert execute_result == invoke_result

# ################################################################################################################################

    def test_execute_with_variables(self, zato_server:'anydict') -> 'None':
        """ Variables are passed through to the GraphQL server.
        """
        from _graphql_server import GraphQLTestHandler

        GraphQLTestHandler.expected_auth = None
        GraphQLTestHandler.expected_apikey_header = None

        client = self._get_client(zato_server)
        query = '{ flight(id: $flight_id) { id flight_number gate } }'
        result = client.invoke('test.graphql.execute', {
            'conn_name': 'test.graphql.no_auth',
            'query': query,
            'params': {'flight_id': '1'},
        })

        flight = result['flight']
        assert flight['id'] == '1'
        assert flight['flight_number'] == 'ZA-101'

# ################################################################################################################################

    def test_execute_mutation(self, zato_server:'anydict') -> 'None':
        """ Mutations are correctly sent.
        """
        from _graphql_server import GraphQLTestHandler

        GraphQLTestHandler.expected_auth = None
        GraphQLTestHandler.expected_apikey_header = None

        client = self._get_client(zato_server)
        query = 'mutation { assignGate(flightId: "1", gateId: "D5") { id gate } }'
        result = client.invoke('test.graphql.execute', {
            'conn_name': 'test.graphql.no_auth',
            'query': query,
        })

        assert result['assignGate']['gate'] == 'D5'

# ################################################################################################################################
# ################################################################################################################################

class TestGraphQLSecurity:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_basic_auth(self, zato_server:'anydict') -> 'None':
        """ The basic_auth connection injects the correct Authorization header.
        """
        from _graphql_server import GraphQLTestHandler

        # Set the expected auth on the test server ..
        GraphQLTestHandler.expected_auth = zato_server['basic_auth_header']
        GraphQLTestHandler.expected_apikey_header = None

        client = self._get_client(zato_server)
        result = client.invoke('test.graphql.execute', {
            'conn_name': 'test.graphql.basic_auth',
            'query': _flights_query,
        })

        flights = result['flights']
        assert len(flights) == 3

# ################################################################################################################################

    def test_apikey(self, zato_server:'anydict') -> 'None':
        """ The apikey connection injects the correct API key header.
        """
        from _graphql_server import GraphQLTestHandler

        # Set the expected API key on the test server ..
        GraphQLTestHandler.expected_auth = None
        GraphQLTestHandler.expected_apikey_header = 'X-API-Key'
        GraphQLTestHandler.expected_apikey_value = zato_server['apikey_value']

        client = self._get_client(zato_server)
        result = client.invoke('test.graphql.execute', {
            'conn_name': 'test.graphql.apikey',
            'query': _flights_query,
        })

        flights = result['flights']
        assert len(flights) == 3

# ################################################################################################################################
# ################################################################################################################################

class TestGraphQLPing:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ .ping() returns True against the live server.
        """
        from _graphql_server import GraphQLTestHandler

        GraphQLTestHandler.expected_auth = None
        GraphQLTestHandler.expected_apikey_header = None

        client = self._get_client(zato_server)
        result = client.invoke('test.graphql.ping', {
            'conn_name': 'test.graphql.no_auth',
        })

        assert result['alive'] is True

# ################################################################################################################################
# ################################################################################################################################

class TestGraphQLCustomHeaders:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_custom_headers(self, zato_server:'anydict') -> 'None':
        """ Extra JSON headers are sent to the GraphQL server.
        """
        from _graphql_server import GraphQLTestHandler

        GraphQLTestHandler.expected_auth = None
        GraphQLTestHandler.expected_apikey_header = None

        client = self._get_client(zato_server)
        _ = client.invoke('test.graphql.execute', {
            'conn_name': 'test.graphql.custom_headers',
            'query': _flights_query,
        })

        # Verify the custom headers arrived at the test server ..
        received = GraphQLTestHandler.received_headers
        assert received.get('X-Tenant') == 'acme'
        assert received.get('X-Request-Source') == 'zato-test'

# ################################################################################################################################
# ################################################################################################################################
