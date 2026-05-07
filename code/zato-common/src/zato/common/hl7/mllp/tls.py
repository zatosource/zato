# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ssl

# ################################################################################################################################
# ################################################################################################################################

_Minimum_TLS_Version = ssl.TLSVersion.TLSv1_2

# Maps human-readable verify mode names to ssl constants
_verify_mode_map:'dict[str, ssl.VerifyMode]' = {
    'none':     ssl.CERT_NONE,
    'optional': ssl.CERT_OPTIONAL,
    'required': ssl.CERT_REQUIRED,
}

# ################################################################################################################################
# ################################################################################################################################

def build_server_ssl_context(
    cert_file:'str',
    key_file:'str',
    ca_file:'str',
    verify_mode:'str' = 'none',
    ) -> 'ssl.SSLContext':
    """ Builds an SSLContext for the MLLP server side.
    """

    # Create a context for the server role with TLS 1.2 as the minimum ..
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = _Minimum_TLS_Version

    # .. load the server's own certificate and private key ..
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    # .. configure peer (client) certificate verification ..
    resolved_verify_mode = _verify_mode_map[verify_mode]
    context.verify_mode = resolved_verify_mode

    # .. if we need to verify the client at all, load the CA bundle ..
    if resolved_verify_mode != ssl.CERT_NONE:
        context.load_verify_locations(cafile=ca_file)

    out = context
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_client_ssl_context(
    ca_file:'str',
    cert_file:'str' = '',
    key_file:'str' = '',
    ) -> 'ssl.SSLContext':
    """ Builds an SSLContext for the MLLP client side.
    """

    # Create a context for the client role with TLS 1.2 as the minimum ..
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = _Minimum_TLS_Version

    # .. always verify the server's certificate against the CA ..
    context.load_verify_locations(cafile=ca_file)

    # .. if a client certificate is provided, load it for mTLS ..
    if cert_file:
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    out = context
    return out

# ################################################################################################################################
# ################################################################################################################################
