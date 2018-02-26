# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from traceback import format_exc

# Zato
from zato.server.service.internal.sso import BaseService, BaseSIO
from zato.sso import status_code

# ################################################################################################################################

class Login(BaseService):
    """ Logs an SSO user in.
    """
    class SimpleIO(BaseSIO):
        input_required = ('username', 'password', 'current_app')
        input_optional = ('new_password', 'remote_addr', 'user_agent')
        output_required = ('status',)
        output_optional = BaseSIO.output_optional + ('ust',)

# ################################################################################################################################

    def _handle_sso(self, ctx):

        input = ctx.input
        has_remote_addr = input.get('remote_addr')
        has_user_agent = input.get('user_agent')

        input.has_remote_addr = has_remote_addr
        input.has_user_agent = has_user_agent

        input.remote_addr = input.remote_addr if has_remote_addr else self.wsgi_environ['zato.http.remote_addr'].decode('utf8')
        input.user_agent = input.user_agent if has_user_agent else self.wsgi_environ['HTTP_USER_AGENT']

        out = self._call_sso_api(self.sso.user.login, 'SSO user `{username}` cannot log in to `{current_app}`', **ctx.input)
        if out:
            self.response.payload.ust = out.ust

# ################################################################################################################################

class Logout(BaseService):
    """ Logs a user out of SSO.
    """
    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app')
        output_required = ('status',)

    def _handle_sso(self, ctx):

        # Note that "ok" is always returned no matter the outcome - this is to thwart any attempts
        # to learn which USTs are/were valid or not.
        try:
            self.sso.user.logout(ctx.input.ust, ctx.input.current_app, ctx.input.remote_addr)
        except Exception:
            self.logger.warn('CID: `%s`, e:`%s`', self.cid, format_exc())
        finally:
            self.response.payload.status = status_code.ok

# ################################################################################################################################
