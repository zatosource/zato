# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.common.api import RATE_LIMIT, SEC_DEF_TYPE

# ################################################################################################################################

# Type checking
if 0:
    from bunch import Bunch
    from zato.server.base.parallel import ParallelServer

    Bunch = Bunch
    ParallelServer = ParallelServer

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

# Definitions of these security types may be linked to SSO users and their rate limiting definitions
_sec_def_sso_rate_limit = SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.JWT

# ################################################################################################################################
# ################################################################################################################################

class SSOTool:
    """ Server-wide utilities related to SSO.
    """
    def __init__(self, server):
        # type: (ParallelServer)
        self.server = server

    def on_external_auth(self, sec_type, sec_def_id, sec_def_username, cid, wsgi_environ, ext_session_id=None,
        totp_code=None, _rate_limit_type_sso_user=RATE_LIMIT.OBJECT_TYPE.SSO_USER, _basic_auth=SEC_DEF_TYPE.BASIC_AUTH):
        # type: (str, int, str, str, dict, object, object)

        if sec_type in _sec_def_sso_rate_limit:

            # Do we have an SSO user related to this sec_def?
            auth_id_link_map = self.server.sso_api.user.auth_id_link_map['zato.{}'.format(sec_type)] # type: dict
            sso_user_id = auth_id_link_map.get(sec_def_id)

            if sso_user_id:

                # At this point we have an SSO user and we know that credentials
                # from the request were valid so we may check rate-limiting
                # first and then create or extend the user's associated SSO session.
                # In other words, we can already act as though the user was already
                # logged in because in fact he or she is logged in, just using
                # a security definition from sec_def.

                # Check rate-limiting
                self.server.rate_limiting.check_limit(cid, _rate_limit_type_sso_user,
                    sso_user_id, wsgi_environ['zato.http.remote_addr'], False)

                # Rate-limiting went fine, we can now create or extend
                # the person's SSO session linked to credentials from the request.

                current_app = wsgi_environ.get(self.server.sso_config.apps.http_header) or \
                    self.server.sso_config.apps.default

                session_info = self.server.sso_api.user.session.on_external_auth_succeeded(
                    cid,
                    sec_type,
                    sec_def_id,
                    sec_def_username,
                    sso_user_id,
                    ext_session_id,
                    totp_code,
                    current_app,
                    wsgi_environ['zato.http.remote_addr'],
                    wsgi_environ.get('HTTP_USER_AGENT'),
                )

                if session_info:
                    wsgi_environ['zato.http.response.headers']['X-Zato-SSO-UST'] = self.server.encrypt(
                        session_info.ust, _prefix='')

# ################################################################################################################################
# ################################################################################################################################
