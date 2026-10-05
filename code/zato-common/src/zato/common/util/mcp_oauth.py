# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.defaults import http_plain_server_port
from zato.common.util.tcp import get_current_ip

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The environment variable naming the address under which clients reach this server
Server_Address_Env_Key = 'Zato_Server_Address'

# Where RFC 9728 places the protected resource metadata of a resource at a given path
Metadata_Path_Prefix = '/.well-known/oauth-protected-resource'

# The channel that serves the metadata of every gateway, one path segment per gateway path
Metadata_Channel_Name = 'zato.mcp.oauth-protected-resource'
Metadata_Channel_Url_Path = Metadata_Path_Prefix + '/{path}'
Metadata_Service_Name = 'zato.server.service.internal.gateway.mcp_oauth.ProtectedResourceMetadata'

# How long clients may keep a metadata document before asking again, in seconds
Metadata_Cache_Max_Age = 300

# The one way a token reaches a gateway
Bearer_Methods_Supported = ['header']

# ################################################################################################################################
# ################################################################################################################################

def get_server_address() -> 'str':
    """ Returns the address clients reach this server at, without a trailing slash -
    the configured one when there is one, otherwise this host's IP and the default port.
    """
    out = os.environ.get(Server_Address_Env_Key) or ''

    if not out:
        out = f'http://{get_current_ip()}:{http_plain_server_port}'

    out = out.rstrip('/')
    return out

# ################################################################################################################################

def get_metadata_url(server_address:'str', url_path:'str') -> 'str':
    """ Returns the metadata URL of the gateway at the given path.
    """
    out = f'{server_address}{Metadata_Path_Prefix}{url_path}'
    return out

# ################################################################################################################################

def build_challenge_header(metadata_url:'str', has_token:'bool') -> 'str':
    """ Builds the WWW-Authenticate value a gateway answers an unauthenticated request with.
    A request that carried a token is additionally told that the token was not accepted.
    """
    out = f'Bearer resource_metadata="{metadata_url}"'

    if has_token:
        out += ', error="invalid_token"'

    return out

# ################################################################################################################################

def build_metadata_document(resource:'str', authorization_servers:'strlist', scopes:'strlist') -> 'stranydict':
    """ Builds the RFC 9728 document describing one gateway.
    """
    out:'stranydict' = {
        'resource': resource,
        'authorization_servers': authorization_servers,
        'bearer_methods_supported': Bearer_Methods_Supported,
    }

    if scopes:
        out['scopes_supported'] = scopes

    return out

# ################################################################################################################################

def parse_scopes(scopes:'str') -> 'strlist':
    """ Splits the gateway's scopes string, which may use spaces or commas, into a list.
    """
    out:'strlist' = []

    for item in scopes.replace(',', ' ').split():
        if item not in out:
            out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################
