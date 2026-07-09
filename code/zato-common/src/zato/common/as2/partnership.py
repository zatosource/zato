# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.as2.common import Default, MDNMode, TransferMode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The characters an AS2 identifier may contain without quoting - RFC 4130 section 6.2 defines
# AS2-name as printable ASCII without space and without the double quote and backslash specials.
_atom_characters = frozenset(
    'abcdefghijklmnopqrstuvwxyz' +
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
    '0123456789' +
    "!#$%&'*+-._^`|~"
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class HTTPAuth:
    """ Optional HTTP basic authentication for outgoing requests - a Drummond profile,
    meaningful only over TLS.
    """
    username: str = ''
    password: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Partnership:
    """ Everything one AS2 trading relationship needs - who the two parties are, where messages go,
    how they are secured and what kind of MDN comes back.
    """
    # The AS2 identities - as2_from is always our own identifier and as2_to is the partner's.
    as2_from: str = ''
    as2_to:   str = ''

    # Where outgoing messages are delivered.
    endpoint_url: str = ''

    # Signing of outgoing messages.
    sign: bool = True
    sign_algorithm: str = Default.Digest_Algorithm

    # Encryption of outgoing messages.
    encrypt: bool = True
    encryption_algorithm: str = Default.Encryption_Algorithm

    # Compression of outgoing messages - both orders relative to signing exist in the wild.
    compress: bool = False
    compress_before_signing: bool = True

    # What kind of MDN to request and whether it must be signed.
    mdn_mode: str = MDNMode.Sync
    mdn_signed: bool = True

    # The signed-receipt-micalg preference list of outgoing requests - assigned by new_partnership.
    mdn_mic_algorithms: 'strlist'

    # Where the partner is to deliver asynchronous MDNs.
    async_mdn_url: str = ''

    # The Subject header of outgoing messages.
    subject: str = Default.Subject

    # The Content-Type of outgoing payloads.
    content_type: str = Default.Content_Type

    # Whether outgoing payloads carry their filename in a Content-Disposition header.
    preserve_filename: bool = False

    # Optional HTTP basic authentication for outgoing requests.
    http_auth: 'HTTPAuth | None' = None

    # HTTP behavior for outbound requests.
    http_timeout_seconds: int = Default.HTTP_Timeout_Seconds
    verify_tls: bool = True

    # The AS2-Version header of outgoing messages - pinnable for legacy peers,
    # while inbound never rejects on version.
    as2_version: str = Default.AS2_Version

    # The transfer encoding of outgoing payloads and the per-partner escape hatches
    # peers disagreeing about canonicalization make necessary.
    content_transfer_encoding: str = 'binary'
    force_base64: bool = False
    prevent_canonicalization: bool = False

    # How the HTTP request body is framed - Content-Length by default, chunked,
    # or chunked only above the size threshold below.
    http_transfer_mode: str = TransferMode.Content_Length
    chunked_threshold_bytes: int = Default.Chunked_Threshold_Bytes

    # Whether an already-seen filename gets a processed/warning MDN with explicit free text.
    warn_on_duplicate_filename: bool = False

    # After how many seconds a missing acknowledgment counts as overdue,
    # and how many same-Message-ID resends the overdue job may trigger.
    ack_overdue_after: int = 0
    resend_max_retries: int = 0

    # Where this partner's inbound documents are routed - either one overrides
    # the channel's own routing target when set, with the service taking precedence.
    inbound_topic:   str = ''
    inbound_service: str = ''

# ################################################################################################################################
# ################################################################################################################################

partnership_list = list[Partnership]

# ################################################################################################################################
# ################################################################################################################################

def new_partnership() -> 'Partnership':
    """ Returns a fresh partnership with its list fields in place.
    """

    # Our response to produce
    out = Partnership()

    out.mdn_mic_algorithms = [Default.Digest_Algorithm]

    return out

# ################################################################################################################################
# ################################################################################################################################

def quote_as2_identifier(value:'str') -> 'str':
    """ Quotes an AS2 identifier for the wire per RFC 4130 section 6.2 - identifiers made of atom
    characters travel bare, anything else becomes a quoted-string with backslash escapes.
    """
    needs_quoting = False

    for character in value:
        if character not in _atom_characters:
            needs_quoting = True
            break

    if not needs_quoting:
        return value

    escaped = value.replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')

    out = f'"{escaped}"'
    return out

# ################################################################################################################################

def unquote_as2_identifier(value:'str') -> 'str':
    """ Undoes the RFC 4130 quoting of an AS2 identifier received on the wire.
    """
    out = value.strip()

    # Bare identifiers arrive as they are ..
    if not out.startswith('"'):
        return out

    # .. quoted-strings lose their quotes and their backslash escapes.
    out = out[1:-1]
    out = out.replace('\\"', '"')
    out = out.replace('\\\\', '\\')

    return out

# ################################################################################################################################

def match_partnership(partnerships:'partnership_list', as2_from:'str', as2_to:'str') -> 'Partnership | None':
    """ Finds the partnership an incoming message belongs to. The message's AS2-From is the partner
    and its AS2-To is us, so the fields compare crosswise against the outbound-oriented partnership.
    """
    for partnership in partnerships:
        if partnership.as2_to == as2_from:
            if partnership.as2_from == as2_to:
                out = partnership
                break
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################
