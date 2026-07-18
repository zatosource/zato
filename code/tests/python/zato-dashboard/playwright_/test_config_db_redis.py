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

_Page_Url_Pattern = '/zato/config-db/redis/'

_Test_Name_Prefix = 'test.config.db.redis.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestConfigDBRedis:
    """ Tests for the Config DB Redis screen.
    """

    def test_01_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the Redis screen and verifies its structure:
        - the form shows the localhost defaults
        - the SSL fields are present
        - the Test and Save buttons are present
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the Redis screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_host', state='visible')

        # .. by default the connection points at a plain localhost server ..
        host_value = page.input_value('#id_host')
        assert host_value == 'localhost', f'Expected "localhost", got: {host_value}'

        port_value = page.input_value('#id_port')
        assert port_value == '6379', f'Expected "6379", got: {port_value}'

        db_value = page.input_value('#id_db')
        assert db_value == '0', f'Expected "0", got: {db_value}'

        ssl_checked = page.is_checked('#id_ssl')
        assert ssl_checked is False, 'Expected SSL to be off by default'

        ssl_verify_checked = page.is_checked('#id_ssl_verify')
        assert ssl_verify_checked is True, 'Expected SSL verification to be on by default'

        # .. the certificate fields are present ..
        _ = page.wait_for_selector('#id_ssl_ca_file', state='visible')
        _ = page.wait_for_selector('#id_ssl_cert_file', state='visible')
        _ = page.wait_for_selector('#id_ssl_key_file', state='visible')

        # .. and both buttons are present.
        test_button_text = page.inner_text('#check-button')
        assert test_button_text.strip() == 'Test', f'Expected "Test", got: {test_button_text}'

        save_button_text = page.inner_text('#update-button')
        assert save_button_text.strip() == 'Save', f'Expected "Save", got: {save_button_text}'

# ################################################################################################################################

    def test_02_test_connection(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Runs a live connection test against the Redis server this test session started
        and verifies the OK result appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The dedicated Redis this test session runs is always available
        redis_port = zato_dashboard['queue_bridge_redis_port']

        # Navigate to the Redis screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_host', state='visible')

        # .. point the form at the session's Redis ..
        page.fill('#id_host', '127.0.0.1')
        page.fill('#id_port', str(redis_port))

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
        """ Saves the connection details, verifies that they all come back after
        the page is reloaded, and restores the original values afterwards -
        the save reconfigures the server's actual Redis connection.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        redis_port = zato_dashboard['queue_bridge_redis_port']

        display_name = _Test_Name_Prefix + 'connection'
        description = 'Description of ' + display_name

        # Navigate to the Redis screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_host', state='visible')

        # .. remember the original values so they can be restored at the end ..
        original_values = {} # type: anydict

        for field in ('display_name', 'description', 'host', 'port', 'db'):
            original_values[field] = page.input_value(f'#id_{field}')

        # .. fill in the connection details ..
        page.fill('#id_display_name', display_name)
        page.fill('#id_description', description)
        page.fill('#id_host', '127.0.0.1')
        page.fill('#id_port', str(redis_port))

        # .. save the form ..
        page.click('#update-button')

        # .. wait for the save confirmation ..
        _ = page.wait_for_selector('#progress-configure .progress-icon.completed', state='visible', timeout=10000)

        progress_text = page.inner_text('#progress-configure .progress-text')
        assert 'Saved' in progress_text, f'Expected "Saved" in progress text, got: {progress_text}'

        # .. reload the page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_host', state='visible')

        # .. verify the values came back from the server ..
        name_value = page.input_value('#id_display_name')
        assert name_value == display_name, f'Expected "{display_name}", got: "{name_value}"'

        description_value = page.input_value('#id_description')
        assert description_value == description, f'Expected "{description}", got: "{description_value}"'

        host_value = page.input_value('#id_host')
        assert host_value == '127.0.0.1', f'Expected "127.0.0.1", got: "{host_value}"'

        port_value = page.input_value('#id_port')
        assert port_value == str(redis_port), f'Expected "{redis_port}", got: "{port_value}"'

        # .. and restore the original connection so later tests see the environment they expect.
        for field, value in original_values.items():
            page.fill(f'#id_{field}', value)

        page.click('#update-button')
        _ = page.wait_for_selector('#progress-configure .progress-icon.completed', state='visible', timeout=10000)

# ################################################################################################################################
# ################################################################################################################################
