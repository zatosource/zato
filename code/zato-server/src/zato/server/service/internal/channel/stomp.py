# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from time import time

# Zato
from zato.common.broker_message import CHANNEL
from zato.common.odb.model import ChannelSTOMP, Service
from zato.common.odb.query import channel_stomp_list
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'stomp_channel'
model = ChannelSTOMP
label = 'a STOMP channel'
broker_message = CHANNEL
broker_message_prefix = 'STOMP_'
output_required_extra = ['service_name']
create_edit_input_required_extra = ['service_name']
create_edit_rewrite = ['service_name']
list_func = channel_stomp_list

def instance_hook(service, input, instance, attrs):
    # So they are not stored as None/NULL
    instance.username = input.username or ''
    instance.password = input.password or ''

    with closing(service.odb.session()) as session:
        instance.service_id = session.query(Service).\
            filter(Service.name==input.service_name).\
            filter(Service.cluster_id==input.cluster_id).\
            one().id

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a STOMP channel.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_channel_stomp_change_password_request'
        response_elem = 'zato_channel_stomp_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(ChannelSTOMP, _auth, CHANNEL.STOMP_CHANGE_PASSWORD.value)

class Ping(AdminService):

    class SimpleIO(AdminSIO):
        request_elem = 'zato_channel_stomp_ping_request'
        response_elem = 'zato_channel_stomp_ping_response'
        input_required = ('id',)
        output_required = ('info',)

    def handle(self):

        with closing(self.odb.session()) as session:
            item = session.query(ChannelSTOMP).filter_by(id=self.request.input.id).one()

        start_time = time()
        self.outgoing.stomp.get(item.name, True).conn.ping()
        response_time = time() - start_time

        self.response.payload.info = 'Ping heartbeat submitted, took:`{0:03.4f} s`, check server logs for details.'.format(response_time)
