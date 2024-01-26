# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.outgoing.zmq import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import OutgoingZMQ

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-zmq'
    template = 'zato/outgoing/zmq.html'
    service_name = 'zato.outgoing.zmq.get-list'
    output_class = OutgoingZMQ
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'socket_type', 'socket_method')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'address', 'socket_type', 'socket_method')
        output_required = ('id',)

    def success_message(self, item):
        return 'Successfully {0} the outgoing Zero MQ connection [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'out-zmq-create'
    service_name = 'zato.outgoing.zmq.create'

class Edit(_CreateEdit):
    url_name = 'out-zmq-edit'
    form_prefix = 'edit-'
    service_name = 'zato.outgoing.zmq.edit'

class Delete(_Delete):
    url_name = 'out-zmq-delete'
    error_message = 'Could not delete the outgoing Zero MQ connection'
    service_name = 'zato.outgoing.zmq.delete'
