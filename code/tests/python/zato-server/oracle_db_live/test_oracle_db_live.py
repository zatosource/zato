# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import time
from base64 import b64encode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The outgoing connection the enmasse template defines
_connection_name = 'test.oracle.db'

# Queries the tests run - all values are strings so results are the same in every driver configuration
_users_query    = "select 'john.doe' as username, 'John Smith' as display_name from dual"
_one_row_query  = "select 'maria.johnson' as username from dual"

# How long to wait for a running server to apply a reloaded connection definition
_reload_timeout       = 60
_reload_poll_interval = 1

# ################################################################################################################################
# ################################################################################################################################

class _AdminClient:
    """ Minimal admin client for invoking Zato services.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self.password = password

    def invoke(self, service_name:'str', payload:'anydict') -> 'anydict':

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

def _get_client(zato_server:'anydict') -> '_AdminClient':
    out = _AdminClient(zato_server['base_url'], zato_server['invoke_password'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOracleDBQueries:

    def test_execute(self, zato_server:'anydict') -> 'None':
        """ A query through the Oracle connection returns its rows as dicts.
        """
        client = _get_client(zato_server)
        result = client.invoke('test.oracle.db.execute', {
            'conn_name': _connection_name,
            'query': _users_query,
        })

        assert len(result) == 1

        first_row = result[0]
        assert first_row['username'] == 'john.doe'
        assert first_row['display_name'] == 'John Smith'

# ################################################################################################################################

    def test_one(self, zato_server:'anydict') -> 'None':
        """ A single-row query through the Oracle connection returns that row directly.
        """
        client = _get_client(zato_server)
        result = client.invoke('test.oracle.db.one', {
            'conn_name': _connection_name,
            'query': _one_row_query,
        })

        assert result['username'] == 'maria.johnson'

# ################################################################################################################################

    def test_one_or_none(self, zato_server:'anydict') -> 'None':
        """ A single-row query through one_or_none returns the row when it exists.
        """
        client = _get_client(zato_server)
        result = client.invoke('test.oracle.db.one-or-none', {
            'conn_name': _connection_name,
            'query': _one_row_query,
        })

        assert result['username'] == 'maria.johnson'

# ################################################################################################################################

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ A ping through the Oracle connection completes and reports its response time.
        """
        client = _get_client(zato_server)
        result = client.invoke('test.oracle.db.ping', {
            'conn_name': _connection_name,
        })

        assert result['response_time'] > 0

# ################################################################################################################################
# ################################################################################################################################

class TestOracleDBCredentials:

    def _wait_for_ping_outcome(self, client:'_AdminClient', needs_success:'bool') -> 'None':
        """ Polls the ping service until it reaches the expected outcome,
        which is how long a reloaded connection definition takes to apply.
        """
        deadline = time.monotonic() + _reload_timeout
        last_error = ''

        while time.monotonic() < deadline:

            try:
                result = client.invoke('test.oracle.db.ping', {'conn_name': _connection_name})
            except Exception as e:
                last_error = str(e)
                if not needs_success:
                    return
            else:
                if needs_success:
                    assert result['response_time'] > 0
                    return
                last_error = 'The ping still succeeds'

            time.sleep(_reload_poll_interval)

        raise Exception(f'The connection did not reach the expected state, last seen: {last_error}')

# ################################################################################################################################

    def test_connection_uses_configured_credentials(self, zato_server:'anydict') -> 'None':
        """ Reimporting the connection with a different password changes what the pool
        connects with, which shows the configured credentials are the ones in use.
        """
        client = _get_client(zato_server)
        server_directory = zato_server['server_directory']
        import_enmasse = zato_server['import_enmasse']

        # The connection works with the password the database knows ..
        self._wait_for_ping_outcome(client, needs_success=True)

        # .. reimporting with a password the database does not know makes it fail ..
        changed_placeholders = dict(zato_server['placeholders'])
        changed_placeholders['oracle_password'] = 'test.oracle.changed.password'

        import_enmasse(server_directory, changed_placeholders, needs_reload=True)
        self._wait_for_ping_outcome(client, needs_success=False)

        # .. and reimporting the real password makes it work again.
        import_enmasse(server_directory, zato_server['placeholders'], needs_reload=True)
        self._wait_for_ping_outcome(client, needs_success=True)

# ################################################################################################################################
# ################################################################################################################################
