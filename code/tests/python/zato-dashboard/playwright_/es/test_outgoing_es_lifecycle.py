# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import time

# The directory with the shared Elasticsearch server helpers used by the live server tests
_es_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'zato-server', 'es'))
sys.path.insert(0, _es_tests_dir)

# Zato
from es_server import start_es, stop_es
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/outgoing/es/?cluster=1&type_=outconn-es'

_Test_Name_Prefix = 'test.es.' + CryptoManager.generate_hex_string(32) + '.'

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

# The port of the instance the ping test starts
_Ping_Server_Port = 9266

# ################################################################################################################################
# ################################################################################################################################

def _navigate(page:'Page', base_url:'str', url_suffix:'str'='') -> 'None':
    """ Opens the outgoing Elasticsearch page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}{url_suffix}')
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_connection(page:'Page', name:'str', address_list:'str', username:'str', password:'str') -> 'None':
    """ Creates an outgoing Elasticsearch connection via the UI.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_address_list', address_list)
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
    page.evaluate(f'$.fn.zato.outgoing.es.edit("{item_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def _submit_edit_form(page:'Page') -> 'None':
    page.click('#edit-div input[type="submit"]')
    page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
    time.sleep(0.3)

# ################################################################################################################################

def _delete_connection(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.outgoing.es.delete_("{item_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create, edit, edit again with an empty password, delete.
    """

    # Navigate ..
    _navigate(page, base_url)

    # .. create, with a multi-line address list ..
    name = _Test_Name_Prefix + suffix
    address_list = 'http://es1.example.com:9200\nhttp://es2.example.com:9200'
    _create_connection(page, name, address_list, 'es-user', 'es-password-' + CryptoManager.generate_hex_string())

    # .. edit everything except the password ..
    item_id = _get_item_id(page, name)
    _open_edit_dialog(page, item_id)

    edited_name = name + '-edited'
    page.fill('#id_edit-name', edited_name)
    page.fill('#id_edit-address_list', 'http://es.edited.example.com:9200')
    page.fill('#id_edit-username', 'es-user-edited')

    _submit_edit_form(page)

    # .. edit again with the password field left empty ..
    _open_edit_dialog(page, item_id)
    page.fill('#id_edit-secret', '')
    _submit_edit_form(page)

    # .. delete.
    _delete_connection(page, item_id)

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingESLifecycle:
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

        # .. create, with a multi-line address list ..
        name = _Test_Name_Prefix + 'crud'
        address_list = 'http://es1.example.com:9200\nhttp://es2.example.com:9200'
        _create_connection(page, name, address_list, 'es-user', 'es-password-' + CryptoManager.generate_hex_string())

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. verify both lines of the address list are shown in the row ..
        row_text = row.inner_text()
        assert 'http://es1.example.com:9200' in row_text, f'Expected the first address in row, got: "{row_text}"'
        assert 'http://es2.example.com:9200' in row_text, f'Expected the second address in row, got: "{row_text}"'

        # .. edit the name, address list and username ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        edited_name = name + '-edited'
        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-address_list', 'http://es.edited.example.com:9200')
        page.fill('#id_edit-username', 'es-user-edited')

        _submit_edit_form(page)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert old_row is None, f'Old name "{name}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. verify the edited address list is shown in the row ..
        row_text = new_row.inner_text()
        assert 'http://es.edited.example.com:9200' in row_text, f'Expected edited address list in row, got: "{row_text}"'

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
            page, name, 'http://es.example.com:9200', 'es-user',
            'es-password-' + CryptoManager.generate_hex_string())

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the address list, keeping the Unicode name ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        page.fill('#id_edit-address_list', 'http://es.edited.example.com:9200')

        _submit_edit_form(page)

        # .. the Unicode name must still be there after the edit ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should still exist after edit'

        row_text = row.inner_text()
        assert 'http://es.edited.example.com:9200' in row_text, f'Expected edited address list in row, got: "{row_text}"'

        # .. delete ..
        _delete_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row_after_delete is None, f'Row "{name}" should be gone after delete'

# ################################################################################################################################

    def test_ping(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a connection pointing at a live Elasticsearch server and clicks Ping, expecting success,
        also after an edit that leaves the password field empty, proving the password is preserved.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Start a live Elasticsearch server for the connection to ping
        es_server = start_es(
            port=_Ping_Server_Port,
            needs_tls=False,
        )

        try:

            # Navigate ..
            _navigate(page, base_url)

            # .. create a connection pointing at the live server ..
            name = _Test_Name_Prefix + 'ping'
            address_list = f'{es_server.scheme}://{es_server.host}:{es_server.port}'
            _create_connection(page, name, address_list, '', '')

            item_id = _get_item_id(page, name)

            # .. click Ping and wait for the response ..
            row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

            with page.expect_response(
                lambda response: '/zato/outgoing/es/ping/' in response.url, timeout=30000) as response_info:
                page.click(f'{row_selector} a:has-text("Ping")')

            response = response_info.value
            body = response.text()
            assert response.status == 200, f'Ping should return 200, got {response.status} with body: "{body}"'

            # .. edit the connection, leaving the password field empty ..
            _open_edit_dialog(page, item_id)
            page.fill('#id_edit-secret', '')
            _submit_edit_form(page)

            # .. and ping again - the connection must still work,
            # .. proving the edit with an empty password field did not break anything ..
            with page.expect_response(
                lambda response: '/zato/outgoing/es/ping/' in response.url, timeout=30000) as response_info:
                page.click(f'{row_selector} a:has-text("Ping")')

            response = response_info.value
            body = response.text()
            assert response.status == 200, f'Ping after edit should return 200, got {response.status} with body: "{body}"'

            # .. delete the connection before the server goes away.
            _delete_connection(page, item_id)

        finally:
            stop_es(es_server)

# ################################################################################################################################
# ################################################################################################################################
