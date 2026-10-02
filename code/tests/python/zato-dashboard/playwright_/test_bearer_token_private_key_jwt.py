# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK

# pytest
import pytest

# Requests
import requests

# Zato
from zato.common.api import OAuth
from zato.common.crypto.api import CryptoManager
from zato.common.private_key_jwt import get_public_key_pem, load_private_key
from zato.common.test.fhir import FHIRTestServer
from zato.common.test.fhir.common import auth_type_oauth
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, submit_create_form, submit_edit_form
from zato.common.test.private_key_jwt import generate_rsa_private_key_pem
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from bearer_token import Bearer_Page_Url, Cell_Name, Cell_Token_Type, Cell_Username, find_definition_row, \
    get_cell_texts, get_definition_id, open_edit_dialog, wait_for_definition_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.bearer.pkjwt.' + CryptoManager.generate_hex_string(32) + '.'

# Hidden cells with the private key JWT fields
Cell_Client_Auth_Method = 26
Cell_Has_Private_Key    = 27
Cell_JWT_Algorithm      = 28
Cell_Key_ID             = 29

# The client the fake FHIR server knows and the key it verifies assertions with
_client_id = 'zato-dashboard-pkjwt-client'
_client_secret = 'secret.' + CryptoManager.generate_hex_string()

_private_key_pem = generate_rsa_private_key_pem()
_public_key_pem = get_public_key_pem(load_private_key(_private_key_pem))

_key_id = 'dashboard-key-1'
_rotated_key_id = 'dashboard-key-2'

# What the edit dialog says about the key under its empty input
_stored_key_hint = 'A key is stored - leave empty to keep it'

# Timeout for HTTP requests made outside the browser, in seconds
_http_timeout = 10

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def token_server() -> 'any_':
    """ A fake FHIR server whose token endpoint accepts assertions signed with the test key.
    """
    server = FHIRTestServer(_client_id, _client_secret, auth_type_oauth, public_key_pem=_public_key_pem)
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

def _is_row_visible(page:'Page', dialog_id:'str', row_class:'str') -> 'bool':
    """ Returns True if any row of the given class in the dialog is visible.
    """
    out = page.is_visible(f'#{dialog_id} tr.{row_class}:not(.bearer-provider-options)')
    return out

# ################################################################################################################################

def _fill_private_key_jwt_form(page:'Page', name:'str', token_url:'str', private_key_pem:'str', key_id:'str') -> 'None':
    """ Fills the create form with a private key JWT definition.
    """
    page.fill('#id_name', name)
    page.fill('#id_username', _client_id)
    page.fill('#id_auth_server_url', token_url)

    _ = page.select_option('#id_client_auth_method', OAuth.Client_Auth_Method.Private_Key_JWT)
    _ = page.wait_for_selector('#create-div #id_private_key', state='visible', timeout=5000)

    page.fill('#id_private_key', private_key_pem)
    page.fill('#id_key_id', key_id)

# ################################################################################################################################

def _create_private_key_jwt_definition(page:'Page', base_url:'str', name:'str', token_url:'str') -> 'str':
    """ Creates a private key JWT definition via the UI and returns its server-side ID.
    """
    navigate_to_page(page, base_url, Bearer_Page_Url)
    open_create_dialog(page)

    _fill_private_key_jwt_form(page, name, token_url, _private_key_pem, _key_id)

    submit_create_form(page)
    _ = wait_for_definition_row(page, name)

    out = get_definition_id(page, name)
    return out

# ################################################################################################################################

def _close_dialog(page:'Page', dialog_id:'str') -> 'None':
    page.evaluate(f'$("#{dialog_id}").dialog("close")')
    _ = page.wait_for_function(f'!document.querySelector("#{dialog_id}").offsetParent')

# ################################################################################################################################
# ################################################################################################################################

class TestBearerTokenPrivateKeyJWT:
    """ Tests for private key JWT definitions in the dashboard - the rows that follow the authentication select,
    creating a definition with a key, an edit that keeps the stored key, the public key link and the Get token link.
    """

