# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/spnego/?cluster=1'

_Test_Name_Prefix = 'test.spnego.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

def _fill_definition_fields(page:'Page', name:'str') -> 'dict':
    """ Fills in the create dialog fields for a definition of the given name and returns the values used.
    """

    principal = f'{name}@EXAMPLE.COM'
    keytab_path = f'/opt/hot-deploy/krb5/{name}.keytab'
    target_spn = f'HTTP@{name}.example.com'

    page.fill('#id_name', name)
    page.fill('#id_principal', principal)
    page.fill('#id_keytab_path', keytab_path)
    page.fill('#id_target_spn', target_spn)

    out = {
        'name': name,
        'principal': principal,
        'keytab_path': keytab_path,
        'target_spn': target_spn,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSPNEGOCreate:
    """ Tests for the Kerberos (SPNEGO) create flow.
    """

    def test_01_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the Kerberos page and verifies its structure:
        - h2 heading contains "Kerberos"
        - data table is visible
        - "Create a Kerberos definition" link is present
        - table headers include Name, Principal, Keytab path
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the Kerberos page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the page heading ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'Kerberos' in heading_text, f'Expected "Kerberos" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = page.query_selector('#markup .page_prompt a')
        create_link_text = create_link.inner_text()
        assert 'Create a Kerberos definition' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. verify table headers (CSS text-transform may uppercase them).
        headers = page.query_selector_all('#data-table thead th a')

        header_texts = [] # type: list

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        assert 'name' in header_texts, f'Expected "name" in headers, got: {header_texts}'
        assert 'principal' in header_texts, f'Expected "principal" in headers, got: {header_texts}'
        assert 'keytab path' in header_texts, f'Expected "keytab path" in headers, got: {header_texts}'

# ################################################################################################################################

    def test_02_create_one(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a single Kerberos definition via the UI dialog and verifies
        that the new row appears in the table with correct cell text for name, principal
        and keytab path.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'create-one'

        # Navigate to the Kerberos page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. click the create link to open the dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. fill in the form fields ..
        defn = _fill_definition_fields(page, definition_name)

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
        principal_cell_text = cells[3].inner_text().strip()
        keytab_path_cell_text = cells[4].inner_text().strip()

        # .. verify each cell has the correct value.
        assert name_cell_text == defn['name'], \
            f'Expected name "{defn["name"]}", got: "{name_cell_text}"'

        assert principal_cell_text == defn['principal'], \
            f'Expected principal "{defn["principal"]}", got: "{principal_cell_text}"'

        assert keytab_path_cell_text == defn['keytab_path'], \
            f'Expected keytab path "{defn["keytab_path"]}", got: "{keytab_path_cell_text}"'

# ################################################################################################################################

    def test_03_create_multiple(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates 3 Kerberos definitions with distinct names and verifies
        that all 3 rows appear in the table with correct cell text.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the Kerberos page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create each definition ..
        definitions = [] # type: list

        for index in range(3):
            name = _Test_Name_Prefix + f'multi-{index}'

            # .. open the create dialog ..
            page.click('#markup .page_prompt a')
            page.wait_for_selector('#create-div', state='visible')

            # .. fill in the form fields ..
            defn = _fill_definition_fields(page, name)
            definitions.append(defn)

            # .. submit and wait for the dialog to close ..
            page.click('#create-div input[type="submit"]')
            page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. verify all 3 rows are present with correct values.
        for defn in definitions:

            row_selector = f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))'
            row = page.wait_for_selector(row_selector, state='visible', timeout=5000)

            cells = row.query_selector_all('td')

            name_cell_text = cells[2].inner_text().strip()
            principal_cell_text = cells[3].inner_text().strip()

            assert name_cell_text == defn['name'], \
                f'Expected name "{defn["name"]}", got: "{name_cell_text}"'

            assert principal_cell_text == defn['principal'], \
                f'Expected principal "{defn["principal"]}", got: "{principal_cell_text}"'

# ################################################################################################################################

    def test_04_create_then_reopen_form_is_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ After a successful create, reopens the create dialog and verifies
        that all input fields are empty and no uniqueness indicator spans remain.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'reopen-empty'

        # Navigate to the Kerberos page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a definition first ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        _ = _fill_definition_fields(page, definition_name)

        page.click('#create-div input[type="submit"]')
        page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. reopen the create dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. verify all fields are empty ..
        for field_id in ('#id_name', '#id_principal', '#id_keytab_path', '#id_target_spn'):
            field_value = page.input_value(field_id)
            assert field_value == '', f'Expected empty {field_id}, got: "{field_value}"'

        # .. verify no uniqueness indicators remain.
        indicators = page.query_selector_all('#create-form .zato-unique-indicator')
        indicator_count = len(indicators)
        assert indicator_count == 0, f'Expected 0 indicators, found: {indicator_count}'

# ################################################################################################################################

    def test_05_duplicate_name_shows_taken_indicator(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, reopens the create dialog, types the same name,
        and verifies that the 'Already taken' indicator appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        existing_name = _Test_Name_Prefix + 'duplicate-check'

        # Navigate and create a definition to have a known name ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        _ = _fill_definition_fields(page, existing_name)

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
# ################################################################################################################################
