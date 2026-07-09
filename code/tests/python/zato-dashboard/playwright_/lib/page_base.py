# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

_No_Results_Label = 'No results'

# ################################################################################################################################
# ################################################################################################################################

class ZatoListPage:
    """ Base class for Zato dashboard list pages that use the jQuery data-table pattern.

    All pages share the same structure:
    - A create link that opens #create-div jQuery UI dialog with #create-form
    - Edit links per row that open #edit-div dialog with #edit-form
    - Delete links per row that trigger a jConfirm dialog
    - Table rows in #data-table tbody tr
    - Change password dialog in #change_password-div
    """

# ################################################################################################################################

    def navigate(self, page:'Page', url:'str') -> 'None':
        """ Navigates to a list page and waits for the data table to be ready.
        """

        # Go to the URL ..
        _ = page.goto(url)

        # .. and wait for the table to appear.
        page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

    def get_row_count(self, page:'Page') -> 'int':
        """ Returns the number of data rows in the table, excluding the 'No results' placeholder.
        """

        # Query all visible data rows ..
        rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')

        out = len(rows)
        return out

# ################################################################################################################################

    def get_row_names(self, page:'Page', name_column_index:'int' = 2) -> 'strlist':
        """ Returns the text content of the name column for all visible rows.
        Column index is 0-based. The default (2) works for pages where columns are:
        0=numbering, 1=checkbox, 2=name.
        """

        # Get all table rows ..
        rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')

        out = [] # type: strlist

        # .. iterate over each row ..
        for row in rows:
            cells = row.query_selector_all('td')
            cell_count = len(cells)

            # .. extract the name if the row has enough columns ..
            if cell_count > name_column_index:
                cell = cells[name_column_index]
                text = cell.inner_text().strip()

                if text:
                    if text != _No_Results_Label:
                        out.append(text)

        return out

# ################################################################################################################################

    def create_item(self, page:'Page', fields:'dict[str, str]') -> 'None':
        """ Opens the create dialog, fills in the fields, and submits.
        """

        # Click the create link ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. fill in each field ..
        for field_name, value in fields.items():
            selector = f'#create-form #id_{field_name}'
            page.fill(selector, value)

        # .. submit the form ..
        page.click('#create-form input[type="submit"]')

        # .. and wait for the dialog to close.
        page.wait_for_selector('#create-div', state='hidden', timeout=5000)

# ################################################################################################################################

    def edit_item(self, page:'Page', name:'str', fields:'dict[str, str]') -> 'None':
        """ Finds a row by name, clicks its Edit link, fills in the fields, and submits.
        """

        # Find the row and open the edit dialog ..
        row = self._find_row_by_name(page, name)
        edit_link = row.query_selector('a[href*="edit"]')
        edit_link.click()

        page.wait_for_selector('#edit-div', state='visible')

        # .. fill in each field ..
        for field_name, value in fields.items():
            selector = f'#edit-form #id_edit-{field_name}'
            page.fill(selector, '')
            page.fill(selector, value)

        # .. submit the form ..
        page.click('#edit-form input[type="submit"]')

        # .. and wait for the dialog to close.
        page.wait_for_selector('#edit-div', state='hidden', timeout=5000)

# ################################################################################################################################

    def delete_item(self, page:'Page', name:'str') -> 'None':
        """ Finds a row by name, clicks Delete, and confirms in the jConfirm dialog.
        """

        # Find the row and click delete ..
        row = self._find_row_by_name(page, name)
        delete_link = row.query_selector('a[href*="delete"]')
        delete_link.click()

        # .. wait for the confirmation dialog and click OK ..
        page.wait_for_selector('#popup_container', state='visible')
        page.click('#popup_ok')

        # .. and wait for the row removal animation.
        page.wait_for_timeout(500)

# ################################################################################################################################

    def change_password(self, page:'Page', name:'str', new_password:'str') -> 'None':
        """ Clicks 'Change password' for a row, fills the new password, and submits.
        """

        # Find the row and open the password dialog ..
        row = self._find_row_by_name(page, name)
        password_link = row.query_selector('a[href*="change_password"]')
        password_link.click()

        # .. fill in the new password ..
        page.wait_for_selector('#change_password-div', state='visible')
        page.fill('#change_password-form #id_password', new_password)

        # .. and submit.
        page.click('#change_password-form input[type="submit"]')
        page.wait_for_selector('#change_password-div', state='hidden', timeout=5000)

# ################################################################################################################################

    def assert_row_exists(self, page:'Page', name:'str') -> 'None':
        """ Asserts that a row with the given name exists in the table.
        """

        names = self.get_row_names(page)
        assert name in names, f'Expected row "{name}" in table, found: {names}'

# ################################################################################################################################

    def assert_row_absent(self, page:'Page', name:'str') -> 'None':
        """ Asserts that no row with the given name exists in the table.
        """

        names = self.get_row_names(page)
        assert name not in names, f'Row "{name}" should not be in table, found: {names}'

# ################################################################################################################################

    def _find_row_by_name(self, page:'Page', name:'str', name_column_index:'int' = 2) -> 'any_':
        """ Finds and returns the tr element for a row matching the given name.
        """

        # Query all data rows ..
        rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')

        # .. search for the one with a matching name ..
        for row in rows:
            cells = row.query_selector_all('td')
            cell_count = len(cells)

            if cell_count > name_column_index:
                cell = cells[name_column_index]
                text = cell.inner_text().strip()

                if text == name:
                    return row

        # .. nothing was found.
        raise AssertionError(f'Row with name "{name}" not found in table')

# ################################################################################################################################
# ################################################################################################################################
