# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Service

# ################################################################################################################################

class Start(Service):
    """ Starts an AMQP connection.
    """
    # We assign the name explicitly because otherwise it is turned into zato.connector.amqp-.start (note - instead of _).
    name = 'zato.connector.amqp_.start'

    class SimpleIO:
        input_required = ('cluster_id', 'frame_max', 'heartbeat', 'host', 'id', 'name', 'port', 'username', 'vhost', 'password')
        input_optional = ('old_name',)
        request_elem = 'zato_connector_amqp_start_request'
        response_elem = 'zato_connector_amqp_start_response'

    def handle(self):
        self.server.worker_store.amqp_connection_create(self.request.input)

# ################################################################################################################################
