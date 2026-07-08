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

_Page_Url_Pattern = '/zato/security/basic-auth/?cluster=1'

_Test_Name_Prefix = 'test.pwd.del.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_definition(page:'Page', suffix:'str') -> 'dict':
    """ Creates a basic auth definition via the UI and returns its details.
    """

    name = _Test_Name_Prefix + suffix
    username = 'user.' + name
    realm = 'realm.' + name
    password = 'password.' + CryptoManager.generate_hex_string()

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_username', username)
    page.fill('#id_realm', realm)
    page.fill('#id_password', password)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    out = {
        'name': name,
        'username': username,
        'realm': realm,
        'password': password,
    }

    return out

# ################################################################################################################################

def _get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')
    out = id_cell.inner_text().strip()

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthPasswordDelete:
    """ Tests for the change password and delete flows.
    """

    def test_19_change_password_dialog(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens the change password dialog and verifies its contents:
        the name label shows the correct name and the password field is empty.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'pwd-dialog')

        # .. open the change password dialog ..
        item_id = _get_item_id(page, defn['name'])
        page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        # .. verify the name label ..
        name_label = page.query_selector('#change-password-name')
        name_text = name_label.inner_text().strip()
        assert name_text == defn['name'], f'Expected name "{defn["name"]}", got: "{name_text}"'

        # .. verify the password field is empty.
        password_value = page.input_value('#change_password-div #id_password')
        assert password_value == '', f'Expected empty password, got: "{password_value}"'

# ################################################################################################################################

    def test_20_change_password_submit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Fills in a new password and submits. Verifies the dialog closes
        and the row is still present in the table.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'pwd-submit')

        # .. open the change password dialog ..
        item_id = _get_item_id(page, defn['name'])
        page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        # .. fill in the password and submit ..
        page.fill('#change_password-div #id_password', 'new-password-123')
        page.click('#change_password-div input[type="submit"]')

        # .. wait for the dialog to close ..
        page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

        # .. verify the row is still present.
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is not None, f'Row "{defn["name"]}" should still be in the table'

