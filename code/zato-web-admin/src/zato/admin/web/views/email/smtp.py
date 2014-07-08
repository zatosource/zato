# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.email.smtp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import SMTP

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'email-smtp'
    template = 'zato/email/smtp.html'
    service_name = 'zato.email.smtp.get-list'
    output_class = SMTP

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'port', 'timeout', 'is_debug', 'mode')
        output_optional = ('username',)
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit')
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'port', 'timeout', 'is_debug', 'mode')
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
