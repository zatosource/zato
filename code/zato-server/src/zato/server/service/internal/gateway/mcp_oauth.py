# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import NOT_FOUND

# Zato
from zato.common.json_internal import dumps
from zato.common.util.mcp_oauth import build_metadata_document, get_server_address, Metadata_Cache_Max_Age, parse_scopes
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Content type of the metadata document
_content_type_json = 'application/json'

# How clients are told to cache the document
_cache_control_header = 'Cache-Control'
_cache_control_value = f'public, max-age={Metadata_Cache_Max_Age}'

# ################################################################################################################################
# ################################################################################################################################

class ProtectedResourceMetadata(AdminService):
    """ Serves the RFC 9728 protected resource metadata of MCP gateways that have OAuth on -
    one channel for the whole environment, the gateway being named by the path parameter.
    """

    name = 'zato.gateway.mcp.oauth-protected-resource'

# ################################################################################################################################

    def handle(self) -> 'None':

        # The path parameter carries the gateway's URL path without its leading slash ..
        path = self.request.http.params.path or ''
        url_path = '/' + path.lstrip('/')

        # .. which must name an active gateway with OAuth on ..
        wrapper = self._find_gateway(url_path)

        if wrapper is None:
            logger.info('No MCP gateway with OAuth on at `%s`', url_path)
            self.response.status_code = NOT_FOUND
            self.response.payload = ''
            return

        # .. whose bearer definitions say which authorization servers issue its tokens ..
        gateway_name = wrapper.config['name']
        authorization_servers = self._get_issuers(gateway_name)

        # .. and whose scopes, if any, the clients are to ask for.
        scopes = parse_scopes(wrapper.config.get('oauth_scopes') or '')
        resource = get_server_address() + url_path

        document = build_metadata_document(resource, authorization_servers, scopes)

        self.response.headers[_cache_control_header] = _cache_control_value
        self.response.data_format = _content_type_json
        self.response.payload = dumps(document)

# ################################################################################################################################

    def _find_gateway(self, url_path:'str') -> 'any_':
        """ Returns the wrapper of the active gateway with OAuth on at the given path, or None.
        """
        for gateway_config in self.server.config_manager.gateway_mcp.values():

            wrapper = gateway_config.conn
            config = wrapper.config

            if config.get('url_path') != url_path:
                continue

            if not config.get('oauth'):
                continue

            if not config.get('is_active', True):
                continue

            return wrapper

        return None

# ################################################################################################################################

    def _get_issuers(self, gateway_name:'str') -> 'strlist':
        """ Returns the distinct issuers of the JWT bearer definitions in the gateway's security groups,
        read from the live context of the gateway's channel so a change to the group is reflected at once.
        """
        out:'strlist' = []

        url_data = self.server.config_manager.request_dispatcher.url_data
        channel_item = url_data.get_channel_by_name(gateway_name)

        if not channel_item:
            return out

        security_groups_ctx = channel_item.get('security_groups_ctx')

        if not security_groups_ctx:
            return out

        for item in security_groups_ctx.bearer_token_credentials.values():
            verify_config = item.verify_config

            if verify_config.static_token:
                continue

            if not verify_config.audience:
                continue

            if verify_config.issuer not in out:
                out.append(verify_config.issuer)

        return out

# ################################################################################################################################
# ################################################################################################################################
