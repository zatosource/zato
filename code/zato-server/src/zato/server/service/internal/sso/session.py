# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from uuid import uuid4

# Zato
from zato.common.api import GENERIC
from zato.common.json_internal import loads
from zato.server.service import DateTime, ListOfDicts
from zato.server.service.internal.sso import BaseRESTService, BaseSIO
from zato.sso import status_code, ValidationError

# ################################################################################################################################

# A marker that indicates a value that will never exist
_invalid = '_invalid.{}'.format(uuid4().hex)

# ################################################################################################################################

class BaseGetSIO(BaseSIO):
    input_required = 'current_app',
    input_optional = 'target_ust', 'current_ust', 'ust'
    output_optional = BaseSIO.output_optional + (DateTime('creation_time'), DateTime('expiration_time'), 'remote_addr',
        'user_agent', 'is_valid', ListOfDicts('session_state_change_list'), 'result')
    default_value = _invalid
    skip_empty_keys = True

# ################################################################################################################################

class SessionList(BaseRESTService):
    """ Returns a list of sessions for current user or another one.
    """
    SimpleIO = BaseGetSIO

    def _handle_sso_GET(self, ctx):

        # Local aliases
        default_value = self.SimpleIO.default_value

        # We either have a single UST on input or both target and current ones, but not both kinds
        if ctx.input.ust:
            if ctx.input.current_ust != default_value or ctx.input.target_ust != default_value:
                raise ValidationError(status_code.common.invalid_input)

        else:

            # Without ctx.input.ust we must require both of the other elements
            if not (ctx.input.current_ust != default_value and ctx.input.target_ust != default_value):
                raise ValidationError(status_code.common.invalid_input)

        result = self.sso.user.session.get_list(
            self.cid, ctx.input.ust, ctx.input.target_ust, ctx.input.current_ust, ctx.input.current_app, ctx.remote_addr)

        for item in result: # type: dict
            item['creation_time'] = item['creation_time'].isoformat()
            item['expiration_time'] = item['expiration_time'].isoformat()

            opaque = item.pop(GENERIC.ATTR_NAME, None)
            if opaque:
                opaque = loads(opaque) # type: dict
                item['session_state_change_list'] = opaque.get('session_state_change_list', [])

        self.response.payload.result = result

# ################################################################################################################################

class Session(BaseRESTService):
    """ Session manipulation through REST.
    """
    SimpleIO = BaseGetSIO

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        """ Returns details of a particular session.
        """
        # Make sure target UST actually was given on input
        if ctx.input.target_ust == _invalid:
            raise ValidationError(status_code.session.no_such_session)

        # Get result
        result = self.sso.user.session.get(self.cid, ctx.input.target_ust, ctx.input.current_ust,
            ctx.input.current_app, ctx.remote_addr, self.wsgi_environ.get('HTTP_USER_AGENT'))

        # Return output
        self.response.payload = result.to_dict()

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):
        """ Verifies whether an input session exists or not.
        """
        # Make sure target UST actually was given on input
        if ctx.input.target_ust == _invalid:
            raise ValidationError(status_code.session.no_such_session)

        self.response.payload.is_valid = self.sso.user.session.verify(self.cid, ctx.input.target_ust, ctx.input.current_ust,
            ctx.input.current_app, ctx.remote_addr, self.wsgi_environ.get('HTTP_USER_AGENT'))

# ################################################################################################################################

    def _handle_sso_PATCH(self, ctx):
        """ Renews a session given on input.
        """
        self.response.payload.expiration_time = self.sso.user.session.renew(self.cid, ctx.input.ust,
            ctx.input.current_app, ctx.remote_addr, self.wsgi_environ.get('HTTP_USER_AGENT')).isoformat()

# ################################################################################################################################
