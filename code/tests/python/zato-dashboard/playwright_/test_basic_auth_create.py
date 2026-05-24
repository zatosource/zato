# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/basic-auth/?cluster=1'

_Test_Name_Prefix = 'test.basic.auth.' + os.urandom(4).hex() + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthCreate:
    """ Tests for the basic auth create flow.

    **DONE** test_01_page_loads
    **DONE** test_02_create_one
    """

    def test_01_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the basic auth page and verifies its structure:
        - h2 heading contains "Basic Auth"
        - data table is visible
        - "Create a Basic Auth definition" link is present
        - table headers include Name, Username, Realm
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the basic auth page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the page heading ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'Basic Auth' in heading_text, f'Expected "Basic Auth" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = page.query_selector('#markup .page_prompt a')
        create_link_text = create_link.inner_text()
        assert 'Create a Basic Auth definition' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. verify table headers (CSS text-transform may uppercase them).
        headers = page.query_selector_all('#data-table thead th a')

        header_texts = [] # type: list

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        assert 'name' in header_texts, f'Expected "name" in headers, got: {header_texts}'
        assert 'username' in header_texts, f'Expected "username" in headers, got: {header_texts}'
        assert 'realm' in header_texts, f'Expected "realm" in headers, got: {header_texts}'

# ################################################################################################################################

    def test_02_create_one(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a single Basic Auth definition via the UI dialog and verifies
        that the new row appears in the table with correct cell text for name, username, and realm.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'create-one'
        definition_username = 'user.' + definition_name
        definition_realm = 'realm.' + definition_name
        definition_password = 'password.' + os.urandom(8).hex()

        # Navigate to the basic auth page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. click the create link to open the dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. fill in the form fields ..
        page.fill('#id_name', definition_name)
        page.fill('#id_username', definition_username)
        page.fill('#id_realm', definition_realm)
        page.fill('#id_password', definition_password)

        # .. submit the form ..
        page.click('#create-div input[type="submit"]')

        # .. wait for the dialog to close ..
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. verify the new row appears in the table ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{definition_name}"))'
        row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. extract cell texts from the row ..
        cells = row.query_selector_all('td')

        name_cell_text = cells[2].inner_text().strip()
        username_cell_text = cells[3].inner_text().strip()
        realm_cell_text = cells[4].inner_text().strip()

        # .. verify each cell has the correct value.
        assert name_cell_text == definition_name, \
            f'Expected name "{definition_name}", got: "{name_cell_text}"'

        assert username_cell_text == definition_username, \
            f'Expected username "{definition_username}", got: "{username_cell_text}"'

        assert realm_cell_text == definition_realm, \
            f'Expected realm "{definition_realm}", got: "{realm_cell_text}"'

# ################################################################################################################################
# ################################################################################################################################
