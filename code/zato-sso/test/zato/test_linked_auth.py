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

basic_auth_id = 14
jwt_auth_id = 15

# ################################################################################################################################
# ################################################################################################################################

class LinkedAuthTestCase(BaseTest):

    def test_create(self):

        self.get('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id
        })

        '''
        self.patch('/zato/sso/user/totp', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id
        })
        '''

        '''
        self.get('/zzz', {}, expect_ok=False, auth=('zz', 'zz'))


        self.get('/zato/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
            'user_id': 'zusr20d6006gc18n1t0n0qwbs3wrk2'
        })


        self.post('/zato/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'auth_type': SEC_DEF_TYPE.JWT,
            'auth_id': jwt_auth_id,
            'is_active': True,
        })

        self.delete('/zato/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'auth_type': SEC_DEF_TYPE.BASIC_AUTH,
            'auth_id': basic_auth_id,
        })
        '''

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
