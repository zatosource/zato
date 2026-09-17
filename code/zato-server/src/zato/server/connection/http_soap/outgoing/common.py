# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# requests
from requests import Response as _RequestsResponse
from requests.adapters import HTTPAdapter
from requests.utils import super_len

# requests-toolbelt
from requests_toolbelt import MultipartEncoder

# Zato
from zato.common.api import HTTP_SOAP, SEC_DEF_TYPE
from zato.common.audit_log.common import TransportStatus

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdictnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_rest')

# ################################################################################################################################
# ################################################################################################################################

# The smallest pool a connection may configure. A pool of zero is not a small pool, it is one that
# closes every connection the moment it is done with, so a stored zero means "never configured"
# rather than "keep nothing".
Minimum_Pool_Size = 1

_API_Key = SEC_DEF_TYPE.APIKEY
_Basic_Auth = SEC_DEF_TYPE.BASIC_AUTH
_MTLS = SEC_DEF_TYPE.MTLS
_NTLM = SEC_DEF_TYPE.NTLM
_OAuth = SEC_DEF_TYPE.OAUTH
_SPNEGO = SEC_DEF_TYPE.SPNEGO

_retry = HTTP_SOAP.Retry
_invocation = HTTP_SOAP.Invocation

# What a retry of an outgoing REST request is called in the logs.
_rest_retry_label = 'REST out'

# The transport statuses that read as a connection error to a caller - a TLS handshake that fails is one too
_connection_statuses = (TransportStatus.Connection_Error, TransportStatus.TLS_Error)

# What a connection sends when it has said nothing at all about its content type - neither an explicit
# one, nor a SOAP version, nor a data format.
Default_Content_Type = 'text/plain'

# An outgoing request goes to the address its connection is configured with and to no other one,
# so a redirect, which names a different address, is not followed.
Allow_Redirects = False

# What a configuration field's value is replaced with before the configuration is logged.
Masked_Value = '***'

# The configuration fields that never reach a log. The password is the plain one, and the
# declarative rows are where a token typed into a header, a query parameter or a body ends up.
Masked_Config_Fields = (
    'password',
    'salt',
    'security',
    'body_credentials',
    _invocation.Field_Request_Headers,
    _invocation.Field_Request_Query_String,
    _invocation.Field_Request_Data,
)

# ################################################################################################################################
# ################################################################################################################################

def _get_body_length(data:'any_') -> 'int':
    """ Returns how long a request body is, for the log message that describes the request.

    Strings and bytes answer directly. Everything else - a multipart encoder, a file object,
    a stream - is measured by the same function that requests itself uses to decide what
    Content-Length to send, and it answers zero for a body whose size cannot be known in
    advance. A multipart encoder in particular publishes its length as a property rather than
    through __len__, so len() applied to one raises rather than returning anything.
    """
    if isinstance(data, (str, bytes)):
        out = len(data)
    else:
        out = super_len(data)

    return out

# ################################################################################################################################

def _needs_serialization(data:'any_') -> 'bool':
    """ Says whether a request body still has to be serialized on its way out.

    A string is sent exactly as it stands, and so is a multipart encoder, which is an already
    encoded body that carries its own content type. Anything else - a dict, a list, a model -
    is serialized according to the connection's data format.
    """
    if isinstance(data, (str, MultipartEncoder)):
        out = False
    else:
        out = True

    return out

# ################################################################################################################################
# ################################################################################################################################

class Response(_RequestsResponse):

    # What the raw body turned into, which is genuinely of no one shape - the text as it arrived when
    # nothing says otherwise, whatever JSON parsed into when the response is JSON, and a model
    # instance or a list of them when the caller named a model class.
    data: 'any_'

    zato_method: 'str'
    zato_address: 'str'
    zato_qs_params: 'strdictnone' = None

# ################################################################################################################################
# ################################################################################################################################

class HTTPSAdapter(HTTPAdapter):
    """ An adapter which exposes a method for clearing out the underlying pool. Useful with HTTPS as it allows to update TLS
    material on the fly.
    """
    def clear_pool(self):
        self.poolmanager.clear()

# ################################################################################################################################
# ################################################################################################################################
