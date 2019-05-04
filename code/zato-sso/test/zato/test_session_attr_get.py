# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from unittest import main

# dateutil
from dateutil.parser import parse as dt_parse

# ipaddress
from ipaddress import ip_address

# Zato
from base import BaseTest, Config, logger
from zato.common.ipaddress_ import ip_network
from zato.sso import const, status_code

# ################################################################################################################################
# ################################################################################################################################

class SessionAttrGetTestCase(BaseTest):

# ################################################################################################################################

    def test_get(self):

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

        response = self.get('/zato/sso/session/attr', {
            'current_ust': self.ctx.super_user_ust,
            'target_ust': self.ctx.super_user_ust,
            'name': name,
        })

        self.assertTrue(response.found)
        self.assertEqual(response.name, name)
        self.assertEqual(response.value, value)

        # Will raise an exception if date parsing fails
        dt_parse(response.creation_time)
        dt_parse(response.last_modified)
        dt_parse(response.expiration_time)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
