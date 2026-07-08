# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.api import API_Key
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/apikey/?cluster=1'

_Test_Name_Prefix = 'test.apikey.life.' + CryptoManager.generate_hex_string(32) + '.'

_Custom_Header = 'X-Custom-Token'

_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

# ################################################################################################################################
# ################################################################################################################################

def _create_definition(page:'Page', suffix:'str', header:'str'=API_Key.Default_Header) -> 'dict':
    """ Creates an API key definition via the UI and returns its details.
    """

    name = _Test_Name_Prefix + suffix
    key = 'key.' + CryptoManager.generate_hex_string()

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_header', header)
    page.fill('#id_password', key)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    out = {
        'name': name,
        'header': header,
        'key': key,
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

def _get_header_cell_text(page:'Page', item_id:'str') -> 'str':
    """ Returns the text of the header column cell for a row of the given ID.
    """

    cell = page.query_selector(f'#item_header_{item_id}')
    out = cell.inner_text().strip()

    return out

# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create with a custom header, edit the header, change the key, delete.
    """

    # Navigate ..
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

    # .. create with a custom header ..
    definition = _create_definition(page, suffix, _Custom_Header)
    name = definition['name']

    # .. edit the header ..
    item_id = _get_item_id(page, name)
    page.evaluate(f'$.fn.zato.security.apikey.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

    page.fill('#id_edit-header', '')
    page.fill('#id_edit-header', API_Key.Default_Header)

    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
    time.sleep(0.3)

    # .. change the key ..
    page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}")')
    page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

    page.fill('#change_password-div #id_password', 'new-crud-key')
    page.click('#change_password-div input[type="submit"]')
    page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

    # .. delete.
    page.evaluate(f'$.fn.zato.security.apikey.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################
# ################################################################################################################################

class TestAPIKeyLifecycle:
    """ Tests for console errors, HTTP 500s and full CRUD of API key definitions with the editable header field.
    """

    def test_01_no_console_errors_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Performs a full CRUD session and asserts no console.error messages appear.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect console errors ..
        console_errors = [] # type: list

        def _on_console(msg:'object') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        page.on('console', _on_console)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'console-check')

        # .. filter known noise ..
        real_errors = [] # type: list

        for error_text in console_errors:
            is_noise = False
            for noise_pattern in _Console_Noise_Patterns:
                if noise_pattern in error_text:
                    is_noise = True
                    break

            if not is_noise:
                real_errors.append(error_text)

        # .. assert no real errors.
        assert not real_errors, f'Console errors during CRUD:\n' + '\n'.join(real_errors)

# ################################################################################################################################

    def test_02_no_http_500_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Performs a full CRUD session and asserts no HTTP 500+ responses.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect server errors ..
        server_errors = [] # type: list

        def _on_response(response:'object') -> 'None':
            if response.status >= 500:
                server_errors.append(f'{response.status} {response.url}')

        page.on('response', _on_response)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'http500-check')

        # .. assert no 500s.
        assert not server_errors, f'HTTP 500+ responses during CRUD:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def test_03_full_crud_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Create with the default header, create with a custom header, verify the header column,
        edit the header, change the key, delete, verify gone.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create with the default header ..
        default_defn = _create_definition(page, 'crud-default')

        # .. the header column shows the default header ..
        default_id = _get_item_id(page, default_defn['name'])
        header_text = _get_header_cell_text(page, default_id)
        assert header_text == API_Key.Default_Header, \
            f'Expected "{API_Key.Default_Header}" in the header column, got: "{header_text}"'

        # .. create with a custom header ..
        custom_defn = _create_definition(page, 'crud-custom', _Custom_Header)

        # .. the header column shows the custom header ..
        custom_id = _get_item_id(page, custom_defn['name'])
        header_text = _get_header_cell_text(page, custom_id)
        assert header_text == _Custom_Header, f'Expected "{_Custom_Header}" in the header column, got: "{header_text}"'

        # .. reload the page and confirm the server-rendered rows show the same headers ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={_Test_Name_Prefix}crud')
        page.wait_for_selector('#data-table', state='visible')

        header_text = _get_header_cell_text(page, default_id)
        assert header_text == API_Key.Default_Header, \
            f'Expected "{API_Key.Default_Header}" after a reload, got: "{header_text}"'

        header_text = _get_header_cell_text(page, custom_id)
        assert header_text == _Custom_Header, f'Expected "{_Custom_Header}" after a reload, got: "{header_text}"'

        # .. the edit dialog shows the stored header ..
        page.evaluate(f'$.fn.zato.security.apikey.edit("{custom_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        edit_header_value = page.input_value('#id_edit-header')
        assert edit_header_value == _Custom_Header, \
            f'Expected "{_Custom_Header}" in the edit dialog, got: "{edit_header_value}"'

        # .. edit both the name and the header ..
        edited_name = custom_defn['name'] + '-edited'
        page.fill('#id_edit-name', '')
        page.fill('#id_edit-name', edited_name)

        page.fill('#id_edit-header', '')
        page.fill('#id_edit-header', 'X-Another-Token')

        page.click('#edit-div input[type="submit"]')
        page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.3)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{custom_defn["name"]}"))')
        assert old_row is None, f'Old name "{custom_defn["name"]}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. the header column reflects the edit ..
        header_text = _get_header_cell_text(page, custom_id)
        assert header_text == 'X-Another-Token', f'Expected "X-Another-Token" after edit, got: "{header_text}"'

        # .. change the key ..
        page.evaluate(f'$.fn.zato.data_table.change_password("{custom_id}")')
        page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

        page.fill('#change_password-div #id_password', 'new-crud-key')
        page.click('#change_password-div input[type="submit"]')
        page.wait_for_function('!document.querySelector("#change_password-div").offsetParent')

        # .. verify the row still present after the key change ..
        row_after_pwd = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert row_after_pwd is not None, f'Row should remain after the key change'

        # .. delete both definitions ..
        for item_id, name in ((custom_id, edited_name), (default_id, default_defn['name'])):
            page.evaluate(f'$.fn.zato.security.apikey.delete_("{item_id}")')
            page.wait_for_selector('#popup_container', state='visible', timeout=5000)
            page.click('#popup_ok')
            time.sleep(0.5)

            # .. and verify each is gone.
            row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
            assert row_after_delete is None, f'Row "{name}" should be gone after delete'

# ################################################################################################################################
# ################################################################################################################################
