# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service.internal.sso import BaseService, BaseSIO
from zato.sso.api import status_code, ValidationError

# ################################################################################################################################

class Login(BaseService):
    """ Logs an SSO user in.
    """
    class SimpleIO(BaseSIO):
        input_required = ('username', 'password', 'current_app')
        input_optional = ('new_password', 'remote_addr', 'user_agent')
        output_required = ('status',)
        output_optional = BaseSIO.output_optional + ('ust',)

    def _handle_sso(self, ctx):

        input = ctx.input
        current_app = input.current_app
        has_remote_addr = input.get('remote_addr')
        has_user_agent = input.get('user_agent')

        if has_remote_addr or has_user_agent:
            if current_app not in self.server.sso_config.apps.login_metadata_allowed:
                self._set_response_error(status_code.metadata.not_allowed)
                return

        input.remote_addr = input.remote_addr if has_remote_addr else self.wsgi_environ['zato.http.remote_addr'].decode('utf8')
        input.user_agent = input.user_agent if has_user_agent else self.wsgi_environ['HTTP_USER_AGENT']

        try:
            out = self.sso.user.login(**input)
        except ValidationError as e:
            self.logger.warn('SSO user `%s` cannot log in to `%s`, e:`%s`, cid:`%s`',
                input.username, input.current_app, e, self.cid)
            if e.return_status:
                self._set_response_error(e.sub_status, e.status)
            else:
                self._set_response_error()
        else:
            self.response.payload.ust = out.ust
            self._set_response_ok()

# ################################################################################################################################
