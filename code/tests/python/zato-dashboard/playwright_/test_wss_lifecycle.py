# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery
from wss_definition import change_wss_password, create_wss_definition, delete_wss_definition, edit_wss_definition, \
    find_wss_row, open_edit_dialog, open_wss_page, wait_for_wss_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.wss.' + CryptoManager.generate_hex_string(32) + '.'

_Sample_Key_PEM = '-----BEGIN PRIVATE KEY-----\nc2FtcGxlLWtleS1ib2R5\n-----END PRIVATE KEY-----'
_Sample_Cert_PEM = '-----BEGIN CERTIFICATE-----\nc2FtcGxlLWNlcnQtYm9keQ==\n-----END CERTIFICATE-----'

# ################################################################################################################################
# ################################################################################################################################

class TestWSSLifecycle:
    """ WS-Security definition lifecycle per mode - create, edit, change password, delete.
    Everything runs through the browser and every value is verified by reloading the page,
    so the table is rebuilt from the server, and reading the edit dialog.
    """

# ################################################################################################################################

    def test_username_token_lifecycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'token'
        username = 'user.' + name

        # Create a UsernameToken definition with the digest form on ..
        wss_id = create_wss_definition(page, base_url, name, username, 'username_token', {
            'use_digest': True,
        })

        # .. reload the page so the table is rebuilt from what the server persisted ..
        open_wss_page(page, base_url, query=name)
        _ = wait_for_wss_row(page, name)

        # .. and verify every value through the edit dialog ..
        open_edit_dialog(page, wss_id)

        assert page.input_value('#id_edit-name') == name
        assert page.input_value('#id_edit-username') == username
        assert page.input_value('#id_edit-mode') == 'username_token'
        assert page.is_checked('#id_edit-use_digest')

        close_dialog_via_jquery(page, 'edit-div')

        # .. edit - a new name, a new username, digest off ..
        edited_name = name + '-edited'
        edit_wss_definition(page, wss_id, {
            'name': edited_name,
            'username': username + '-edited',
            'use_digest': False,
        })
        _ = wait_for_wss_row(page, edited_name)

        # .. reload and verify the changes round-tripped through the server ..
        open_wss_page(page, base_url, query=edited_name)
        _ = wait_for_wss_row(page, edited_name)
        open_edit_dialog(page, wss_id)

        assert page.input_value('#id_edit-name') == edited_name
        assert page.input_value('#id_edit-username') == username + '-edited'
        assert not page.is_checked('#id_edit-use_digest')

        close_dialog_via_jquery(page, 'edit-div')

        # .. change the password, which must go through without an error ..
        change_wss_password(page, wss_id, 'new-password-' + CryptoManager.generate_hex_string(32))

        # .. and delete, verifying the definition is gone after a reload too.
        delete_wss_definition(page, wss_id)
        assert find_wss_row(page, edited_name) is None

        open_wss_page(page, base_url, query=edited_name)
        assert find_wss_row(page, edited_name) is None

# ################################################################################################################################

    def test_x509_lifecycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'x509'
        username = 'user.' + name

        # Create an X.509 definition with signing and encryption on, plus its crypto material ..
        wss_id = create_wss_definition(page, base_url, name, username, 'x509', {
            'sign': True,
            'encrypt': True,
            'signing_key': _Sample_Key_PEM,
            'signing_certificate_chain': _Sample_Cert_PEM,
            'decryption_key': _Sample_Key_PEM,
            'peer_certificate': _Sample_Cert_PEM,
        })

        # .. reload and verify every value through the edit dialog ..
        open_wss_page(page, base_url, query=name)
        _ = wait_for_wss_row(page, name)
        open_edit_dialog(page, wss_id)

        assert page.input_value('#id_edit-mode') == 'x509'
        assert page.is_checked('#id_edit-sign')
        assert page.is_checked('#id_edit-encrypt')
        assert page.input_value('#id_edit-signing_key') == _Sample_Key_PEM
        assert page.input_value('#id_edit-signing_certificate_chain') == _Sample_Cert_PEM
        assert page.input_value('#id_edit-decryption_key') == _Sample_Key_PEM
        assert page.input_value('#id_edit-peer_certificate') == _Sample_Cert_PEM

        close_dialog_via_jquery(page, 'edit-div')

        # .. edit - encryption off, trust anchors instead of a pinned peer certificate ..
        edit_wss_definition(page, wss_id, {
            'encrypt': False,
            'peer_certificate': '',
            'trust_anchors': _Sample_Cert_PEM,
        })

        # .. reload and verify the changes round-tripped through the server ..
        open_wss_page(page, base_url, query=name)
        _ = wait_for_wss_row(page, name)
        open_edit_dialog(page, wss_id)

        assert not page.is_checked('#id_edit-encrypt')
        assert page.input_value('#id_edit-peer_certificate') == ''
        assert page.input_value('#id_edit-trust_anchors') == _Sample_Cert_PEM

        close_dialog_via_jquery(page, 'edit-div')

        # .. and delete.
        delete_wss_definition(page, wss_id)

        open_wss_page(page, base_url, query=name)
        assert find_wss_row(page, name) is None

