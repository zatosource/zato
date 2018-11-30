# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import SMS
from zato.common.odb.model import SMSTwilio
from zato.common.odb.query import sms_twilio, sms_twilio_list
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

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

class GetList(AdminService):
    _filter_by = SMSTwilio.name,
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
