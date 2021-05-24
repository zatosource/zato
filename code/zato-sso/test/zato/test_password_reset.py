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
from zato.common.odb.model import SSOPasswordReset, SSOUser

# ################################################################################################################################
# ################################################################################################################################

class FlowPRTTestCase(BaseTest):

# ################################################################################################################################

    def get_random_prt_info(self, session):
        return session.query(
            SSOUser.user_id,
            SSOPasswordReset.token,
            ).\
            filter(SSOUser.user_id == SSOPasswordReset.user_id).\
            filter(SSOPasswordReset.has_been_accessed.is_(False)).\
            limit(1).\
            one()

# ################################################################################################################################

    def test_user_reset_password(self):

        # Generated in each test
        password = CryptoManager.generate_password(to_str=True)

        # Request a new PRT ..
        self.post('/zato/sso/password/reset', {
            'credential': Config.super_user_name,
        })

        # .. above, we never receive the PRT so we know there will be at least one PRT
        # when we look it up along with user_id in the ODB ..
        prt_info = self.get_random_prt_info(self.odb_session)

        # .. make it easier to access the information received ..
        prt_info = prt_info._asdict() # type: dict

        # .. extract the details ..
        user_id = prt_info['user_id']
        token = prt_info['token']

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