# ################################################################################################################################

    def test_saml_lifecycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'saml'
        username = 'user.' + name

        # Create a SAML definition with a signed assertion and its signing material ..
        wss_id = create_wss_definition(page, base_url, name, username, 'saml', {
            'issuer': 'urn:issuer:' + name,
            'subject': 'subject.' + name,
            'audience': 'urn:audience:' + name,
            'sign': True,
            'signing_key': _Sample_Key_PEM,
            'signing_certificate_chain': _Sample_Cert_PEM,
        })

        # .. reload and verify every value through the edit dialog ..
        open_wss_page(page, base_url, query=name)
        _ = wait_for_wss_row(page, name)
        open_edit_dialog(page, wss_id)

        assert page.input_value('#id_edit-mode') == 'saml'
        assert page.input_value('#id_edit-issuer') == 'urn:issuer:' + name
        assert page.input_value('#id_edit-subject') == 'subject.' + name
        assert page.input_value('#id_edit-audience') == 'urn:audience:' + name
        assert page.is_checked('#id_edit-sign')
        assert page.input_value('#id_edit-signing_key') == _Sample_Key_PEM

        close_dialog_via_jquery(page, 'edit-div')

        # .. edit - new issuer, signing off ..
        edit_wss_definition(page, wss_id, {
            'issuer': 'urn:issuer:edited',
            'sign': False,
        })

        # .. reload and verify the changes round-tripped through the server ..
        open_wss_page(page, base_url, query=name)
        _ = wait_for_wss_row(page, name)
        open_edit_dialog(page, wss_id)

        assert page.input_value('#id_edit-issuer') == 'urn:issuer:edited'
        assert not page.is_checked('#id_edit-sign')

        close_dialog_via_jquery(page, 'edit-div')

        # .. and delete.
        delete_wss_definition(page, wss_id)

        open_wss_page(page, base_url, query=name)
        assert find_wss_row(page, name) is None

# ################################################################################################################################

    def test_mode_selector_toggles_tabs(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The mode selector shows only the tabs the mode makes use of.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        open_wss_page(page, base_url)

        # Open the create dialog ..
        page.click('#markup .page_prompt a')
        _ = page.wait_for_selector('#create-div', state='visible')

        # .. UsernameToken - the token tab is visible, SAML and crypto are not ..
        page.evaluate('$("#id_mode").val("username_token").trigger("change")')
        assert page.is_visible('#create-div .dashboard-tab[data-tab="token"]')
        assert not page.is_visible('#create-div .dashboard-tab[data-tab="saml"]')
        assert not page.is_visible('#create-div .dashboard-tab[data-tab="crypto"]')

        # .. X.509 - crypto only ..
        page.evaluate('$("#id_mode").val("x509").trigger("change")')
        assert not page.is_visible('#create-div .dashboard-tab[data-tab="token"]')
        assert not page.is_visible('#create-div .dashboard-tab[data-tab="saml"]')
        assert page.is_visible('#create-div .dashboard-tab[data-tab="crypto"]')

        # .. SAML - both the SAML and crypto tabs.
        page.evaluate('$("#id_mode").val("saml").trigger("change")')
        assert not page.is_visible('#create-div .dashboard-tab[data-tab="token"]')
        assert page.is_visible('#create-div .dashboard-tab[data-tab="saml"]')
        assert page.is_visible('#create-div .dashboard-tab[data-tab="crypto"]')

# ################################################################################################################################
# ################################################################################################################################
