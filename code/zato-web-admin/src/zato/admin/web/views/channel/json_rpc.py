# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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

class JSONRPC(object):
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
        output_repeated = True

    def on_before_append_item(self, item):

        item.service_whitelist = '\n'.join(item.service_whitelist)
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
        output_required = 'id', 'name'

    def on_after_set_input(self):

        self.input.security_id = get_security_id_from_select(self.input, '', 'security_id')
        self.input.service_whitelist = self.input.service_whitelist.strip().splitlines()

    def success_message(self, item):
        return 'WebSocket channel `{}` successfully {}'.format(item.name, self.verb)

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
    error_message = 'Could not delete WebSocket channel'
    service_name = 'zato.channel.json-rpc.delete'

# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.exception import BadRequest, InternalServerError

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:
    from typing import Callable

# ################################################################################################################################

json_rpc_version_supported = '2.0'

# ################################################################################################################################
# ################################################################################################################################

class JSONRPCException(object):
    code = -32000

# ################################################################################################################################
# ################################################################################################################################

class JSONRPCBadRequest(JSONRPCException, BadRequest):
    def __init__(self, cid, message):
        # type: (unicode, unicode)
        super(BadRequest, self).__init__(cid, message)

# ################################################################################################################################
# ################################################################################################################################

class InvalidRequest(JSONRPCBadRequest):
    code = -32600

# ################################################################################################################################
# ################################################################################################################################

class MethodNotFound(JSONRPCBadRequest):
    code = -32601

# ################################################################################################################################
# ################################################################################################################################

class InvalidParams(JSONRPCBadRequest):
    code = -32602

# ################################################################################################################################
# ################################################################################################################################

class InternalError(JSONRPCException, InternalServerError):
    code = -32603

# ################################################################################################################################
# ################################################################################################################################

class JSONRPCItem(object):
    """ An object describing an individual JSON-RPC request.
    """
    __slots__ = 'jsonrpc', 'method', 'params', 'id', 'is_notification'

# ################################################################################################################################

    def __init__(self):
        self.jsonrpc = None # type: unicode
        self.method = None  # type: unicode
        self.params = None  # type: object
        self.id = None      # type: unicode
        self.is_notification = None # type: bool

# ################################################################################################################################

    def to_dict(self):
        # type: () -> dict
        return {
            'jsonrpc': self.jsonrpc,
            'method': self.method,
            'params': self.params,
            'id': self.id
        }

# ################################################################################################################################

    @staticmethod
    def from_dict(self, item):
        # type: (dict) -> JSONRPCItem

        # Our object to return
        out = JSONRPCItem()

        # At this stage we only create a Python-level object and input
        # validation is performed by our caller.
        out.jsonrpc = item.get('jsonrpc')
        out.id = item.get('id')
        out.method = item.get('method')
        out.params = item.get('params')
        out.is_notification = bool(out.id)

        return out

# ################################################################################################################################
# ################################################################################################################################

class JSONRPCHandler(object):
    def __init__(self, config, invoke_func):
        # type: (dict, Callable)
        self.config = config
        self.invoke_func = invoke_func

# ################################################################################################################################

    def handle(self, data):
        # type: (object) -> object
        return self.handle_list(data) if isinstance(data, list) else self.handle_one_item(data)

# ################################################################################################################################

    def can_handle(self, method):
        # type: (unicode) -> bool
        return method in self.config['service_whitelist']

# ################################################################################################################################

    def handle_one_item(self, data):
        # type: (dict) -> object

        # Construct a Python object out of incoming data
        item = JSONRPCItem.from_dict(data)

        # Confirm that we can handle the JSON-RPC version requested
        if item.jsonrpc != json_rpc_version_supported:
            raise InvalidRequest(cid, 'Unsupported JSON-RPC version `{}` in `{}`'.format(item.jsonrpc, data))

        # Confirm that method requested is one that we can handle
        if not self.can_handle(item.method):
            raise InvalidRequest(cid, 'Method not supported `{}` in `{}`'.format(item.method, data))

# ################################################################################################################################

    def handle_list(self, data):
        # type: (list) -> list
        pass

# ################################################################################################################################
# ################################################################################################################################
'''
