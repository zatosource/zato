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

    def test_03_create_multiple(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates 3 Basic Auth definitions with distinct names and verifies
        that all 3 rows appear in the table with correct cell text.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Prepare 3 distinct definitions ..
        definitions = []

        for index in range(3):
            name = _Test_Name_Prefix + f'multi-{index}'
            username = f'user.{name}'
            realm = f'realm.{name}'
            password = 'password.' + os.urandom(8).hex()
            definitions.append((name, username, realm, password))

        # Navigate to the basic auth page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create each definition ..
        for name, username, realm, password in definitions:

            # .. open the create dialog ..
            page.click('#markup .page_prompt a')
            page.wait_for_selector('#create-div', state='visible')

            # .. fill in the form fields ..
            page.fill('#id_name', name)
            page.fill('#id_username', username)
            page.fill('#id_realm', realm)
            page.fill('#id_password', password)

            # .. submit and wait for the dialog to close ..
            page.click('#create-div input[type="submit"]')
            page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. verify all 3 rows are present with correct values.
        for name, username, realm, _ in definitions:

            row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
            row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

            cells = row.query_selector_all('td')

            name_cell_text = cells[2].inner_text().strip()
            username_cell_text = cells[3].inner_text().strip()
            realm_cell_text = cells[4].inner_text().strip()

            assert name_cell_text == name, \
                f'Expected name "{name}", got: "{name_cell_text}"'

            assert username_cell_text == username, \
                f'Expected username "{username}", got: "{username_cell_text}"'

            assert realm_cell_text == realm, \
                f'Expected realm "{realm}", got: "{realm_cell_text}"'

# ################################################################################################################################

    def test_04_create_then_reopen_form_is_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ After a successful create, reopens the create dialog and verifies
        that all input fields are empty and no uniqueness indicator spans remain.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'reopen-empty'
        definition_password = 'password.' + os.urandom(8).hex()

        # Navigate to the basic auth page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a definition first ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', definition_name)
        page.fill('#id_username', 'user.' + definition_name)
        page.fill('#id_realm', 'realm.' + definition_name)
        page.fill('#id_password', definition_password)

        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. reopen the create dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. verify all fields are empty ..
        name_value = page.input_value('#id_name')
        username_value = page.input_value('#id_username')
        realm_value = page.input_value('#id_realm')
        password_value = page.input_value('#id_password')

        assert name_value == '', f'Expected empty name, got: "{name_value}"'
        assert username_value == '', f'Expected empty username, got: "{username_value}"'
        assert realm_value == 'API', f'Expected default realm "API", got: "{realm_value}"'
        assert password_value == '', f'Expected empty password, got: "{password_value}"'

        # .. verify no uniqueness indicators remain.
        indicators = page.query_selector_all('#create-form .zato-unique-indicator')
        indicator_count = len(indicators)
        assert indicator_count == 0, f'Expected 0 indicators, found: {indicator_count}'

# ################################################################################################################################

    def test_05_create_cancel_then_reopen_form_is_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens the create dialog, fills all fields, clicks Cancel,
        reopens the dialog and verifies that all fields have been reset to empty.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the basic auth page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog and fill fields ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', _Test_Name_Prefix + 'cancel-test')
        page.fill('#id_username', 'cancel-user')
        page.fill('#id_realm', 'cancel-realm')
        page.fill('#id_password', 'cancel-password')

        # .. close the dialog via jQuery UI ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        # .. reopen the dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. verify all fields are empty.
        name_value = page.input_value('#id_name')
        username_value = page.input_value('#id_username')
        realm_value = page.input_value('#id_realm')
        password_value = page.input_value('#id_password')

        assert name_value == '', f'Expected empty name, got: "{name_value}"'
        assert username_value == '', f'Expected empty username, got: "{username_value}"'
        assert realm_value == 'API', f'Expected default realm "API", got: "{realm_value}"'
        assert password_value == '', f'Expected empty password, got: "{password_value}"'

# ################################################################################################################################

    def test_06_create_cancel_no_row_added(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens the create dialog, fills all fields, clicks Cancel,
        and verifies that no new row was added to the table.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        cancelled_name = _Test_Name_Prefix + 'should-not-exist'

        # Navigate to the basic auth page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count rows before ..
        rows_before = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_before = len(rows_before)

        # .. open the create dialog and fill fields ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', cancelled_name)
        page.fill('#id_username', 'user.' + cancelled_name)
        page.fill('#id_realm', 'realm.' + cancelled_name)
        page.fill('#id_password', 'password.cancelled')

        # .. close the dialog via jQuery UI ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        # .. verify row count is unchanged ..
        rows_after = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_after = len(rows_after)

        assert count_after == count_before, \
            f'Expected {count_before} rows after cancel, got: {count_after}'

        # .. verify the cancelled name does not appear in the table.
        page_content = page.content()
        assert cancelled_name not in page_content, \
            f'Cancelled name "{cancelled_name}" should not be in the page'

# ################################################################################################################################

    def test_07_duplicate_name_shows_taken_indicator(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, reopens the create dialog, types the same name,
        and verifies that the 'Already taken' indicator appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        existing_name = _Test_Name_Prefix + 'duplicate-check'
        existing_password = 'password.' + os.urandom(8).hex()

        # Navigate and create a definition to have a known name ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        page.fill('#id_name', existing_name)
        page.fill('#id_username', 'user.' + existing_name)
        page.fill('#id_realm', 'realm.' + existing_name)
        page.fill('#id_password', existing_password)

        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. reload the page so the server's check_attr_exists picks up the new definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. reopen the create dialog and type the same name character by character
        # .. so that the input event handler triggers the uniqueness check ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        name_field = page.locator('#id_name')
        name_field.click()
        name_field.press_sequentially(existing_name, delay=10)

        # .. wait for the async uniqueness check (300ms timer + network) ..
        taken_indicator = page.wait_for_selector(
            '#create-form .zato-unique-taken', state='visible', timeout=10000)

        # .. verify the indicator text.
        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

# ################################################################################################################################

    def test_08_unique_name_shows_ok_indicator(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens the create dialog, types a name that does not exist,
        and verifies that the checkmark indicator appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        unique_name = _Test_Name_Prefix + 'unique-check-' + os.urandom(4).hex()

        # Navigate to the basic auth page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog and type a unique name character by character
        # .. so that the input event handler triggers the uniqueness check ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        name_field = page.locator('#id_name')
        name_field.click()
        name_field.press_sequentially(unique_name, delay=10)

        # .. wait for the async uniqueness check ..
        ok_indicator = page.wait_for_selector(
            '#create-form .zato-unique-ok', state='visible', timeout=10000)

        # .. verify the checkmark is present.
        ok_text = ok_indicator.inner_text()
        assert '\u2713' in ok_text, f'Expected checkmark in indicator, got: "{ok_text}"'

# ################################################################################################################################
# ################################################################################################################################
