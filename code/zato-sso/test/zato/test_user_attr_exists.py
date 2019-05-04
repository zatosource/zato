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

        response = self.get('/zato/sso/user/attr/exists', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name1,
        })

        self.assertTrue(response.result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
