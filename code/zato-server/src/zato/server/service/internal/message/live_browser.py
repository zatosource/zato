# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Bunch
from bunch import bunchify

# Zato
from zato.common import WEB_SOCKET
from zato.common.odb.model import WebSocketSubscription
from zato.common.odb.query import jwt_by_username, web_socket_client_by_pub_id, web_socket_sub_list
from zato.server.service import AsIs, Opaque
from zato.server.service.internal import AdminService, AdminSIO


# Services that live browser is allowed to invoke
whitelist = (
    'tmp.live-browser.subscribe',
    'zato.ping',
)

_pattern = WEB_SOCKET.PATTERN

# ################################################################################################################################

class DeleteCurrentSubscriptions(AdminService):
    """ Deletes all message browsing subscriptions of a given client by its ID.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_live_browser_delete_current_subscriptions_request'
        response_elem = 'zato_message_live_browser_delete_current_subscriptions_response'
        input_required = ('client_id', AsIs('pub_client_id'))

    def handle(self):
        with closing(self.odb.session()) as session:

            web_socket_sub_list(session, self.server.cluster_id).\
                filter(WebSocketSubscription.client_id==self.request.input.client_id).\
                delete()

            session.commit()

# ################################################################################################################################

class Subscribe(AdminService):
    """ Subscribes the client to messages matching given criteria.
    """
    class SimpleIO:
        input_required = (AsIs('pub_client_id'), 'query',)

    def handle(self):

        with closing(self.odb.session()) as session:
            client, channel_name = web_socket_client_by_pub_id(session, self.request.input.pub_client_id)

            # First, remove all current subscriptions ..
            self.invoke(DeleteCurrentSubscriptions.get_name(), {
                'client_id':client.id,
                'pub_client_id':self.request.input.pub_client_id,
            })

            # .. now subscribe to all the new patterns.
            for pattern in set(elem.strip() for elem in self.request.input.query.strip().split()):

                self.invoke('zato.channel.web-socket.subscription.create', {
                    'ext_client_id': client.ext_client_id,
                    'client_id': client.id,
                    'channel_id': client.channel_id,
                    'channel_name': channel_name,
                    'pattern': _pattern.MSG_BROWSER.format(pattern),
                    'is_by_ext_id': False,
                    'is_by_channel': False,
                    'is_internal': False,
                    'is_durable': False,
                    'has_gd': False,
                })

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
        data = self.request.bunchified().data
        if data.service_name not in whitelist:
            raise ValueError('Service `{}` is not on whitelist'.format(data.service_name))

        request = data.get('request', {})
        request.update(self.environ)
        self.invoke(data.service_name, request)

# ################################################################################################################################