# ################################################################################################################################

    def test_01_rows_follow_the_authentication_select(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The create dialog shows the client secret rows by default and swaps them for the private key rows
        when private key JWT is selected, with the provider options staying collapsed.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        navigate_to_page(page, base_url, Bearer_Page_Url)
        open_create_dialog(page)

        # The default is the client secret ..
        method = page.input_value('#id_client_auth_method')
        assert method == OAuth.Client_Auth_Method.Client_Secret, f'Expected client secret by default, got: {method}'

        assert _is_row_visible(page, 'create-div', 'bearer-auth-client-secret'), 'Expected the client secret rows'
        assert not _is_row_visible(page, 'create-div', 'bearer-auth-private-key-jwt'), 'Expected no private key rows yet'

        # .. selecting private key JWT swaps the rows ..
        _ = page.select_option('#id_client_auth_method', OAuth.Client_Auth_Method.Private_Key_JWT)

        _ = page.wait_for_selector('#create-div #id_private_key', state='visible', timeout=5000)

        assert not _is_row_visible(page, 'create-div', 'bearer-auth-client-secret'), 'Expected the secret rows to hide'
        assert page.is_visible('#create-div #id_jwt_algorithm'), 'Expected the algorithm select'
        assert page.is_visible('#create-div #id_key_id'), 'Expected the key ID input'

        # .. the algorithm defaults to RS384 ..
        algorithm = page.input_value('#id_jwt_algorithm')
        assert algorithm == OAuth.Default.JWT_Algorithm, f'Expected {OAuth.Default.JWT_Algorithm}, got: {algorithm}'

        # .. the provider options stay collapsed until asked for ..
        assert not page.is_visible('#create-div #id_assertion_audience'), 'Expected the provider options to be collapsed'
        assert not page.is_visible('#create-div #id_certificate'), 'Expected the certificate to be collapsed'

        # .. and going back to the client secret restores the secret rows.
        _ = page.select_option('#id_client_auth_method', OAuth.Client_Auth_Method.Client_Secret)
        _ = page.wait_for_selector('#create-div #id_secret', state='visible', timeout=5000)

        assert not _is_row_visible(page, 'create-div', 'bearer-auth-private-key-jwt'), 'Expected the key rows to hide'

        _close_dialog(page, 'create-div')

# ################################################################################################################################

    def test_02_create_with_a_private_key(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        token_server:'FHIRTestServer',
        ) -> 'None':
        """ Creates a private key JWT definition and verifies the row carries the method, the algorithm,
        the key ID and the fact that a key is stored, both right away and after a reload.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'create'

        _ = _create_private_key_jwt_definition(page, base_url, definition_name, token_server.token_endpoint)

        for reload_page in (False, True):

            if reload_page:
                navigate_to_page(page, base_url, Bearer_Page_Url)
                _ = wait_for_definition_row(page, definition_name)

            row = find_definition_row(page, definition_name)
            cells = get_cell_texts(row)

            assert cells[Cell_Name] == definition_name, f'Expected name "{definition_name}", got: "{cells[Cell_Name]}"'
            assert cells[Cell_Token_Type] == 'Dynamic', f'Expected a dynamic definition, got: "{cells[Cell_Token_Type]}"'
            assert cells[Cell_Username] == _client_id, f'Expected client ID "{_client_id}", got: "{cells[Cell_Username]}"'

            assert cells[Cell_Client_Auth_Method] == OAuth.Client_Auth_Method.Private_Key_JWT, \
                f'Expected private key JWT, got: "{cells[Cell_Client_Auth_Method]}"'
            assert cells[Cell_Has_Private_Key] == 'True', f'Expected a stored key, got: "{cells[Cell_Has_Private_Key]}"'
            assert cells[Cell_JWT_Algorithm] == OAuth.Default.JWT_Algorithm, \
                f'Expected {OAuth.Default.JWT_Algorithm}, got: "{cells[Cell_JWT_Algorithm]}"'
            assert cells[Cell_Key_ID] == _key_id, f'Expected key ID "{_key_id}", got: "{cells[Cell_Key_ID]}"'

# ################################################################################################################################

    def test_03_create_without_a_usable_key_is_refused(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A private key JWT definition whose key does not parse is not created and the page says why.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'bad-key'

        navigate_to_page(page, base_url, Bearer_Page_Url)
        open_create_dialog(page)

        _fill_private_key_jwt_form(page, definition_name, 'https://example.com/oauth2/token', 'this is not a key', _key_id)

        # The submission fails on the server side, which the page reports in its message area ..
        page.click('#create-div input[type="submit"]')
        _ = page.wait_for_selector('#user-message-div', state='visible', timeout=10000)

        message = cast_('any_', page.query_selector('#user-message')).inner_text()
        assert 'could not be parsed' in message, f'Expected a parsing error, got: {message}'

        # .. and no row was added.
        navigate_to_page(page, base_url, Bearer_Page_Url)

        row = find_definition_row(page, definition_name)
        assert row is None, f'Expected no row for "{definition_name}"'

# ################################################################################################################################

    def test_04_edit_keeps_the_stored_key(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        token_server:'FHIRTestServer',
        ) -> 'None':
        """ The edit dialog never shows the stored key, says that one is stored and keeps it
        when the key input is left empty and another field changes.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'edit'
        definition_id = _create_private_key_jwt_definition(page, base_url, definition_name, token_server.token_endpoint)

        # The row must come from the server for the edit dialog to know a key is stored ..
        navigate_to_page(page, base_url, Bearer_Page_Url)
        _ = wait_for_definition_row(page, definition_name)

        open_edit_dialog(page, definition_id)

        # .. the key input is empty and the hint says a key is stored ..
        method = page.input_value('#id_edit-client_auth_method')
        assert method == OAuth.Client_Auth_Method.Private_Key_JWT, f'Expected private key JWT, got: {method}'

        key_input = page.input_value('#id_edit-private_key')
        assert key_input == '', 'Expected the stored key not to be shown'

        hint = cast_('any_', page.query_selector('#edit-private-key-hint')).inner_text()
        assert hint == _stored_key_hint, f'Expected the stored key hint, got: {hint}'

        assert page.is_visible('#edit-public-key-link'), 'Expected the public key link'

        # .. changing the key ID alone keeps the key ..
        page.fill('#id_edit-key_id', _rotated_key_id)
        submit_edit_form(page)

        navigate_to_page(page, base_url, Bearer_Page_Url)
        _ = wait_for_definition_row(page, definition_name)

        row = find_definition_row(page, definition_name)
        cells = get_cell_texts(row)

        assert cells[Cell_Has_Private_Key] == 'True', f'Expected the key to be kept, got: "{cells[Cell_Has_Private_Key]}"'
        assert cells[Cell_Key_ID] == _rotated_key_id, f'Expected key ID "{_rotated_key_id}", got: "{cells[Cell_Key_ID]}"'

# ################################################################################################################################

    def test_05_public_key_link(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        token_server:'FHIRTestServer',
        ) -> 'None':
        """ The public key link in the edit dialog serves the public half of the stored key as PEM and as a JWK set.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'public-key'
        definition_id = _create_private_key_jwt_definition(page, base_url, definition_name, token_server.token_endpoint)

        navigate_to_page(page, base_url, Bearer_Page_Url)
        _ = wait_for_definition_row(page, definition_name)

        open_edit_dialog(page, definition_id)

        href = cast_('any_', page.query_selector('#edit-public-key-link')).get_attribute('href')
        assert f'/public-key/{definition_id}/cluster/1/' in href, f'Unexpected public key link: {href}'

        # The link is fetched with the browser's own session, so it is the dashboard that serves it
        response = page.request.get(f'{base_url}{href}')
        assert response.status == OK, f'Expected 200 from the public key link, got: {response.status}'

        body = response.text()

        assert _public_key_pem.strip() in body, f'Expected the public key PEM in the response, got: {body}'
        assert f'"kid": "{_key_id}"' in body, f'Expected the key ID in the JWK set, got: {body}'
        assert f'"alg": "{OAuth.Default.JWT_Algorithm}"' in body, f'Expected the algorithm in the JWK set, got: {body}'
        assert 'PRIVATE KEY' not in body, 'The private key must never be served'

        _close_dialog(page, 'edit-div')

# ################################################################################################################################

    def test_06_get_token_signs_an_assertion(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        token_server:'FHIRTestServer',
        ) -> 'None':
        """ The Get token link of a private key JWT definition obtains a token from the token endpoint
        with a signed assertion, and the token is one the endpoint accepts.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'get-token'
        _ = _create_private_key_jwt_definition(page, base_url, definition_name, token_server.token_endpoint)

        navigate_to_page(page, base_url, Bearer_Page_Url)
        row = wait_for_definition_row(page, definition_name)

        # Clicking the link posts to the dashboard, which asks the server for a token ..
        with page.expect_response(lambda response: '/get-token/' in response.url) as response_info:
            link = row.query_selector('a:text-is("Get token")')
            link.click()

        result = response_info.value.json()

        assert result['is_success'] is True, f'Expected a token, got: {result}'
        assert result['token'], f'Expected a non-empty token, got: {result}'

        # .. and the token opens the resources behind the token endpoint.
        headers = {'Authorization': f'Bearer {result["token"]}'}
        response = requests.get(f'{token_server.address}/Patient', headers=headers, timeout=_http_timeout)

        assert response.status_code == OK, f'Expected the token to be accepted, got: {response.status_code} -> {response.text}'

# ################################################################################################################################
# ################################################################################################################################
