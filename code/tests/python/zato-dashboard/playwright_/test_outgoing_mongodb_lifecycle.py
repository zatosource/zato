# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import time

# The directory with the shared MongoDB container helpers used by the live server tests
_mongodb_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-server', 'mongodb'))
sys.path.insert(0, _mongodb_tests_dir)

# Zato
from containers import start_mongodb, stop_container
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/outgoing/mongodb/?cluster=1&type_=outconn-mongodb'

_Test_Name_Prefix = 'test.mongodb.' + CryptoManager.generate_hex_string(32) + '.'

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

# Details of the container the ping test starts
_Container_Name = 'zato-playwright-test-mongodb'
_Container_Port = 27121
_Container_Username = 'zato_playwright_mongodb'
_Container_Password = 'test-playwright-mongodb-password'

# ################################################################################################################################
# ################################################################################################################################

def _navigate(page:'Page', base_url:'str', url_suffix:'str'='') -> 'None':
    """ Opens the outgoing MongoDB page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}{url_suffix}')
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_connection(page:'Page', name:'str', server_list:'str', username:'str', password:'str') -> 'None':
    """ Creates an outgoing MongoDB connection via the UI.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_server_list', server_list)
    page.fill('#id_username', username)
    page.fill('#id_secret', password)

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
    page.evaluate(f'$.fn.zato.outgoing.mongodb.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def _submit_edit_form(page:'Page') -> 'None':
    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
    time.sleep(0.3)

# ################################################################################################################################

def _delete_connection(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.outgoing.mongodb.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create, edit, edit again with an empty password, delete.
    """

    # Navigate ..
    _navigate(page, base_url)

    # .. create, with a multi-line server list ..
    name = _Test_Name_Prefix + suffix
    server_list = 'mongodb1.example.com:27017\nmongodb2.example.com:27017'
    _create_connection(page, name, server_list, 'mongodb-user', 'mongodb-password-' + CryptoManager.generate_hex_string())

    # .. edit everything except the password ..
    item_id = _get_item_id(page, name)
    _open_edit_dialog(page, item_id)

    edited_name = name + '-edited'
    page.fill('#id_edit-name', edited_name)
    page.fill('#id_edit-server_list', 'mongodb.edited.example.com:27017')
    page.fill('#id_edit-username', 'mongodb-user-edited')

    _submit_edit_form(page)

    # .. edit again with the password field left empty ..
    _open_edit_dialog(page, item_id)
    page.fill('#id_edit-secret', '')
    _submit_edit_form(page)

    # .. delete.
    _delete_connection(page, item_id)

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingMongoDBLifecycle:
    """ Tests for console errors, HTTP 500s, full CRUD, Unicode names, and live pings.
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
        """ Create, verify, edit, verify, edit with an empty password, verify, delete, verify gone.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _navigate(page, base_url)

        # .. create, with a multi-line server list ..
        name = _Test_Name_Prefix + 'crud'
        server_list = 'mongodb1.example.com:27017\nmongodb2.example.com:27017'
        _create_connection(page, name, server_list, 'mongodb-user', 'mongodb-password-' + CryptoManager.generate_hex_string())

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. verify both lines of the server list are shown in the row ..
        row_text = row.inner_text()
        assert 'mongodb1.example.com:27017' in row_text, f'Expected the first server in row, got: "{row_text}"'
        assert 'mongodb2.example.com:27017' in row_text, f'Expected the second server in row, got: "{row_text}"'

        # .. edit the name, server list and username ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        edited_name = name + '-edited'
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-server_list', 'mongodb.edited.example.com:27017')
        page.fill('#id_edit-username', 'mongodb-user-edited')

        _submit_edit_form(page)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert old_row is None, f'Old name "{name}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. verify the edited server list is shown in the row ..
        row_text = new_row.inner_text()
        assert 'mongodb.edited.example.com:27017' in row_text, f'Expected edited server list in row, got: "{row_text}"'

        # .. edit again with the password field left empty and make sure nothing breaks ..
        _open_edit_dialog(page, item_id)
        page.fill('#id_edit-secret', '')
        _submit_edit_form(page)

        row_after_empty_password = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert row_after_empty_password is not None, 'Row should remain after an edit with an empty password'

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
        _create_connection(
            page, name, 'mongodb.example.com:27017', 'mongodb-user',
            'mongodb-password-' + CryptoManager.generate_hex_string())

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the server list, keeping the Unicode name ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        page.fill('#id_edit-server_list', 'mongodb.edited.example.com:27017')

        _submit_edit_form(page)

        # .. the Unicode name must still be there after the edit ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should still exist after edit'

        row_text = row.inner_text()
        assert 'mongodb.edited.example.com:27017' in row_text, f'Expected edited server list in row, got: "{row_text}"'

        # .. delete ..
        _delete_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row_after_delete is None, f'Row "{name}" should be gone after delete'

# ################################################################################################################################

    def test_ping(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection pointing at a live MongoDB server and clicks Ping, expecting success,
        also after an edit that leaves the password field empty, proving the password is preserved.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Start a live MongoDB server for the connection to ping
        mongodb_server = start_mongodb(
            container_name=_Container_Name,
            port=_Container_Port,
            username=_Container_Username,
            password=_Container_Password,
            needs_tls=False,
        )

        try:

            # Navigate ..
            _navigate(page, base_url)

            # .. create a connection pointing at the live server ..
            name = _Test_Name_Prefix + 'ping'
            server_list = f'{mongodb_server.host}:{mongodb_server.port}'
            _create_connection(page, name, server_list, mongodb_server.username, mongodb_server.password)

            item_id = _get_item_id(page, name)

            # .. click Ping and wait for the response ..
            row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

            with page.expect_response(
                lambda response: '/zato/outgoing/mongodb/ping/' in response.url, timeout=30000) as response_info:
                page.click(f'{row_selector} a:has-text("Ping")')

            response = response_info.value
            body = response.text()
            assert response.status == 200, f'Ping should return 200, got {response.status} with body: "{body}"'

            # .. edit the connection, leaving the password field empty ..
            _open_edit_dialog(page, item_id)
            page.fill('#id_edit-secret', '')
            _submit_edit_form(page)

            # .. and ping again - the connection must still authenticate,
            # .. proving the empty field did not overwrite the stored password ..
            with page.expect_response(
                lambda response: '/zato/outgoing/mongodb/ping/' in response.url, timeout=30000) as response_info:
                page.click(f'{row_selector} a:has-text("Ping")')

            response = response_info.value
            body = response.text()
            assert response.status == 200, f'Ping after edit should return 200, got {response.status} with body: "{body}"'

            # .. delete the connection before the server goes away.
            _delete_connection(page, item_id)

        finally:
            stop_container(_Container_Name)

# ################################################################################################################################
# ################################################################################################################################
