# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.views import change_password as _change_password
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.definition.amqp_ import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import ConnDefAMQP

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'def-amqp'
    template = 'zato/definition/amqp.html'
    service_name = 'zato.definition.amqp.get-list'
    output_class = ConnDefAMQP
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'host', 'port', 'vhost', 'username', 'frame_max', 'heartbeat')
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
        input_required = ('name', 'host', 'port', 'vhost', 'username', 'frame_max', 'heartbeat')
        output_required = ('id',)

    def success_message(self, item):
        return 'Successfully {} the AMQP definition `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'def-amqp-create'
    service_name = 'zato.definition.amqp.create'

class Edit(_CreateEdit):
    url_name = 'def-amqp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.definition.amqp.edit'

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.definition.amqp.change-password')

class Delete(_Delete):
    url_name = 'def-amqp-delete'
    error_message = 'Could not delete the AMQP definition'
    service_name = 'zato.definition.amqp.delete'
