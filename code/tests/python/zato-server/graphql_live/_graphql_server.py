# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strnone

# ################################################################################################################################
# ################################################################################################################################

_introspection_response = {
    'data': {
        '__schema': {
            'queryType': {'name': 'Query'},
            'mutationType': {'name': 'Mutation'},
            'types': [
                {
                    'kind': 'OBJECT',
                    'name': 'Query',
                    'fields': [
                        {
                            'name': 'flights',
                            'args': [
                                {'name': 'status', 'type': {'name': 'String'}},
                            ],
                            'type': {
                                'kind': 'LIST',
                                'ofType': {'kind': 'OBJECT', 'name': 'Flight'},
                            },
                        },
                        {
                            'name': 'flight',
                            'args': [
                                {'name': 'id', 'type': {'name': 'ID'}},
                            ],
                            'type': {'kind': 'OBJECT', 'name': 'Flight'},
                        },
                    ],
                },
                {
                    'kind': 'OBJECT',
                    'name': 'Flight',
                    'fields': [
                        {'name': 'id', 'args': [], 'type': {'kind': 'SCALAR', 'name': 'ID'}},
                        {'name': 'flight_number', 'args': [], 'type': {'kind': 'SCALAR', 'name': 'String'}},
                        {'name': 'origin', 'args': [], 'type': {'kind': 'SCALAR', 'name': 'String'}},
                        {'name': 'destination', 'args': [], 'type': {'kind': 'SCALAR', 'name': 'String'}},
                        {'name': 'status', 'args': [], 'type': {'kind': 'SCALAR', 'name': 'String'}},
                        {'name': 'gate', 'args': [], 'type': {'kind': 'SCALAR', 'name': 'String'}},
                    ],
                },
                {
                    'kind': 'OBJECT',
                    'name': 'Mutation',
                    'fields': [
                        {
                            'name': 'assignGate',
                            'args': [
                                {'name': 'flightId', 'type': {'name': 'ID'}},
                                {'name': 'gateId', 'type': {'name': 'ID'}},
                            ],
                            'type': {'kind': 'OBJECT', 'name': 'Flight'},
                        },
                    ],
                },
            ],
        }
    }
}

_flights_data = [
    {'id': '1', 'flight_number': 'ZA-101', 'origin': 'WAW', 'destination': 'JFK', 'status': 'airborne', 'gate': 'A1'},
    {'id': '2', 'flight_number': 'ZA-202', 'origin': 'LHR', 'destination': 'CDG', 'status': 'boarding', 'gate': 'B3'},
    {'id': '3', 'flight_number': 'ZA-303', 'origin': 'FRA', 'destination': 'SFO', 'status': 'airborne', 'gate': 'C7'},
]

# ################################################################################################################################
# ################################################################################################################################

class GraphQLTestHandler(BaseHTTPRequestHandler):

    expected_auth:'strnone' = None
    expected_apikey_header:'strnone' = None
    expected_apikey_value:'strnone' = None
    received_headers:'anydict' = {}

    def log_message(self, format, *args) -> 'None':
        pass

# ################################################################################################################################

    def _check_auth(self) -> 'bool':

        # No auth required
        if not self.expected_auth and not self.expected_apikey_header:
            return True

        # API key auth
        if self.expected_apikey_header:
            value = self.headers.get(self.expected_apikey_header)
            if value == self.expected_apikey_value:
                return True
            return False

        # Basic auth or Bearer token
        auth_header = self.headers.get('Authorization', '')

        if self.expected_auth:
            if auth_header == self.expected_auth:
                return True

            # For basic auth, also check decoded value
            if self.expected_auth.startswith('Basic ') and auth_header.startswith('Basic '):
                return auth_header == self.expected_auth

            # For bearer tokens
            if self.expected_auth.startswith('Bearer ') and auth_header.startswith('Bearer '):
                return auth_header == self.expected_auth

        return False

# ################################################################################################################################

    def _handle_query(self, query:'str', variables:'anydict | None') -> 'anydict':

        # Introspection
        if '__schema' in query or '__type' in query:
            return _introspection_response

        # Flights query
        if 'flights' in query:
            return {'data': {'flights': _flights_data}}

        # Single flight query
        if 'flight' in query and variables and 'flight_id' in variables:
            flight_id = variables['flight_id']
            for flight in _flights_data:
                if flight['id'] == flight_id:
                    return {'data': {'flight': flight}}
            return {'data': {'flight': None}}

        # Mutation
        if 'assignGate' in query:
            flight_id = variables['flight_id'] if variables else '1'
            gate_id = variables['gate_id'] if variables else 'X1'

            # .. also extract inline arguments from the query itself ..
            match_flight = re.search(r'flightId:\s*"([^"]+)"', query)
            match_gate = re.search(r'gateId:\s*"([^"]+)"', query)
            if match_flight:
                flight_id = match_flight.group(1)
            if match_gate:
                gate_id = match_gate.group(1)

            return {'data': {'assignGate': {
                'id': flight_id,
                'flight_number': 'ZA-101',
                'gate': gate_id,
            }}}

        return {'data': {}}

# ################################################################################################################################

    def do_POST(self) -> 'None':

        # Store received headers for test inspection
        GraphQLTestHandler.received_headers = dict(self.headers)

        # Check auth
        if not self._check_auth():
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            body = json.dumps({'errors': [{'message': 'Unauthorized'}]})
            _ = self.wfile.write(body.encode('utf-8'))
            return

        # Parse request body
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length)
        body = json.loads(raw_body)

        query = body.get('query', '')
        variables = body.get('variables')

        # Handle
        result = self._handle_query(query, variables)

        # Respond
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response_body = json.dumps(result)
        _ = self.wfile.write(response_body.encode('utf-8'))

# ################################################################################################################################
# ################################################################################################################################

def start_graphql_server(port:'int', auth:'strnone'=None, apikey_header:'strnone'=None,
                         apikey_value:'strnone'=None) -> 'tuple':
    """ Starts the test GraphQL server in a background thread. Returns (server, thread).
    """
    GraphQLTestHandler.expected_auth = auth
    GraphQLTestHandler.expected_apikey_header = apikey_header
    GraphQLTestHandler.expected_apikey_value = apikey_value
    GraphQLTestHandler.received_headers = {}

    server = HTTPServer(('127.0.0.1', port), GraphQLTestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    return server, thread

# ################################################################################################################################
# ################################################################################################################################
