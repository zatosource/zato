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

class UserAttrExistsTestCase(BaseTest):

# ################################################################################################################################

    def test_exists(self):

        name1 = self._get_random_data()
        value1 = self._get_random_data()

        name2 = self._get_random_data()
        value2 = self._get_random_data()

        data = [
            {'name':name1, 'value':value1},
            {'name':name2, 'value':value2},
        ]

        self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'data': data
        })

        response = self.get('/zato/sso/user/attr/names', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
        })

        self.assertIn(name1, response.result)
        self.assertIn(name2, response.result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
