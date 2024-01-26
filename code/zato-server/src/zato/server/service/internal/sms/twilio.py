# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.broker_message import SMS
from zato.common.odb.model import SMSTwilio
from zato.common.odb.query import sms_twilio, sms_twilio_list
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.service import Service

    Bunch = Bunch
    Service = Service

# ################################################################################################################################

elem = 'sms_twilio'
model = SMSTwilio
label = 'a Twilio connection'
get_list_docs = 'Twilio connections'
broker_message = SMS
broker_message_prefix = 'TWILIO_'
list_func = sms_twilio_list
skip_input_params = ['is_internal']

# ################################################################################################################################

def response_hook(self, input, instance, attrs, service_type):
    # type: (Service, Bunch, SMSTwilio, Bunch, str)

    if service_type == 'get_list':

        for item in self.response.payload: # type: SMSTwilio
            item.auth_token = self.server.decrypt(item.auth_token)

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = SMSTwilio.name,

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

class Get(AdminService):
    """ Returns details of an SMS Twilio connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_sms_twilio_get_request'
        response_elem = 'zato_sms_twilio_get_response'
        input_required = ('cluster_id', 'id')
        output_required = ('name', 'is_active', 'account_sid', 'auth_token')
        output_optional = ('default_from', 'default_to')

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = sms_twilio(session, self.request.input.cluster_id, self.request.input.id)

# ################################################################################################################################

class SendMessage(AdminService):
    """ Sends a text message through an SMS Twilio connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_sms_twilio_send_message_request'
        response_elem = 'zato_sms_twilio_send_message_response'
        input_required = ('cluster_id', 'id', 'from_', 'to', 'body')

    def handle(self):
        item = self.invoke(Get.get_name(), payload=self.request.input, as_bunch=True).zato_sms_twilio_get_response
        msg = self.out.sms.twilio[item.name].conn.send(self.request.input.body, self.request.input.to, self.request.input.from_)
        self.logger.info('Sent message %s', msg)

# ################################################################################################################################
