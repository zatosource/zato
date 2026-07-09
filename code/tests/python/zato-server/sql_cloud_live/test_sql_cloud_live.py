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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.sql_cloud_live')

_flights_query = 'select id, flight_number from flights'

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

class TestSQLCloudExecute:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_execute_snowflake(self, zato_server:'anydict') -> 'None':
        """ A query through the Snowflake connection returns the simulator's canned rows.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.sql.cloud.execute', {
            'conn_name': 'test.sql.snowflake',
            'query': _flights_query,
        })

        assert len(result) == 3

        first_row = result[0]
        assert first_row['id'] == 1
        assert first_row['flight_number'] == 'ZA-101'

# ################################################################################################################################

    def test_execute_redshift(self, zato_server:'anydict') -> 'None':
        """ A query through the Redshift connection returns the simulator's canned rows.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.sql.cloud.execute', {
            'conn_name': 'test.sql.redshift',
            'query': _flights_query,
        })

        assert len(result) == 3

        first_row = result[0]
        assert first_row['id'] == 1
        assert first_row['flight_number'] == 'ZA-101'

# ################################################################################################################################

    def test_snowflake_received_wire_requests(self, zato_server:'anydict') -> 'None':
        """ The Snowflake simulator saw the login and the query on the wire.
        """
        snowflake_server = zato_server['snowflake_server']

        login_requests = []
        query_requests = []

        for request in snowflake_server.recorded_requests:
            if request['path'] == '/session/v1/login-request':
                login_requests.append(request)
            elif request['path'] == '/queries/v1/query-request':
                query_requests.append(request)

        assert len(login_requests) >= 1

        query_sql = []
        for request in query_requests:
            query_sql.append(request['body']['sqlText'])

        assert _flights_query in query_sql

# ################################################################################################################################

    def test_redshift_received_wire_requests(self, zato_server:'anydict') -> 'None':
        """ The Redshift simulator saw the startup exchange and the query on the wire.
        """
        redshift_server = zato_server['redshift_server']

        startup_requests = []
        parsed_sql = []

        for request in redshift_server.recorded_requests:
            if request['type'] == 'startup':
                startup_requests.append(request)
            elif request['type'] == 'parse':
                parsed_sql.append(request['sql'])

        assert len(startup_requests) >= 1
        assert startup_requests[0]['parameters']['user'] == 'test_user'

        assert _flights_query in parsed_sql

# ################################################################################################################################
# ################################################################################################################################

class TestSQLCloudPing:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_ping_snowflake(self, zato_server:'anydict') -> 'None':
        """ A ping through the Snowflake connection completes and reports its response time.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.sql.cloud.ping', {
            'conn_name': 'test.sql.snowflake',
        })

        assert result['response_time'] > 0

# ################################################################################################################################

    def test_ping_redshift(self, zato_server:'anydict') -> 'None':
        """ A ping through the Redshift connection completes and reports its response time.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.sql.cloud.ping', {
            'conn_name': 'test.sql.redshift',
        })

        assert result['response_time'] > 0

# ################################################################################################################################
# ################################################################################################################################
