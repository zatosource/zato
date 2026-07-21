# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from http.client import FORBIDDEN, NO_CONTENT, NOT_FOUND
from time import monotonic

# Zato
from zato.common.json_internal import dumps
from zato.server.connection.mcp.audit import build_audit_event, Method_Session_Delete
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone
    from zato.server.connection.mcp.handler import MCPResponse

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Content type for JSON-RPC responses
_content_type_json = 'application/json'

# MCP session header name (lowercase, as stored by HTTPRequestData._extract_headers)
_session_header = 'mcp-session-id'

# MCP session response header name (original casing for the HTTP response)
_session_response_header = 'Mcp-Session-Id'

# MCP protocol version header name (lowercase, as stored by HTTPRequestData._extract_headers)
_protocol_version_header = 'mcp-protocol-version'

# WSGI environ key set by the Rust HTTP layer with the resolved client address
_remote_addr_key = 'zato.http.remote_addr'

# Origin header name (lowercase, as stored by HTTPRequestData._extract_headers)
_origin_header = 'origin'

# Environment variable that enables Origin validation
_check_origin_env_key = 'Zato_MCP_Check_Origin'

# Whether to validate the Origin header on incoming requests
check_origin = os.environ.get(_check_origin_env_key) == 'true'

# Origin values allowed by default when Origin validation is enabled
_default_allowed_origins:'tuple' = ()

# How many milliseconds one second has, for request duration measurements
_ms_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

class MCPEndpoint(AdminService):
    """ Built-in service that serves as the MCP endpoint.
    Receives raw JSON-RPC requests, dispatches them through the MCP gateway's handler,
    and returns JSON-RPC responses. Supports MCP-Session-Id headers and DELETE for
    session termination.
    """

    name = 'zato.gateway.mcp.endpoint'

