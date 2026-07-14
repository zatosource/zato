# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import navigate_to_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

from bearer_token import Bearer_Page_Url, Cell_Audience, Cell_Auth_URL, Cell_Claims, Cell_Issuer, Cell_JWKS_URL, \
    Cell_Name, Cell_Token_Type, Cell_Username, create_dynamic_definition, create_static_definition, delete_definition, \
    edit_definition, find_definition_row, get_cell_texts, open_edit_dialog, wait_for_definition_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.bearer.crud.' + CryptoManager.generate_hex_string(32) + '.'

# The number of claims rows used in the many-claims boundary test
_Many_Claims_Count = 12

# ################################################################################################################################
# ################################################################################################################################

class TestBearerTokenCRUD:
    """ Tests for the Bearer token definition create, edit and delete flows,
    with the inbound verification fields and boundary values for claims rows.
    """

# ################################################################################################################################

    def test_01_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the Bearer tokens page and verifies its structure.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the Bearer tokens page ..
        navigate_to_page(page, base_url, Bearer_Page_Url)

        # .. verify the page heading ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'Bearer tokens' in heading_text, f'Expected "Bearer tokens" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = page.query_selector('#markup .page_prompt a')
        create_link_text = create_link.inner_text()
        assert 'Create a Bearer token definition' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. verify table headers.
        headers = page.query_selector_all('#data-table thead th a')

        header_texts:'anylist' = []

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        assert 'name' in header_texts, f'Expected "name" in headers, got: {header_texts}'
        assert 'token type' in header_texts, f'Expected "token type" in headers, got: {header_texts}'

# ################################################################################################################################

    def test_02_create_dynamic_with_inbound_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a dynamic definition with all the inbound verification fields
        and verifies the row carries them all.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'dynamic'
        client_id = 'client.' + definition_name
        issuer = 'https://idp.example.com/realms/test'
        jwks_url = 'https://idp.example.com/realms/test/protocol/openid-connect/certs'
        audience = 'test-audience'
        claims = 'department=Accounting'

        # Create the definition ..
        _ = create_dynamic_definition(page, base_url, definition_name, {
            'username': client_id,
            'secret': 'secret.' + CryptoManager.generate_hex_string(),
            'issuer': issuer,
            'jwks_url': jwks_url,
            'audience': audience,
            'claims': claims,
        })

        # .. and verify the row's cells, including the hidden inbound ones.
        row = find_definition_row(page, definition_name)
        cells = get_cell_texts(row)

        assert cells[Cell_Name] == definition_name, f'Expected name "{definition_name}", got: "{cells[Cell_Name]}"'
        assert cells[Cell_Token_Type] == 'Dynamic', f'Expected token type "Dynamic", got: "{cells[Cell_Token_Type]}"'
        assert cells[Cell_Username] == client_id, f'Expected client ID "{client_id}", got: "{cells[Cell_Username]}"'

        assert cells[Cell_Issuer] == issuer, f'Expected issuer "{issuer}", got: "{cells[Cell_Issuer]}"'
        assert cells[Cell_JWKS_URL] == jwks_url, f'Expected JWKS URL "{jwks_url}", got: "{cells[Cell_JWKS_URL]}"'
        assert cells[Cell_Audience] == audience, f'Expected audience "{audience}", got: "{cells[Cell_Audience]}"'
        assert cells[Cell_Claims] == claims, f'Expected claims "{claims}", got: "{cells[Cell_Claims]}"'

