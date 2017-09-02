# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

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
    """ Returns basic information regarding a message from a topic or a consumer queue.
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
