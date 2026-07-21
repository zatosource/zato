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

_Page_Url_Pattern = '/zato/cloud/microsoft-fabric/?cluster=1&type_=cloud-microsoft-fabric'

_Test_Name_Prefix = 'test.microsoft.fabric.' + CryptoManager.generate_hex_string(32) + '.'

# Letters from three alphabets - one of the tests below runs a whole create-edit-delete
# cycle with a connection whose name contains them all.
_Dutch_Letters = 'ÁÉÍÓÚË'
_Greek_Letters = 'ΑΒΓΔΕΖ'
_Korean_Letters = 'ㄱㄴㄷㄹㅁㅂ'

_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

# ################################################################################################################################
# ################################################################################################################################

def _navigate(page:'Page', base_url:'str', url_suffix:'str'='') -> 'None':
    """ Opens the Microsoft Fabric connections page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}{url_suffix}')
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_connection(page:'Page', name:'str', tenant_id:'str', client_id:'str', client_secret:'str') -> 'None':
    """ Creates a Microsoft Fabric connection via the UI.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields, keeping the prefilled default address ..
    page.fill('#id_name', name)
    page.fill('#id_tenant_id', tenant_id)
    page.fill('#id_client_id', client_id)
    page.fill('#id_client_secret', client_secret)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. and wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

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

def _open_edit_dialog(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.cloud.microsoft_fabric.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def _submit_edit_form(page:'Page') -> 'None':
    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
    time.sleep(0.3)

# ################################################################################################################################

def _change_secret(page:'Page', item_id:'str', client_secret:'str') -> 'None':
    """ Sets the client secret of a connection via the change-secret dialog.
    """

    # Open the dialog ..
    page.evaluate(f'$.fn.zato.data_table.change_password("{item_id}", "Change secret")')
    _ = page.wait_for_selector('#change_password-div', state='visible', timeout=5000)

    # .. fill in the new secret ..
    page.fill('#change_password-div #id_password', client_secret)

    # .. and submit, waiting for the dialog to close.
    page.click('#change_password-div input[type="submit"]')
    _ = page.wait_for_selector('#change_password-div', state='hidden', timeout=10000)

# ################################################################################################################################

def _delete_connection(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.cloud.microsoft_fabric.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')

    # The server-side delete waits for the connection queue builder to stop,
    # which takes over a second, so wait until the row is actually removed
    # instead of sleeping for a fixed period.
    page.wait_for_selector(f'#tr_{item_id}', state='detached', timeout=10000)

# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create, edit, delete.
    """

    # Navigate ..
    _navigate(page, base_url)

    # .. create ..
    name = _Test_Name_Prefix + suffix
    client_secret = 'fabric-secret-' + CryptoManager.generate_hex_string()
    _create_connection(page, name, 'tenant-id-initial', 'client-id-initial', client_secret)

    # .. edit everything except the secret ..
    item_id = _get_item_id(page, name)
    _open_edit_dialog(page, item_id)

    edited_name = name + '-edited'
    page.fill('#id_edit-name', edited_name)
    page.fill('#id_edit-tenant_id', 'tenant-id-edited')
    page.fill('#id_edit-client_id', 'client-id-edited')

    _submit_edit_form(page)

    # .. change the secret through its own dialog ..
    _change_secret(page, item_id, client_secret + '-changed')

    # .. delete.
    _delete_connection(page, item_id)

# ################################################################################################################################
# ################################################################################################################################

class TestCloudMicrosoftFabricLifecycle:
    """ Tests for console errors, HTTP 500s, full CRUD and Unicode names.
    """

    def test_no_console_errors_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
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
        assert not real_errors, 'Console errors during CRUD:\n' + '\n'.join(real_errors)

# ################################################################################################################################

    def test_no_http_500_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
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
        assert not server_errors, 'HTTP 500+ responses during CRUD:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def test_full_crud_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Create, verify, edit, verify, delete, verify gone.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _navigate(page, base_url)

        # .. create ..
        name = _Test_Name_Prefix + 'crud'
        client_secret = 'fabric-secret-' + CryptoManager.generate_hex_string()
        _create_connection(page, name, 'tenant-id-initial', 'client-id-initial', client_secret)

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. verify the tenant and client IDs are shown in the row ..
        row_text = row.inner_text()
        assert 'tenant-id-initial' in row_text, f'Expected the tenant ID in row, got: "{row_text}"'
        assert 'client-id-initial' in row_text, f'Expected the client ID in row, got: "{row_text}"'

        # .. edit the name, tenant ID and client ID ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        edited_name = name + '-edited'
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-tenant_id', 'tenant-id-edited')
        page.fill('#id_edit-client_id', 'client-id-edited')

        _submit_edit_form(page)

        # .. change the secret through its own dialog ..
        _change_secret(page, item_id, client_secret + '-changed')

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert old_row is None, f'Old name "{name}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. verify the edited tenant and client IDs are shown in the row ..
        row_text = new_row.inner_text()
        assert 'tenant-id-edited' in row_text, f'Expected edited tenant ID in row, got: "{row_text}"'
        assert 'client-id-edited' in row_text, f'Expected edited client ID in row, got: "{row_text}"'

        # .. delete ..
        _delete_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert row_after_delete is None, f'Row "{edited_name}" should be gone after delete'

# ################################################################################################################################

    def test_unicode_name_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Runs the whole create-edit-delete cycle with a name containing Dutch, Greek and Korean letters.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _navigate(page, base_url)

        # .. create a connection with a Unicode name ..
        name = _Test_Name_Prefix + _Dutch_Letters + '.' + _Greek_Letters + '.' + _Korean_Letters
        client_secret = 'fabric-secret-' + CryptoManager.generate_hex_string()
        _create_connection(page, name, 'tenant-id-unicode', 'client-id-unicode', client_secret)

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the tenant ID, keeping the Unicode name ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        page.fill('#id_edit-tenant_id', 'tenant-id-unicode-edited')

        _submit_edit_form(page)

        # .. the Unicode name must still be there after the edit ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should still exist after edit'

        row_text = row.inner_text()
        assert 'tenant-id-unicode-edited' in row_text, f'Expected edited tenant ID in row, got: "{row_text}"'

        # .. delete ..
        _delete_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row_after_delete is None, f'Row "{name}" should be gone after delete'

# ################################################################################################################################
# ################################################################################################################################
