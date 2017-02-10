# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from logging import getLogger

# Bunch
from bunch import bunchify

# Zato
from zato.common import WEB_SOCKET
from zato.common.odb.query import web_socket_client_list

logger = getLogger(__name__)

_pattern = WEB_SOCKET.PATTERN

# ################################################################################################################################

class OutgoingWebSocket(object):
    """ Lets services send outgoing messages to WebSocket clients.
    """
    def __init__(self, cluster_id, servers_api, odb_session_maker):
        self.cluster_id = cluster_id
        self.servers_api = servers_api
        self.odb_session_maker = odb_session_maker

    def invoke(self, request, id=None, channel=None, pattern=None):
        if not any((id, channel, pattern)):
            raise ValueError('At least one of `id`, `channel` or `pattern` parameters is required')

        is_by_ext_id = bool(id)
        is_by_channel = bool(channel)

        if pattern:
            p = pattern
        else:
            p = _pattern.BY_EXT_ID.format(id) if is_by_ext_id else _pattern.BY_CHANNEL.format(channel)

        # All individual responses from each WebSocket client that received this request
        responses = []

        with closing(self.odb_session_maker.session()) as session:

            for item, channel_name in web_socket_client_list(session, self.cluster_id, is_by_ext_id, is_by_channel, p).all():

                item = bunchify(item.asdict())

                logger.warn('zzzz %r', item)

                response = self.servers_api[item.server_name].invoke('zato.channel.web-socket.client.deliver-request', {
                    'pub_client_id': item.pub_client_id,
                    'channel_name': channel_name,
                    'request': request,
                }, pid=item.server_proc_pid)

                responses.append({
                    'ext_client_id': item.ext_client_id,
                    'ext_client_name': item.ext_client_name,
                    'local_address': item.local_address,
                    'peer_address': item.peer_address,
                    'peer_fqdn': item.peer_fqdn,
                    'response': response['response']
                })

        return responses

# ################################################################################################################################