# ################################################################################################################################

    def test_03_create_static(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a static definition via the static tokens tab and verifies the row
        marks it as static, with the dynamic-only columns holding placeholders.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'static'
        token = 'token.' + CryptoManager.generate_hex_string()

        # Create the definition ..
        _ = create_static_definition(page, base_url, definition_name, token)

        # .. and verify the row's cells.
        row = find_definition_row(page, definition_name)
        cells = get_cell_texts(row)

        assert cells[Cell_Name] == definition_name, f'Expected name "{definition_name}", got: "{cells[Cell_Name]}"'
        assert cells[Cell_Token_Type] == 'Static', f'Expected token type "Static", got: "{cells[Cell_Token_Type]}"'

        # .. static definitions have no client ID or auth endpoint.
        assert cells[Cell_Username] == '---', f'Expected a placeholder client ID, got: "{cells[Cell_Username]}"'
        assert cells[Cell_Auth_URL] == '---', f'Expected a placeholder auth endpoint, got: "{cells[Cell_Auth_URL]}"'

# ################################################################################################################################

    def test_04_claims_boundary_values(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates definitions with no claims, a single claim and many claims rows
        with values containing spaces, then verifies each set round-trips through the edit dialog.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Build the many-claims value, with rows whose values contain spaces and dots ..
        many_claims_rows:'anylist' = []

        for claim_index in range(_Many_Claims_Count):
            many_claims_rows.append(f'claim.number.{claim_index}=Department Value {claim_index}')

        many_claims = '\n'.join(many_claims_rows)

        # .. each case is a suffix and the claims value to round-trip ..
        cases = [
            ('claims-none', ''),
            ('claims-one', 'department=Accounting'),
            ('claims-many', many_claims),
        ]

        for suffix, claims in cases:

            definition_name = _Test_Name_Prefix + suffix
            client_id = 'client.' + definition_name

            # .. create the definition with this claims set ..
            definition_id = create_dynamic_definition(page, base_url, definition_name, {
                'username': client_id,
                'audience': 'test-audience',
                'claims': claims,
            })

            # .. reload the page so the row comes from the server rather than from the AJAX response ..
            navigate_to_page(page, base_url, Bearer_Page_Url)
            _ = wait_for_definition_row(page, definition_name)

            # .. open the edit dialog and verify the claims round-tripped exactly ..
            open_edit_dialog(page, definition_id)

            edit_claims = page.input_value('#id_edit-claims')
            assert edit_claims == claims, f'[{suffix}] expected claims "{claims}", got: "{edit_claims}"'

            # .. and close the dialog before the next case.
            page.evaluate('$("#edit-div").dialog("close")')
            page.wait_for_function('!document.querySelector("#edit-div").offsetParent')

# ################################################################################################################################

    def test_05_edit_updates_inbound_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, changes its audience and claims via the edit dialog
        and verifies the row reflects the new values.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'edit'
        client_id = 'client.' + definition_name

        new_audience = 'audience-after-edit'
        new_claims = 'department=Sales'

        # Create the definition with the initial inbound fields ..
        definition_id = create_dynamic_definition(page, base_url, definition_name, {
            'username': client_id,
            'audience': 'audience-before-edit',
            'claims': 'department=Accounting',
        })

        # .. change the audience and the claims via the edit dialog ..
        edit_definition(page, base_url, definition_id, {
            'audience': new_audience,
            'claims': new_claims,
        })

        # .. and verify the row carries the new values.
        row = find_definition_row(page, definition_name)
        cells = get_cell_texts(row)

        assert cells[Cell_Audience] == new_audience, f'Expected audience "{new_audience}", got: "{cells[Cell_Audience]}"'
        assert cells[Cell_Claims] == new_claims, f'Expected claims "{new_claims}", got: "{cells[Cell_Claims]}"'

# ################################################################################################################################

    def test_06_delete(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, deletes it via the UI and verifies it is gone,
        also after a page reload.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'delete'
        client_id = 'client.' + definition_name

        # Create the definition ..
        definition_id = create_dynamic_definition(page, base_url, definition_name, {
            'username': client_id,
        })

        # .. delete it via the confirmation dialog ..
        delete_definition(page, definition_id)

        # .. the row is gone from the current view ..
        row = find_definition_row(page, definition_name)
        assert row is None, f'Expected no row for "{definition_name}" after delete'

        # .. and it stays gone after a reload.
        navigate_to_page(page, base_url, Bearer_Page_Url)

        page_content = page.content()
        assert definition_name not in page_content, f'Deleted definition "{definition_name}" should not be in the page'

# ################################################################################################################################
# ################################################################################################################################
