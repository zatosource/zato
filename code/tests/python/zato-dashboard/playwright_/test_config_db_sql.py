# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/config-db/sql/'

_Test_Name_Prefix = 'test.config.db.sql.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestConfigDBSQL:
    """ Tests for the Config DB SQL screen.
    """

    def test_01_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the SQL screen and verifies its structure:
        - the database selector offers the audit log and analytics databases
        - the form shows SQLite as the default type
        - the Test and Save buttons are present
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the SQL screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_database', state='visible')

        # .. verify the database selector offers both databases ..
        database_options = page.query_selector_all('#id_database option')

        option_values = [] # type: list

        for option in database_options:
            value = option.get_attribute('value')
            option_values.append(value)

        assert option_values == ['audit-log', 'analytics'], f'Unexpected databases: {option_values}'

        # .. by default the audit log database is shown, backed by SQLite ..
        database_value = page.input_value('#id_database')
        assert database_value == 'audit-log', f'Expected "audit-log", got: {database_value}'

        type_value = page.input_value('#id_type')
        assert type_value == 'sqlite', f'Expected "sqlite", got: {type_value}'

        # .. the SQLite file path points at the audit database file ..
        name_value = page.input_value('#id_name')
        assert name_value.endswith('audit.db'), f'Expected a path ending in audit.db, got: {name_value}'

        # .. and both buttons are present.
        test_button_text = page.inner_text('#check-button')
        assert test_button_text.strip() == 'Test', f'Expected "Test", got: {test_button_text}'

        save_button_text = page.inner_text('#update-button')
        assert save_button_text.strip() == 'Save', f'Expected "Save", got: {save_button_text}'

# ################################################################################################################################

    def test_02_test_connection(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Runs a live connection test against the default SQLite database
        and verifies the OK result appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the SQL screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_database', state='visible')

        # .. run the connection test ..
        page.click('#check-button')

        # .. and verify the OK result with the response time appears.
        result = page.wait_for_selector('.test-results .result-status.ok', state='visible', timeout=10000)
        result_text = result.inner_text()
        assert result_text == 'OK', f'Expected "OK", got: {result_text}'

        message = page.inner_text('.test-results .result-message')
        assert 'Connection OK' in message, f'Expected "Connection OK" in message, got: {message}'

# ################################################################################################################################

    def test_03_save_and_reload(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Saves a name and description for the audit log database and verifies
        that both come back after the page is reloaded.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        display_name = _Test_Name_Prefix + 'audit-log'
        description = 'Description of ' + display_name

        # Navigate to the SQL screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_database', state='visible')

        # .. fill in the name and description ..
        page.fill('#id_display_name', display_name)
        page.fill('#id_description', description)

        # .. save the form ..
        page.click('#update-button')

        # .. wait for the save confirmation ..
        _ = page.wait_for_selector('#progress-configure .progress-icon.completed', state='visible', timeout=10000)

        progress_text = page.inner_text('#progress-configure .progress-text')
        assert 'Saved' in progress_text, f'Expected "Saved" in progress text, got: {progress_text}'

        # .. reload the page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_database', state='visible')

        # .. and verify the values came back from the server.
        name_value = page.input_value('#id_display_name')
        assert name_value == display_name, f'Expected "{display_name}", got: "{name_value}"'

        description_value = page.input_value('#id_description')
        assert description_value == description, f'Expected "{description}", got: "{description_value}"'

# ################################################################################################################################

    def test_04_switch_database(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Switches the selector to the analytics database and verifies the form repopulates -
        the analytics database has its own SQLite file and no name of its own yet.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the SQL screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_database', state='visible')

        # .. switch to the analytics database ..
        _ = page.select_option('#id_database', 'analytics')

        # .. its SQLite file path points at the analytics database file ..
        name_value = page.input_value('#id_name')
        assert name_value.endswith('analytics.db'), f'Expected a path ending in analytics.db, got: {name_value}'

        # .. and the display name saved for the audit log database does not leak into it.
        display_name_value = page.input_value('#id_display_name')
        assert display_name_value == '', f'Expected an empty name, got: "{display_name_value}"'

# ################################################################################################################################
# ################################################################################################################################
