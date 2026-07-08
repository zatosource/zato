# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery
from soap_outconn import create_soap_outconn, delete_soap_outconn, edit_soap_outconn, find_soap_outconn_row, \
    open_edit_dialog, open_soap_outconn_page, ping_soap_outconn, wait_for_soap_outconn_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.soap.out.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPOutconnLifecycle:
    """ Outgoing SOAP connection lifecycle across every tab - Main, SOAP, Security,
    Body credentials and More - plus the ping button against a live test server.
    Everything runs through the browser and every value is verified by reloading
    the page, so the table is rebuilt from the server, and reading the edit dialog.
    """

# ################################################################################################################################

    def test_full_lifecycle_across_all_tabs(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'tabs'

        # Create a connection touching every tab of the dialog ..
        outconn_id = create_soap_outconn(page, base_url, name, 'https://example.com:8443', {

            # Main
            'url_path': '/services/endpoint',
            'soap_action': 'urn:example:submit',
            'timeout': '20',

            # SOAP
            'soap_version': '1.2',
            'use_ws_addressing': True,
            'use_mtom': True,

            # Security
            'validate_tls': 'False',
            'tls_client_cert': '/opt/certs/client-cert.pem',
            'tls_client_key': '/opt/certs/client-key.pem',

            # Body credentials
            'body_credentials': [
                {'name': 'username'},
                {'name': 'password', 'position': 2},
            ],

            # More
            'ping_method': 'GET',
            'content_type': 'application/soap+xml',
        })

        # .. reload the page so the table is rebuilt from what the server persisted ..
        open_soap_outconn_page(page, base_url, query=name)
        _ = wait_for_soap_outconn_row(page, name)

        # .. open the edit dialog and verify every value came back ..
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-name') == name
        assert page.input_value('#id_edit-host') == 'https://example.com:8443'
        assert page.input_value('#id_edit-url_path') == '/services/endpoint'
        assert page.input_value('#id_edit-soap_action') == 'urn:example:submit'
        assert page.input_value('#id_edit-timeout') == '20'

        assert page.input_value('#id_edit-soap_version') == '1.2'
        assert page.is_checked('#id_edit-use_ws_addressing')
        assert page.is_checked('#id_edit-use_mtom')

        assert page.input_value('#id_edit-validate_tls') == 'False'
        assert page.input_value('#id_edit-tls_client_cert') == '/opt/certs/client-cert.pem'
        assert page.input_value('#id_edit-tls_client_key') == '/opt/certs/client-key.pem'

        credential_names = page.eval_on_selector_all(
            '#body-credentials-edit .body-credential-name', 'elements => elements.map(element => element.value)')
        credential_positions = page.eval_on_selector_all(
            '#body-credentials-edit .body-credential-position', 'elements => elements.map(element => element.value)')

        assert credential_names == ['username', 'password']
        assert credential_positions == ['', '2']

        assert page.input_value('#id_edit-ping_method') == 'GET'
        assert page.input_value('#id_edit-content_type') == 'application/soap+xml'

        # .. now edit fields from several tabs at once ..
        edited_name = name + '-edited'
        edit_soap_outconn(page, outconn_id, {
            'name': edited_name,
            'soap_version': '1.1',
            'use_mtom': False,
            'tls_client_key': '',
            'body_credentials': [
                {'name': 'accessToken'},
            ],
        })
        _ = wait_for_soap_outconn_row(page, edited_name)

        # .. reload again and verify the changes round-tripped through the server ..
        open_soap_outconn_page(page, base_url, query=edited_name)
        _ = wait_for_soap_outconn_row(page, edited_name)
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-name') == edited_name
        assert page.input_value('#id_edit-soap_version') == '1.1'
        assert page.is_checked('#id_edit-use_ws_addressing')
        assert not page.is_checked('#id_edit-use_mtom')
        assert page.input_value('#id_edit-tls_client_cert') == '/opt/certs/client-cert.pem'
        assert page.input_value('#id_edit-tls_client_key') == ''

        credential_names = page.eval_on_selector_all(
            '#body-credentials-edit .body-credential-name', 'elements => elements.map(element => element.value)')

        assert credential_names == ['accessToken']

        # .. close the dialog ..
        close_dialog_via_jquery(page, 'edit-div')

        # .. delete and verify the row is gone ..
        delete_soap_outconn(page, outconn_id)
        assert find_soap_outconn_row(page, edited_name) is None

        # .. and one more reload to confirm the server no longer knows the connection.
        open_soap_outconn_page(page, base_url, query=edited_name)
        assert find_soap_outconn_row(page, edited_name) is None

# ################################################################################################################################

    def test_ping_against_live_server(
        self, logged_in_page:'Page', zato_dashboard:'anydict', soap_test_server:'any_') -> 'None':
        """ The ping button reaches a live test server and reports success.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'ping'

        outconn_id = create_soap_outconn(page, base_url, name, soap_test_server.address, {
            'url_path': '/ping',
            'ping_method': 'GET',
        })

        result = ping_soap_outconn(page, name)
        assert result['is_success'], f'Ping should succeed, got: {result}'

        delete_soap_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
