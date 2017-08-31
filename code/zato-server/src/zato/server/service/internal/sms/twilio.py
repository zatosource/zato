# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import SMS
from zato.common.odb.model import SMSTwilio
from zato.common.odb.query import sms_twilio_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'sms_twilio'
model = SMSTwilio
label = 'a Twilio connection'
broker_message = SMS
broker_message_prefix = 'TWILIO_'
list_func = sms_twilio_list
skip_input_params = ['is_internal']

class GetList(AdminService):
    _filter_by = SMSTwilio.name,
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
