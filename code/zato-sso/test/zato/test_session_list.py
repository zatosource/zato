# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main

# Zato
from base import BaseTest
from zato.sso import status_code

# ################################################################################################################################
# ################################################################################################################################

class SessionGetListTestCase(BaseTest):

# ################################################################################################################################

    def test_get_list_self_super_user(self):

        self.post('/zato/sso/user/session', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': self.ctx.super_user_ust,
        })

        self.patch('/zato/sso/user/session', {
            'ust': self.ctx.super_user_ust,
        })

        response = self.get('/zato/sso/user/session/list', {
            'ust': self.ctx.super_user_ust,
        })

        self.assertEqual(response.status, status_code.ok)
        self.assertTrue(len(response.result) > 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
