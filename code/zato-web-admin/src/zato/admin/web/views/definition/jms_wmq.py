# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.definition.jms_wmq import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed, ping_connection
from zato.common.odb.model import ConnDefWMQ

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'definition-wmq'
    template = 'zato/definition/jms-wmq.html'
    service_name = 'zato.definition.jms-wmq.get-list'
    output_class = ConnDefWMQ
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'host', 'port', 'queue_manager', 'channel', 'cache_open_send_queues',
            'cache_open_receive_queues', 'use_shared_connections', 'ssl', 'ssl_cipher_spec', 'ssl_key_repository',
            'needs_mcd', 'max_chars_printed', 'username', 'use_jms')
        output_repeated = True

    def handle(self):
        return {
            'change_password_form': ChangePasswordForm(),
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'host', 'port', 'queue_manager', 'channel', 'cache_open_send_queues',
            'cache_open_receive_queues', 'use_shared_connections', 'ssl', 'ssl_cipher_spec', 'ssl_key_repository', 'needs_mcd',
            'max_chars_printed', 'username', 'use_jms')
        output_required = ('id',)

    def success_message(self, item):
        return 'Successfully {} IBM MQ definition `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'definition-wmq-create'
    service_name = 'zato.definition.jms-wmq.create'

class Edit(_CreateEdit):
    url_name = 'definition-wmq-edit'
    form_prefix = 'edit-'
    service_name = 'zato.definition.jms-wmq.edit'

class Delete(_Delete):
    url_name = 'definition-wmq-delete'
    error_message = 'Could not delete IBM MQ definition'
    service_name = 'zato.definition.jms-wmq.delete'

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.definition.jms-wmq.ping', id, 'IBM MQ definition')

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.definition.jms-wmq.change-password')
