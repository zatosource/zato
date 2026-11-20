# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.smb_ import SMBTestServer
from zato.common.typing_ import cast_

# Playwright helpers
from smb_connection import create_connection, delete_connection, get_item_id, navigate_to_list, \
     open_edit_dialog, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page, Response
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.smb.' + CryptoManager.generate_hex_string(32) + '.'

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

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create, edit, edit again with an empty password, delete.
    """

    # Navigate ..
    navigate_to_list(page, base_url)

    # .. create ..
    name = _Test_Name_Prefix + suffix
    create_connection(page, name, 'smb.example.com', 445, 'smb-user', 'smb-password-' + CryptoManager.generate_hex_string())

    # .. edit everything except the password ..
    item_id = get_item_id(page, name)
    open_edit_dialog(page, item_id)

    edited_name = name + '-edited'
    page.fill('#id_edit-name', edited_name)
    page.fill('#id_edit-host', 'smb.edited.example.com')
    page.fill('#id_edit-port', '10445')
    page.fill('#id_edit-username', 'smb-user-edited')

    submit_edit_form(page)

    # .. edit again with the password field left empty ..
    open_edit_dialog(page, item_id)
    page.fill('#id_edit-secret', '')
    submit_edit_form(page)

    # .. delete.
    delete_connection(page, item_id)

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingSMBLifecycle:
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
            if cast_('any_', msg).type == 'error':
                console_errors.append(cast_('any_', msg).text)

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

        def _on_response(response:'Response') -> 'None':
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
        navigate_to_list(page, base_url)

        # .. create ..
        name = _Test_Name_Prefix + 'crud'
        create_connection(page, name, 'smb.example.com', 445, 'smb-user', 'smb-password-' + CryptoManager.generate_hex_string())

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the name, host, port and username ..
        item_id = get_item_id(page, name)
        open_edit_dialog(page, item_id)

        edited_name = name + '-edited'
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-host', 'smb.edited.example.com')
        page.fill('#id_edit-port', '10445')
        page.fill('#id_edit-username', 'smb-user-edited')

        submit_edit_form(page)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert old_row is None, f'Old name "{name}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. verify the edited host and username are shown in the row ..
        row_text = new_row.inner_text()
        assert 'smb.edited.example.com' in row_text, f'Expected edited host in row, got: "{row_text}"'
        assert 'smb-user-edited' in row_text, f'Expected edited username in row, got: "{row_text}"'
        assert '10445' in row_text, f'Expected edited port in row, got: "{row_text}"'

        # .. edit again with the password field left empty and make sure nothing breaks ..
        open_edit_dialog(page, item_id)
        page.fill('#id_edit-secret', '')
        submit_edit_form(page)

        row_after_empty_password = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert row_after_empty_password is not None, 'Row should remain after an edit with an empty password'

        # .. delete ..
        delete_connection(page, item_id)

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
        navigate_to_list(page, base_url)

        # .. create a connection with a Unicode name ..
        name = _Test_Name_Prefix + _Dutch_Letters + '.' + _Greek_Letters + '.' + _Korean_Letters
        create_connection(page, name, 'smb.example.com', 445, 'smb-user', 'smb-password-' + CryptoManager.generate_hex_string())

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the host, keeping the Unicode name ..
        item_id = get_item_id(page, name)
        open_edit_dialog(page, item_id)

        page.fill('#id_edit-host', 'smb.edited.example.com')

        submit_edit_form(page)

        # .. the Unicode name must still be there after the edit ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should still exist after edit'

        row_text = row.inner_text()
        assert 'smb.edited.example.com' in row_text, f'Expected edited host in row, got: "{row_text}"'

        # .. delete ..
        delete_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row_after_delete is None, f'Row "{name}" should be gone after delete'

# ################################################################################################################################

    def test_ping(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection pointing at a live SMB server and clicks Ping, expecting success,
        also after an edit that leaves the password field empty, proving the password is preserved.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Start a live SMB server for the connection to ping
        smb_server = SMBTestServer()
        smb_server.start()

        try:

            # Navigate ..
            navigate_to_list(page, base_url)

            # .. create a connection pointing at the live server ..
            name = _Test_Name_Prefix + 'ping'
            create_connection(page, name, smb_server.host, smb_server.port, smb_server.username, smb_server.password)

            item_id = get_item_id(page, name)

            # .. click Ping and wait for the response ..
            row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

            with page.expect_response(lambda response: '/zato/outgoing/smb/ping/' in response.url, timeout=30000) as response_info:
                page.click(f'{row_selector} a:has-text("Ping")')

            response = response_info.value
            body = response.text()
            assert response.status == 200, f'Ping should return 200, got {response.status} with body: "{body}"'

            # .. edit the connection, leaving the password field empty ..
            open_edit_dialog(page, item_id)
            page.fill('#id_edit-secret', '')
            submit_edit_form(page)

            # .. and ping again - the connection must still authenticate,
            # .. proving the empty field did not overwrite the stored password ..
            with page.expect_response(lambda response: '/zato/outgoing/smb/ping/' in response.url, timeout=30000) as response_info:
                page.click(f'{row_selector} a:has-text("Ping")')

            response = response_info.value
            body = response.text()
            assert response.status == 200, f'Ping after edit should return 200, got {response.status} with body: "{body}"'

            # .. delete the connection before the server goes away.
            delete_connection(page, item_id)

        finally:
            smb_server.stop()

# ################################################################################################################################
# ################################################################################################################################
