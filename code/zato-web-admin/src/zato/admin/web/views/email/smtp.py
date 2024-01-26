# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.email.smtp import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, id_only_service, \
     Index as _Index, method_allowed
from zato.common.api import EMAIL
from zato.common.odb.model import SMTP

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'email-smtp'
    template = 'zato/email/smtp.html'
    service_name = 'zato.email.smtp.get-list'
    output_class = SMTP
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'host', 'port', 'timeout', 'username', 'is_debug', 'mode', 'ping_address')
        output_optional = ('username',)
        output_repeated = True

    def handle(self):
        return {
            'default_ping_address': EMAIL.DEFAULT.PING_ADDRESS,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'host', 'port', 'timeout', 'username', 'is_debug', 'mode', 'ping_address')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {0} the SMTP connection [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'email-smtp-create'
    service_name = 'zato.email.smtp.create'

class Edit(_CreateEdit):
    url_name = 'email-smtp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.email.smtp.edit'

class Delete(_Delete):
    url_name = 'email-smtp-delete'
    error_message = 'Could not delete the SMTP connection'
    service_name = 'zato.email.smtp.delete'

@method_allowed('POST')
def ping(req, id, cluster_id):
    ret = id_only_service(req, 'zato.email.smtp.ping', id, 'SMTP ping error: {}')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse(ret.data.info)

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.email.smtp.change-password')
