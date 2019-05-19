# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main

# Zato
from base import BaseTest

# ################################################################################################################################
# ################################################################################################################################

class LinkedAuthTestCase(BaseTest):

    def test_create(self):

        self.get('/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
        })

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
