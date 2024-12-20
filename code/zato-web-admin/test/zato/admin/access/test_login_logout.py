# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from .base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from selenium.webdriver.remote.webelement import WebElement

# ################################################################################################################################
# ################################################################################################################################

class LoginLogoutTestCase(BaseTestCase):

    needs_auto_login = False
    run_in_background = True

# ################################################################################################################################

    def test_login_logout(self):

        # stdlib
        import os

        if not os.environ.get('ZATO_TEST_DASHBOARD'):
            return

        # Default address to visit
        address = self.config.web_admin_address + '/zato/'

        # Log to web admin ..
        self.login()

        # .. confirm that we are in ..
        self.assertEqual(self.client.title, 'Hello - Zato')
        self.assertEqual(self.client.current_url, address)

        # .. now, log us out ..
        logout:'WebElement' = self.client.find_element_by_partial_link_text('Log out')
        logout.click()

        # .. try to access an address ..
        self.client.get(address)

        # .. confirm that we are truly logged out ..
        self._confirm_not_logged_in()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
