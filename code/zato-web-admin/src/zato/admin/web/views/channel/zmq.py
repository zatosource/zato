# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.channel.zmq import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import ChannelZMQ

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-zmq'
    template = 'zato/channel/zmq.html'
    service_name = 'zato.channel.zmq.get-list'
    output_class = ChannelZMQ
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'socket_type', 'socket_method', 'sub_key',
            'service_name', 'pool_strategy', 'service_source', 'data_format')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'address', 'socket_type', 'socket_method', 'sub_key',
            'service', 'pool_strategy', 'service_source', 'data_format')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'ZeroMQ channel `{}` successfully {}'.format(item.name, self.verb)

class Create(_CreateEdit):
    url_name = 'channel-zmq-create'
    service_name = 'zato.channel.zmq.create'

class Edit(_CreateEdit):
    url_name = 'channel-zmq-edit'
    form_prefix = 'edit-'
    service_name = 'zato.channel.zmq.edit'

class Delete(_Delete):
    url_name = 'channel-zmq-delete'
    error_message = 'Could not delete the Zero MQ channel'
    service_name = 'zato.channel.zmq.delete'
