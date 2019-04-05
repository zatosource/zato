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
from zato.admin.web.forms.channel.json_rpc import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common import ZATO_NONE
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
        self.service_whitelist = None

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-json-rpc'
    template = 'zato/channel/json-rpc.html'
    service_name = 'aaa.zato.channel.json-rpc.get-list'
    output_class = JSONRPC
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'cluster_id', 'id', 'name', 'is_active', 'url_path', 'security', 'service_whitelist'
        output_repeated = True

    def on_before_append_item(self, item):
        if item.security:
            item.security = '{}/{}'.format(item.sec_type, item.security)
        else:
            item.security = ZATO_NONE
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
        input_required = 'cluster_id', 'name', 'is_active', 'url_path', 'security', 'service_whitelist'
        output_required = 'id', 'name'

    def on_after_set_input(self):
        if self.input.security != ZATO_NONE:
            self.input.security = int(self.input.security.split('/')[1])
        else:
            self.input.security = None

    def success_message(self, item):
        logger.warn('WWW %s', item)
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
from zato.common import CONNECTION, DATA_FORMAT, JSON_RPC, URL_TYPE
from zato.common.odb.model import HTTPSOAP
from zato.common.py23_ import maxint
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

get_attrs = 'id', 'name', 'is_active', 'url_path', 'security_id', 'service_whitelist'

# ################################################################################################################################

class _BaseSimpleIO(AdminSIO):
    skip_empty_keys = True
    response_elem = None

# ################################################################################################################################

class GetList(AdminService):
    name = 'aaa.zato.channel.json-rpc.get-list'
    _filter_by = HTTPSOAP.name,

    class SimpleIO(GetListAdminSIO):
        input_required = 'cluster_id'
        output_required = get_attrs
        output_repeated = True

    def handle(self):
        out = []

        response = self.invoke('zato.http-soap.get-list', {
            'cluster_id': self.request.input.cluster_id,
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
        })

        response_elem = response.keys()[0]
        response = response[response_elem]

        for item in response:
            if item['name'].startswith(JSON_RPC.PREFIX.CHANNEL):
                item['name'] = item['name'].replace(JSON_RPC.PREFIX.CHANNEL + '.', '', 1)
                item['service_whitelist'] = '333'
                out.append(item)

        self.response.payload[:] = out

# ################################################################################################################################

class Get(AdminService):
    name = 'aaa.zato.channel.json-rpc.get'

    class SimpleIO(_BaseSimpleIO):
        input_required = 'cluster_id'
        input_optional = 'id', 'name'
        output_required = get_attrs

# ################################################################################################################################

class _CreateEdit(AdminService):
    name = 'aaa.zato.channel.json-rpc.create'

    class SimpleIO(_BaseSimpleIO):
        input_required = 'cluster_id', 'name', 'is_active', 'url_path', 'security', 'service_whitelist'
        output_required = 'id', 'name'
        skip_empty_keys = True
        response_elem = None

    def handle(self):

        # Local aliases
        input = self.request.input

        request = self.request.input.deepcopy()

        request.is_internal = False
        request.name = '{}.{}'.format(JSON_RPC.PREFIX.CHANNEL, request.name)
        request.connection = CONNECTION.CHANNEL
        request.transport = URL_TYPE.PLAIN_HTTP
        request.data_format = DATA_FORMAT.JSON
        request.http_accept = 'application/json'
        request.method = 'POST'
        request.service = 'pub.zato.channel.json-rpc.gateway'
        request.cache_expiry = 0

        response = self.invoke('zato.http-soap.create', request)
        response_elem = response.keys()[0]
        response = response[response_elem]

        self.response.payload.id = response['id']
        self.response.payload.name = response['name']

# ################################################################################################################################

class Create(_CreateEdit):
    name = 'aaa.zato.channel.json-rpc.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    name = 'aaa.zato.channel.json-rpc.edit'

    class SimpleIO(_CreateEdit.SimpleIO):
        input_required = _CreateEdit.SimpleIO.input_required + ('id',)

# ################################################################################################################################

class Delete(AdminService):
    name = 'aaa.zato.channel.json-rpc.delete'

    class SimpleIO(_BaseSimpleIO):
        input_required = 'cluster_id', 'id'

    def handle(self):
        self.invoke('zato.http-soap.delete', self.request.input)

# ################################################################################################################################

class JSONRPCGateway(AdminService):
    name = 'pub.zato.channel.json-rpc.gateway'

# ################################################################################################################################
'''
