# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import any_, cast_

# Zato - test library
from lib.config_db_screen import redis_field_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/redis/'

_Test_Name_Prefix = 'test.redis.' + CryptoManager.generate_hex_string(32) + '.'

_Save_Button = '.redis-save-group input[type="submit"]'
_Test_Link   = '.redis-test-link'

# ################################################################################################################################
# ################################################################################################################################

class TestRedis:
    """ Tests for the Redis screen.
    """

    def test_01_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the Redis screen and verifies its structure:
        - the form shows the localhost defaults
        - the SSL fields are present
        - the Test connection link and the Save button are present
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the Redis screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#redis-host', state='visible')

        # .. by default the connection points at a plain localhost server ..
        host_value = page.input_value('#redis-host')
        assert host_value == 'localhost', f'Expected "localhost", got: {host_value}'

        port_value = page.input_value('#redis-port')
        assert port_value == '6379', f'Expected "6379", got: {port_value}'

        db_value = page.input_value('#redis-db')
        assert db_value == '0', f'Expected "0", got: {db_value}'

        ssl_checked = page.is_checked('#redis-ssl')
        assert ssl_checked is False, 'Expected SSL to be off by default'

        ssl_verify_checked = page.is_checked('#redis-ssl-verify')
        assert ssl_verify_checked is True, 'Expected SSL verification to be on by default'

        # .. the certificate fields are present ..
        _ = page.wait_for_selector('#redis-ssl-ca-file', state='visible')
        _ = page.wait_for_selector('#redis-ssl-cert-file', state='visible')
        _ = page.wait_for_selector('#redis-ssl-key-file', state='visible')

        # .. and both the test link and the Save button are present.
        test_link_text = page.inner_text(_Test_Link)
        assert test_link_text.strip() == 'Test connection', f'Expected "Test connection", got: {test_link_text}'

        save_button_value = page.input_value(_Save_Button)
        assert save_button_value == 'Save', f'Expected "Save", got: {save_button_value}'

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
        _ = page.wait_for_selector('#redis-host', state='visible')

        # .. point the form at the session's Redis ..
        page.fill('#redis-host', '127.0.0.1')
        page.fill('#redis-port', str(redis_port))

        # .. run the connection test ..
        page.click(_Test_Link)

        # .. and verify the OK result with the response time appears in the tooltip.
        tooltip = cast_('any_', page.wait_for_selector('.tippy-content', state='visible', timeout=10000))
        tooltip_text = tooltip.inner_text()
        assert 'Connection OK' in tooltip_text, f'Expected "Connection OK" in tooltip, got: {tooltip_text}'

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
        _ = page.wait_for_selector('#redis-host', state='visible')

        # .. remember the original values so they can be restored at the end ..
        original_values = {} # type: anydict

        for field in ('display_name', 'description', 'host', 'port', 'db'):
            original_values[field] = page.input_value(redis_field_selector(field))

        # .. fill in the connection details ..
        page.fill('#redis-display-name', display_name)
        page.fill('#redis-description', description)
        page.fill('#redis-host', '127.0.0.1')
        page.fill('#redis-port', str(redis_port))

        # .. save the form ..
        page.click(_Save_Button)

        # .. wait for the save confirmation ..
        status = cast_('any_', page.wait_for_selector('#redis-status.status-message-success', state='visible', timeout=10000))
        status_text = status.inner_text()
        assert 'OK, saved' in status_text, f'Expected "OK, saved" in status, got: {status_text}'

        # .. reload the page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#redis-host', state='visible')

        # .. verify the values came back from the server ..
        name_value = page.input_value('#redis-display-name')
        assert name_value == display_name, f'Expected "{display_name}", got: "{name_value}"'

        description_value = page.input_value('#redis-description')
        assert description_value == description, f'Expected "{description}", got: "{description_value}"'

        host_value = page.input_value('#redis-host')
        assert host_value == '127.0.0.1', f'Expected "127.0.0.1", got: "{host_value}"'

        port_value = page.input_value('#redis-port')
        assert port_value == str(redis_port), f'Expected "{redis_port}", got: "{port_value}"'

        # .. and restore the original connection so later tests see the environment they expect.
        for field, value in original_values.items():
            page.fill(redis_field_selector(field), value)

        page.click(_Save_Button)
        _ = page.wait_for_selector('#redis-status.status-message-success', state='visible', timeout=10000)

# ################################################################################################################################
# ################################################################################################################################
