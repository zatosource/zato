# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps, loads
from traceback import format_exc

# Bunch
from bunch import bunchify

# Zato
from zato.common import CONNECTION, JSON_RPC, URL_TYPE
from zato.common.json_rpc import ErrorCtx, InternalError, ItemResponse, JSONRPCHandler, ParseError, RequestContext
from zato.common.json_schema import ValidationException as JSONSchemaValidationException
from zato.common.odb.model import HTTPSOAP
from zato.server.service import List
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

get_attrs = 'id', 'name', 'is_active', 'url_path', 'sec_type', 'sec_use_rbac', 'security_id', List('service_whitelist')

# ################################################################################################################################
# ################################################################################################################################

class _BaseSimpleIO(AdminSIO):
    skip_empty_keys = True
    response_elem = None

# ################################################################################################################################
# ################################################################################################################################

class _GetBase(AdminService):
    def pre_process_item(self, item):
        item['name'] = item['name'].replace(JSON_RPC.PREFIX.CHANNEL + '.', '', 1)

# ################################################################################################################################
# ################################################################################################################################

class GetList(_GetBase):
    _filter_by = HTTPSOAP.name,

    class SimpleIO(GetListAdminSIO):
        input_required = 'cluster_id'
        output_required = get_attrs
        output_repeated = True
        response_elem = None

    def handle(self):
        out = []

        response = self.invoke('zato.http-soap.get-list', {
            'cluster_id': self.request.input.cluster_id,
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
        }, skip_response_elem=True)

        for item in response:
            if item['name'].startswith(JSON_RPC.PREFIX.CHANNEL):
                self.pre_process_item(item)
                out.append(item)

        self.response.payload[:] = out

# ################################################################################################################################
# ################################################################################################################################

class Get(AdminService):
    class SimpleIO(_BaseSimpleIO):
        input_required = 'cluster_id'
        input_optional = 'id', 'name'
        output_required = get_attrs

    def handle(self):
        self.response.payload = self.invoke('zato.http-soap.get', self.request.input, skip_response_elem=True)

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(AdminService):
    target_service_suffix = '<undefined>'

    class SimpleIO(_BaseSimpleIO):
        input_required = 'cluster_id', 'name', 'is_active', 'url_path', 'security_id', List('service_whitelist')
        output_required = 'id', 'name'
        skip_empty_keys = True
        response_elem = None

    def handle(self):

        request = self.request.input.deepcopy()
        request.is_internal = False
        request.name = '{}.{}'.format(JSON_RPC.PREFIX.CHANNEL, request.name)
        request.connection = CONNECTION.CHANNEL
        request.transport = URL_TYPE.PLAIN_HTTP
        request.http_accept = 'application/json'
        request.method = 'POST'
        request.service = 'pub.zato.channel.json-rpc.gateway'
        request.cache_expiry = 0

        response = self.invoke('zato.http-soap.{}'.format(self.target_service_suffix), request, skip_response_elem=True)

        self.response.payload.id = response['id']
        self.response.payload.name = response['name']

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    target_service_suffix = 'create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    target_service_suffix = 'edit'

    class SimpleIO(_CreateEdit.SimpleIO):
        input_required = _CreateEdit.SimpleIO.input_required + ('id',)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    class SimpleIO(_BaseSimpleIO):
        input_required = 'cluster_id', 'id'

    def handle(self):
        self.invoke('zato.http-soap.delete', self.request.input)

# ################################################################################################################################
# ################################################################################################################################

class JSONRPCGateway(AdminService):
    """ A gateway service via which JSON-RPC requests are accepted.
    """
    name = 'pub.zato.channel.json-rpc.gateway'

# ################################################################################################################################

    def handle(self):
        try:
            channel_config = self.server.worker_store.request_dispatcher.url_data.get_channel_by_name(self.channel.name)
            message = loads(self.request.payload.decode('utf8'))

        except Exception as e:

            self.logger.warn('JSON-RPC error in `%s` (%s), e:`%s`', self.channel.name, self.cid, format_exc())

            error_ctx = ErrorCtx()
            error_ctx.cid = self.cid

            # JSON parsing error
            if isinstance(e, ValueError):
                code = ParseError.code
                message = 'Parsing error'

            # Any other error
            else:
                code = InternalError.code
                message = 'Message could not be handled'


            error_ctx.code = code
            error_ctx.message = message

            out = ItemResponse()
            out.error = error_ctx

            response = out.to_dict()

        else:
            ctx = RequestContext()
            ctx.cid = self.cid
            ctx.message = message
            ctx.orig_message = self.request.raw_request

            handler = JSONRPCHandler(bunchify(channel_config), self.invoke, JSONSchemaValidationException)
            response = handler.handle(ctx)

        self.response.content_type = 'application/json'
        self.response.payload = dumps(response)

# ################################################################################################################################
# ################################################################################################################################
