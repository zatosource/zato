# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class PublishToOutgoingConnection(Service):
    """ Publishes one message to an outgoing connection, the way an application does it.
    """

    name = 'test.outgoing.publish'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        data = self.request.raw_request['data']

        result = self.out.rest[conn_name].publish(data)

        self.response.payload = {'msg_id': result.msg_id}

# ################################################################################################################################
# ################################################################################################################################

class PublishThroughFacade(Service):
    """ Publishes one message to an outgoing connection named through the REST facade, which is
    the other way of naming the same connection.
    """

    name = 'test.outgoing.publish-through-facade'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        data = self.request.raw_request['data']

        result = self.rest[conn_name].publish(data)

        self.response.payload = {'msg_id': result.msg_id}

# ################################################################################################################################
# ################################################################################################################################
