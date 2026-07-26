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

# ################################################################################################################################
# ################################################################################################################################

# There is no server-side counterpart here. Inbound TLS terminates at the load balancer, which
# verifies the client certificate and reports its common name to the listener, so the listener
# itself never wraps a socket.

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
