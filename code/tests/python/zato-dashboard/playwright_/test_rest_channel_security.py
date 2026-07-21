# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK, UNAUTHORIZED

# pytest
import pytest

# Zato
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import create_basic_auth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from rest_channel import create_apikey_definition, create_bearer_token_definition, create_channel, \
    create_mtls_definition, create_ntlm_definition, edit_channel, find_channel_row, get_row_cell_texts, invoke_channel, \
    invoke_until_status, open_channel_page, open_edit_dialog

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.sec.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

_API_Key_Header = 'X-API-Key'

# Row cell index with the channel's security definition
_Cell_Security = 6

# Log patterns produced by the server when credentials are rejected
_Auth_Log_Patterns = ('401 Unauthorized path_info', 'Unauthorized; path_info')

# Headers a TLS-terminating proxy injects after verifying the client certificate
_MTLS_Header_Verify      = 'X-Zato-SSL-Client-Verify'
_MTLS_Header_Fingerprint = 'X-Zato-SSL-Client-SHA256'
_MTLS_Header_Subject_DN  = 'X-Zato-SSL-Client-Subject-DN'

# ################################################################################################################################
# ################################################################################################################################

def _get_selected_security_label(page:'Page') -> 'str':
    """ Returns the visible label of the security definition selected in the edit dialog.
    """

    out = page.evaluate('$("#id_edit-security option:selected").text()')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelSecurity:
    """ Tests for security definitions assigned to REST channels via the web admin UI.
    """

# ################################################################################################################################

    def test_no_security_allows_anonymous(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel without any security definition and confirms anonymous requests pass.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'no-security'
        url_path = '/test/rest/sec-none/' + rand_string()

        # Create the channel ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
        })

        # .. and an anonymous request goes through.
        request_payload = {'anonymous': True}
        response = invoke_channel(server_port, url_path, json_data=request_payload)

        assert response.status_code == OK, f'Expected OK for an open channel, got {response.status_code}: {response.text}'
        assert response.json() == request_payload, f'Expected the request echoed back, got: {response.text}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_basic_auth(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a Basic Auth definition and a channel using it, then verifies valid credentials
        pass while invalid and missing ones get 401.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'basic-auth'
        url_path = '/test/rest/sec-basic/' + rand_string()

        # Create the security definition ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'channel')

        # .. create the channel with that definition assigned ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. a server-rendered row shows the definition, so reload the page first ..
        open_channel_page(page, base_url)
        row = find_channel_row(page, channel_name)
        cells = get_row_cell_texts(row)
        assert definition['name'] in cells[_Cell_Security], \
            f'Expected "{definition["name"]}" in the security cell, got: "{cells[_Cell_Security]}"'

        # .. valid credentials pass ..
        auth = (definition['username'], definition['password'])
        response = invoke_until_status(server_port, url_path, OK, data='{"creds": "valid"}', auth=auth)
        assert response.status_code == OK, f'Expected OK with valid credentials, got {response.status_code}: {response.text}'

        # .. invalid credentials are rejected ..
        wrong_auth = (definition['username'], 'invalid.' + rand_string())
        response = invoke_channel(server_port, url_path, data='{"creds": "invalid"}', auth=wrong_auth)
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED with invalid credentials, got {response.status_code}'

        # .. the 401 carries a Basic challenge ..
        www_authenticate = response.headers['WWW-Authenticate']
        assert www_authenticate.startswith('Basic realm='), f'Expected a Basic challenge, got: {www_authenticate}'

        # .. and missing credentials are rejected too.
        response = invoke_channel(server_port, url_path, data='{"creds": "missing"}')
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED with no credentials, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_apikey(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an API key definition and a channel using it, then verifies the key header
        passes while a wrong or missing key gets 401.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'apikey'
        url_path = '/test/rest/sec-apikey/' + rand_string()

        # Create the security definition ..
        definition = create_apikey_definition(page, base_url, _Test_Name_Prefix + 'apikey-def')

        # .. create the channel with that definition assigned ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'API key/{definition["name"]}',
        })

        # .. the correct key passes ..
        headers = {_API_Key_Header: definition['key']}
        response = invoke_until_status(server_port, url_path, OK, data='{"key": "valid"}', headers=headers)
        assert response.status_code == OK, f'Expected OK with a valid key, got {response.status_code}: {response.text}'

        # .. a wrong key is rejected ..
        wrong_headers = {_API_Key_Header: 'invalid.' + rand_string()}
        response = invoke_channel(server_port, url_path, data='{"key": "invalid"}', headers=wrong_headers)
        assert response.status_code == UNAUTHORIZED, f'Expected UNAUTHORIZED with a wrong key, got {response.status_code}'

        # .. and a missing key header is rejected too.
        response = invoke_channel(server_port, url_path, data='{"key": "missing"}')
        assert response.status_code == UNAUTHORIZED, f'Expected UNAUTHORIZED with no key header, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_apikey_custom_header(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an API key definition with a custom header and a channel using it, then verifies
        the custom header passes while the default header, a wrong value and a missing header get 401.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'apikey-custom'
        url_path = '/test/rest/sec-apikey-custom/' + rand_string()
        custom_header = 'X-Custom-Token'

        # Create the security definition with a custom header ..
        definition = create_apikey_definition(page, base_url, _Test_Name_Prefix + 'apikey-custom-def', custom_header)

        # .. create the channel with that definition assigned ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'API key/{definition["name"]}',
        })

        # .. the correct key in the custom header passes ..
        headers = {custom_header: definition['key']}
        response = invoke_until_status(server_port, url_path, OK, data='{"key": "valid"}', headers=headers)
        assert response.status_code == OK, f'Expected OK with a valid key, got {response.status_code}: {response.text}'

        # .. the same key in the default header is rejected ..
        default_headers = {_API_Key_Header: definition['key']}
        response = invoke_channel(server_port, url_path, data='{"key": "default-header"}', headers=default_headers)
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED with the key in the default header, got {response.status_code}'

        # .. a wrong value in the custom header is rejected ..
        wrong_headers = {custom_header: 'invalid.' + rand_string()}
        response = invoke_channel(server_port, url_path, data='{"key": "invalid"}', headers=wrong_headers)
        assert response.status_code == UNAUTHORIZED, f'Expected UNAUTHORIZED with a wrong key, got {response.status_code}'

        # .. and a missing key header is rejected too.
        response = invoke_channel(server_port, url_path, data='{"key": "missing"}')
        assert response.status_code == UNAUTHORIZED, f'Expected UNAUTHORIZED with no key header, got {response.status_code}'

