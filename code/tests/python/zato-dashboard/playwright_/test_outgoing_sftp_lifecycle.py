# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import subprocess
import time

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.sftp_ import SFTPTestServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/outgoing/sftp/?cluster=1&type_=outconn-sftp'

_Test_Name_Prefix = 'test.sftp.' + CryptoManager.generate_hex_string(32) + '.'

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
    """ Opens the outgoing SFTP page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}{url_suffix}')
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_connection(
    page:'Page',
    name:'str',
    address:'str',
    username:'str',
    password:'str',
    private_key:'str'='',
    strict_host_key_checking:'bool'=True,
    ) -> 'None':
    """ Creates an outgoing SFTP connection via the UI.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_address', address)
    page.fill('#id_username', username)
    page.fill('#id_secret', password)
    page.fill('#id_private_key', private_key)

    # .. the slider is on by default, which means it only ever needs to be clicked to turn it off ..
    if not strict_host_key_checking:
        page.click('#id_strict_host_key_checking')

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
    page.evaluate(f'$.fn.zato.outgoing.sftp.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def _submit_edit_form(page:'Page') -> 'None':
    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
    time.sleep(0.3)

# ################################################################################################################################

def _forget_host_key(host:'str', port:'int') -> 'None':
    """ Removes the given host and port from the user's known_hosts file. The zato server pings
    the test SSH server through the real sftp binary, and because the test server's port may have
    been used by an earlier test run with a different key, any recorded entry must go away first.
    """
    _ = subprocess.run(['ssh-keygen', '-R', f'[{host}]:{port}'], capture_output=True)

# ################################################################################################################################

def _delete_connection(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.outgoing.sftp.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create, edit, edit again with an empty password, delete.
    """

    # Navigate ..
    _navigate(page, base_url)

    # .. create ..
    name = _Test_Name_Prefix + suffix
    _create_connection(page, name, 'sftp.example.com:22', 'sftp-user', 'sftp-password-' + CryptoManager.generate_hex_string())

    # .. edit everything except the password, flipping the host key checking slider too ..
    item_id = _get_item_id(page, name)
    _open_edit_dialog(page, item_id)

    edited_name = name + '-edited'
    page.fill('#id_edit-name', edited_name)
    page.fill('#id_edit-address', 'sftp.edited.example.com:22022')
    page.fill('#id_edit-username', 'sftp-user-edited')
    page.fill('#id_edit-private_key', 'My_Edited_SFTP_Key_File')
    page.click('#id_edit-strict_host_key_checking')

    _submit_edit_form(page)

    # .. edit again with the password field left empty ..
    _open_edit_dialog(page, item_id)
    page.fill('#id_edit-secret', '')
    _submit_edit_form(page)

    # .. delete.
    _delete_connection(page, item_id)

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingSFTPLifecycle:
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

        # .. create ..
        name = _Test_Name_Prefix + 'crud'
        _create_connection(page, name, 'sftp.example.com:22', 'sftp-user', 'sftp-password-' + CryptoManager.generate_hex_string())

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the name, address and username, flipping the host key checking slider too ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        edited_name = name + '-edited'
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-address', 'sftp.edited.example.com:22022')
        page.fill('#id_edit-username', 'sftp-user-edited')
        page.click('#id_edit-strict_host_key_checking')

        _submit_edit_form(page)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert old_row is None, f'Old name "{name}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. verify the edited address and username are shown in the row ..
        row_text = new_row.inner_text()
        assert 'sftp.edited.example.com:22022' in row_text, f'Expected edited address in row, got: "{row_text}"'
        assert 'sftp-user-edited' in row_text, f'Expected edited username in row, got: "{row_text}"'

        # .. the slider was flipped off during the edit, which the hidden cell must reflect -
        # .. note that text_content is needed here because the cell is not visible.
        row_hidden_text = new_row.text_content()
        assert row_hidden_text, 'Row text content should not be empty'
        assert 'False' in row_hidden_text, f'Expected strict host key checking to be off, got: "{row_hidden_text}"'

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
        _create_connection(page, name, 'sftp.example.com:22', 'sftp-user', 'sftp-password-' + CryptoManager.generate_hex_string())

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the address, keeping the Unicode name ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        page.fill('#id_edit-address', 'sftp.edited.example.com:22022')

        _submit_edit_form(page)

        # .. the Unicode name must still be there after the edit ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should still exist after edit'

        row_text = row.inner_text()
        assert 'sftp.edited.example.com:22022' in row_text, f'Expected edited address in row, got: "{row_text}"'

        # .. delete ..
        _delete_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row_after_delete is None, f'Row "{name}" should be gone after delete'

# ################################################################################################################################

    def test_ping(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection pointing at a live SSH server and clicks Ping, expecting success,
        also after an edit that leaves the password field empty, proving the password is preserved.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Start a live SSH server for the connection to ping
        sftp_server = SFTPTestServer()
        sftp_server.start()

        # An earlier run may have recorded a different key for this same host and port
        _forget_host_key(sftp_server.host, sftp_server.port)

        # The zato server was started with an environment variable pointing to this path -
        # the key itself is copied there only now, with the permissions that ssh requires.
        sftp_key_env_name = zato_dashboard['sftp_key_env_name']
        sftp_key_path = zato_dashboard['sftp_key_path']

        shutil.copyfile(sftp_server.client_key_encrypted_path, sftp_key_path)
        os.chmod(sftp_key_path, 0o600)

        try:

            # Navigate ..
            _navigate(page, base_url)

            # .. create a connection pointing at the live server - it authenticates with an encrypted key
            # .. whose passphrase is the connection's password, referred to through the environment
            # .. variable, and host key checking must be off because the server's host key
            # .. was generated a moment ago ..
            name = _Test_Name_Prefix + 'ping'
            address = f'{sftp_server.host}:{sftp_server.port}'

            _create_connection(
                page,
                name,
                address,
                sftp_server.username,
                sftp_server.password,
                private_key=sftp_key_env_name,
                strict_host_key_checking=False,
            )

            item_id = _get_item_id(page, name)

            # .. click Ping and wait for the response ..
            row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

            with page.expect_response(lambda response: '/zato/outgoing/sftp/ping/' in response.url, timeout=30000) as response_info:
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
            with page.expect_response(lambda response: '/zato/outgoing/sftp/ping/' in response.url, timeout=30000) as response_info:
                page.click(f'{row_selector} a:has-text("Ping")')

            response = response_info.value
            body = response.text()
            assert response.status == 200, f'Ping after edit should return 200, got {response.status} with body: "{body}"'

            # .. delete the connection before the server goes away.
            _delete_connection(page, item_id)

        finally:
            sftp_server.stop()

# ################################################################################################################################
# ################################################################################################################################
