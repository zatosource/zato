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

# stdlib
from contextlib import closing
from uuid import uuid4

# Zato
from zato.server.service import DateTime, ListOfDicts
from zato.server.service.internal.sso import BaseRESTService, BaseSIO

# ################################################################################################################################

# A marker that indicates a value that will never exist
_invalid = '_invalid.{}'.format(uuid4().hex)

# ################################################################################################################################
# ################################################################################################################################

class LinkedAuth(BaseRESTService):

    name = 'sso.user.linked-auth'

    class SimpleIO(BaseSIO):
        input_required = 'current_app',
        input_optional = 'ust', 'user_id'
        output_optional = BaseSIO.output_optional + ('result',)
        default_value = _invalid
        skip_empty_keys = True

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        self.response.payload.result = self.sso.user.get_linked_auth_list(self.cid, ctx.input.ust,
            ctx.input.user_id, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):
        self.logger.warn('POST %s', ctx)

# ################################################################################################################################
# ################################################################################################################################
'''
