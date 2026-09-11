# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.sftp_ import SFTPTestServer

# Tests
from alerts_tab import click_active_slider, get_field_value, is_checked, set_popover_value, summary_text, switch_to_tab, \
     Field_Consecutive_Failures, Field_Is_Active, Line_Failures_In_A_Row, Tab_Alerts, Tab_Main
from outgoing_sftp import create_sftp_connection, delete_sftp_connection, expand_more_options, forget_host_key, \
     get_sftp_conn_id, open_edit_dialog, open_sftp_page, row_selector, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.sftp.' + CryptoManager.generate_hex_string(32) + '.'

# Letters from three alphabets - one of the tests below runs a whole create-edit-delete
# cycle with a connection whose name contains them all.
_Dutch_Letters = 'ÁÉÍÓÚË'
_Greek_Letters = 'ΑΒΓΔΕΖ'
_Korean_Letters = 'ㄱㄴㄷㄹㅁㅂ'

# The prefix the SFTP page names its tab panels after
_Page_Prefix = 'out-sftp'

# The threshold the Alerts tab round trip stores, well away from the seeded default of 3
_Edited_Consecutive_Failures = '7'

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
    open_sftp_page(page, base_url)

    # .. create with the host key checking slider on so that the edit below has something to flip ..
    name = _Test_Name_Prefix + suffix
    create_sftp_connection(page, name, 'sftp.example.com:22', 'sftp-user',
        'sftp-password-' + CryptoManager.generate_hex_string(), strict_host_key_checking=True)

    # .. edit everything except the password, flipping the host key checking slider too ..
    item_id = get_sftp_conn_id(page, name)
    open_edit_dialog(page, item_id)

    edited_name = name + '-edited'
    page.fill('#id_edit-name', edited_name)
    page.fill('#id_edit-address', 'sftp.edited.example.com:22022')
    page.fill('#id_edit-username', 'sftp-user-edited')
    page.fill('#id_edit-private_key', '/tmp/my-edited-sftp-key')
    expand_more_options(page, 'edit')
    page.click('#id_edit-strict_host_key_checking')

    submit_edit_form(page)

    # .. edit again with the password field left empty ..
    open_edit_dialog(page, item_id)
    page.fill('#id_edit-secret', '')
    submit_edit_form(page)

    # .. delete.
    delete_sftp_connection(page, item_id)

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

        def _on_console(msg:'any_') -> 'None':
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

        def _on_response(response:'any_') -> 'None':
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
        open_sftp_page(page, base_url)

        # .. create with the host key checking slider on so that the edit below turns it off ..
        name = _Test_Name_Prefix + 'crud'
        create_sftp_connection(page, name, 'sftp.example.com:22', 'sftp-user',
            'sftp-password-' + CryptoManager.generate_hex_string(), strict_host_key_checking=True)

        # .. verify row exists ..
        row = page.query_selector(row_selector(name))
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the name, address and username, flipping the host key checking slider too ..
        item_id = get_sftp_conn_id(page, name)
        open_edit_dialog(page, item_id)

        edited_name = name + '-edited'
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-address', 'sftp.edited.example.com:22022')
        page.fill('#id_edit-username', 'sftp-user-edited')
        expand_more_options(page, 'edit')
        page.click('#id_edit-strict_host_key_checking')

        submit_edit_form(page)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(row_selector(name))
        assert old_row is None, f'Old name "{name}" should be gone after edit'

        new_row = page.query_selector(row_selector(edited_name))
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
        open_edit_dialog(page, item_id)
        page.fill('#id_edit-secret', '')
        submit_edit_form(page)

        row_after_empty_password = page.query_selector(row_selector(edited_name))
        assert row_after_empty_password is not None, 'Row should remain after an edit with an empty password'

        # .. delete ..
        delete_sftp_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(row_selector(edited_name))
        assert row_after_delete is None, f'Row "{edited_name}" should be gone after delete'

# ################################################################################################################################

    def test_unicode_name_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Runs the whole create-edit-delete cycle with a name containing Dutch, Greek and Korean letters.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        open_sftp_page(page, base_url)

        # .. create a connection with a Unicode name ..
        name = _Test_Name_Prefix + _Dutch_Letters + '.' + _Greek_Letters + '.' + _Korean_Letters
        create_sftp_connection(page, name, 'sftp.example.com:22', 'sftp-user',
            'sftp-password-' + CryptoManager.generate_hex_string())

        # .. verify row exists ..
        row = page.query_selector(row_selector(name))
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the address, keeping the Unicode name ..
        item_id = get_sftp_conn_id(page, name)
        open_edit_dialog(page, item_id)

        page.fill('#id_edit-address', 'sftp.edited.example.com:22022')

        submit_edit_form(page)

        # .. the Unicode name must still be there after the edit ..
        row = page.query_selector(row_selector(name))
        assert row is not None, f'Row "{name}" should still exist after edit'

        row_text = row.inner_text()
        assert 'sftp.edited.example.com:22022' in row_text, f'Expected edited address in row, got: "{row_text}"'

        # .. delete ..
        delete_sftp_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(row_selector(name))
        assert row_after_delete is None, f'Row "{name}" should be gone after delete'

