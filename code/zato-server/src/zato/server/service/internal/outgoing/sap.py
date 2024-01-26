# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from time import time
from uuid import uuid4

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingSAP
from zato.common.odb.query import out_sap_list
from zato.common.util.api import ping_sap
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'email_imap'
model = OutgoingSAP
label = 'a SAP RFC connection'
get_list_docs = 'SAP RFC connections'
broker_message = OUTGOING
broker_message_prefix = 'SAP_'
list_func = out_sap_list
skip_input_params = ['password']

# ################################################################################################################################

def instance_hook(service, input, instance, attrs):
    if 'create' in service.get_name().lower():
        instance.password = uuid4().hex

# ################################################################################################################################

def broker_message_hook(service, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        input.password = instance.password

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = OutgoingSAP.name,

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
    """ Changes the password of an SAP connection
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_outgoing_sap_change_password_request'
        response_elem = 'zato_outgoing_sap_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(OutgoingSAP, _auth, OUTGOING.SAP_CHANGE_PASSWORD.value,
            publish_instance_attrs=['host', 'sysnr', 'client', 'sysid', 'user', 'password', 'router', 'pool_size'])

# ################################################################################################################################

class Ping(AdminService):
    """ Pings a SAP connection to check its configuration.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sap_ping_request'
        response_elem = 'zato_outgoing_sap_ping_response'
        input_required = ('id',)
        output_required = ('info',)

    def handle(self):

        with closing(self.odb.session()) as session:
            item = session.query(OutgoingSAP).filter_by(id=self.request.input.id).one()

        with self.outgoing.sap[item.name].conn.client() as client:

            start_time = time()
            ping_sap(client)
            response_time = time() - start_time

            self.response.payload.info = 'Ping OK, took:`{0:03.4f} s`'.format(response_time)

# ################################################################################################################################
