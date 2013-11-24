# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.basic_auth import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import HTTPBasicAuth

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'message-xpath'
    template = 'zato/message/xpath.html'
    service_name = 'zato.message.xpath.get-list'
    output_class = HTTPBasicAuth

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'username', 'realm')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'username', 'realm')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {0} the ElemPath [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'message-xpath-create'
    service_name = 'zato.message.xpath.create'

class Edit(_CreateEdit):
    url_name = 'message-xpath-edit'
    form_prefix = 'edit-'
    service_name = 'zato.message.xpath.edit'

class Delete(_Delete):
    url_name = 'message-xpath-delete'
    error_message = 'Could not delete the xpath'
    service_name = 'zato.message.xpath.delete'