# ################################################################################################################################

    def test_alerts_tab_round_trip(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Changes a threshold through its popover and flips the Active slider on the Alerts tab,
        saves, reopens the edit form and expects both to come back, with the Main tab still holding its own fields.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        open_sftp_page(page, base_url)

        # .. create a connection, which stores the seeded alert defaults ..
        name = _Test_Name_Prefix + 'alerts'
        create_sftp_connection(page, name, 'sftp.example.com:22', 'sftp-user',
            'sftp-password-' + CryptoManager.generate_hex_string())

        item_id = get_sftp_conn_id(page, name)

        # .. open the edit form and go to the Alerts tab ..
        open_edit_dialog(page, item_id)
        switch_to_tab(page, _Page_Prefix, 'edit', Tab_Alerts)

        assert is_checked(page, 'edit', Field_Is_Active), 'The Active slider should be on by default'

        # .. change the threshold through its popover, which rewrites the line's summary ..
        set_popover_value(page, _Page_Prefix, 'edit', Line_Failures_In_A_Row, Field_Consecutive_Failures,
            _Edited_Consecutive_Failures)

        assert get_field_value(page, 'edit', Field_Consecutive_Failures) == _Edited_Consecutive_Failures
        assert _Edited_Consecutive_Failures in summary_text(page, _Page_Prefix, 'edit', Line_Failures_In_A_Row)

        # .. flip the Active slider off and save ..
        click_active_slider(page, 'edit')
        assert not is_checked(page, 'edit', Field_Is_Active)

        submit_edit_form(page)

        # .. reopen the edit form - the Alerts tab reads what was saved ..
        open_edit_dialog(page, item_id)
        switch_to_tab(page, _Page_Prefix, 'edit', Tab_Alerts)

        assert get_field_value(page, 'edit', Field_Consecutive_Failures) == _Edited_Consecutive_Failures, \
            'The edited threshold should come back after a save'
        assert not is_checked(page, 'edit', Field_Is_Active), 'The Active slider should stay off after a save'
        assert _Edited_Consecutive_Failures in summary_text(page, _Page_Prefix, 'edit', Line_Failures_In_A_Row)

        # .. and the Main tab still holds the connection's own fields ..
        switch_to_tab(page, _Page_Prefix, 'edit', Tab_Main)

        assert page.input_value('#id_edit-name') == name
        assert page.input_value('#id_edit-address') == 'sftp.example.com:22'
        assert page.input_value('#id_edit-username') == 'sftp-user'

        # .. save once more from the Main tab, which must not disturb the Alerts tab's values ..
        submit_edit_form(page)

        open_edit_dialog(page, item_id)
        switch_to_tab(page, _Page_Prefix, 'edit', Tab_Alerts)

        assert get_field_value(page, 'edit', Field_Consecutive_Failures) == _Edited_Consecutive_Failures
        assert not is_checked(page, 'edit', Field_Is_Active)

        page.click('#edit-div button:has-text("Cancel")')
        _ = page.wait_for_selector('#edit-div', state='hidden')

        # .. delete.
        delete_sftp_connection(page, item_id)

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
        forget_host_key(sftp_server.host, sftp_server.port)

        # The connection below points at this path - the key itself is copied there
        # only now, with the permissions that ssh requires.
        sftp_key_path = zato_dashboard['sftp_key_path']

        shutil.copyfile(sftp_server.client_key_encrypted_path, sftp_key_path)
        os.chmod(sftp_key_path, 0o600)

        try:

            # Navigate ..
            open_sftp_page(page, base_url)

            # .. create a connection pointing at the live server - it authenticates with an encrypted key
            # .. whose passphrase is the connection's password, and host key checking must be off
            # .. because the server's host key was generated a moment ago ..
            name = _Test_Name_Prefix + 'ping'
            address = f'{sftp_server.host}:{sftp_server.port}'

            create_sftp_connection(
                page,
                name,
                address,
                sftp_server.username,
                sftp_server.password,
                private_key=sftp_key_path,
                strict_host_key_checking=False,
            )

            item_id = get_sftp_conn_id(page, name)

            # .. click Ping and wait for the response ..
            ping_link_selector = row_selector(name) + ' a:has-text("Ping")'

            with page.expect_response(lambda response: '/zato/outgoing/sftp/ping/' in response.url, timeout=30000) as response_info:
                page.click(ping_link_selector)

            response = response_info.value
            body = response.text()
            assert response.status == 200, f'Ping should return 200, got {response.status} with body: "{body}"'

            # .. edit the connection, leaving the password field empty ..
            open_edit_dialog(page, item_id)
            page.fill('#id_edit-secret', '')
            submit_edit_form(page)

            # .. and ping again - the connection must still authenticate,
            # .. proving the empty field did not overwrite the stored password ..
            with page.expect_response(lambda response: '/zato/outgoing/sftp/ping/' in response.url, timeout=30000) as response_info:
                page.click(ping_link_selector)

            response = response_info.value
            body = response.text()
            assert response.status == 200, f'Ping after edit should return 200, got {response.status} with body: "{body}"'

            # .. delete the connection before the server goes away.
            delete_sftp_connection(page, item_id)

        finally:
            sftp_server.stop()

# ################################################################################################################################
# ################################################################################################################################