# ################################################################################################################################

    def test_21_change_password_cancel_then_reopen(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens change password, types a value, cancels, reopens.
        Verifies the password field is empty after cancel.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'pwd-cancel')
        item_id = _get_item_id(page, defn['name'])

        # .. open the dialog and type a password ..
        page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        page.fill('#change_password-div #id_password', 'typed-then-cancelled')

        # .. close the dialog ..
        page.evaluate('$("#change_password-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

        # .. reopen for the same row ..
        page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        # .. verify the password field is empty.
        password_value = page.input_value('#change_password-div #id_password')
        assert password_value == '', f'Expected empty password after cancel, got: "{password_value}"'

# ################################################################################################################################

    def test_22_change_password_for_different_rows(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens change password for A, closes, then opens for B.
        Verifies the name label shows B's name.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create two definitions ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn_a = _create_definition(page, 'pwd-row-a')
        defn_b = _create_definition(page, 'pwd-row-b')

        id_a = _get_item_id(page, defn_a['name'])
        id_b = _get_item_id(page, defn_b['name'])

        # .. open for A and verify ..
        page.evaluate(f'$.fn.zato.data_table.change_password("{id_a}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        name_text_a = page.query_selector('#change-password-name').inner_text().strip()
        assert name_text_a == defn_a['name'], f'Expected A name, got: "{name_text_a}"'

        # .. close A ..
        page.evaluate('$("#change_password-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

        # .. open for B and verify.
        page.evaluate(f'$.fn.zato.data_table.change_password("{id_b}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        name_text_b = page.query_selector('#change-password-name').inner_text().strip()
        assert name_text_b == defn_b['name'], f'Expected B name "{defn_b["name"]}", got: "{name_text_b}"'

# ################################################################################################################################

    def test_23_change_password_for_a_does_not_affect_b(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates two definitions A and B, changes A's password,
        then verifies B's row still has its original name, username, and realm.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create two definitions ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn_a = _create_definition(page, 'pwd-iso-a')
        defn_b = _create_definition(page, 'pwd-iso-b')

        # .. change A's password ..
        id_a = _get_item_id(page, defn_a['name'])
        page.evaluate(f'$.fn.zato.data_table.change_password("{id_a}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        page.fill('#change_password-div #id_password', 'changed-password-for-a')
        page.click('#change_password-div input[type="submit"]')
        page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

        # .. verify B's row is still present with original values ..
        row_b = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn_b["name"]}"))')
        assert row_b is not None, f'Row B "{defn_b["name"]}" should still be present'

        cells = row_b.query_selector_all('td')
        cell_texts = [cell.inner_text().strip() for cell in cells]

        # .. verify B's name, username, and realm are unchanged.
        assert defn_b['name'] in cell_texts, f'Expected B name in cells, got: {cell_texts}'
        assert defn_b['username'] in cell_texts, f'Expected B username in cells, got: {cell_texts}'
        assert defn_b['realm'] in cell_texts, f'Expected B realm in cells, got: {cell_texts}'

# ################################################################################################################################

    def test_24_delete_confirm(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Deletes a definition via jConfirm OK and verifies the row is removed.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'delete-confirm')

        # .. count rows before ..
        rows_before = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_before = len(rows_before)

        # .. trigger delete ..
        item_id = _get_item_id(page, defn['name'])
        page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id}")')

        # .. wait for the jConfirm popup ..
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)

        # .. verify the popup message contains the definition name ..
        popup_text = page.query_selector('#popup_message').inner_text()
        assert defn['name'] in popup_text, f'Expected name in popup, got: "{popup_text}"'

        # .. click OK ..
        page.click('#popup_ok')

        # .. wait for the row to be removed (200ms fade animation) ..
        time.sleep(0.5)

        # .. verify the row is gone ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is None, f'Row "{defn["name"]}" should be removed after delete'

        # .. verify count decreased.
        rows_after = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_after = len(rows_after)
        assert count_after == count_before - 1, \
            f'Expected {count_before - 1} rows, got: {count_after}'

# ################################################################################################################################

    def test_25_delete_cancel(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Triggers delete but clicks Cancel in jConfirm.
        Verifies the row is still present.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'delete-cancel')

        # .. trigger delete ..
        item_id = _get_item_id(page, defn['name'])
        page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id}")')

        # .. wait for the jConfirm popup ..
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)

        # .. click Cancel ..
        page.click('#popup_cancel')

        # .. wait for the popup to be removed ..
        page.wait_for_function('!document.querySelector("#popup_container")', timeout=3000)

        # .. verify the row is still present.
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is not None, f'Row "{defn["name"]}" should still be present after cancel'

# ################################################################################################################################

    def test_26_delete_down_to_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, deletes it, and verifies the row count decreases.
        If the table becomes empty, asserts the 'No results' placeholder appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to a fresh page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a definition ..
        defn = _create_definition(page, 'delete-empty')

        # .. count rows before ..
        rows_before = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        count_before = len(rows_before)

        # .. delete it ..
        item_id = _get_item_id(page, defn['name'])
        page.evaluate(f'$.fn.zato.security.basic_auth.delete_("{item_id}")')
        page.wait_for_selector('#popup_container', state='visible', timeout=5000)
        page.click('#popup_ok')
        time.sleep(0.5)

        # .. verify the row is gone ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is None, f'Row "{defn["name"]}" should be removed after delete'

        # .. if the table had only our row, verify "No results" appears.
        if count_before == 1:
            no_results_cell = page.query_selector('#data-table tbody td')
            cell_text = no_results_cell.inner_text().strip()
            assert cell_text == 'No results', f'Expected "No results", got: "{cell_text}"'

# ################################################################################################################################
# ################################################################################################################################
