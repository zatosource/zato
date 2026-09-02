# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.ftp_ import FTPTestServer

# Tests
from outgoing_ftp import create_ftp_connection, delete_ftp_connection, get_ftp_conn_id, open_edit_dialog, open_ftp_page, \
    row_selector, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import ConsoleMessage, Page, Response
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.ftp.' + CryptoManager.generate_hex_string(32) + '.'

# Letters from three alphabets.
_Dutch_Letters  = 'ÁÉÍÓÚË'
_Greek_Letters  = 'ΑΒΓΔΕΖ'
_Korean_Letters = 'ㄱㄴㄷㄹㅁㅂ'

# How long to wait for a ping response, in milliseconds
_Ping_Timeout = 30000

_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

# ################################################################################################################################
# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create with Use SSL on, edit, edit again with an empty password, delete.
    """

    # Navigate ..
    open_ftp_page(page, base_url)

    # .. create ..
    name = _Test_Name_Prefix + suffix
    password = 'ftp-password-' + CryptoManager.generate_hex_string()
    create_ftp_connection(page, name, 'ftp.example.com', 21, 'ftp-user', password, use_ssl=True)

    # .. edit everything except the password ..
    item_id = get_ftp_conn_id(page, name)
    open_edit_dialog(page, item_id)

    edited_name = name + '-edited'
    page.fill('#id_edit-name', edited_name)
    page.fill('#id_edit-host', 'ftp.edited.example.com')
    page.fill('#id_edit-port', '10021')
    page.fill('#id_edit-username', 'ftp-user-edited')

    submit_edit_form(page)

    # .. edit again with the password field left empty ..
    open_edit_dialog(page, item_id)
    page.fill('#id_edit-secret', '')
    submit_edit_form(page)

    # .. delete.
    delete_ftp_connection(page, item_id)

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingFTPLifecycle:
    """ Tests for console errors, HTTP 500s, full CRUD, the Use SSL flag, Unicode names, and live pings.
    """

    def test_no_console_errors_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Performs a full CRUD session and asserts no console.error messages appear.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect console errors ..
        console_errors:'strlist' = []

        def _on_console(msg:'ConsoleMessage') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        page.on('console', _on_console)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'console-check')

        # .. filter known noise ..
        real_errors:'strlist' = []

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
        server_errors:'strlist' = []

        def _on_response(response:'Response') -> 'None':
            if response.status >= INTERNAL_SERVER_ERROR:
                server_errors.append(f'{response.status} {response.url}')

        page.on('response', _on_response)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'http500-check')

        # .. assert no 500s.
        assert not server_errors, 'HTTP 500+ responses during CRUD:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def test_full_crud_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Create with Use SSL on, verify, edit, verify, edit with an empty password, verify, delete, verify gone.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        open_ftp_page(page, base_url)

        # .. create with the Use SSL flag on ..
        name = _Test_Name_Prefix + 'crud'
        password = 'ftp-password-' + CryptoManager.generate_hex_string()
        create_ftp_connection(page, name, 'ftp.example.com', 21, 'ftp-user', password, use_ssl=True)

        # .. verify row exists ..
        selector = row_selector(name)
        row = page.query_selector(selector)
        assert row is not None, f'Row "{name}" should exist after create'

        # .. the edit dialog must come back with the flag still on ..
        item_id = get_ftp_conn_id(page, name)
        open_edit_dialog(page, item_id)

        assert page.is_checked('#id_edit-use_ssl'), 'Use SSL should be on after a create that turned it on'

        # .. edit the name, host, port and username, turning the flag off along the way ..
        edited_name = name + '-edited'
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-host', 'ftp.edited.example.com')
        page.fill('#id_edit-port', '10021')
        page.fill('#id_edit-username', 'ftp-user-edited')
        page.click('#id_edit-use_ssl')

        submit_edit_form(page)

        # .. verify old name gone, new name present ..
        old_selector = row_selector(name)
        old_row = page.query_selector(old_selector)
        assert old_row is None, f'Old name "{name}" should be gone after edit'

        edited_selector = row_selector(edited_name)
        new_row = page.query_selector(edited_selector)
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. verify the edited host, port and username are shown in the row ..
        row_text = new_row.inner_text()
        assert 'ftp.edited.example.com' in row_text, f'Expected edited host in row, got: "{row_text}"'
        assert 'ftp-user-edited' in row_text, f'Expected edited username in row, got: "{row_text}"'
        assert '10021' in row_text, f'Expected edited port in row, got: "{row_text}"'

        # .. the edit turned the flag off and the dialog must say so now ..
        open_edit_dialog(page, item_id)
        assert not page.is_checked('#id_edit-use_ssl'), 'Use SSL should be off after an edit that turned it off'

        # .. edit again with the password field left empty and make sure nothing breaks ..
        page.fill('#id_edit-secret', '')
        submit_edit_form(page)

        row_after_empty_password = page.query_selector(edited_selector)
        assert row_after_empty_password is not None, 'Row should remain after an edit with an empty password'

        # .. delete ..
        delete_ftp_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(edited_selector)
        assert row_after_delete is None, f'Row "{edited_name}" should be gone after delete'

# ################################################################################################################################

    def test_unicode_name_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Runs the whole create-edit-delete cycle with a name containing Dutch, Greek and Korean letters.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        open_ftp_page(page, base_url)

        # .. create a connection with a Unicode name ..
        name = _Test_Name_Prefix + _Dutch_Letters + '.' + _Greek_Letters + '.' + _Korean_Letters
        password = 'ftp-password-' + CryptoManager.generate_hex_string()
        create_ftp_connection(page, name, 'ftp.example.com', 21, 'ftp-user', password)

        # .. verify row exists ..
        selector = row_selector(name)
        row = page.query_selector(selector)
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the host, keeping the Unicode name ..
        item_id = get_ftp_conn_id(page, name)
        open_edit_dialog(page, item_id)

        page.fill('#id_edit-host', 'ftp.edited.example.com')

        submit_edit_form(page)

        # .. the Unicode name must still be there after the edit ..
        row = page.query_selector(selector)
        assert row is not None, f'Row "{name}" should still exist after edit'

        row_text = row.inner_text()
        assert 'ftp.edited.example.com' in row_text, f'Expected edited host in row, got: "{row_text}"'

        # .. delete ..
        delete_ftp_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(selector)
        assert row_after_delete is None, f'Row "{name}" should be gone after delete'

# ################################################################################################################################

    def _run_ping_cycle(self, page:'Page', base_url:'str', suffix:'str', use_ssl:'bool') -> 'None':
        """ Creates a connection pointing at a live FTP server and clicks Ping, expecting success,
        also after an edit that leaves the password field empty.
        """

        def _is_ping_response(response:'Response') -> 'bool':
            return '/zato/outgoing/ftp/ping/' in response.url

        # Start a live FTP server for the connection to ping - a plain one or one that requires TLS.
        ftp_server = FTPTestServer(use_ssl=use_ssl)
        ftp_server.start()

        try:

            # Navigate ..
            open_ftp_page(page, base_url)

            # .. create a connection pointing at the live server ..
            name = _Test_Name_Prefix + suffix
            password = ftp_server.password
            create_ftp_connection(
                page, name, ftp_server.host, ftp_server.port, ftp_server.username, password, use_ssl=use_ssl)

            item_id = get_ftp_conn_id(page, name)
            selector = row_selector(name)

            # .. click Ping and wait for the response ..
            with page.expect_response(_is_ping_response, timeout=_Ping_Timeout) as response_info:
                page.click(f'{selector} a:has-text("Ping")')

            response = response_info.value
            body = response.text()
            assert response.status == OK, f'Ping should return 200, got {response.status} with body: "{body}"'

            # .. edit the connection, leaving the password field empty ..
            open_edit_dialog(page, item_id)
            page.fill('#id_edit-secret', '')
            submit_edit_form(page)

            # .. and ping again - the connection must still authenticate ..
            with page.expect_response(_is_ping_response, timeout=_Ping_Timeout) as response_info:
                page.click(f'{selector} a:has-text("Ping")')

            response = response_info.value
            body = response.text()
            assert response.status == OK, f'Ping after edit should return 200, got {response.status} with body: "{body}"'

            # .. delete the connection before the server goes away.
            delete_ftp_connection(page, item_id)

        finally:
            ftp_server.stop()

# ################################################################################################################################

    def test_ping(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A live ping over plain FTP.
        """
        base_url = zato_dashboard['dashboard_url']
        self._run_ping_cycle(logged_in_page, base_url, 'ping', use_ssl=False)

# ################################################################################################################################

    def test_ping_ftps(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A live ping over FTPS - the connection has Use SSL on and the server requires TLS.
        """
        base_url = zato_dashboard['dashboard_url']
        self._run_ping_cycle(logged_in_page, base_url, 'ping-ftps', use_ssl=True)

# ################################################################################################################################
# ################################################################################################################################
