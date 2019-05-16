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
from zato.common import SEC_DEF_TYPE

# ################################################################################################################################
# ################################################################################################################################

class LinkedAuthTestCase(BaseTest):

    def test_create(self):

        self.get('/zato/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
        })

        self.post('/zato/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'auth_type': SEC_DEF_TYPE.BASIC_AUTH,
            'auth_id': 1,
            'is_active': True,
        })


        self.delete('/zato/sso/user/linked', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'auth_type': SEC_DEF_TYPE.BASIC_AUTH,
            'auth_id': 1,
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
from zato.server.service import Opaque
from zato.server.service.internal.sso import BaseRESTService, BaseSIO

# ################################################################################################################################

# A marker that indicates a value that will never exist
_invalid = '_invalid.{}'.format(uuid4().hex)

# ################################################################################################################################
# ################################################################################################################################

class LinkedAuth(BaseRESTService):

    name = 'sso.user.linked-auth'

    class SimpleIO(BaseSIO):
        input_required = 'current_app', 'ust'
        input_optional = Opaque('user_id'), 'auth_type', 'auth_id', 'is_active',
        output_optional = BaseSIO.output_optional + ('result',)
        default_value = _invalid
        skip_empty_keys = True

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        user_id = ctx.input.user_id
        user_id = user_id if user_id != _invalid else None

        out = []
        result = self.sso.user.get_linked_auth_list(self.cid, ctx.input.ust, user_id, ctx.input.current_app, ctx.remote_addr)

        for item in result:

            item = item._asdict()
            item['creation_time'] = item['creation_time'].isoformat()

            for name in 'auth_principal', 'auth_source':
                if item[name] == 'reserved':
                    del item[name]

            item.pop('is_internal', None)
            item.pop('auth_principal', None)
            item.pop('has_ext_principal', None)

            out.append(item)

        self.response.payload.result = out

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):
        self.sso.user.create_linked_auth(self.cid, ctx.input.ust, ctx.input.user_id, ctx.input.auth_type,
            ctx.input.auth_id, ctx.input.is_active, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################

    def _handle_sso_DELETE(self, ctx):
        self.sso.user.delete_linked_auth(self.cid, ctx.input.ust, ctx.input.user_id, ctx.input.auth_type,
            ctx.input.auth_id, ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################
# ################################################################################################################################
'''
