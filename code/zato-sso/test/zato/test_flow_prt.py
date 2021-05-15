# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from base import BaseTest
from zato.sso import status_code

# ################################################################################################################################
# ################################################################################################################################

class FlowPRTTestCase(BaseTest):

# ################################################################################################################################

    def test_user_create_token(self):

        # Request a new PRT ..
        response = self.post('/zato/sso/flow/prt', {
            'credential': 'admin3',
        })

        # .. access the PRT received ..
        response = self.patch('/zato/sso/flow/prt', {
            'token': '7xatacm95c89vs6xb3mgpbxsrj',
        })

        # .. change the password ..
        #response = self.delete('/zato/sso/flow/prt', {
        #    'credential': 'admin3',
        #})

        # .. confirm that the new password can be used for logging in.

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
