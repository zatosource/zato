# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ssl

# Zato
from zato.common.hl7.exception import HL7Exception

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_Minimum_TLS_Version = ssl.TLSVersion.TLSv1_2

# What a definition that names a client certificate without a CA bundle is refused with
_Certificate_Without_CA = 'A client certificate requires a CA bundle'

# ################################################################################################################################
# ################################################################################################################################

def validate_client_paths(config:'anydict') -> 'None':
    """ A client certificate is loaded only into a context that verifies the server, so a definition that
    names one without a CA bundle is refused. Either path may be absent from the definition.
    """
    if config.get('tls_cert_path'):
        if not config.get('tls_ca_path'):
            raise HL7Exception(_Certificate_Without_CA)

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
