# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from unittest import main

# Zato
from base import BaseTest, Config
from zato.sso import const, status_code

# ################################################################################################################################
# ################################################################################################################################

class SessionVerifyTestCase(BaseTest):

    def test_verify_self(self):

        response = self.post('/zato/sso/user/session', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': self.ctx.super_user_ust,
            'current_app': Config.current_app,
        })

        self.assertEquals(response.status, status_code.ok)
        self.assertTrue(response.is_valid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
