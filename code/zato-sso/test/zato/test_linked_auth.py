# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from unittest import main

# Zato
from base import BaseTest

# ################################################################################################################################
# ################################################################################################################################

class LinkedAuthTestCase(BaseTest):

    def test_create(self):

        response = self.get('/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
        })

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service.internal.sso import BaseRESTService, BaseSIO

# ################################################################################################################################
# ################################################################################################################################

class LinkedAuth(BaseRESTService):

    name = 'sso.user.linked-auth'

    class SimpleIO(BaseSIO):
        input_required = 'ust', 'current_app'
        output_required = 'status',

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        self.logger.warn('GET %s', ctx.input)

        user = self.sso.user.get_current_user(self.cid, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

        print(111, user.to_dict())

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):
        self.logger.warn('POST %s', ctx)

# ################################################################################################################################
# ################################################################################################################################
'''
