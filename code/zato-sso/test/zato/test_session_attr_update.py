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

# ################################################################################################################################
# ################################################################################################################################

class SessionAttrUpdateTestCase(BaseTest):

# ################################################################################################################################

    def test_update(self):

        name = self._get_random_data()
        value = self._get_random_data()
        expiration = 900

        new_value = self._get_random_data()
        new_expiration = 123

        self.post('/zato/sso/session/attr', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
            'value': value,
            'expiration': expiration
        })

        self.patch('/zato/sso/session/attr', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
            'value': new_value,
            'expiration': new_expiration
        })

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
