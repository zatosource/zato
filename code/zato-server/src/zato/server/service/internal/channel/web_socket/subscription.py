# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.api import WEB_SOCKET
from zato.common.odb.model import WebSocketSubscription
from zato.server.service import AsIs, Bool
from zato.server.service.internal import AdminService, AdminSIO

_pattern = WEB_SOCKET.PATTERN
_create_input_required = (AsIs('ext_client_id'), AsIs('client_id'), AsIs('channel_id'), 'channel_name')
_create_input_optional = ('is_internal', 'is_durable', Bool('has_gd'))

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new message subscription for a given WebSocket client.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_web_socket_subscription_create_request'
        response_elem = 'zato_channel_web_socket_subscription_create_response'
        input_required = _create_input_required + ('pattern', 'is_by_ext_id', 'is_by_channel')
        input_optional = _create_input_optional

    def handle(self):
        req = self.request.input

        with closing(self.odb.session()) as session:

            sub = WebSocketSubscription()
            sub.is_internal = req.is_internal
            sub.pattern = req.pattern
            sub.is_by_ext_id = req.is_by_ext_id
            sub.is_by_channel = req.is_by_channel
            sub.is_durable = req.is_durable
            sub.has_gd = req.has_gd
            sub.client_id = req.client_id
            sub.channel_id = req.channel_id
            sub.server_id = self.server.id

            session.add(sub)
            session.commit()

# ################################################################################################################################

class CreateDefault(AdminService):
    """ Creates default subscriptions for a client.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_web_socket_subscription_create_default_request'
        response_elem = 'zato_channel_web_socket_subscription_create_default_response'
        input_required = _create_input_required
        input_optional = _create_input_optional

    def handle(self):
        req = self.request.input

        # pattern, is_by_ext_id, is_by_channel
        patterns = [
            (_pattern.BY_EXT_ID.format(req.ext_client_id), True, False),
            (_pattern.BY_CHANNEL.format(req.channel_name), False, True),
        ]

        for pattern, is_by_ext_id, is_by_channel in patterns:
            self.invoke(Create.get_name(), {
                'ext_client_id': req.ext_client_id,
                'client_id.': req.client_id,
                'channel_id': req.channel_id,
                'channel_name': req.channel_name,
                'pattern': pattern,
                'is_by_ext_id': is_by_ext_id,
                'is_by_channel': is_by_channel,
                'is_internal': req.get('is_internal', False),
                'is_durable': req.get('is_durable', False),
                'has_gd': req.get('has_gd', False),
            })

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub subscription previously created or resumed by current WebSocket.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_web_socket_subscription_delete_request'
        response_elem = 'zato_channel_web_socket_subscription_delete_response'

# ################################################################################################################################
