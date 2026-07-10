# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sqlite3

# Zato
from zato.common.crypto.api import CryptoManager
from zato.x12.control import ControlNumberStore, Kind_Group, Kind_Interchange, Kind_Transaction_Set, get_control_db_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Control_Numbers_Page_Url = '/zato/b2b-control-numbers/?cluster=1'

# The receiver shared by all the seeded rows
_Receiver = 'RECEIVERID'

# ################################################################################################################################
# ################################################################################################################################

def _open_control_numbers_page(page:'Page', base_url:'str') -> 'None':
    """ Navigates to the control numbers page and waits for its table.
    """
    _ = page.goto(f'{base_url}{_Control_Numbers_Page_Url}')
    page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def _row_selector(sender:'str', kind:'str') -> 'str':
    """ The selector of one sequence's table row.
    """
    out = f'tr[data-sender="{sender}"][data-kind="{kind}"]'
    return out

# ################################################################################################################################

def _delete_seeded_rows(sender:'str') -> 'None':
    """ Removes everything the test seeded, keying off the unique sender name.
    """
    pair_prefix = sender + ':%'

    connection = sqlite3.connect(get_control_db_path())

    with connection:
        _ = connection.execute('DELETE FROM x12_control_sequence WHERE pair LIKE ?', (pair_prefix,))

    connection.close()

# ################################################################################################################################
# ################################################################################################################################

class TestB2BControlNumbers:
    """ The Dashboard page showing X12 control number sequences - one row per
    sender-receiver pair and level, with the next number editable in place.
    """

# ################################################################################################################################

    def test_control_numbers_page(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # A unique sender keeps this test's rows apart from anything else in the store.
        sender = 'test.sender.' + CryptoManager.generate_hex_string(16)

        # Seed the store the page reads from - the interchange sequence has handed out
        # two numbers, the group sequence one, and the transaction set sequence
        # was repositioned by hand so it has no last-used information.
        store = ControlNumberStore(get_control_db_path())

        _ = store.next_number(sender, _Receiver, Kind_Interchange)
        _ = store.next_number(sender, _Receiver, Kind_Interchange)
        _ = store.next_number(sender, _Receiver, Kind_Group)
        store.set_next(sender, _Receiver, Kind_Transaction_Set, 77)

        store.close()

        try:

            # The page shows one row per pair and level ..
            _open_control_numbers_page(page, base_url)

            interchange_row = page.locator(_row_selector(sender, Kind_Interchange))
            group_row = page.locator(_row_selector(sender, Kind_Group))
            set_row = page.locator(_row_selector(sender, Kind_Transaction_Set))

            # .. the interchange sequence handed out 1 and 2, so the next number is 3 ..
            assert interchange_row.locator('td.control-number-next').text_content().strip() == '3'
            assert interchange_row.locator('td').nth(4).text_content().strip() == '2'

            # .. its last-used timestamp is a real ISO timestamp ..
            last_used_time = interchange_row.locator('td').nth(5).text_content().strip()
            assert 'T' in last_used_time

            # .. the group sequence advanced once ..
            assert group_row.locator('td.control-number-next').text_content().strip() == '2'
            assert group_row.locator('td').nth(4).text_content().strip() == '1'

            # .. and the hand-made transaction set sequence has no last-used information.
            assert set_row.locator('td.control-number-next').text_content().strip() == '77'
            assert set_row.locator('td').nth(4).text_content().strip() == '---'
            assert set_row.locator('td').nth(5).text_content().strip() == '---'

            # A value that is not a number is rejected and the row is restored ..
            interchange_row.locator('a.control-number-edit').click()
            interchange_row.locator('input.control-number-input').fill('not-a-number')
            interchange_row.locator('a.control-number-save').click()

            page.wait_for_selector('#user-message-div', state='visible')
            assert 'must be an integer' in page.text_content('#user-message')
            assert interchange_row.locator('td.control-number-next').text_content().strip() == '3'

            # .. while a real number is saved in place - the message left by the error
            # is hidden first so the wait below only passes once this save comes back.
            _ = page.evaluate("$('#user-message-div').hide()")

            interchange_row.locator('a.control-number-edit').click()
            interchange_row.locator('input.control-number-input').fill('500')
            interchange_row.locator('a.control-number-save').click()

            page.wait_for_selector('#user-message-div', state='visible')
            assert 'Next number saved' in page.text_content('#user-message')

            assert interchange_row.locator('td.control-number-next').text_content().strip() == '500'

            # What the page saved is what the store now hands out.
            store = ControlNumberStore(get_control_db_path())
            number = store.next_number(sender, _Receiver, Kind_Interchange)
            store.close()

            assert number == 500

        finally:
            _delete_seeded_rows(sender)

# ################################################################################################################################
# ################################################################################################################################
