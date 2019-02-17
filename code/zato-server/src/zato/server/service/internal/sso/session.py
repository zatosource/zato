# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from uuid import uuid4

# Zato
from zato.server.service.internal.sso import BaseRESTService, BaseSIO
from zato.sso import status_code, ValidationError

# ################################################################################################################################

# A marker that indicates a value that will never exist
_invalid = '_invalid.{}'.format(uuid4().hex)

# ################################################################################################################################

class Session(BaseRESTService):
    """ Session manipulation through REST.
    """
    class SimpleIO(BaseSIO):
        input_required = ('current_ust', 'current_app')
        input_optional = ('target_ust',)
        output_optional = BaseSIO.output_optional + ('creation_time', 'expiration_time', 'remote_addr', 'user_agent',
            'is_valid')
        default_value = _invalid

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        """ Returns details of a particular session.
        """
        # Make sure target UST actually was given on input
        if ctx.input.target_ust == _invalid:
            raise ValidationError(status_code.session.no_such_session)

        # Get result
        result = self.sso.user.session.get(self.cid, ctx.input.target_ust, ctx.input.current_ust,
            ctx.input.current_app, ctx.remote_addr)

        # Serialize datetime objects to string
        result['creation_time'] = result['creation_time'].isoformat()
        result['expiration_time'] = result['expiration_time'].isoformat()

        # Return output
        self.response.payload = result

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):
        """ Verifies whether an input session exists or not.
        """
        # Make sure target UST actually was given on input
        if ctx.input.target_ust == _invalid:
            raise ValidationError(status_code.session.no_such_session)

        self.response.payload.is_valid = self.sso.user.session.verify(self.cid, ctx.input.target_ust, ctx.input.current_ust,
            ctx.input.current_app, ctx.remote_addr)

# ################################################################################################################################

    def _handle_sso_PATCH(self, ctx):
        """ Renews a session given on input.
        """
        self.response.payload.expiration_time = self.sso.user.session.renew(self.cid, ctx.input.current_ust,
            ctx.input.current_app, ctx.remote_addr).isoformat()

# ################################################################################################################################
