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

class LoginLogoutTestCase(BaseTestCase):

    needs_auto_login = False

# ################################################################################################################################

    def test_login(self):

        self.run_in_background = False

        self.login()

        self.assertEquals(self.client.title, 'Log on - Zato')
        self.assertEquals(self.client.current_url, self.config.web_admin_address + '/accounts/login/?next=/zato/')

        zzz ;sldfksdo 'u2340-r'p3r8i  :a;

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
