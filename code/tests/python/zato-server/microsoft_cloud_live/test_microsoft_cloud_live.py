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
import time

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.microsoft_cloud_live')

# The main connection with valid credentials
_conn_name = 'test.microsoft.cloud.main'

# The connection whose client secret the token endpoint rejects
_bad_credentials_conn_name = 'test.microsoft.cloud.bad-credentials'

# The connection whose tokens expire almost immediately
_short_token_conn_name = 'test.microsoft.cloud.short-token'

# The mailbox the email and calendar tests use
_email_from = 'maria.garcia@example.com'

# How long to wait for a short-lived token to expire, in seconds.
_short_token_wait = 5

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

class TestMicrosoftCloudEmail:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_send_email(self, zato_server:'anydict') -> 'None':
        """ An email sent through the connection arrives at the cloud with its content intact.
        """
        from _microsoft_365_server import Microsoft365TestHandler

        client = self._get_client(zato_server)

        result = client.invoke('test.microsoft.cloud.send-email', {
            'conn_name': _conn_name,
            'email_from': _email_from,
            'email_to': 'james.wilson@example.com',
            'subject': 'Invoice INV-2026-0042 is ready',
            'body': 'Please find the invoice attached to the customer portal.',
        })

        assert result['is_sent'] is True

        # The message arrived at the cloud ..
        sent = Microsoft365TestHandler.sent_messages[-1]

        assert sent['email_from'] == _email_from

        # .. with its content intact.
        message = sent['payload']['message']
        recipients = message['toRecipients']

        assert message['subject'] == 'Invoice INV-2026-0042 is ready'
        assert recipients[0]['emailAddress']['address'] == 'james.wilson@example.com'

# ################################################################################################################################
# ################################################################################################################################

class TestMicrosoftCloudCalendar:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_list_calendar_events(self, zato_server:'anydict') -> 'None':
        """ The events of a user's default calendar are returned.
        """
        client = self._get_client(zato_server)

        result = client.invoke('test.microsoft.cloud.list-calendar-events', {
            'conn_name': _conn_name,
            'email': _email_from,
        })

        subjects = result['subjects']

        assert 'Quarterly planning' in subjects
        assert 'Customer onboarding call' in subjects

# ################################################################################################################################
# ################################################################################################################################

class TestMicrosoftCloudDirectory:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_list_users(self, zato_server:'anydict') -> 'None':
        """ The users of the tenant's directory are returned.
        """
        client = self._get_client(zato_server)

        result = client.invoke('test.microsoft.cloud.list-users', {
            'conn_name': _conn_name,
        })

        users = result['users']
        mails = {user['mail'] for user in users}

        assert 'maria.garcia@example.com' in mails
        assert 'james.wilson@example.com' in mails

        # Check that a user carries its full details ..
        for user in users:
            if user['mail'] == 'maria.garcia@example.com':
                assert user['display_name'] == 'Maria Garcia'

# ################################################################################################################################
# ################################################################################################################################

class TestMicrosoftCloudREST:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_direct_rest_call(self, zato_server:'anydict') -> 'None':
        """ Any Graph endpoint can be invoked directly through the connection.
        """
        client = self._get_client(zato_server)

        result = client.invoke('test.microsoft.cloud.get-organization', {
            'conn_name': _conn_name,
        })

        organization = result['value'][0]

        assert organization['displayName'] == 'Test Organization'

# ################################################################################################################################
# ################################################################################################################################

class TestMicrosoftCloudMS365Shim:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_cloud_ms365_shim(self, zato_server:'anydict') -> 'None':
        """ The self.cloud.ms365 API works through the shim - .get(), .conn, .client(),
        the with statement, .refresh() and .impl all map onto the same client.
        """
        client = self._get_client(zato_server)

        result = client.invoke('test.microsoft.cloud.ms365-shim', {
            'conn_name': _conn_name,
        })

        mails = {user['mail'] for user in result['users']}

        assert 'maria.garcia@example.com' in mails
        assert 'james.wilson@example.com' in mails

# ################################################################################################################################
# ################################################################################################################################

class TestMicrosoftCloudPing:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ .ping() succeeds against the live cloud.
        """
        client = self._get_client(zato_server)

        result = client.invoke('test.microsoft.cloud.ping', {
            'conn_name': _conn_name,
        })

        assert result['ok'] is True

# ################################################################################################################################
# ################################################################################################################################

class TestMicrosoftCloudSecurity:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_bad_credentials_are_rejected(self, zato_server:'anydict') -> 'None':
        """ A connection with an invalid client secret cannot obtain a token.
        """
        client = self._get_client(zato_server)

        with pytest.raises(Exception) as exception_info:
            _ = client.invoke('test.microsoft.cloud.list-users', {
                'conn_name': _bad_credentials_conn_name,
            })

        assert 'HTTP' in str(exception_info.value)

# ################################################################################################################################

    def test_token_renewal_after_expiry(self, zato_server:'anydict') -> 'None':
        """ When a token expires, the connection transparently obtains a new one,
        so the caller never notices.
        """
        from _microsoft_365_server import Microsoft365TestHandler

        short_lived_client_id = zato_server['short_lived_client_id']

        client = self._get_client(zato_server)

        # First, make a call so the connection holds a token ..
        result = client.invoke('test.microsoft.cloud.list-users', {
            'conn_name': _short_token_conn_name,
        })
        assert 'users' in result

        token_count_before = Microsoft365TestHandler.issued_token_counts[short_lived_client_id]

        # .. wait until that token expires ..
        time.sleep(_short_token_wait)

        # .. and confirm the next call still succeeds - the connection renewed its token on its own.
        result = client.invoke('test.microsoft.cloud.list-users', {
            'conn_name': _short_token_conn_name,
        })

        mails = {user['mail'] for user in result['users']}
        assert 'maria.garcia@example.com' in mails

        # A new token was indeed issued for the second call.
        token_count_after = Microsoft365TestHandler.issued_token_counts[short_lived_client_id]
        assert token_count_after > token_count_before

# ################################################################################################################################
# ################################################################################################################################
