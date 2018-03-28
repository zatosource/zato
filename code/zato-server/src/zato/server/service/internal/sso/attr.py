# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import AsIs, Bool, Opaque
from zato.server.service.internal.sso import BaseRESTService, BaseSIO

# ################################################################################################################################

_invalid = object()

# ################################################################################################################################

class _Attr(BaseRESTService):
    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app')
        input_optional = (AsIs('user_id'), Opaque('data'), Bool('decrypt'), Bool('serialize_dt'))
        output_optional = BaseSIO.output_optional + (Bool('found'), 'result', 'name', 'value', 'creation_time',
            'last_modified', 'expiration_time', 'is_encrypted')

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        """ Returns data of and metadata about an attribute.
        """
        user = self.sso.user.get_user_by_id(self.cid, ctx.input.user_id, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)

        func = 'get_many' if isinstance(ctx.input.data, list) else 'get'
        func = getattr(user.attr, func)
        decrypt = True if ctx.input.decrypt is _invalid else ctx.input.decrypt

        result = func(ctx.input.data, decrypt=decrypt, serialize_dt=True)
        if result:
            if isinstance(result, list):
                self.response.payload.result = result
            else:
                result = result.to_dict()
                self.response.payload.found = True
                self.response.payload.name = result['name']
                self.response.payload.value = result['value']
                self.response.payload.creation_time = result['creation_time']
                self.response.payload.last_modified = result['last_modified']
                self.response.payload.expiration_time = result['expiration_time']
                self.response.payload.is_encrypted = result['is_encrypted']
        else:
            self.response.payload.found = False

# ################################################################################################################################

class _AttrExists(BaseRESTService):
    pass

# ################################################################################################################################

class _AttrNames(BaseRESTService):
    pass

# ################################################################################################################################
