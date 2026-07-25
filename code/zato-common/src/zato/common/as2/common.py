# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from hmac import compare_digest

# ################################################################################################################################
# ################################################################################################################################

class AS2Error:
    """ Disposition modifiers from RFC 4130 section 7.4.3 and RFC 5402 that this implementation raises or recognizes.
    An MDN carries one of these after "processed/error:" or "failed/failure:" to say what went wrong.
    """
    Decryption_Failed             = 'decryption-failed'
    Authentication_Failed         = 'authentication-failed'
    Integrity_Check_Failed        = 'integrity-check-failed'
    Insufficient_Message_Security = 'insufficient-message-security'
    Unexpected_Processing_Error   = 'unexpected-processing-error'
    Decompression_Failed          = 'decompression-failed'

    # The additional registry modifiers of the AS2 specification modernization draft,
    # recognized on input as known values.
    Duplicate_Filename            = 'duplicate-filename'
    Illegal_Filename              = 'illegal-filename'
    Invalid_Message_ID            = 'invalid-message-id'
    Unknown_Trading_Relationship  = 'unknown-trading-relationship'
    Unknown_Trading_Partner       = 'unknown-trading-partner'

# ################################################################################################################################
# ################################################################################################################################

class Failure:
    """ Failure descriptions for "failed/Failure:" dispositions, which RFC 4130 reserves
    for problems with the MDN request itself rather than with content processing.
    """
    Unsupported_Format         = 'unsupported format'
    Unsupported_MIC_Algorithms = 'unsupported MIC-algorithms'

# ################################################################################################################################
# ################################################################################################################################

class DigestAlgorithm:
    """ Digest algorithms for signatures and MIC values, in their RFC 5751 spelling.
    SHA-1 exists only for partners that require it and cannot do better.
    """
    SHA1   = 'sha-1'
    SHA256 = 'sha-256'
    SHA384 = 'sha-384'
    SHA512 = 'sha-512'

# ################################################################################################################################
# ################################################################################################################################

class EncryptionAlgorithm:
    """ Content encryption algorithms for outgoing messages. The AES-CBC ones are the interop baseline,
    the GCM ones use CMS AuthEnvelopedData and are opt-in per partner, never the default.
    3DES exists for partners that cannot decrypt AES and for interoperability certification events,
    never the default either.
    """
    AES_128_CBC  = 'aes-128-cbc'
    AES_256_CBC  = 'aes-256-cbc'
    AES_128_GCM  = 'aes-128-gcm'
    AES_256_GCM  = 'aes-256-gcm'
    DES_EDE3_CBC = 'des-ede3-cbc'

# ################################################################################################################################
# ################################################################################################################################

class MDNMode:
    """ How the receiver is to deliver its MDN - not at all, on the HTTP response,
    or asynchronously to a separate URL.
    """
    None_ = 'none'
    Sync  = 'sync'
    Async = 'async'

# ################################################################################################################################
# ################################################################################################################################

class TransferMode:
    """ How the HTTP request body is framed - with a Content-Length header, with chunked
    transfer encoding, or with chunking only above a configurable size threshold.
    """
    Content_Length = 'content-length'
    Chunked        = 'chunked'
    Threshold      = 'threshold'

# ################################################################################################################################
# ################################################################################################################################

class DeliveryKind:
    """ The reliability taxonomy every recorded delivery attempt says which of it was - the first
    attempt at a document, a retry of an attempt that never reached the partner, a resend of one
    that reached it without a receipt coming back, or an operator resubmit.

    A retry and a resend both carry the same content under the same Message-ID, which is what
    makes the receiver's duplicate detection the thing that decides whether the document is
    delivered once or twice. They are told apart by what the original attempt achieved: a retry
    follows an attempt with no successful HTTP exchange behind it, a resend follows one the
    partner accepted and then never answered with an MDN. A resubmit is the operator action
    that deliberately delivers the content again as a new message.
    """
    Original = 'original'
    Retry    = 'retry'
    Resend   = 'resend'
    Resubmit = 'resubmit'

# ################################################################################################################################
# ################################################################################################################################

class Default:
    """ Default algorithm and configuration choices for outgoing messages.
    """
    Digest_Algorithm     = DigestAlgorithm.SHA256
    Encryption_Algorithm = EncryptionAlgorithm.AES_256_CBC

    # The AS2-Version header value of outgoing messages - pinnable per partner for peers
    # that require an older value, while inbound never rejects on version
    # and an absent version means 1.0.
    AS2_Version = '1.2'

    # The Content-Type of outgoing payloads unless the partnership names another one.
    Content_Type = 'application/edi-x12'

    # The Subject header of outgoing messages.
    Subject = 'AS2 message'

    # How long outbound HTTP requests may take, in seconds.
    HTTP_Timeout_Seconds = 60

    # Above this many bytes the threshold transfer mode switches to chunked framing.
    Chunked_Threshold_Bytes = 10 * 1024 * 1024

    # What every outgoing message advertises in its EDIINT-Features header - real capabilities
    # only, informational per its RFC, and inbound values never drive behavior.
    #
    # multiple-attachments is the multipart/related payload of outbound.py, which inbound.py
    # unwraps document by document. AS2-Reliability is the pair that makes a lost receipt
    # recoverable: the same-Message-ID resend of resend.py on our side, and the replay detection
    # of duplicates.py on the receiving side, which is what keeps a partner's own resend from
    # delivering a document twice.
    EDIINT_Features = 'multiple-attachments, AS2-Reliability'

    # How many days after a next certificate's activation date its rotation is completed
    # in the stored configuration - the window keeps inbound messages signed
    # with the old certificate verifiable shortly after the cutover.
    Rotation_Grace_Days = 1

# ################################################################################################################################
# ################################################################################################################################

class AS2Exception(Exception):
    """ Base class for all AS2-related exceptions.
    """

# ################################################################################################################################
# ################################################################################################################################

class AS2ProtocolException(AS2Exception):
    """ Raised when an incoming message violates the AS2 rules. Carries the RFC 4130 disposition modifier
    so that the inbound pipeline can produce the matching MDN disposition.
    """
    def __init__(self, modifier:'str', detail:'str') -> 'None':
        super().__init__(f'{modifier} {detail}')
        self.modifier = modifier
        self.detail = detail

# ################################################################################################################################
# ################################################################################################################################

class AS2SecurityException(AS2ProtocolException):
    """ Raised when signature verification, decryption or certificate validation fails.
    """

# ################################################################################################################################
# ################################################################################################################################

class AS2MalformedCMSException(AS2Exception):
    """ Raised when a CMS structure does not parse as valid DER at all. The call sites translate it
    into the disposition matching their context - integrity-check-failed for signatures,
    decryption-failed for envelopes, decompression-failed for compressed entities.
    """

# ################################################################################################################################
# ################################################################################################################################

def is_digest_equal(left:'str', right:'str') -> 'bool':
    """ Compares two digests in their base64 wire form without leaking where they first differ.

    One side of every such comparison is supplied by a remote party - the Received-Content-MIC of
    an incoming MDN against the value computed at send time, or the message-digest attribute of a
    signature against the digest of the content it covers. A plain string comparison returns as
    soon as it finds a difference, which tells a peer prepared to measure how much of a guessed
    digest was right, so the comparison runs in constant time instead.
    """
    # The values travel as base64 text, while a constant-time comparison needs bytes -
    # a peer is free to send anything at all in that header, encoding included.
    left_bytes = left.encode('utf8', 'replace')
    right_bytes = right.encode('utf8', 'replace')

    out = compare_digest(left_bytes, right_bytes)
    return out

# ################################################################################################################################
# ################################################################################################################################