# ################################################################################################################################

    def handle(self) -> 'None':
        """ Processes an incoming MCP request.
        """

        # MCP gateways require authentication via security groups ..
        # .. if the HTTP layer did not authenticate the caller, reject immediately.
        channel_security = self.channel.security

        if not channel_security.id:
            logger.info(
                'MCP gateway `%s` rejected unauthenticated request (sec name=`%s` username=`%s`)',
                self.channel.name, channel_security.name, channel_security.username)
            self.response.status_code = FORBIDDEN
            self.response.payload = ''
            return

        logger.info(
            'MCP gateway `%s` authenticated sec_def id=`%s` username=`%s`',
            self.channel.name, channel_security.id, channel_security.username)

        # Look up the MCP gateway config from the config manager - the entry may be gone
        # if the gateway is being deleted while this request is already in flight,
        # in which case the resource no longer exists ..
        gateway_config = self.server.config_manager.gateway_mcp.get(self.channel.name)

        if gateway_config is None:
            logger.info(
                'MCP gateway `%s` has no config entry (gateway deleted) (sec name=`%s` username=`%s`)',
                self.channel.name, channel_security.name, channel_security.username)
            self.response.status_code = NOT_FOUND
            self.response.payload = ''
            return

        # .. reach the GatewayMCPWrapper through its .conn attribute ..
        wrapper = gateway_config.conn

        # .. when Origin validation is enabled and the header is present,
        # it must match the gateway's allowed origins ..
        if check_origin:
            if origin := self.request.http.headers.get(_origin_header):

                allowed_origins = wrapper.config.get('allowed_origins') or _default_allowed_origins

                if origin not in allowed_origins:
                    logger.info(
                        'MCP gateway `%s` rejected origin `%s` (sec name=`%s` username=`%s`)',
                        self.channel.name, origin, channel_security.name, channel_security.username)
                    self.response.status_code = FORBIDDEN
                    self.response.payload = ''
                    return

        # .. read the session ID from the request header if present ..
        session_id = self.request.http.headers.get(_session_header)

        # .. read the protocol version header if present, used to detect a version mismatch ..
        protocol_version_header = self.request.http.headers.get(_protocol_version_header)

        # .. get the remote address for session logging ..
        remote_address = self.wsgi_environ[_remote_addr_key]

        # .. get the sec_def id of the authenticated caller ..
        sec_def_id = channel_security.id

        # .. get the handler for request dispatch, reading it once into a local so a gateway
        # deletion later in this request cannot affect the dispatch already underway ..
        handler = wrapper.handler

        # .. no handler means the gateway is not usable - it was not built yet,
        # its build failed, or it is being deleted - in all cases the resource does not exist ..
        if handler is None:
            logger.info(
                'MCP gateway `%s` has no handler (not built yet, build failed, or gateway deleted) ' + \
                '(sec name=`%s` username=`%s`)',
                self.channel.name, channel_security.name, channel_security.username)
            self.response.status_code = NOT_FOUND
            self.response.payload = ''
            return

        # .. whether this gateway's traffic goes to the audit log - the key is absent
        # in configurations predating the field, which means it is off ..
        is_audit_log_active = wrapper.config.get('is_audit_log_active')

        # .. handle DELETE requests for session termination ..
        if self.request.http.method == 'DELETE':

            # .. measure how long the dispatch takes for the audit log ..
            start_time = monotonic()
            mcp_response = handler.handle_delete_session(session_id, sec_def_id, protocol_version_header)
            duration_ms = (monotonic() - start_time) * _ms_per_second

            self.response.status_code = mcp_response.status_code

            if mcp_response.body:
                payload = dumps(mcp_response.body)
                self.response.data_format = _content_type_json
            else:
                payload = ''

            self.response.payload = payload

            # .. one audit event per request, when this gateway has its audit log on - a DELETE
            # has no JSON-RPC method, it audits under its own marker and carries no request body.
            if is_audit_log_active:
                self._insert_audit_event(
                    wrapper, Method_Session_Delete, None, session_id, remote_address,
                    mcp_response, payload, duration_ms, 0)

            return

        # .. get the raw request body ..
        raw_request = self.request.raw

        if isinstance(raw_request, str):
            raw_request = raw_request.encode('utf8')

        # .. dispatch through the MCP handler, measuring how long it takes for the audit log ..
        start_time = monotonic()
        mcp_response = handler.handle_raw_request(
            raw_request, sec_def_id, session_id, remote_address, protocol_version_header)
        duration_ms = (monotonic() - start_time) * _ms_per_second

        # .. if the handler returned a session ID (from initialize), set it as a response header ..
        if mcp_response.session_id:
            self.response.headers[_session_response_header] = mcp_response.session_id

        # .. set the response ..
        self.response.status_code = mcp_response.status_code

        if mcp_response.status_code == NO_CONTENT:
            payload = ''

        else:
            payload = dumps(mcp_response.body)
            self.response.data_format = _content_type_json

        self.response.payload = payload

        # .. and record the one audit event of this request, when this gateway has its audit log on.
        if is_audit_log_active:

            # A session created by initialize takes precedence over the one the request carried
            if mcp_response.session_id:
                audit_session_id = mcp_response.session_id
            else:
                audit_session_id = session_id

            self._insert_audit_event(
                wrapper, mcp_response.method, mcp_response.tool_name, audit_session_id, remote_address,
                mcp_response, payload, duration_ms, len(raw_request))

# ################################################################################################################################

    def _insert_audit_event(
        self,
        wrapper:'any_',
        method:'strnone',
        tool_name:'strnone',
        session_id:'strnone',
        remote_address:'str',
        mcp_response:'MCPResponse',
        payload:'str',
        duration_ms:'float',
        request_size:'int',
        ) -> 'None':
        """ Builds and writes the one audit event of this request - the payloads themselves
        are never recorded, only their sizes are.
        """

        # The caller is always authenticated by the time an audit event is built, so both
        # the gateway's channel name and the security definition's name are always present.
        gateway_name = self.channel.name
        sec_def_name = self.channel.security.name

        assert gateway_name is not None
        assert sec_def_name is not None

        event = build_audit_event(
            gateway_name=gateway_name,
            sec_def_name=sec_def_name,
            cid=self.cid,
            method=method,
            tool_name=tool_name,
            session_id=session_id,
            remote_address=remote_address,
            response_body=mcp_response.body,
            response_size=len(payload.encode('utf8')),
            status_code=mcp_response.status_code,
            duration_ms=duration_ms,
            request_size=request_size,
        )

        wrapper.get_audit_log().insert(**event)

# ################################################################################################################################
# ################################################################################################################################
