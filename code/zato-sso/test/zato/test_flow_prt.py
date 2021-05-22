# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from base import BaseTest
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

class FlowPRTTestCase(BaseTest):

# ################################################################################################################################

    def test_user_reset_password(self):

        # This needs to be filled in manually
        token = '9z0hv4qs59sqt1rskna3k3t9e'

        # Generated in each test
        password = CryptoManager.generate_password(to_str=True)

        # Request a new PRT ..
        response = self.post('/zato/sso/flow/prt', {
            'credential': 'admin3',
        })

        # .. access the PRT received ..
        response = self.patch('/zato/sso/flow/prt', {
            'token': token,
        })

        # .. read the reset key received from the .patch call ..
        reset_key = response.reset_key

        # .. change the password now ..
        response = self.delete('/zato/sso/flow/prt', {
            'token': token,
            'reset_key': reset_key,
            'password': password
        })

        # .. confirm the status ..
        self.assertEqual(response.status, 'ok')

        # .. finally, confirm that the new password can be used for logging in.

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
