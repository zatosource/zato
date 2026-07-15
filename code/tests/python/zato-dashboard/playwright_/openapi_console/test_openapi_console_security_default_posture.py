# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import NOT_FOUND, OK, UNAUTHORIZED

# pytest
import pytest

# Zato
from zato.common.api import ZATO_NONE
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import edit_channel_by_name, Path_Untyped, Service_Untyped
from rest_channel import invoke_channel, invoke_until_status

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.posture.' + CryptoManager.generate_hex_string(32) + '.'

# What the untyped fixture service always replies with
_Expected_Response = {'echo': True}

# A path no channel has ever existed for
_Unknown_Path = '/no/such/path/on/this/server'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleSecurityDefaultPosture:
    """ Verifies the default security posture of channels on the server port - an inactive
    channel is indistinguishable from an unknown path, an active channel with no security
    serves openly and an assigned definition is enforced immediately.
    """

# ################################################################################################################################

    # The 401 checks below make the server log its Unauthorized rejections
    @pytest.mark.expect_log_errors('Unauthorized')
    def test_default_posture(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Walks the untyped channel through inactive, active-with-no-security
        and active-with-security, asserting the server's behavior at each step.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # The channel arrives here inactive - strip its security so it matches
        # the boot state of a fresh auto-created channel: inactive, no security ..
        _ = edit_channel_by_name(page, base_url, Service_Untyped, {
            'security_value': ZATO_NONE,
        })

        # .. an inactive channel is 404 and the response names no service and no channel ..
        response = invoke_until_status(server_port, Path_Untyped, NOT_FOUND, json_data={})
        assert response.status_code == NOT_FOUND, f'Expected 404 from an inactive channel, got {response.status_code}'
        assert Service_Untyped not in response.text, f'The service name leaked into the 404 body: {response.text}'

        # .. and an unknown path is 404 just the same.
        response = invoke_channel(server_port, _Unknown_Path, json_data={})
        assert response.status_code == NOT_FOUND, f'Expected 404 from an unknown path, got {response.status_code}'
        assert Service_Untyped not in response.text, f'The service name leaked into the 404 body: {response.text}'

        # Activate the channel with no security assigned ..
        _ = edit_channel_by_name(page, base_url, Service_Untyped, {
            'is_active': True,
        })

        # .. no security means open once active - the request carries no credentials at all.
        response = invoke_until_status(server_port, Path_Untyped, OK, json_data={})
        assert response.status_code == OK, f'Expected OK from an open channel, got {response.status_code}: {response.text}'

        data = response.json()
        assert data == _Expected_Response, f'Unexpected channel response: {data}'

        # Assign a Basic Auth definition ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'posture')

        _ = edit_channel_by_name(page, base_url, Service_Untyped, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. a request with no credentials is now rejected ..
        response = invoke_until_status(server_port, Path_Untyped, UNAUTHORIZED, json_data={})
        assert response.status_code == UNAUTHORIZED, \
            f'Expected 401 without credentials, got {response.status_code}: {response.text}'

        # .. and the right credentials open the channel again.
        response = invoke_until_status(
            server_port, Path_Untyped, OK,
            json_data={},
            auth=(definition['username'], definition['password']),
        )
        assert response.status_code == OK, f'Expected OK with credentials, got {response.status_code}: {response.text}'

        data = response.json()
        assert data == _Expected_Response, f'Unexpected channel response: {data}'

# ################################################################################################################################
# ################################################################################################################################
