# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main

# Zato
from base import BaseTest
from zato.common import SEC_DEF_TYPE

# For Pyflakes
SEC_DEF_TYPE = SEC_DEF_TYPE

# ################################################################################################################################

basic_auth_user_name = 'pubapi'

# ################################################################################################################################
# ################################################################################################################################

class LinkedAuthTestCase(BaseTest):

    def test_create(self):

        self.post('/zato/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'auth_type': SEC_DEF_TYPE.BASIC_AUTH,
            'auth_username': basic_auth_user_name,
            'is_active': True,
        })

        self.get('/zato/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id
        })

        self.delete('/zato/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'auth_type': SEC_DEF_TYPE.BASIC_AUTH,
            'auth_username': basic_auth_user_name,
        })

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
