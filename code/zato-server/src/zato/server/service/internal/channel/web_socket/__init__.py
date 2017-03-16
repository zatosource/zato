# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import CHANNEL
from zato.common.odb.model import ChannelWebSocket, Service as ServiceModel
from zato.common.odb.query import channel_web_socket_list, channel_web_socket
from zato.common.util import is_port_taken
from zato.server.service import Int, Service
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'channel_web_socket'
model = ChannelWebSocket
label = 'a WebSocket channel'
broker_message = CHANNEL
broker_message_prefix = 'WEB_SOCKET_'
list_func = channel_web_socket_list
skip_input_params = ['service_id']
create_edit_input_required_extra = ['service_name']
output_optional_extra = ['service_name', 'sec_type']

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):
    input.source_server = self.server.get_full_name()
    input.config_cid = 'channel.web_socket.{}.{}.{}'.format(service_type, input.source_server, self.cid)

    if service_type == 'create_edit':

        with closing(self.odb.session()) as session:
            full_data = channel_web_socket(session, input.cluster_id, instance.id)

        input.sec_type = full_data.sec_type
        input.sec_name = full_data.sec_name
        input.vault_conn_default_auth_method = full_data.vault_conn_default_auth_method

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):

    with closing(self.odb.session()) as session:

        instance.service_id = session.query(ServiceModel).\
            filter(ServiceModel.name==input.service_name).\
            filter(ServiceModel.cluster_id==input.cluster_id).\
            one().id

# ################################################################################################################################

class GetList(AdminService):
    _filter_by = ChannelWebSocket.name,
    __metaclass__ = GetListMeta

# ################################################################################################################################

class Create(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Delete(AdminService):
    __metaclass__ = DeleteMeta

# ################################################################################################################################

class GetToken(AdminService):
    pass

# ################################################################################################################################

class InvalidateToken(AdminService):
    pass

# ################################################################################################################################

class Start(Service):
    """ Starts a WebSocket channel.
    """
    class SimpleIO(object):
        input_required = tuple(Edit.SimpleIO.input_required) + ('id', 'config_cid')
        input_optional = tuple(Edit.SimpleIO.input_optional) + (Int('bind_port'), 'service_name', 'sec_name', 'sec_type')
        request_elem = 'zato_channel_web_socket_start_request'
        response_elem = 'zato_channel_web_socket_start_response'

    def handle(self):
        input = self.request.input
        if input.bind_port and is_port_taken(input.bind_port):
            self.logger.warn('Cannot bind WebSocket channel `%s` to TCP port %s (already taken)', input.name, input.bind_port)
        else:
            self.server.worker_store.web_socket_channel_create(self.request.input)

# ################################################################################################################################
