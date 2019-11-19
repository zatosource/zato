# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Python 2/3 compatibility
from six import add_metaclass

# stdlib
from contextlib import closing
from time import time

# Zato
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingSTOMP
from zato.common.odb.query import out_stomp_list
from zato.server.connection.stomp import create_stomp_session
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'stomp'
model = OutgoingSTOMP
label = 'a STOMP connection'
get_list_docs = 'STOMP connections'
broker_message = OUTGOING
broker_message_prefix = 'STOMP_'
list_func = out_stomp_list

# ################################################################################################################################

def instance_hook(service, input, instance, attrs):
    # So they are not stored as None/NULL
    instance.username = input.username or ''
    instance.password = input.password or ''

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = OutgoingSTOMP.name,

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a STOMP connection.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_outgoing_stomp_change_password_request'
        response_elem = 'zato_outgoing_stomp_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(OutgoingSTOMP, _auth, OUTGOING.STOMP_CHANGE_PASSWORD.value)

# ################################################################################################################################

class Ping(AdminService):

    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_stomp_ping_request'
        response_elem = 'zato_outgoing_stomp_ping_response'
        input_required = ('id',)
        output_required = ('info',)

    def handle(self):

        with closing(self.odb.session()) as session:
            item = session.query(OutgoingSTOMP).filter_by(id=self.request.input.id).one()

        start_time = time()

        # Will connect and disconnect hence confirming the path to a broker.
        session = create_stomp_session(self.outgoing.stomp[item.name].config)
        session.disconnect()

        response_time = time() - start_time

        self.response.payload.info = 'Ping heartbeat submitted, took:`{0:03.4f} s`, check server logs for details.'.format(response_time)

# ################################################################################################################################
