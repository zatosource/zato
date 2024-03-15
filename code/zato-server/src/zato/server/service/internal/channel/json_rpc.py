# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Bunch
from bunch import bunchify

# Zato
from zato.common.api import CONNECTION, JSON_RPC, URL_TYPE
from zato.common. exception import Unauthorized
from zato.common.json_internal import dumps, loads
from zato.common.json_rpc import ErrorCtx, Forbidden, InternalError, ItemResponse, JSONRPCHandler, ParseError, \
     RateLimitReached as JSONRPCRateLimitReached, RequestContext
from zato.common.json_schema import ValidationException as JSONSchemaValidationException
from zato.common.odb.model import HTTPSOAP
from zato.common.simpleio_ import drop_sio_elems
from zato.common.rate_limiting.common import AddressNotAllowed, RateLimitReached
from zato.server.service import Boolean, List
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

get_attrs_req = 'id', 'name', 'is_active', 'url_path', 'sec_type', 'sec_use_rbac', 'security_id'
attrs_opt = 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', Boolean('rate_limit_check_parent_def'), \
    List('service_whitelist')

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
        output_required = get_attrs_req
        output_optional = attrs_opt
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
        output_required = get_attrs_req
        output_optional = attrs_opt

    def handle(self):
        self.response.payload = self.invoke('zato.http-soap.get', self.request.input, skip_response_elem=True)

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(AdminService):
    target_service_suffix = '<undefined>'

    class SimpleIO(_BaseSimpleIO):
        input_required = 'cluster_id', 'name', 'is_active', 'url_path', 'security_id', List('service_whitelist')
        input_optional = drop_sio_elems(attrs_opt, 'service_whitelist')
        output_required = 'id', 'name'
        skip_empty_keys = True
        response_elem = None

    def handle(self):

        request = self.request.input.deepcopy()
        request.is_internal = False
        request.name = '{}.{}'.format(JSON_RPC.PREFIX.CHANNEL, request.name)
        request.connection = CONNECTION.CHANNEL
        request.transport = URL_TYPE.PLAIN_HTTP
        request.http_accept = '*/*'
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

            #
            # At this point we know that our own service can be invoked (the gateway itself),
            # but we also need to check security as it pertains to the JSON-RPC method itself
            # which is another Zato service. Note that since JSON-RPC is a kind of an HTTP-based channel
            # we can have security definitions of three types:
            #
            # a) No security defined
            # b) A specific security definition
            # c) Deletegated to RBAC
            #
            # Case a) does not require anything
            # Case b) assumes that the very JSON-RPC and the service being invoked share the definition
            # Case c) requires an additional check because different RBAC permissions may be assigned
            #         to the gateway itself vs. the service that is to be invoked
            #

            channel_item = self.wsgi_environ['zato.channel_item'] # type: dict

            if channel_item['sec_use_rbac']:
                inner_channel_item = {}
                inner_channel_item['url_path'] = channel_item['url_path']
                inner_channel_item['service_id'] = self.server.service_store.get_service_id_by_name(message['method'])

                self.server.worker_store.request_dispatcher.url_data.check_rbac_delegated_security(
                    self.chan.sec, self.cid, inner_channel_item, inner_channel_item['url_path'], self.request.raw_request,
                    self.wsgi_environ, self.request.http.POST, self.server.worker_store)

        except Exception as e:

            self.logger.warning('JSON-RPC error in `%s` (%s), e:`%s`', self.channel.name, self.cid, format_exc())

            error_ctx = ErrorCtx()
            error_ctx.cid = self.cid

            # JSON parsing error
            if isinstance(e, ValueError):
                code = ParseError.code
                message = 'Parsing error'

            # Source address is not allowed to invoke the service
            if isinstance(e, (AddressNotAllowed, Unauthorized)):
                code = Forbidden.code
                message = 'You are not allowed to access this resource'

            elif isinstance(e, RateLimitReached):
                code = JSONRPCRateLimitReached.code
                message = 'Rate limit reached'

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

            handler = JSONRPCHandler(
                self.server.service_store, self.wsgi_environ, bunchify(channel_config), self.invoke, self.channel,
                JSONSchemaValidationException)
            response = handler.handle(ctx)

        self.response.content_type = 'application/json'
        self.response.payload = dumps(response)

# ################################################################################################################################
# ################################################################################################################################
