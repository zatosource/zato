# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Putting one built message onto the wire - how the request is framed and how it is authenticated.
"""

# httpx
import httpx

# Zato
from zato.common.as2.common import TransferMode
from zato.common.as2.outbound.common import Chunk_Size

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.outbound.common import bytesgen
    from zato.common.as2.partnership import Partnership
    from zato.common.typing_ import strstrdict
    bytesgen = bytesgen
    strstrdict = strstrdict
    Partnership = Partnership

# ################################################################################################################################
# ################################################################################################################################

def _iterate_chunks(body:'bytes') -> 'bytesgen':
    """ Yields the body in chunks, which makes the HTTP client frame the request
    with chunked transfer encoding instead of a Content-Length header.
    """
    body_size = len(body)

    for offset in range(0, body_size, Chunk_Size):
        yield body[offset:offset + Chunk_Size]

# ################################################################################################################################

def _should_chunk(partnership:'Partnership', body:'bytes') -> 'bool':
    """ Tells whether the request body is to be framed with chunked transfer encoding.
    """
    if partnership.http_transfer_mode == TransferMode.Chunked:
        out = True

    elif partnership.http_transfer_mode == TransferMode.Threshold:
        body_size = len(body)
        out = body_size > partnership.chunked_threshold_bytes

    # .. anything else is the Content-Length default.
    else:
        out = False

    return out

# ################################################################################################################################

def post(
    partnership:'Partnership',
    body:'bytes',
    headers:'strstrdict',
    client:'httpx.Client | None',
    ) -> 'httpx.Response':
    """ Delivers one AS2 request over HTTP, with a per-call client unless one was supplied.
    """
    # Chunked framing rides on an iterable body - a plain bytes body gets a Content-Length.
    if _should_chunk(partnership, body):
        content = _iterate_chunks(body)
    else:
        content = body

    # Basic authentication is a per-partner option, meaningful only over TLS.
    if auth_config := partnership.http_auth:
        auth = (auth_config.username, auth_config.password)
    else:
        auth = httpx.USE_CLIENT_DEFAULT

    url = partnership.endpoint_url

    if client:
        out = client.post(url, content=content, headers=headers, auth=auth)
    else:
        verify = partnership.verify_tls
        timeout = partnership.http_timeout_seconds

        with httpx.Client(verify=verify, timeout=timeout) as own_client:
            out = own_client.post(url, content=content, headers=headers, auth=auth)

    return out

# ################################################################################################################################
# ################################################################################################################################
