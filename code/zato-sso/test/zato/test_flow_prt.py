# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from base import BaseTest

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
        self.patch('/zato/sso/flow/prt', {
            'token': '5spsy3fgv49swaw876gh34d5fk',
        })

        # .. change the password ..
        # response = self.delete('/zato/sso/flow/prt', {
        #    'credential': 'admin3',
        # })

        # .. confirm that the new password can be used for logging in.

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
