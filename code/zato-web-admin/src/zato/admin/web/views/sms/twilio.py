# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# elasticutils
from elasticutils import DEFAULT_TIMEOUT

# Zato
from zato.admin.web.forms.sms.twilio import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import SMSTwilio

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'sms-twilio'
    template = 'zato/sms/twilio.html'
    service_name = 'zato.sms.twilio.get-list'
    output_class = SMSTwilio
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'account_sid', 'auth_token')
        output_optional = ('default_from', 'default_to')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'account_sid', 'auth_token')
        input_optional = ('default_from', 'default_to')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the SMS Twilio connection `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'sms-twilio-create'
    service_name = 'zato.sms.twilio.create'

class Edit(_CreateEdit):
    url_name = 'sms-twilio-edit'
    form_prefix = 'edit-'
    service_name = 'zato.sms.twilio.edit'

class Delete(_Delete):
    url_name = 'sms-twilio-delete'
    error_message = 'Could not delete the SMS Twilio connection'
    service_name = 'zato.sms.twilio.delete'
