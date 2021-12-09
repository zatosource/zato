# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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

# ################################################################################################################################

    def test_login_logout(self):

        self.run_in_background = False

        # Log to web admin ..
        self.login()

        # .. confirm that we are in ..
        self.assertEquals(self.client.title, 'Hello - Zato')
        self.assertEquals(self.client.current_url, self.config.web_admin_address + '/zato/')

        # .. now, log us out ..
        logout = self.client.find_element_by_partial_link_text('Log out') # type: WebElement
        logout.click()

        # .. confirm that we are truly logged out ..
        self._confirm_not_logged_in()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
