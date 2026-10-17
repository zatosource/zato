# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from http.client import OK, UNAUTHORIZED

# requests
import requests

# Zato
from zato.common.util.mcp_oauth import Metadata_Path_Prefix

# Zato - test helpers - Keycloak issues the tokens
_keycloak_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'test'))

if _keycloak_directory not in sys.path:
    sys.path.insert(0, _keycloak_directory)

import keycloak_

# Zato - test helpers
import _mcp_wizard as wizard_page

from bearer_token import create_dynamic_definition
from mcp_gateway_live import assert_status, Echo_Service, HTTP_Timeout, Refusal_Wait

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The scopes the gateways ask clients for, in the order they are typed in
Scopes = ['openid', 'profile']

# What the server logs when it refuses a save with OAuth and no verifying definition
Refused_Save_Log_Patterns = ('has OAuth on but',)

# What the security card's OAuth tab holds
_security_body = '#mcp-wizard-security-body'
_scope_text_field = f'{_security_body} .mcp-scope-list .search-field input'

# ################################################################################################################################
# ################################################################################################################################

def get_metadata(server_port:'int', url_path:'str') -> 'anydict':
    """ Returns the OAuth metadata document the gateway at the given path publishes.
    """
    metadata_url = f'http://127.0.0.1:{server_port}{Metadata_Path_Prefix}{url_path}'
    response = requests.get(metadata_url, timeout=HTTP_Timeout)
    assert response.status_code == OK, f'Expected the metadata document, got {response.status_code} -> {response.text}'

    out = response.json()
    return out

# ################################################################################################################################

def assert_oauth_challenge(server_port:'int', url_path:'str') -> 'None':
    """ Asserts that a request with no credentials receives the 401 naming the gateway's metadata document,
    and that the document names the issuer and the scopes.
    """
    response = assert_status(server_port, url_path, None, UNAUTHORIZED)

    challenge = response.headers['WWW-Authenticate']
    expected_end = f'{Metadata_Path_Prefix}{url_path}"'

    assert challenge.startswith('Bearer resource_metadata="'), challenge
    assert challenge.endswith(expected_end), challenge

    document = get_metadata(server_port, url_path)

    assert document['resource'].endswith(url_path), document
    assert document['authorization_servers'] == [keycloak_.get_issuer()], document
    assert document['scopes_supported'] == Scopes, document

# ################################################################################################################################

def get_token() -> 'str':
    """ Returns a token Keycloak issues to the accounting client.
    """
    out = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)
    return out

# ################################################################################################################################

def create_bearer_definition(page:'Page', base_url:'str', name:'str', options:'anydict | None'=None) -> 'str':
    """ Creates a bearer token definition of the given name verifying the tokens Keycloak issues and returns its id.
    Options override the Keycloak settings, e.g. to verify tokens of another issuer.
    """
    definition_options = {
        'username': name,
        'secret': keycloak_.Secret_Accounting,
        'auth_server_url': keycloak_.get_token_url(),
        'issuer': keycloak_.get_issuer(),
        'audience': keycloak_.Audience_Main,
    }

    if options:
        definition_options.update(options)

    out = create_dynamic_definition(page, base_url, name, definition_options)
    return out

# ################################################################################################################################

def open_oauth_tab(page:'Page') -> 'None':
    """ Opens the security card and shows its OAuth tab.
    """
    wizard_page.open_picker_card(page, 'security')

    page.click('#mcp-wizard-security-tabs .dashboard-tab[data-pane="oauth"]')

    active_pane = f'{_security_body} .mcp-wizard-security-pane-active[data-pane="oauth"]'
    _ = page.wait_for_selector(active_pane, state='attached', timeout=HTTP_Timeout * 1000)

# ################################################################################################################################

def open_definitions_tab(page:'Page') -> 'None':
    """ Opens the security card and shows its tab with the picker.
    """
    wizard_page.open_picker_card(page, 'security')
    page.click('#mcp-wizard-security-tabs .dashboard-tab[data-pane="definitions"]')

# ################################################################################################################################

def type_scopes(page:'Page') -> 'None':
    """ Types the scopes into the OAuth tab, one chip each.
    """
    for scope in Scopes:
        page.fill(_scope_text_field, scope)
        page.press(_scope_text_field, 'Enter')

# ################################################################################################################################

def fill_oauth_gateway(page:'Page', base_url:'str', gateway_name:'str', url_path:'str', security_names:'strlist') -> 'None':
    """ Answers the create wizard for a gateway with OAuth on, the scopes typed in and the given definitions assigned,
    without saving it.
    """
    wizard_page.open_wizard_create(page, base_url)

    page.fill(wizard_page.field_selector('name'), gateway_name)
    page.fill(wizard_page.field_selector('url_path'), url_path)

    wizard_page.assign_badge(page, 'services', Echo_Service)

    for name in security_names:
        wizard_page.assign_badge(page, 'security', name)

    open_oauth_tab(page)
    page.check(wizard_page.field_selector('oauth'))

    type_scopes(page)

# ################################################################################################################################

def create_oauth_gateway(page:'Page', base_url:'str', gateway_name:'str', url_path:'str', security_names:'strlist') -> 'None':
    """ Creates a gateway with OAuth on through the wizard, with the given definitions assigned.
    """
    fill_oauth_gateway(page, base_url, gateway_name, url_path, security_names)
    wizard_page.save_create(page)

# ################################################################################################################################

def attempt_refused_save(page:'Page', button_selector:'str') -> 'None':
    """ Clicks a save button of a save the server refuses and asserts that the wizard stays on its page.
    """
    page.click(button_selector)
    page.wait_for_timeout(Refusal_Wait)

    assert wizard_page.is_on_wizard_page(page), f'Expected no redirect for a refused save, got: {page.url}'

# ################################################################################################################################
# ################################################################################################################################
