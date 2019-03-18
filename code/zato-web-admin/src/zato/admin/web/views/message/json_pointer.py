# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.message.json_pointer import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import JSONPointer

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'message-json-pointer'
    template = 'zato/message/json_pointer.html'
    service_name = 'zato.message.json-pointer.get-list'
    output_class = JSONPointer
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'value')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit')
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'value')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {0} the JSON Pointer [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'message-json-pointer-create'
    service_name = 'zato.message.json-pointer.create'

class Edit(_CreateEdit):
    url_name = 'message-json-pointer-edit'
    form_prefix = 'edit-'
    service_name = 'zato.message.json-pointer.edit'

class Delete(_Delete):
    url_name = 'message-json-pointer-delete'
    error_message = 'Could not delete the JSON Pointer'
    service_name = 'zato.message.json-pointer.delete'
