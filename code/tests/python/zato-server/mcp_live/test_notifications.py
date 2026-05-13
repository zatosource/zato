# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from http.client import NO_CONTENT, NOT_FOUND, OK

# pytest
import pytest

# local
from _client import MCPClient

# ################################################################################################################################
# ################################################################################################################################

_notification_poll_timeout  = 15
_notification_poll_interval = 1

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'dict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestNotifications:
    """ Tests for GET notification polling.
    """

    def test_get_notifications_returns_no_content_when_empty(self, client:'MCPClient') -> 'None':
        """ GET with a valid session returns 204 when there are no pending notifications.
        """

        # Create a session ..
        _, session_id = client.initialize()

        # .. poll for notifications.
        response = client.get_notifications(session_id=session_id)

        assert response.status_code == NO_CONTENT

# ################################################################################################################################

    def test_get_notifications_without_session_returns_not_found(self, client:'MCPClient') -> 'None':
        """ GET without a session ID returns 404.
        """

        response = client.get_notifications()

        assert response.status_code == NOT_FOUND

# ################################################################################################################################

    def test_get_notifications_with_invalid_session_returns_not_found(self, client:'MCPClient') -> 'None':
        """ GET with an invalid session ID returns 404.
        """

        response = client.get_notifications(session_id='not-a-real-session')

        assert response.status_code == NOT_FOUND

# ################################################################################################################################

    def test_hot_deploy_triggers_notification(self, client:'MCPClient', zato_server:'dict') -> 'None':
        """ Dropping a .py file into the pickup directory triggers a tools/list_changed notification.
        """

        # Create a session first ..
        _, session_id = client.initialize()

        # .. build the path to the server's hot-deploy pickup directory ..
        server_directory = zato_server['server_directory']
        pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')

        # .. write a minimal service file to the pickup directory ..
        service_file_name = '_mcp_test_hot_deploy_notification.py'
        service_file_path = os.path.join(pickup_directory, service_file_name)

        service_code = '''\
from zato.server.service import Service

class MCPTestHotDeployNotification(Service):
    name = 'mcp-test.hot-deploy-notification'

    def handle(self):
        pass
'''

        with open(service_file_path, 'w') as service_file:
            _ = service_file.write(service_code)

        # .. poll for notifications with a timeout,
        # giving the server time to detect the new file ..
        notification_received = False
        deadline = time.monotonic() + _notification_poll_timeout

        while time.monotonic() < deadline:
            response = client.get_notifications(session_id=session_id)

            if response.status_code == OK:
                data = response.json()

                # .. check if any notification is tools/list_changed ..
                for notification in data:
                    if notification['method'] == 'notifications/tools/list_changed':
                        notification_received = True
                        break

                if notification_received:
                    break

            time.sleep(_notification_poll_interval)

        # .. clean up the deployed file.
        os.remove(service_file_path)

        assert notification_received, \
            f'Expected notifications/tools/list_changed notification within {_notification_poll_timeout} seconds'

# ################################################################################################################################
# ################################################################################################################################
