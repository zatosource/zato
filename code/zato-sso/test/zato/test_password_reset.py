# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from base import BaseTest, Config
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

class FlowPRTTestCase(BaseTest):

# ################################################################################################################################

    def manual_test_user_reset_password(self):

        # This needs to be filled in manually
        token = '5rgfkm9c7z9xh8q1t7qhxw62e3'
        user_id = None

        # Generated in each test
        password = CryptoManager.generate_password(to_str=True)

        # Request a new PRT ..
        response = self.post('/zato/sso/password/reset', {
            'credential': Config.super_user_name,
        })

        # .. access the PRT received ..
        response = self.patch('/zato/sso/password/reset', {
            'token': token,
        })

        # .. read the reset key received from the .patch call ..
        reset_key = response.reset_key

        # .. change the password now ..
        response = self.delete('/zato/sso/password/reset', {
            'token': token,
            'reset_key': reset_key,
            'password': password
        })

        # .. confirm the status ..
        self.assertEqual(response.status, 'ok')

        self.patch('/zato/sso/user/password', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
            'old_password': password,
            'new_password': Config.super_user_password
        })

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
