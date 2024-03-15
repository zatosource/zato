# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# Zato
from base import BaseTest

# ################################################################################################################################
# ################################################################################################################################

class UserAttrGetTestCase(BaseTest):

# ################################################################################################################################

    def test_get(self):

        name = self._get_random_data()
        value = self._get_random_data()
        expiration = 900

        self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
            'value': value,
            'expiration': expiration
        })

        response = self.get('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
        })

        self.assertTrue(response.found)
        self.assertEqual(response.name, name)
        self.assertEqual(response.value, value)

        # Will raise an exception if date parsing fails
        parse_datetime(response.creation_time)
        parse_datetime(response.last_modified)
        parse_datetime(response.expiration_time)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
