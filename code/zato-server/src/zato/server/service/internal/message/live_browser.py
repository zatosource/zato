# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common import WEB_SOCKET
from zato.common.odb.query import jwt_by_username
from zato.server.service import Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class Dispatch(AdminService):
    """ Dispatches incoming requests from live message browsers.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_live_browser_dispatch_request'
        response_elem = 'zato_message_live_browser_dispatch_response'
        input_required = (Opaque('data'),)
        output_optional = ('response',)

    def handle(self):
        self.logger.warn(self.request.raw_request)

# ################################################################################################################################

class GetWebAdminConnectionDetails(AdminService):

    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_live_browser_get_web_admin_connection_details_request'
        response_elem = 'zato_message_live_browser_get_web_admin_connection_details_response'
        output_required = ('address', 'username', 'jwt_token')

    def handle(self):

        with closing(self.odb.session()) as session:

            defs = WEB_SOCKET.DEFAULT.LIVE_MSG_BROWSER

            username = defs.USER
            self.response.payload.address = 'ws://{}:{}/{}'.format(self.server.preferred_address, defs.PORT, defs.CHANNEL)
            self.response.payload.username = username
            self.response.payload.jwt_token = self.invoke('zato.security.jwt.log-in', {
                'username': username,
                'password': jwt_by_username(session, self.server.cluster_id, username).password
            }, as_bunch=True).zato_security_jwt_log_in_response.token

# ################################################################################################################################