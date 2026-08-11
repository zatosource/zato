# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import any_, cast_

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
        - the tab strip offers the audit log, analytics and pub/sub databases
        - the form shows SQLite as the default type
        - the Test connection link and the Save button are present
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the SQL screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#config-db-sql-tabs', state='visible')

        # .. verify the tab strip offers all three databases ..
        tab_buttons = page.query_selector_all('#config-db-sql-tabs .dashboard-tab')

        tab_names = [] # type: list

        for tab_button in tab_buttons:
            tab_name = tab_button.get_attribute('data-tab')
            tab_names.append(tab_name)

        assert tab_names == ['audit-log', 'analytics', 'pubsub'], f'Unexpected databases: {tab_names}'

        # .. by default the audit log database is shown, backed by SQLite ..
        active_tab = page.get_attribute('#config-db-sql-tabs .dashboard-tab-active', 'data-tab')
        assert active_tab == 'audit-log', f'Expected "audit-log", got: {active_tab}'

        type_value = page.input_value('#id_audit-log_type')
        assert type_value == 'sqlite', f'Expected "sqlite", got: {type_value}'

        # .. the SQLite file path points at the audit database file ..
        name_value = page.input_value('#id_audit-log_name')
        assert name_value.endswith('audit.db'), f'Expected a path ending in audit.db, got: {name_value}'

        # .. and both actions are present.
        test_link_text = page.inner_text('.config-db-sql-test-link')
        assert test_link_text.strip() == 'Test connection', f'Expected "Test connection", got: {test_link_text}'

        save_button_value = page.input_value('.config-db-sql-save-group input[type="submit"]')
        assert save_button_value == 'Save', f'Expected "Save", got: {save_button_value}'

# ################################################################################################################################

    def test_02_test_connection(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Runs a live connection test against the default SQLite database
        and verifies the OK result appears in the green status message.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the SQL screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#config-db-sql-tabs', state='visible')

        # .. run the connection test ..
        page.click('.config-db-sql-test-link')

        # .. and verify the OK result with the response time appears.
        status = cast_('any_', page.wait_for_selector('#config-db-sql-status.status-message-success', state='visible', timeout=10000))
        status_text = status.inner_text()
        assert 'Connection OK' in status_text, f'Expected "Connection OK" in status, got: {status_text}'

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
        _ = page.wait_for_selector('#config-db-sql-tabs', state='visible')

        # .. fill in the name and description ..
        page.fill('#id_audit-log_display_name', display_name)
        page.fill('#id_audit-log_description', description)

        # .. save the form ..
        page.click('.config-db-sql-save-group input[type="submit"]')

        # .. wait for the save confirmation ..
        status = cast_('any_', page.wait_for_selector('#config-db-sql-status.status-message-success', state='visible', timeout=10000))
        status_text = status.inner_text()
        assert 'OK, saved' in status_text, f'Expected "OK, saved" in status, got: {status_text}'

        # .. reload the page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#config-db-sql-tabs', state='visible')

        # .. and verify the values came back from the server.
        name_value = page.input_value('#id_audit-log_display_name')
        assert name_value == display_name, f'Expected "{display_name}", got: "{name_value}"'

        description_value = page.input_value('#id_audit-log_description')
        assert description_value == description, f'Expected "{description}", got: "{description_value}"'

# ################################################################################################################################

    def test_04_switch_database(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens the analytics tab and verifies its own panel shows -
        the analytics database has its own SQLite file and no name of its own yet.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the SQL screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#config-db-sql-tabs', state='visible')

        # .. switch to the analytics database ..
        page.click('#config-db-sql-tabs .dashboard-tab[data-tab="analytics"]')

        # .. its SQLite file path points at the analytics database file ..
        name_value = page.input_value('#id_analytics_name')
        assert name_value.endswith('analytics.db'), f'Expected a path ending in analytics.db, got: {name_value}'

        # .. and the display name saved for the audit log database does not carry over into it.
        display_name_value = page.input_value('#id_analytics_display_name')
        assert display_name_value == '', f'Expected an empty name, got: "{display_name_value}"'

# ################################################################################################################################
# ################################################################################################################################