# ################################################################################################################################

    def test_bearer_token_assignment(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a Bearer token definition, assigns it to a channel and verifies the assignment
        persists across the row and the edit dialog. Bearer token channels require an external
        identity provider so there is no live invocation here.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name = _Test_Name_Prefix + 'bearer'
        url_path = '/test/rest/sec-bearer/' + rand_string()

        # Create the security definition ..
        definition = create_bearer_token_definition(page, base_url, _Test_Name_Prefix + 'bearer-def')

        # .. create the channel with that definition assigned ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'Bearer token/{definition["name"]}',
        })

        # .. a server-rendered row shows the definition, so reload the page first ..
        open_channel_page(page, base_url)
        row = find_channel_row(page, channel_name)
        cells = get_row_cell_texts(row)
        assert definition['name'] in cells[_Cell_Security], \
            f'Expected "{definition["name"]}" in the security cell, got: "{cells[_Cell_Security]}"'

        # .. and the edit dialog has it selected.
        open_edit_dialog(page, channel_id)

        selected_label = _get_selected_security_label(page)
        expected_label = f'Bearer token/{definition["name"]}'
        assert selected_label == expected_label, f'Expected "{expected_label}" selected, got: "{selected_label}"'

# ################################################################################################################################

    def test_ntlm_assignment(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an NTLM definition, assigns it to a channel and verifies the assignment
        persists across the row and the edit dialog. NTLM requires a Windows domain so there
        is no live invocation here.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name = _Test_Name_Prefix + 'ntlm'
        url_path = '/test/rest/sec-ntlm/' + rand_string()

        # Create the security definition ..
        definition = create_ntlm_definition(page, base_url, _Test_Name_Prefix + 'ntlm-def')

        # .. create the channel with that definition assigned ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'NTLM/{definition["name"]}',
        })

        # .. a server-rendered row shows the definition, so reload the page first ..
        open_channel_page(page, base_url)
        row = find_channel_row(page, channel_name)
        cells = get_row_cell_texts(row)
        assert definition['name'] in cells[_Cell_Security], \
            f'Expected "{definition["name"]}" in the security cell, got: "{cells[_Cell_Security]}"'

        # .. and the edit dialog has it selected.
        open_edit_dialog(page, channel_id)

        selected_label = _get_selected_security_label(page)
        expected_label = f'NTLM/{definition["name"]}'
        assert selected_label == expected_label, f'Expected "{expected_label}" selected, got: "{selected_label}"'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_mtls_fingerprint(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an mTLS definition with a fingerprint and a channel using it, then verifies
        that requests carrying the matching proxy-injected headers pass while requests with
        a wrong fingerprint, an unverified certificate or no headers at all get 401.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'mtls'
        url_path = '/test/rest/sec-mtls/' + rand_string()
        fingerprint = rand_string() + rand_string()

        # Create the security definition ..
        definition = create_mtls_definition(page, base_url, _Test_Name_Prefix + 'mtls-def', {
            'client_cert_fingerprint': fingerprint,
        })

        # .. create the channel with that definition assigned ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'mTLS/{definition["name"]}',
        })

        # .. a server-rendered row shows the definition, so reload the page first ..
        open_channel_page(page, base_url)
        row = find_channel_row(page, channel_name)
        cells = get_row_cell_texts(row)
        assert definition['name'] in cells[_Cell_Security], \
            f'Expected "{definition["name"]}" in the security cell, got: "{cells[_Cell_Security]}"'

        # .. a verified certificate with the matching fingerprint passes ..
        headers = {
            _MTLS_Header_Verify: 'SUCCESS',
            _MTLS_Header_Fingerprint: fingerprint,
        }
        response = invoke_until_status(server_port, url_path, OK, data='{"cert": "valid"}', headers=headers)
        assert response.status_code == OK, \
            f'Expected OK with a matching fingerprint, got {response.status_code}: {response.text}'

        # .. a verified certificate with a different fingerprint is rejected ..
        wrong_headers = {
            _MTLS_Header_Verify: 'SUCCESS',
            _MTLS_Header_Fingerprint: 'wrong.' + rand_string(),
        }
        response = invoke_channel(server_port, url_path, data='{"cert": "wrong"}', headers=wrong_headers)
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED with a wrong fingerprint, got {response.status_code}'

        # .. an unverified certificate is rejected even with the right fingerprint ..
        unverified_headers = {
            _MTLS_Header_Verify: 'FAILED',
            _MTLS_Header_Fingerprint: fingerprint,
        }
        response = invoke_channel(server_port, url_path, data='{"cert": "unverified"}', headers=unverified_headers)
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED with an unverified certificate, got {response.status_code}'

        # .. and a request without any of the headers is rejected too.
        response = invoke_channel(server_port, url_path, data='{"cert": "missing"}')
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED with no client certificate headers, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_mtls_subject_dn(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an mTLS definition with a subject DN and a channel using it, then verifies
        that requests with the matching subject DN pass while a different one gets 401.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'mtls-dn'
        url_path = '/test/rest/sec-mtls-dn/' + rand_string()
        subject_dn = f'CN=client.{rand_string()},O=Test,C=US'

        # Create the security definition ..
        definition = create_mtls_definition(page, base_url, _Test_Name_Prefix + 'mtls-dn-def', {
            'client_cert_subject_dn': subject_dn,
        })

        # .. create the channel with that definition assigned ..
        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'mTLS/{definition["name"]}',
        })

        # .. a verified certificate with the matching subject DN passes ..
        headers = {
            _MTLS_Header_Verify: 'SUCCESS',
            _MTLS_Header_Subject_DN: subject_dn,
        }
        response = invoke_until_status(server_port, url_path, OK, data='{"subject": "valid"}', headers=headers)
        assert response.status_code == OK, \
            f'Expected OK with a matching subject DN, got {response.status_code}: {response.text}'

        # .. and a verified certificate with a different subject DN is rejected.
        wrong_headers = {
            _MTLS_Header_Verify: 'SUCCESS',
            _MTLS_Header_Subject_DN: 'CN=intruder,O=Elsewhere,C=US',
        }
        response = invoke_channel(server_port, url_path, data='{"subject": "wrong"}', headers=wrong_headers)
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED with a wrong subject DN, got {response.status_code}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_transition_none_to_basic_auth(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates an open channel, then assigns Basic Auth via edit and verifies
        anonymous requests are now rejected while valid credentials pass.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'none-to-basic'
        url_path = '/test/rest/sec-add/' + rand_string()

        # Create the security definition first ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'transition-add')

        # .. create the channel without security and confirm anonymous access ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path)

        response = invoke_channel(server_port, url_path, data='{"open": true}')
        assert response.status_code == OK, f'Expected OK before the transition, got {response.status_code}'

        # .. assign the definition via edit ..
        edit_channel(page, channel_id, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. anonymous requests are now rejected ..
        response = invoke_until_status(server_port, url_path, UNAUTHORIZED, data='{"open": false}')
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED after assigning Basic Auth, got {response.status_code}'

        # .. and valid credentials pass.
        auth = (definition['username'], definition['password'])
        response = invoke_channel(server_port, url_path, data='{"creds": "valid"}', auth=auth)
        assert response.status_code == OK, f'Expected OK with valid credentials, got {response.status_code}: {response.text}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_transition_basic_auth_to_none(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a Basic Auth channel, then removes the security definition via edit
        and verifies anonymous requests now pass.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'basic-to-none'
        url_path = '/test/rest/sec-remove/' + rand_string()

        # Create the security definition ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'transition-remove')

        # .. create the channel with the definition and confirm anonymous requests are rejected ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        response = invoke_until_status(server_port, url_path, UNAUTHORIZED, data='{"locked": true}')
        assert response.status_code == UNAUTHORIZED, f'Expected UNAUTHORIZED before the transition, got {response.status_code}'

        # .. remove the security definition via edit ..
        edit_channel(page, channel_id, {
            'security': 'No security definition',
        })

        # .. and anonymous requests now pass.
        response = invoke_until_status(server_port, url_path, OK, data='{"locked": false}')
        assert response.status_code == OK, f'Expected OK after removing security, got {response.status_code}: {response.text}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_transition_between_definitions(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates two Basic Auth definitions and a channel using the first one, then switches
        to the second one via edit and verifies only the new credentials pass.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'switch-defs'
        url_path = '/test/rest/sec-switch/' + rand_string()

        # Create both definitions ..
        definition_first = create_basic_auth(page, base_url, _Test_Name_Prefix, 'switch-first')
        definition_second = create_basic_auth(page, base_url, _Test_Name_Prefix, 'switch-second')

        # .. create the channel with the first one ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'security': f'Basic Auth/{definition_first["name"]}',
        })

        auth_first = (definition_first['username'], definition_first['password'])
        auth_second = (definition_second['username'], definition_second['password'])

        # .. the first credentials pass, the second do not ..
        response = invoke_until_status(server_port, url_path, OK, data='{"def": "first"}', auth=auth_first)
        assert response.status_code == OK, f'Expected OK with the first credentials, got {response.status_code}'

        response = invoke_channel(server_port, url_path, data='{"def": "second"}', auth=auth_second)
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED with the second credentials, got {response.status_code}'

        # .. switch the channel to the second definition ..
        edit_channel(page, channel_id, {
            'security': f'Basic Auth/{definition_second["name"]}',
        })

        # .. now only the second credentials pass.
        response = invoke_until_status(server_port, url_path, OK, data='{"def": "second"}', auth=auth_second)
        assert response.status_code == OK, f'Expected OK with the second credentials, got {response.status_code}'

        response = invoke_channel(server_port, url_path, data='{"def": "first"}', auth=auth_first)
        assert response.status_code == UNAUTHORIZED, \
            f'Expected UNAUTHORIZED with the first credentials, got {response.status_code}'

# ################################################################################################################################
# ################################################################################################################################
