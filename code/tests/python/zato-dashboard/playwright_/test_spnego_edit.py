# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

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

_Test_Name_Prefix = 'test.spnego.edit.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_definition(page:'Page', suffix:'str') -> 'dict':
    """ Creates a Kerberos (SPNEGO) definition via the UI and returns its details.
    """

    name = _Test_Name_Prefix + suffix
    principal = f'{name}@EXAMPLE.COM'
    keytab_path = f'/opt/hot-deploy/krb5/{name}.keytab'
    target_spn = f'HTTP@{name}.example.com'

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_principal', principal)
    page.fill('#id_keytab_path', keytab_path)
    page.fill('#id_target_spn', target_spn)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    out = {
        'name': name,
        'principal': principal,
        'keytab_path': keytab_path,
        'target_spn': target_spn,
    }

    return out

# ################################################################################################################################

def _click_edit_for_row(page:'Page', name:'str') -> 'None':
    """ Finds the row with the given name and opens its edit dialog.
    """

    # Extract the row's item ID from the hidden td ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')
    item_id = id_cell.inner_text().strip()

    # .. call the edit function directly via JS ..
    page.evaluate(f'$.fn.zato.security.spnego.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################

class TestSPNEGOEdit:
    """ Tests for the Kerberos (SPNEGO) edit flow.
    """

    def test_06_edit_form_is_prepopulated(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, opens its edit dialog and verifies
        that all form fields hold the values the definition was created with.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'prepopulated')

        # .. open the edit dialog ..
        _click_edit_for_row(page, defn['name'])

        # .. verify each field holds the created value.
        field_map = {
            '#id_edit-name': defn['name'],
            '#id_edit-principal': defn['principal'],
            '#id_edit-keytab_path': defn['keytab_path'],
            '#id_edit-target_spn': defn['target_spn'],
        }

        for field_id, expected in field_map.items():
            field_value = page.input_value(field_id)
            assert field_value == expected, f'Expected "{expected}" in {field_id}, got: "{field_value}"'

# ################################################################################################################################

    def test_07_edit_changes_are_saved(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, edits its name and principal,
        and verifies the row reflects the new values.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'save-changes')

        # .. open the edit dialog ..
        _click_edit_for_row(page, defn['name'])

        # .. change the name and the principal ..
        edited_name = defn['name'] + '-edited'
        edited_principal = 'edited.' + defn['principal']

        page.fill('#id_edit-name', '')
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-principal', '')
        page.fill('#id_edit-principal', edited_principal)

        # .. submit and wait for the dialog to close ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.3)

        # .. the old name is gone ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert old_row is None, f'Old name "{defn["name"]}" should be gone after edit'

        # .. and the new row holds the new values.
        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        cells = new_row.query_selector_all('td')
        principal_cell_text = cells[3].inner_text().strip()

        assert principal_cell_text == edited_principal, \
            f'Expected principal "{edited_principal}", got: "{principal_cell_text}"'

# ################################################################################################################################

    def test_08_duplicate_name_in_edit_shows_taken(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates two definitions A and B. Opens edit for A and types B's name.
        Asserts the 'Already taken' indicator appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create two definitions ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn_a = _create_definition(page, 'dup-edit-a')
        defn_b = _create_definition(page, 'dup-edit-b')

        # .. reload so the server knows about both for the uniqueness check ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open edit for A ..
        _click_edit_for_row(page, defn_a['name'])

        # .. clear the name field and type B's name ..
        name_field = page.locator('#id_edit-name')
        name_field.fill('')
        name_field.click()
        name_field.press_sequentially(defn_b['name'], delay=10)

        # .. wait for the uniqueness indicator ..
        taken_indicator = page.wait_for_selector(
            '#edit-form .zato-unique-taken', state='visible', timeout=10000)

        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

# ################################################################################################################################
# ################################################################################################################################
