# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.sms.twilio import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.json_internal import dumps
from zato.common.odb.model import SMSTwilio

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'sms-twilio'
    template = 'zato/sms/twilio/index.html'
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

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'account_sid', 'auth_token')
        input_optional = ('default_from', 'default_to')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the SMS Twilio connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'sms-twilio-create'
    service_name = 'zato.sms.twilio.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'sms-twilio-edit'
    form_prefix = 'edit-'
    service_name = 'zato.sms.twilio.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'sms-twilio-delete'
    error_message = 'Could not delete the SMS Twilio connection'
    service_name = 'zato.sms.twilio.delete'

# ################################################################################################################################

@method_allowed('GET')
def send_message(req, cluster_id, conn_id, name_slug):

    response = req.zato.client.invoke('zato.sms.twilio.get', {
        'cluster_id': cluster_id,
        'id': conn_id,
    })

    if not response.ok:
        raise Exception(response.details)

    return_data = {
        'cluster_id': cluster_id,
        'name_slug': name_slug,
        'item': response.data,
        'conn_id': conn_id
    }

    return TemplateResponse(req, 'zato/sms/twilio/send-message.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def send_message_action(req, cluster_id, conn_id, name_slug):

    try:
        request = {
            'cluster_id': req.zato.cluster_id,
            'id': req.POST['id'],
            'from_': req.POST['from_'],
            'to': req.POST['to'],
            'body': req.POST['body'],
        }

        response = req.zato.client.invoke('zato.sms.twilio.send-message', request)

        if response.ok:
            return HttpResponse(dumps({'msg': 'OK, message sent successfully.'}), content_type='application/javascript')
        else:
            raise Exception(response.details)
    except Exception:
        msg = 'Caught an exception, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
