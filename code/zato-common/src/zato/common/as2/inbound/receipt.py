# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Placing the receipt a message calls for on the result - on the HTTP response for a synchronous MDN,
as a pending delivery for an asynchronous one, and only to a destination the partnership vouches for.
"""

# stdlib
import logging
from http.client import ACCEPTED, NO_CONTENT, OK
from urllib.parse import urlsplit

# Zato
from zato.common.as2.inbound.common import PendingAsyncMDN
from zato.common.as2.mdn import build_mdn, MDNSigningConfig
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.inbound.common import InboundResult, keystorenone, partnershipnone
    from zato.common.as2.mdn import Disposition, MDNRequest
    from zato.common.as2.partnership import Partnership
    keystorenone = keystorenone
    partnershipnone = partnershipnone
    Disposition = Disposition
    InboundResult = InboundResult
    MDNRequest = MDNRequest
    Partnership = Partnership

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The URL schemes an asynchronous MDN may be delivered over - the two AS2 itself travels on,
# so that a destination naming any other scheme reaches no handler for it.
_allowed_async_mdn_schemes = ('http', 'https')

# ################################################################################################################################
# ################################################################################################################################

def _is_async_mdn_url_allowed(partnership:'partnershipnone', url:'str') -> 'bool':
    """ Tells whether an asynchronous MDN may be delivered to the URL the sender named.

    The destination arrives in the sender's Receipt-Delivery-Option header, which means an
    unauthenticated caller would otherwise choose where the server makes an outgoing request to -
    and the header is read on the error paths too, before the message has proven to come from
    the partner at all. An asynchronous receipt goes back to the party we exchange messages with,
    so the destination has to sit on the same host as that party's own AS2 endpoint.
    """
    # Without a partnership there is nothing to hold the destination against, which is the
    # unknown-trading-relationship case - a stranger does not get to name a destination.
    if not partnership:
        return False

    if not partnership.endpoint_url:
        return False

    named = urlsplit(url)
    endpoint = urlsplit(partnership.endpoint_url)

    # Only the two schemes AS2 travels over, so that no other URL handler is ever reached ..
    if named.scheme not in _allowed_async_mdn_schemes:
        return False

    # .. and only the partner's own host, port included, since a different port on the same
    # host is a different service.
    named_host = named.netloc.lower()
    endpoint_host = endpoint.netloc.lower()

    if named_host != endpoint_host:
        return False

    return True

# ################################################################################################################################

def attach_mdn(
    result:'InboundResult',
    request:'MDNRequest',
    disposition:'Disposition',
    mic:'str',
    keystore:'keystorenone',
    partnership:'partnershipnone' = None,
    ) -> 'None':
    """ Builds the MDN a message calls for and places it on the result - on the HTTP response
    for a synchronous one, as a pending delivery for an asynchronous one. Positive and negative
    MDNs alike ride on HTTP 200 - the disposition carries the outcome, not the status code.
    """
    # No MDN was requested at all - the response stays empty.
    if not request.requests_mdn:
        result.status_code = NO_CONTENT
        return

    # A signed receipt request is honored whenever signing material is available,
    # even when processing failed - build_mdn itself checks the requested protocol.
    signing_config = None

    if keystore:
        if keystore.signing_key:
            signing_config = MDNSigningConfig()
            signing_config.keystore = keystore

    body, headers = build_mdn(request, disposition, mic, signing_config)

    # A destination we will not deliver to falls back to the response body. The receipt still
    # reaches whoever made the request, which is more use to a genuine partner that named a
    # destination we do not recognize than a refusal would be.
    is_async = False

    if request.async_mdn_url:
        is_async = _is_async_mdn_url_allowed(partnership, request.async_mdn_url)

        if not is_async:
            logger.warning(
                'Refusing to deliver an AS2 async MDN to `%s`, which is not the endpoint of partner `%s`',
                request.async_mdn_url, result.as2_from)

    # An asynchronous MDN is the caller's to deliver - the inbound POST itself is merely accepted ..
    if is_async:
        partnership = cast_('Partnership', partnership)

        pending = PendingAsyncMDN()
        pending.url = request.async_mdn_url
        pending.body = body
        pending.headers = headers
        pending.verify_tls = partnership.verify_tls
        pending.timeout_seconds = partnership.http_timeout_seconds

        result.pending_async_mdn = pending
        result.status_code = ACCEPTED

    # .. a synchronous one rides back on the HTTP response.
    else:
        result.status_code = OK
        result.body = body
        result.headers = headers
        result.content_type = headers['Content-Type']

# ################################################################################################################################
# ################################################################################################################################
