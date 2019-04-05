# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.channel.web_socket import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common import ZATO_NONE
from zato.common.odb.model import ChannelWebSocket
from zato.common.util.json_ import dumps

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class JSONRPC(object):
    def __init__(self):
        self.id = None
        self.name = None
        self.url_path = None
        self.security = None
        self.has_rbac = None
        self.service_whitelist = None

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-json-rpc'
    template = 'zato/channel/json-rpc.html'
    service_name = 'aaa.zato.channel.json-rpc.get-list'
    output_class = ChannelWebSocket
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'url_path', 'security', 'service_whitelist'
        output_optional = 'has_rbac',
        output_repeated = True

    def on_before_append_item(self, item):
        if item.security_id:
            item.security_id = '{}/{}'.format(item.sec_type, item.security_id)
        else:
            item.security_id = ZATO_NONE
        return item

    def handle(self):
        if self.req.zato.cluster_id:
            sec_list = self.get_sec_def_list('basic_auth').def_items
            sec_list.extend(self.get_sec_def_list('jwt'))
            sec_list.extend(self.get_sec_def_list('vault_conn_sec'))
        else:
            sec_list = []

        return {
            'create_form': CreateForm(sec_list, req=self.req),
            'edit_form': EditForm(sec_list, prefix='edit', req=self.req),
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_active', 'url_path', 'security', 'service_whitelist'
        input_optional = 'has_rbac',
        output_required = 'id', 'name'

    def on_after_set_input(self):
        if self.input.security_id != ZATO_NONE:
            self.input.security_id = int(self.input.security_id.split('/')[1])
        else:
            self.input.security_id = None

    def success_message(self, item):
        return 'WebSocket channel `{}` successfully {}'.format(item.name, self.verb)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-json-rpc-create'
    service_name = 'aaa.zato.channel.json-rpc.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-json-rpc-edit'
    form_prefix = 'edit-'
    service_name = 'aaa.zato.channel.json-rpc.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-json-rpc-delete'
    error_message = 'Could not delete WebSocket channel'
    service_name = 'aaa.zato.channel.json-rpc.delete'

# ################################################################################################################################

'''
# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Service

class GetList(Service):
    name = 'aaa.zato.channel.json-rpc.get-list'

    def handle(self):
        self.response.payload = '[]'
'''
