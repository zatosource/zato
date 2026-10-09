# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page, Response
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/chat/discord/?cluster=1'

_Test_Name_Prefix = 'test.discord.' + CryptoManager.generate_hex_string(32) + '.'

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

# The connections point at an address nothing listens on, so that the server's handshake loop
# fails at once and makes no request to Discord itself
_Test_Address = 'http://127.0.0.1:1'

# The default channel of the test connections and the one an edit changes it to
_Default_Channel = '200000000000000001'
_Edited_Channel = '200000000000000002'

# How long to wait for dialogs to close and rows to disappear (in milliseconds)
_Dialog_Timeout = 10000

# How long to wait for selectors to become visible (in milliseconds)
_Selector_Timeout = 5000

# How long to wait after an edit form closes before reading the table (in seconds)
_Edit_Settle_Time = 0.3

# ################################################################################################################################
# ################################################################################################################################

def _navigate(page:'Page', base_url:'str', url_suffix:'str'='') -> 'None':
    """ Opens the Discord connections page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}{url_suffix}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _create_connection(page:'Page', name:'str', default_channel_id:'str') -> 'None':
    """ Creates a Discord connection via the UI.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    _ = page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    token = 'token.' + CryptoManager.generate_hex_string()

    page.fill('#id_name', name)
    page.fill('#id_token', token)
    page.fill('#id_default_channel_id', default_channel_id)
    page.fill('#id_address', _Test_Address)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=_Dialog_Timeout)

    # .. and wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    _ = page.wait_for_selector(row_selector, state='visible', timeout=_Selector_Timeout)

# ################################################################################################################################

def _get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row_element = page.query_selector(row_selector)
    row = cast_('any_', row_element)

    id_cell = row.query_selector('td[class*="item_id_"]')
    id_text = id_cell.inner_text()
    out = id_text.strip()

    return out

# ################################################################################################################################

def _open_edit_dialog(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.chat.discord.edit("{item_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=_Selector_Timeout)

# ################################################################################################################################

def _submit_edit_form(page:'Page') -> 'None':
    page.click('#edit-div input[type="submit"]')
    _ = page.wait_for_selector('#edit-div', state='hidden', timeout=_Dialog_Timeout)
    time.sleep(_Edit_Settle_Time)

# ################################################################################################################################

def _delete_connection(page:'Page', item_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.chat.discord.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=_Selector_Timeout)
    page.click('#popup_ok')

    # The server-side delete stops the handshake in progress and waits for the connection queue builder
    # to stop, so wait until the row is actually removed instead of sleeping for a fixed period.
    _ = page.wait_for_selector(f'#tr_{item_id}', state='detached', timeout=_Dialog_Timeout)

# ################################################################################################################################

def _do_full_crud(page:'Page', base_url:'str', suffix:'str') -> 'None':
    """ Performs a full CRUD cycle: create, edit, delete.
    """

    # Navigate ..
    _navigate(page, base_url)

    # .. create ..
    name = _Test_Name_Prefix + suffix
    _create_connection(page, name, _Default_Channel)

    # .. edit the name and the default channel ..
    item_id = _get_item_id(page, name)
    _open_edit_dialog(page, item_id)

    edited_name = name + '-edited'

    page.fill('#id_edit-name', edited_name)
    page.fill('#id_edit-default_channel_id', _Edited_Channel)

    _submit_edit_form(page)

    # .. delete.
    _delete_connection(page, item_id)

# ################################################################################################################################
# ################################################################################################################################

class TestChatDiscordLifecycle:
    """ Tests for console errors, HTTP 500s, full CRUD and Unicode names.
    """

    def test_no_console_errors_during_crud(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Performs a full CRUD session and asserts no console.error messages appear.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Collect console errors ..
        console_errors:'anylist' = []

        def _on_console(msg:'object') -> 'None':
            message = cast_('any_', msg)
            if message.type == 'error':
                console_errors.append(message.text)

        page.on('console', _on_console)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'console-check')

        # .. filter known noise ..
        real_errors:'anylist' = []

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
        server_errors:'anylist' = []

        def _on_response(response:'Response') -> 'None':
            if response.status >= 500:
                server_errors.append(f'{response.status} {response.url}')

        page.on('response', _on_response)

        # .. perform the full CRUD cycle ..
        _do_full_crud(page, base_url, 'http500-check')

        # .. assert no 500s.
        assert not server_errors, 'HTTP 500+ responses during CRUD:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def test_create_requires_a_token(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The create form does not submit without a token.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _navigate(page, base_url)

        page.click('#markup .page_prompt a')
        _ = page.wait_for_selector('#create-div', state='visible')

        name = _Test_Name_Prefix + 'no-token'
        page.fill('#id_name', name)
        page.fill('#id_address', _Test_Address)

        page.click('#create-div input[type="submit"]')
        time.sleep(_Edit_Settle_Time)

        # The dialog stays open and no row appears
        create_div = page.query_selector('#create-div')
        assert create_div is not None
        assert create_div.is_visible(), 'The create dialog should stay open without a token'

        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is None, f'Row "{name}" should not exist without a token'

        # Close the dialog
        page.click('#create-div .form-buttons button')
        _ = page.wait_for_selector('#create-div', state='hidden', timeout=_Dialog_Timeout)

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
        _create_connection(page, name, _Default_Channel)

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. verify the default channel is shown in the row ..
        row_text = row.inner_text()
        assert _Default_Channel in row_text, f'Expected the default channel in row, got: "{row_text}"'

        # .. edit the name and the default channel ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        edited_name = name + '-edited'

        page.fill('#id_edit-name', edited_name)
        page.fill('#id_edit-default_channel_id', _Edited_Channel)

        _submit_edit_form(page)

        # .. verify old name gone, new name present ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert old_row is None, f'Old name "{name}" should be gone after edit'

        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        # .. verify the edited default channel is shown in the row ..
        row_text = new_row.inner_text()
        assert _Edited_Channel in row_text, f'Expected the edited default channel in row, got: "{row_text}"'

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
        _create_connection(page, name, _Default_Channel)

        # .. verify row exists ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should exist after create'

        # .. edit the default channel, keeping the Unicode name ..
        item_id = _get_item_id(page, name)
        _open_edit_dialog(page, item_id)

        page.fill('#id_edit-default_channel_id', _Edited_Channel)

        _submit_edit_form(page)

        # .. the Unicode name must still be there after the edit ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row is not None, f'Row "{name}" should still exist after edit'

        row_text = row.inner_text()
        assert _Edited_Channel in row_text, f'Expected the edited default channel in row, got: "{row_text}"'

        # .. delete ..
        _delete_connection(page, item_id)

        # .. verify gone.
        row_after_delete = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
        assert row_after_delete is None, f'Row "{name}" should be gone after delete'

# ################################################################################################################################
# ################################################################################################################################
