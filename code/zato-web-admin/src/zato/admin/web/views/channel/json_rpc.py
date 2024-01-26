# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.channel.json_rpc import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, get_http_channel_security_id, get_security_id_from_select, \
     Index as _Index

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class JSONRPC:
    def __init__(self):
        self.id = None
        self.name = None
        self.url_path = None
        self.sec_type = None
        self.security_id = None
        self.service_whitelist = None

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-json-rpc'
    template = 'zato/channel/json-rpc.html'
    service_name = 'zato.channel.json-rpc.get-list'
    output_class = JSONRPC
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'cluster_id', 'id', 'name', 'is_active', 'url_path', 'sec_type', 'sec_use_rbac', 'security_id', \
            'service_whitelist'
        output_optional = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def'
        output_repeated = True

    def on_before_append_item(self, item):

        item.service_whitelist = '\n'.join(item.service_whitelist) if item.service_whitelist else ''
        item.security_id = get_http_channel_security_id(item)

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
        input_required = 'cluster_id', 'name', 'is_active', 'url_path', 'security_id', 'service_whitelist'
        input_optional = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def'
        output_required = 'id', 'name'

    def on_after_set_input(self):

        self.input.security_id = get_security_id_from_select(self.input, '', 'security_id')
        self.input.service_whitelist = self.input.service_whitelist.strip().splitlines()

    def success_message(self, item):
        return 'JSON-RPC channel `{}` successfully {}'.format(item.name, self.verb)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-json-rpc-create'
    service_name = 'zato.channel.json-rpc.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-json-rpc-edit'
    form_prefix = 'edit-'
    service_name = 'zato.channel.json-rpc.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-json-rpc-delete'
    error_message = 'Could not delete JSON-RPC channel'
    service_name = 'zato.channel.json-rpc.delete'

# ################################################################################################################################
